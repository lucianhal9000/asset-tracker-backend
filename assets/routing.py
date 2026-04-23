from django.urls import path
from .consumers import AssetConsumer

websocket_urlpatterns = [
    path('ws/assets/', AssetConsumer.as_asgi()),
]
