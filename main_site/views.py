from django.conf import settings
from django.db import utils
from django.views.generic import TemplateView
from django_tenants.utils import remove_www
from schools.models import Client, Domain
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django_tenants.utils import schema_context, schema_exists
from authentication.models import User
from sms.sms_sender import send_sms
from sms.models import Setting, Notification

@login_required(login_url='/login/')
def dashboard(request):
    template = 'authenticated/dashboard.html'
    tenants = Client.objects.all()
    students_count = 0
    for tenant in tenants:
        with schema_context(tenant.schema_name):
            students_count += User.objects.filter(is_student=True).count()
    target = 500 * students_count # N500 times Number of students in all tenants
    context = {"tenants_count": tenants.count()}
    context['students_count'] = students_count
    context['target'] = target
    return render(request, template, context)

@login_required(login_url='/login/')
def schools_list(request):
    context = {}
    tenants_list = Client.objects.exclude(schema_name='public')
    context['tenants_list'] = tenants_list
    template = 'authenticated/schools_list.html'
    return render(request, template, context)

@login_required(login_url='/login/')
def school_add(request):
    template = 'authenticated/schools_add.html'
    return render(request, template, {})

@login_required(login_url='/login/')
def school_add_save(request):
    if request.is_ajax():
        data = request.GET

        #tenant related data
        school_name = data.get('school_name')
        subdomain = data.get('subdomain')
        description = data.get('description')
        on_trial = data.get('ontrial')
        active_until = data.get('active_until')

        # user related data
        admin_email = data.get('email')
        phone = data.get('phone')
        username = data.get('username')
        password = data.get('password')

        if (' ' in subdomain) == True:
            return HttpResponse(1) # error 1 means space is present in subdomain

        if (' ' in username) == True:
            return HttpResponse(2) # error 2 means space is present in username

        if schema_exists(subdomain):
            return HttpResponse(3) # client already exist
        else:
            tenant = Client(schema_name=subdomain,
                    name=subdomain,
                    description=description,
                    on_trial=False,
                    active_until=active_until)
            tenant.save() # migrate_schemas will automatically be called

            # Create Domain
            domain = Domain()
            domain.domain = '{}.bitpoint.com'.format(subdomain)
            domain.tenant = tenant
            domain.is_primary = True
            domain.save()

            with schema_context(tenant.schema_name):
                admin = User.objects.create_superuser(
                    username=username,
                    password=password,
                    email=admin_email,
                    phone=phone
                )
                Setting.objects.create(
                    school_name=school_name, 
                    business_email=admin_email,
                    business_phone1=phone).save()
                Notification.objects.create(
                    user=admin,
                    title='Welcome to Bitpoint inc.',
                    body='Hello {} and  Welcome to Bitpoint Inc., \
                          we wish you and the entire a happy schooling. \
                          Thank you for choosing bitpoint',
                    message_type='Info')
                message = 'Dear {}, Welcome to Bitpoint inc.,\
                            please login to http://{}/app\
                            using username: {} and password: {}\
                            '.format(school_name, domain.domain, username, password)
                send_sms(phone=phone, msg=message)
            tenant.school_admin=admin
            tenant.save()
            return HttpResponse('success')

@login_required(login_url='/login/')
def school_change(request, tenant_id):
    if request.method == "GET":
        template = 'authenticated/school_change.html'
        tenant = get_object_or_404(Client, id=tenant_id)
        context = {"tenant": tenant}
        return render(request, template,context)

@login_required(login_url='/login/')   
def school_change_save(request, tenant_id):
    if request.is_ajax():
        data = request.GET

        #tenant related data
        school_name = data.get('school_name')
        subdomain = data.get('subdomain')
        description = data.get('description')
        on_trial = data.get('ontrial')
        active_until = data.get('active_until')

        # user related data
        admin_email = data.get('email')
        phone = data.get('phone')
        username = data.get('username')
        password = data.get('password')

        if (' ' in subdomain) == True:
            return HttpResponse(1) # error 1 means space is present in subdomain

        if (' ' in username) == True:
            return HttpResponse(2) # error 2 means space is present in username

        if Client.objects.filter(id=tenant_id).exists():
            tenant = Client.objects.get(id=tenant_id)
            tenant.name = school_name
            tenant.description = description
            tenant.on_trial = True
            tenant.active_until = active_until

            with schema_context(tenant.schema_name):
                admin = User.objects.get(username=username)
                admin.password=password
                admin.email=admin_email,
                admin.phone=phone,
                admin.is_superuser=True
                admin.save()
                tenant.school_admin=admin
                tenant.save()

                # update Domain
                domain = Domain.objects.get(tenant_id=tenant_id)
                domain.domain = '{}.bitpoint.com'.format(subdomain)
                domain.tenant = tenant
                domain.is_primary = True
                domain.save()
                return HttpResponse('success')
        else:
            return HttpResponse(3) # client does not exist


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