from . import views
from django.urls import path, include

urlpatterns = [
	path('', views.frontend, name="frontend_home"),
	path('admission/apply', views.process_online_admission, name="apply_online"),
	path('find/classes', views.get_filtered_classes, name="get_filtered_classes"),
	path('admission/status/', views.search_admission_status, name="search_admission_status"),
	path('onlineadmission/download/<str:admID>/download/', views.download_admission, name="download_admission_pdf"),
]