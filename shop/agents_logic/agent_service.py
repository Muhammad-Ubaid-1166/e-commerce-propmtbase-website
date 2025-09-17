from dataclasses import dataclass
import os
import asyncio
import logging
from typing import Any
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool, set_tracing_disabled, RunContextWrapper, ModelSettings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from pydantic import BaseModel
from asgiref.sync import sync_to_async
from dotenv import load_dotenv
from shop.models import Product

# ===============================
# Setup
# ===============================
load_dotenv()  
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not set.")

set_tracing_disabled(disabled=True)

external_client: AsyncOpenAI = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

llm_model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

logger = logging.getLogger(__name__)

# ===============================
# Data Schema
# ===============================
class product_information(BaseModel):
    product_id: str = ""
    product_name: str = ""
    product_price: str = ""
    product_description: str = ""
    product_image: str = ""
    is_add: bool = False

# ===============================
# Tools
# ===============================
@function_tool
def extract_product_info(wrapper: RunContextWrapper[product_information], user_input: str):
    """Extract product information from user input only when user explicitly wants to add a product"""
    user_lower = user_input.lower()
    
    # Only process if user explicitly mentions adding/creating a product
    if any(keyword in user_lower for keyword in ["add product", "create product", "new product", "make product"]):
        # Extract name
        if "name:" in user_lower or "called" in user_lower:
            lines = user_input.split('\n')
            for line in lines:
                if "name:" in line.lower():
                    wrapper.context.product_name = line.split("name:")[-1].strip()
                elif "called" in line.lower():
                    words = line.split()
                    if "called" in words:
                        idx = words.index("called")
                        if idx + 1 < len(words):
                            wrapper.context.product_name = words[idx + 1]
        
        # Extract price
        if "$" in user_input:
            import re
            price_match = re.search(r'\$(\d+(?:\.\d{2})?)', user_input)
            if price_match:
                wrapper.context.product_price = price_match.group(1)
        
        # Extract description
        if "description:" in user_lower:
            lines = user_input.split('\n')
            for line in lines:
                if "description:" in line.lower():
                    wrapper.context.product_description = line.split("description:")[-1].strip()
        
        # Set is_add to True only if user explicitly requested product creation
        wrapper.context.is_add = True
        
        return f"Product information extracted from your request. Name: {wrapper.context.product_name}, Price: ${wrapper.context.product_price}, Description: {wrapper.context.product_description}"
    
    return "I can help you add products. Please say 'add product' or 'create product' and provide the details."

@function_tool
def get_missing_info(wrapper: RunContextWrapper[product_information]):
    """Check what information is missing and ask user for it"""
    data = wrapper.context
    missing = []
    
    if not data.product_name:
        missing.append("product name")
    if not data.product_price:
        missing.append("price")
    if not data.product_description:
        missing.append("description")
    
    if missing:
        return f"I need the following information to create the product: {', '.join(missing)}. Please provide them."
    
    return f"Ready to create product: {data.product_name} for ${data.product_price}"

@function_tool
def confirm_product_creation(wrapper: RunContextWrapper[product_information]):
    """Confirm if all info is ready for product creation"""
    data = wrapper.context
    
    if data.product_name and data.product_price and data.is_add:
        return f"Product ready: {data.product_name} - ${data.product_price}. Description: {data.product_description or 'No description'}"
    
    return "Product information incomplete or not requested."

# ===============================
# Agents
# ===============================
product_add_agent = Agent(
    name="product_manager_agent",
    instructions="""
    You are a product manager assistant. You ONLY create products when users explicitly ask you to add/create products.
    
    Rules:
    1. NEVER automatically create products
    2. ONLY extract product info when user says "add product", "create product", "new product", or similar
    3. Ask for missing information politely
    4. Confirm with user before proceeding
    5. Be helpful but don't assume what the user wants
    
    If user just asks questions or chats normally, respond helpfully but don't try to create products.
    """,
    tools=[extract_product_info, get_missing_info, confirm_product_creation],
    model=llm_model,
)

output_extractor = Agent(
    name="output_extractor",
    instructions="Extract the product information from the conversation context. Only set is_add=True if user explicitly requested product creation.",
    output_type=product_information,
    model=llm_model,
)

async def process_user_query(user_message: str):
    try:
        shared_context = product_information()
        
        # Run the main agent to process user input
        agent_response = await Runner.run(product_add_agent, user_message, context=shared_context)

        # Extract all collected data
        output_response = await Runner.run(output_extractor, f"User said: {user_message}\nAgent response: {agent_response.final_output}", context=shared_context)
        data = output_response.final_output

        # Always return dict
        return {
            "is_add": data.is_add,
            "product_id": data.product_id if data.product_id else None,
            "product_name": data.product_name if data.product_name else None,
            "product_price": data.product_price if data.product_price else None,
            "product_description": data.product_description if data.product_description else None,
            "product_image": data.product_image if data.product_image else None,
            "agent_message": agent_response.final_output
        }
    except Exception as e:
        logger.exception("❌ Unexpected error in process_user_query")
        return {"is_add": False, "error": str(e), "agent_message": "Sorry, I encountered an error."}