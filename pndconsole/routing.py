from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
import pnds.routing


router = AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                pnds.routing.urlpatterns,
            )
        )
    )

