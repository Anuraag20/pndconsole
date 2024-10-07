from rest_framework import routers

from .views import (
        MessageAPI,
)


router = routers.DefaultRouter()
router.register(r'messages', MessageAPI, basename = 'message')

urlpatterns = router.urls
