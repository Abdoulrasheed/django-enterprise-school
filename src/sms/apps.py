from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SmsConfig(AppConfig):
    name = 'sms'
    verbose_name = _('School Core')

    def ready(self):
    	import sms.signals  # noqa