from django.contrib import admin
from django.urls import path, include

urlpatterns = [
	path('', include('clc_main.urls')),
    path('admin/', admin.site.urls),
]
