import uuid
import re
import json
from decimal import Decimal, InvalidOperation

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from asgiref.sync import async_to_sync

from shop.agents_logic.agent_service import process_user_query
from .models import Conversation, Product
from .forms import ProductForm


# ==========================================================
# Global state
# ==========================================================
LAST_AGENT_RESPONSE = None


# ==========================================================
# Helpers
# ==========================================================
def convert_to_decimal(price_value):
    """Convert any input to Decimal safely"""
    if price_value is None:
        return Decimal("0.00")

    try:
        if isinstance(price_value, Decimal):
            return price_value

        price_str = str(price_value).strip()
        price_clean = re.sub(r"[^\d.-]", "", price_str)

        return Decimal(price_clean) if price_clean else Decimal("0.00")
    except (InvalidOperation, ValueError, TypeError):
        return Decimal("0.00")


# ==========================================================
# Views
# ==========================================================
def index(request):
    """Main page with product listing and chat interface"""
    products = Product.objects.all()
    return render(request, "shop/index.html", {"products": products})


@csrf_exempt
@require_http_methods(["POST"])
def chat(request):
    """Main chat endpoint (handles text + image uploads)"""
    global LAST_AGENT_RESPONSE

    try:
        # Case 1: Image Upload
        if "image" in request.FILES:
            product_id = request.POST.get("product_id")
            if not product_id:
                return JsonResponse({"error": "Product ID is required"}, status=400)

            try:
                product = Product.objects.get(product_id=product_id)
                product.image = request.FILES["image"]
                product.save()

                return JsonResponse({
                    "success": True,
                    "message": f"✅ Image uploaded successfully for product {product_id}",
                    "image_url": product.image.url if product.image else None,
                    "trigger_upload": False,
                    "product_id": product.product_id,
                    "product_name": product.name,
                    "product_description": product.description,
                    "product_price": str(product.price),
                })
            except Product.DoesNotExist:
                return JsonResponse({"error": f"❌ Product {product_id} not found"}, status=404)

        # Case 2: Normal text chat
        data = json.loads(request.body or "{}")
        user_message = data.get("message", "").strip()
        if not user_message:
            return JsonResponse({"error": "Message cannot be empty"}, status=400)

        # Run AI agent
        agent_response = async_to_sync(process_user_query)(user_message)
        LAST_AGENT_RESPONSE = agent_response

        # Extract response
        is_add = agent_response.get("is_add", False)
        product_id = agent_response.get("product_id")
        name = agent_response.get("product_name")
        price_raw = agent_response.get("product_price")
        description = agent_response.get("product_description")

        product = None

        # If agent confirms product info, create/update Product
        if is_add and name and price_raw:
            if not product_id:
                product_id = str(uuid.uuid4())[:8]

            price_decimal = convert_to_decimal(price_raw)

            product, created = Product.objects.get_or_create(
                product_id=product_id,
                defaults={
                    "name": name,
                    "price": price_decimal,
                    "description": description or "",
                },
            )
            if not created:
                product.name = name
                product.price = price_decimal
                product.description = description or ""
                product.save()

        # Save conversation
        Conversation.objects.create(
            user_message=user_message,
            agent_response=json.dumps(agent_response),
            session_id=str(request.session.session_key or "anonymous"),
        )

        return JsonResponse({
            "success": True,
            "agent_message": agent_response.get("agent_message", "No response"),
            "is_add": is_add,
            "product_id": product_id,
            "product_name": product.name if product else name,
            "product_price": str(product.price) if product else str(convert_to_decimal(price_raw)) if price_raw else None,
            "product_description": product.description if product else description,
            "trigger_upload": is_add and bool(name and price_raw),
        })

    except Exception as e:
        return JsonResponse({"error": f"❌ Error processing request: {str(e)}"}, status=500)


def product_by_ai(request):
    """Render the AI-powered product creation page"""
    products = Product.objects.all()
    return render(request, "shop/product_by_ai.html", {"products": products})


def retrieve_and_render_products(request):
    """Retrieve products based on LAST_AGENT_RESPONSE and render"""
    global LAST_AGENT_RESPONSE

    if not LAST_AGENT_RESPONSE:
        return render(request, "shop/index.html", {
            "error_message": "No agent response found. Please chat first.",
            "product_list": []
        })

    try:
        if hasattr(LAST_AGENT_RESPONSE, "model_dump"):  # Pydantic
            agent_data = LAST_AGENT_RESPONSE.model_dump()
            is_retrieve = check_if_should_retrieve(agent_data)

            if not is_retrieve:
                return render(request, "shop/index.html", {
                    "message": "Agent response does not indicate product retrieval needed.",
                    "product_list": []
                })

            product_names = agent_data.get("product_name", [])
            product_ids = agent_data.get("product_id", [])
            found_products = search_products_in_database(product_names, product_ids)

            return render(request, "shop/index.html", {
                "product_list": found_products,
                "agent_data": agent_data,
                "success_message": f"Found {len(found_products)} products from agent response.",
                "show_products": True,
            })

        else:  # String response
            response_text = str(LAST_AGENT_RESPONSE)
            if "GO AND RUN IT" in response_text:
                product_names = parse_product_names_from_string(response_text)
                found_products = search_products_by_names(product_names)

                return render(request, "shop/index.html", {
                    "product_list": found_products,
                    "success_message": f"Found {len(found_products)} products.",
                    "show_products": True,
                })

            return render(request, "shop/index.html", {
                "message": "Agent response does not contain retrieval trigger.",
                "product_list": []
            })

    except Exception as e:
        return render(request, "shop/index.html", {
            "error_message": f"Error processing agent response: {str(e)}",
            "product_list": []
        })


