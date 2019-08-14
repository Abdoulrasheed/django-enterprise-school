from django.conf.urls import include, url
from django.urls import path
from .views import MainSiteHomeView

urlpatterns = [
    path('', MainSiteHomeView.as_view()),
    ]
    