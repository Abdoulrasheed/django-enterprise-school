from django.urls import path
from .import views

urlpatterns = [
	path('promotion/', views.promotion, name="promotion_list"),
	path('promotion/load_class_list/', views.to_class_list, name="to_class_list"),
	path('promotion/load_promotion_list', views.load_promotion_list, name="load_promotion_list"),
	path('promotion/promote/\
		<int:stud_id>/\
		<int:to_class_id>/\
		<int:to_session_id>/', views.promote, name="promote"),
]