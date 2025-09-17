from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.index, name='index'),
    # path('blog/', views.blog, name='blogs'),
    path('chat/', views.chat, name='chat'),
    path("choose-creation/", views.choose_creation_mode, name="choose_creation"),
    path("product-by-ai/", views.product_by_ai, name="product_by_ai"),  # new AI page
    path('history/', views.chat_history, name='chat_history'),
    path('create-product/', views.create_product, name='create_product'),
    path('api/products/', views.get_products, name='get_products'),
    path('api/filter-products/', views.filter_products, name='filter_products'),
    path('trigger-retrieve/', views.trigger_retrieve, name='trigger_retrieve'),  # Add this line
]