from rest_framework.routers import DefaultRouter

from .views import (
        MessageAPI,
)


router = DefaultRouter()
router.register(r'messages', MessageAPI, basename = 'message')

urlpatterns = router.urls
