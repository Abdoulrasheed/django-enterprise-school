from .import settings
from django.contrib import admin
from django.contrib.auth import views
from django.urls import path, include
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from sms.views import change_password

urlpatterns = [
	path('', include('frontend.urls')),
	path('app/', include('sms.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('change-password/', change_password, name="change_password"),
    path('accounts/login/', views.LoginView.as_view(), name='login'),
    path('accounts/logout/', views.LogoutView.as_view(), name='logout', kwargs={'next_page': '/'}),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'sms.views.handler404'