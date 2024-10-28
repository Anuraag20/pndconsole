from django.urls import re_path

from . import consumers

urlpatterns = [
    re_path(r"ws/pnd/(?P<target>\w+)-(?P<pair>\w+)/$", consumers.PNDConsumer.as_asgi()),
]
