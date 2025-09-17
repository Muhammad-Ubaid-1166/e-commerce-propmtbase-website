from django.contrib import admin
from .models import Product, Conversation


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'name', 'price', 'created_at')  # removed category
    list_filter = ('created_at',)  # removed category
    search_fields = ('product_id', 'name', 'description')
    ordering = ('price',)  # removed category


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'session_id', 'user_message_snippet', 'agent_response_snippet')
    list_filter = ('timestamp',)
    search_fields = ('user_message', 'agent_response', 'session_id')
    readonly_fields = ('user_message', 'agent_response', 'timestamp', 'session_id')
    ordering = ('-timestamp',)

    def user_message_snippet(self, obj):
        return obj.user_message[:50] + "..." if len(obj.user_message) > 50 else obj.user_message

    def agent_response_snippet(self, obj):
        return obj.agent_response[:50] + "..." if len(obj.agent_response) > 50 else obj.agent_response

    user_message_snippet.short_description = 'User Message'
    agent_response_snippet.short_description = 'Agent Response'
