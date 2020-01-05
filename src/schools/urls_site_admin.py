from django.conf.urls import include, url
from django.urls import path
from django.contrib.auth import views as auth_views
from .import views as views

urlpatterns = [
    path('', views.Dashboard.as_view(), name="admin_dashboard"),
    path('login/', 
        auth_views.LoginView.as_view(), 
        name="login"),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('schools/', views.SchoolList.as_view(), name="schools_list"),
    path('schools/add/', views.school_add, name="school_add"),
    path('session_security/', include('session_security.urls')),
    path('schools/view/<int:tenant_id>/', views.schools_view, name="school_view"),
    path('schools/add/save/', views.school_add_save, name="school_add_save"),
    path('schools/change/<int:pk>/', views.SchoolChangeView.as_view(), name="school_change"),
    path('schools/delete/<int:pk>/', views.SchoolDeleteView.as_view(), name="school_del"),
    path('schools/sms/subscription/manage/', views.SchoolSMSUnitView.as_view(), name="schools_sms_sub"),
    path('schools/sms/subscription/manage/update/', views.schools_sms_sub_update, name="schools_sms_sub_update"),
    path('schools/backup/<int:tenant_id>/', views.site_backup, name="site_backup"),
    ]