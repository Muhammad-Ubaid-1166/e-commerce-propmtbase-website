from django.db import models
from django.utils import timezone

class Product(models.Model):
    """Product model for storing product information"""

    product_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} - ${self.price}"

    @property
    def price_display(self):
        return f"${self.price}"

    class Meta:
        ordering = ['price']


class Conversation(models.Model):
    """Model to store user conversations with the AI agent"""
    user_message = models.TextField()
    agent_response = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    session_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Chat {self.id} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-timestamp']
