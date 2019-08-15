from django.conf.urls import include, url
from django.urls import path
from authentication import views

urlpatterns = [
    path('', views.dashboard, name="admin_login"),
    path('login/', views.login_request, name="process_login"),
    path('logout/', views.logout_request, name="logout_url"),
    ]
    