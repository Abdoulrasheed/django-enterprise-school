from .import views
from django.urls import path

urlpatterns = [
	path('', views.home, name="home_page"),
	path('students', views.students_view, name="students_list"),
	path('students/<int:id>', views.students_list_view, name="students_list_view"),
	path('students/add', views.add_student, name="add_student"),
	path('parents', views.parents_view, name="parents_list"),
	path('parents/add', views.parents_view, name="add_parent"),
	path('teachers', views.teachers_view, name="teachers_list"),
	path('teachers/add', views.teachers_view, name="add_teacher"),
	path('class', views.class_view, name="class_list"),
	path('class/add', views.class_view, name="add_class"),
	path('subject/', views.subjects_view, name="subjects_list"),
	path('subject/add', views.subjects_view, name="add_subject"),
	path('api/chart', views.expenditure_graph, name="expense_graph_url"),
	]