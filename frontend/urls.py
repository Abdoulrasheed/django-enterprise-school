from . import views
from django.urls import path, include

urlpatterns = [
	path('', views.frontend, name="frontend_home"),
	path('admission/apply', views.process_online_admission, name="apply_online"),
	path('find/classes', views.get_filtered_classes, name="get_filtered_classes"),
]