from django.conf.urls import include, url
from django.urls import path
from authentication import views
from . import views as su_view

urlpatterns = [
    path('', su_view.dashboard, name="admin_dashboard"),
    path('login/', views.login_request, name="process_login"),
    path('logout/', views.logout_request, name="logout_url"),
    path('schools/', su_view.schools_list, name="schools_list"),
    path('schools/add/', su_view.school_add, name="school_add"),
    path('session_security/', include('session_security.urls')),
    path('schools/view/<int:tenant_id>/', su_view.schools_view, name="school_view"),
    path('schools/add/save/', su_view.school_add_save, name="school_add_save"),
    path('schools/change/<int:tenant_id>/', su_view.school_change, name="school_change"),
    path('schools/change/save/<int:tenant_id>/', su_view.school_change_save, name="school_change_save"),
    path('schools/delete/', su_view.school_del, name="school_del"),
    path('markdownx/', include('markdownx.urls')),
    path('schools/sms/subscription/manage/', su_view.schools_sms_sub, name="schools_sms_sub"),
    path('schools/sms/subscription/manage/update/', su_view.schools_sms_sub_update, name="schools_sms_sub_update"),
    path('schools/backup/<int:tenant_id>/', su_view.site_backup, name="site_backup"),
    ]
    