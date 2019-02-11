import datetime
from django.conf import settings
from sms.models import Setting, Session, Notification
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage

y = datetime.datetime.today()
session = str(y.year) + " / " + str(y.year + 1)

try:
	s = Session.objects.get(current_session=True)
except Session.DoesNotExist:
	s = Session.objects.create(name=session, current_session=True)
	s.save()

def school_setting_processor(request):
	if request.user.is_anonymous:
		user_type = None
	elif request.user.is_teacher:
		user_type = "Teacher"
	elif request.user.is_parent:
		user_type = "Parent"
	elif request.user.is_student:
		user_type = "Student"
	else:
		user_type = "Administrator"

	notifications = {}
	if not request.user.is_anonymous:
		notifications = Notification.objects.filter(user=request.user)

	current_session = Session.objects.get(current_session=True)
	all_sessions = Session.objects.all()
	default_logo = 'logo.png'
	default_name = "Cosmotech"
	if Setting.objects.filter(id=1).exists():
		logo = Setting.objects.get(id=1)
		school_logo = logo.school_logo.url
		school_name = logo.school_name
	else:
		Setting.objects.create(id=1, school_name=default_name, school_logo=default_logo, school_address="Yola", "Great movement")
		logo = Setting.objects.get(id=1)
		school_logo = logo.school_logo.url
		school_name = logo.school_name

	return {
			"school_name": school_name, 
			"school_logo": school_logo,
			"current_session": current_session, 
			"all_sessions": all_sessions,
			"user_type": user_type,
			"notifications": notifications,
			}

	
