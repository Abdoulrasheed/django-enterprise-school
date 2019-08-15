from django.conf.urls import include, url
from django.urls import path
from authentication import views
from .views import dashboard

urlpatterns = [
    path('', dashboard, name="admin_dashboard"),
    path('login/', views.login_request, name="process_login"),
    path('logout/', views.logout_request, name="logout_url"),
    ]
    