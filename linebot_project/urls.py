from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
]

if settings.ENVIRONMENT == "production":
    urlpatterns.append(path("rainshinegrace/", include("rainshinegrace.urls")))
else:
    urlpatterns.append(path("", include("rainshinegrace.urls")))
