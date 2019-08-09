from schools.views import TenantView, TenantViewRandomForm, TenantViewFileUploadCreate
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views
from sms.views import change_password

urlpatterns = [
    path('', include('frontend.urls')),
    path('', include('pwa.urls')),
	path('app/', include('sms.urls')),
    path('u/i/admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/login/', views.LoginView.as_view(), name='login'),
    path('change-password/', change_password, name="change_password"),
    path('accounts/logout/', views.LogoutView.as_view(), name='logout', kwargs={'next_page': '/'}),
    ]
