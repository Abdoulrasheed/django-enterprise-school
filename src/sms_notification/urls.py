from django.urls import path
from .import views


urlpatterns = [
	path('sms/', views.sms_list, name="sms_list"),
	path('sms/send/', views.send_bulk_sms, name="send_sms"),
	path('mail/', views.mail, name="mail"),
	path('mail/save_draft/', views.save_draft_mail, name="save_draft"),
]