from django.urls import path
from .import views


urlpatterns = [
	path('profile/<int:pk>/', views.UserProfileView.as_view(), name="profile"),
	path('student/', views.StudentView.as_view(), name="students_list"),
	path('student/<int:id>/', views.students_list_view, name="students_list_view"),
	path('student/add/', views.AddStudent.as_view(), name="add_student"),
	path('student/edit/<int:id>/', views.update_student, name="edit_student"),
	path('del/<int:id>/', views.delete_user, name="delete_user"),
	path('parent/', views.parents_view, name="parents_list"),
	path('parent/add/', views.add_parent, name="add_parent"),
	path('teacher/', views.TeacherView.as_view(), name="teachers_list"),
	path('teacher/add/', views.AddTeacherView.as_view(), name="add_teacher"),
	path('teacher/edit/<int:id>/', views.update_teacher, name="update_teacher"),
	path('admin/', views.system_admin, name="system_admin"),
	path('admin/add/', views.add_system_admin, name="add_system_admin"),
	path('changepassword/', views.change_password, name="change_password"),
	path('users_password/', views.reset_users_password, name="reset_users_password"),
	path('reset/', views.reset_users_password_view, name="reset_users_password_view"),
	path('edit/<int:id>/', views.update_user, name="edit_user"),
	path('toggle/<int:id>/', views.toggle_user_status, name='toggle_user_status'),
	path('upload-profile-picture', views.upload_picture, name="upload_profile_picture"),
	path('getusers/', views.ajax_get_users_list, name='get_users_list'),
	path('import/', views.import_users, name='import_users'),
	path('import/download/', views.download_template, name='download_template_url'),
]