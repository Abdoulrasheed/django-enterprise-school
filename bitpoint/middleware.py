from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.http import Http404, HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin

from django_tenants.utils import remove_www_and_dev, get_public_schema_name, get_tenant_domain_model
from django.db import utils
from datetime import date 
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