from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/vote/(?P<question_id>[0-9a-f-]+)/$', consumers.VoteConsumer.as_asgi()),
] 