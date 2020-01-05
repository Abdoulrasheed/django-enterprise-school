from django.urls import path
from .import views

urlpatterns = [
	path('', views.attendance_list, name="attendance_list"),
	path('add/', views.add_attendance, name="add_attendance"),
	path('save/', views.save_attendance, name="save_attendance"),
	path('del<int:id>/', views.delete_attendance, name="delete_attendance"),
]