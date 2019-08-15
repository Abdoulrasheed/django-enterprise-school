from django.conf import settings
from django.db import utils
from django.views.generic import TemplateView
from django_tenants.utils import remove_www
from schools.models import Client
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required(login_url='/login/')
def dashboard(request):
    template = 'authenticated/dashboard.html'
    return render(request, template, {})


class MainSiteHomeView(TemplateView):
    template_name = "public/index_public.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        hostname_without_port = remove_www(self.request.get_host().split(':')[0])

        try:
            Client.objects.get(schema_name='public')

        except utils.DatabaseError:
            context['need_sync'] = True
            context['shared_apps'] = settings.SHARED_APPS
            context['tenants_list'] = []
            return context
            
        except Client.DoesNotExist:
            context['no_public_tenant'] = True
            context['hostname'] = hostname_without_port

        if Client.objects.count() == 1:
            context['only_public_tenant'] = True

        context['tenants_list'] = Client.objects.all()
        return context