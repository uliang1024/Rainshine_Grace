from django.contrib import admin
from django.urls import path, include
 
urlpatterns = [
    path('admin/', admin.site.urls),
    path('rainshinegrace/', include('rainshinegrace.urls')) #包含應用程式的網址
]