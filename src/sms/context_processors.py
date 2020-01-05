import datetime
from sms.models import Setting, Session, Notification
from django.core.files.storage import FileSystemStorage
from schools.models import Domain
from django_tenants.utils import remove_www_and_dev

def school_setting_processor(request):
    subdomain = remove_www_and_dev(request.get_host().split(':')[0]).split('.')[0]

    # get list of registered domains
    subdomains = [i.domain for i in Domain.objects.all()]

    if subdomain in subdomains:
    	# try getting the current session if exist, otherwise create the current Session

        session = Session.objects.get_current_session()

        notifications = {}
        if not request.user.is_anonymous:
            notifications = Notification.objects.filter(user=request.user)

        all_sessions = Session.objects.all()

        
        school_setting = Setting.objects.first()

        return {
            "school_setting": school_setting,
            "current_session": session,
            "all_sessions": all_sessions,
            "notifications": notifications,}
    else:
        return {}