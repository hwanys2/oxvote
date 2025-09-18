"""
ASGI config for oxvote project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

# Django settings를 먼저 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oxvote.settings')

# Django ASGI 애플리케이션을 먼저 초기화
django_asgi_app = get_asgi_application()

# Django가 완전히 초기화된 후에 Channels 관련 import
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from voting import routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})
