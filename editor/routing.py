from django.urls import re_path
from .consumers import EditorConsumer

websocket_urlpatterns = [
    re_path(r"ws/editor/(?P<room_id>\w+)/$", EditorConsumer.as_asgi()),
]