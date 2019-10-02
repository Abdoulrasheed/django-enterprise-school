from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from django.template.loader import get_template
from django.template.loader import render_to_string

from django_tenants.utils import remove_www_and_dev, get_public_schema_name, get_tenant_domain_model
from django.db import utils
from datetime import date, datetime, timedelta
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

class BitpointTenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.META['SMS-CONTEXT-EXIST'] = False
        connection.set_schema_to_public()
        hostname_without_port = remove_www_and_dev(request.get_host().split(':')[0])
        subdomain = hostname_without_port.split('.')[0]
        sms_context_processor ="sms.context_processors.school_setting_processor"
        context_processors = settings.TEMPLATES[0]['OPTIONS']['context_processors']

        if subdomain == 'admin':
            request.urlconf = settings.ADMIN_URLCONF
            return

        elif subdomain == "www":
            request.urlconf = settings.PUBLIC_SCHEMA_URLCONF
            return

        else:
            try:
                domain = get_tenant_domain_model().objects.select_related('tenant').get(domain=hostname_without_port)
                request.tenant = domain.tenant
                if sms_context_processor not in context_processors:
                    context_processors.append(sms_context_processor)
                request.META['SMS-CONTEXT-EXIST'] = True
            except utils.DatabaseError:
                request.urlconf = settings.PUBLIC_SCHEMA_URLCONF
                return
            except get_tenant_domain_model().DoesNotExist:
                request.urlconf = settings.PUBLIC_SCHEMA_URLCONF
                return

            connection.set_tenant(request.tenant)
            ContentType.objects.clear_cache()

            if hasattr(settings, 'PUBLIC_SCHEMA_URLCONF') and request.tenant.schema_name == get_public_schema_name():
                request.urlconf = settings.PUBLIC_SCHEMA_URLCONF


class BlockUnpaidTenantMiddleware:
    """
        Blocks unpaid tenants or adds warning messages if tenant is about to
        expire soon!
        .. warning:
            This must be placed after
            ``tcms_tenants.middleware.BlockUnauthorizedUserMiddleware`` -
            usually goes at the end.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        dt = datetime.today()
        try:
            active_until = request.tenant.active_until
            todays_date = date(dt.year, dt.month, dt.day)

            if active_until is None or active_until <= todays_date:
                response = '<center>\
                                403 Access Denied <br> \
                                If this is your website \
                                contact bitpoint administrator\
                            </center>'

                return HttpResponseForbidden(response)

            if active_until <= todays_date + timedelta(days=20):
                for msg in messages.get_messages(request):
                    if msg.level_tag == 'warning':
                        break
                else:
                    # will be shown only if no other warnings are present
                    difference = active_until - todays_date
                    messages.warning(request,
                                         _(f'Your subscription expires in {difference.days} days'),
                                         fail_silently=True)

            return self.get_response(request)
        except:
            return self.get_response(request)