def check_if_should_retrieve(agent_data):
    """Check if agent response includes product info"""
    return bool(agent_data.get("product_name") or agent_data.get("product_id"))


def search_products_in_database(product_names, product_ids):
    """Search products by names and IDs"""
    found_products = []

    for name in product_names or []:
        if name:
            products = Product.objects.filter(name__icontains=name)
            for product in products:
                product_dict = {
                    "id": product.id,
                    "product_id": product.product_id,
                    "name": product.name,
                    "price": str(product.price),
                    "description": product.description or "",
                    "image_url": product.image.url if product.image else None,
                    "found_by": f"name: {name}",
                }
                if product_dict not in found_products:
                    found_products.append(product_dict)

    for product_id in product_ids or []:
        if product_id:
            try:
                product = Product.objects.get(product_id=product_id)
                product_dict = {
                    "id": product.id,
                    "product_id": product.product_id,
                    "name": product.name,
                    "price": str(product.price),
                    "description": product.description or "",
                    "image_url": product.image.url if product.image else None,
                    "found_by": f"ID: {product_id}",
                }
                if product_dict not in found_products:
                    found_products.append(product_dict)
            except Product.DoesNotExist:
                pass

    return found_products


def search_products_by_names(product_names):
    """Search products by names only"""
    found_products = []

    for name in product_names or []:
        if name:
            products = Product.objects.filter(name__icontains=name)
            for product in products:
                found_products.append({
                    "id": product.id,
                    "product_id": product.product_id,
                    "name": product.name,
                    "price": str(product.price),
                    "description": product.description or "",
                    "image_url": product.image.url if product.image else None,
                    "found_by": f"name: {name}",
                })

    return found_products


def parse_product_names_from_string(response_text):
    """Extract product names from raw agent string response"""
    product_names = []
    for line in response_text.split("\n"):
        if "Name:" in line:
            name_part = line.split("Name:")[-1].strip()
            if name_part:
                product_names.append(name_part)
    return product_names


def trigger_retrieve(request):
    """Manual trigger for product retrieval"""
    return retrieve_and_render_products(request)


def chat_history(request):
    """Return last 10 chat history entries"""
    try:
        conversations = Conversation.objects.all()[:10]
        history = [{
            "id": conv.id,
            "user_message": conv.user_message,
            "agent_response": conv.agent_response,
            "timestamp": conv.timestamp.isoformat(),
        } for conv in conversations]
        return JsonResponse({"history": history})
    except Exception:
        return JsonResponse({"history": []})


def choose_creation_mode(request):
    """Page to choose between manual creation and AI creation"""
    return render(request, "shop/choose_creation.html")


@csrf_exempt
def create_product(request):
    """Handle creation of a new product"""
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True, "message": "✅ Product created successfully!"})
        return JsonResponse({"success": False, "errors": form.errors})

    initial_data = {
        "product_id": request.GET.get("product_id", ""),
        "name": request.GET.get("name", ""),
        "description": request.GET.get("description", ""),
        "price": request.GET.get("price", ""),
    }
    form = ProductForm(initial=initial_data)
    return render(request, "shop/create_product.html", {"form": form})


def get_products(request):
    """Return all products as JSON"""
    products = Product.objects.all()
    product_list = [{
        "id": product.id,
        "product_id": product.product_id,
        "name": product.name,
        "price": str(product.price),
        "description": product.description or "",
        "image_url": product.image.url if product.image else None,
        "created_at": product.created_at.isoformat(),
    } for product in products]
    return JsonResponse({"products": product_list})


@csrf_exempt
def filter_products(request):
    """Filter products by name"""
    if request.method == "POST":
        data = json.loads(request.body or "{}")
        name = data.get("name")

        if name and name != "all":
            products = Product.objects.filter(name__icontains=name)
        else:
            products = Product.objects.all()

        product_list = [{
            "id": product.id,
            "product_id": product.product_id,
            "name": product.name,
            "price": str(product.price),
            "description": product.description or "",
            "image_url": product.image.url if product.image else None,
        } for product in products]

        return JsonResponse({"products": product_list})

    return JsonResponse({"error": "Invalid request method"})
