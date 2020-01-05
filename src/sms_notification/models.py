from django.db import models
from utils.constants import PENDING, STATUS
from django.utils.translation import ugettext_lazy as _

class Sms(models.Model):
	to_user 	= models.CharField(_('To User'), max_length=10)
	title 		= models.CharField(_('Title'), max_length=100)
	date_send 	= models.DateTimeField(_('Date Send'), auto_now_add=True)
	body 		= models.CharField(_('Body'), max_length=250)
	status 		= models.CharField(_('Status'), max_length=1, choices=STATUS, default=PENDING)

	class Meta:
		verbose_name 		= _("Send Notification")
		verbose_name_plural = _("Send Notifications")

	def __str__(self):
		return self.title

class Setting(models.Model):
	available_unit	= models.IntegerField(_('Available Unit'), default=500)
	show_grade 		= models.BooleanField(_('Show Grade'), default=True)
	show_position 	= models.BooleanField(_('Show Position'), default=True)
	show_promotion_status = models.BooleanField(_('Show promotion status'), default=False)
	sms_prefix		= models.CharField(_('SMS Prefix'), max_length=20, blank=True, null=True)
	sms_suffix		= models.CharField(_('SMS Suffix'), max_length=20, blank=True, null=True)
	sender_id		= models.CharField(_('SMS Sender ID'), max_length=20, blank=True, null=True)

	def __str__(self):
		return self.sender_id


	class Meta:
		verbose_name 		= _("Notification Setting")
		verbose_name_plural = _("Notifications Setting")