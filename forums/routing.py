from django.urls import re_path

from . import consumers

urlpatterns = [
    re_path(r"(?P<forum>\w+)/$", consumers.ForumConsumer.as_asgi()),
]
