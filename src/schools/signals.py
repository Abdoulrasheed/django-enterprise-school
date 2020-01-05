from django_tenants.signals import post_schema_sync
from django_tenants.models import TenantMixin
from django_tenants.utils import schema_context, schema_exists
from django.dispatch import receiver


@receiver(post_schema_sync, sender=TenantMixin)
def created_client(sender, **kwargs):
	import datetime
	from django.conf import settings
	from sms.models import Setting, Session
	from sms_notification.models import Setting as sms_setting
	from django.contrib.auth.models import Group
	from django.contrib.auth import get_user_model
	client = kwargs['tenant']
	default_groups = \
	[
		Group(name="admin"),
		Group(name="student"),
		Group(name="parent"),
		Group(name="teacher")
	]

	date = datetime.datetime.today()
	session = "{} / {}".format(date.year, date.year + 1)
	
	with schema_context(client.name):
		g = Group.objects.bulk_create(default_groups)
		get_user_model().objects.create_superuser(
			username=client, 
			password=client, email="example.com")

		Session.objects.create(name=session, current_session=True)
		today = date.today()
		Setting.objects.create(
			school_name=client.name,
			ft_begins=today,
			ft_ends=today,
			st_begins=today,
			st_ends=today,
			tt_begins=today,
			tt_ends=today)
		sms_setting.objects.create(
			sender_id=client
		)