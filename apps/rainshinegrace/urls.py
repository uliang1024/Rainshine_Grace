from django.urls import path
from .views.linebot import callback, send_quiz_to_group

urlpatterns = [
    path("callback", callback, name="callback"),
    path("send_quiz_to_group", send_quiz_to_group, name="send_quiz_to_group"),
]
