from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views
from . import views as http_verb_views
from .import settings
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('', include('frontend.urls')),
	path('app/', include('sms.urls')),
    path('u/i/admin/', admin.site.urls),
    path('session_security/', include('session_security.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/login/', views.LoginView.as_view(), name='login'),
    path('accounts/logout/', views.LogoutView.as_view(), name='logout', kwargs={'next_page': '/'}),
    ]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = http_verb_views.Handler404.as_view()
handler403 = http_verb_views.Handler403.as_view()