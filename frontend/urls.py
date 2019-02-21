from . import views
from django.urls import path, include

urlpatterns = [
	path('', views.frontend, name="frontend_home"),
]