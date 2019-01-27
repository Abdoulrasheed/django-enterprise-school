import datetime
from django.conf import settings
from sms.models import Setting, Session
from django.shortcuts import redirect

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

	current_session = Session.objects.get(current_session=True)
	all_sessions = Session.objects.all()
	default_logo = settings.STATIC_URL + 'img/logo.png'
	default_name = "Cosmotech"

	if Setting.objects.all():
		logo = Setting.objects.all()[0]
		logo = logo.school_logo
		school_logo = logo
	else:
		school_logo = default_logo

	if Setting.objects.all():
		name = Setting.objects.all()[0]
		name = name.school_name
		school_name = name
	else:
		school_name = default_name

	return {
			"school_name": school_name, 
			"school_logo": school_logo,
			"current_session": current_session, 
			"all_sessions": all_sessions,
			"user_type": user_type,
			}

	
