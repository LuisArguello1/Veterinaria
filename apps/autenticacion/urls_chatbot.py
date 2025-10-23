"""
URLs para la integración con el chatbot
"""
from django.urls import path
from .views.chatbot_views import get_chatbot_token

# URLs específicas para la integración del chatbot
urlpatterns = [
    path('get-chatbot-token/', get_chatbot_token, name='get_chatbot_token'),
]