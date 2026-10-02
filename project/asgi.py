import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from django.urls import path
from document.consumers import MyConsumer
from document.middleware import JWTAuthMiddleWare

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
  'http': django_asgi_app,

  "websocket": JWTAuthMiddleWare(
            URLRouter([
                path("doc/<int:id>/", MyConsumer.as_asgi()),
            ])  
    ),
})