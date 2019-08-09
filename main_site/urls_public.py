from django.conf.urls import include, url
from django.urls import path
from .views import MainSiteHomeView
from django.contrib import admin

urlpatterns = [
    path('', MainSiteHomeView.as_view()),
    path('admin/', admin.site.urls),
    ]