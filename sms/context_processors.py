import datetime
from sms.models import Setting, Session, Notification
from django.core.files.storage import FileSystemStorage

date = datetime.datetime.today()
session = "{} / {}".format(date.year, date.year + 1)

def add_months(sourcedate, months):
	import datetime
	import calendar
	month = sourcedate.month - 1 + months
	year = sourcedate.year + month // 12
	month = month % 12 + 1
	day = min(sourcedate.day, calendar.monthrange(year,month)[1])
	return datetime.date(year, month, day)

def school_setting_processor(request):
	if request.META['SMS-CONTEXT-EXIST']:
		# try getting the current session if exist, otherwise create the current Session
		try:
			current_session = Session.objects.get(current_session=True)
		except Session.DoesNotExist:
			current_session = Session.objects.create(name=session, current_session=True)
			current_session.save()

		# detect the usertype from request
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

		all_sessions = Session.objects.all()
		default_logo = 'logo.png'
		default_name = "Bitpoint Academy"

		try:
		    school_setting = Setting.objects.first()
		except Setting.DoesNotExist:
			school_setting = Setting.objects.create(school_name=default_name,
				school_logo=default_logo,
				school_address="Yola, Nigeria",
				school_slogan="Bringing the future closer the world !",
				ft_begins=date.today(),
				ft_ends=add_months(date.today(), 3),
				st_begins=add_months(date.today(), 4),
				st_ends=add_months(date.today(), 7),
				tt_begins=add_months(date.today(), 8),
				tt_ends=add_months(date.today(), 11)
				)
			school_setting.save()
		return {
			"school_setting": school_setting,
			"current_session": current_session,
			"all_sessions": all_sessions,
			"user_type": user_type,
			"notifications": notifications,
			}
	else:
		return {}