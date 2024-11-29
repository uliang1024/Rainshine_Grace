from django.urls import path
from .views.linebot import callback

urlpatterns = [
    path("callback", callback),
]
