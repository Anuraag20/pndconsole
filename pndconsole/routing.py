from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path, include
import pnds.routing
import forums.routing

router = AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                path('ws/pnd/', URLRouter(pnds.routing.urlpatterns)),
                path('ws/forum/', URLRouter(forums.routing.urlpatterns)),
            ])
        )
    )

