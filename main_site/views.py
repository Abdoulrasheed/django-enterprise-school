from django.conf import settings
from django.db import utils
from django.views.generic import TemplateView
from django_tenants.utils import remove_www
from schools.models import Client, Domain
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django_tenants.utils import schema_context, schema_exists
from authentication.models import User
from sms.sms_sender import send_sms
from sms.models import Setting, Notification
from django.contrib import messages

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
def schools_view(request, tenant_id):
    context = {}
    template = 'authenticated/school_view.html'
    school = get_object_or_404(Client, id=tenant_id)
    context['school'] = school
    with schema_context(school.schema_name):
        no_students = User.objects.filter(is_student=True).count()
        no_teachers = User.objects.filter(is_teacher=True).count()
        no_parents = User.objects.filter(is_parent=True).count()
        setting = Setting.objects.first()

        context['no_students'] = no_students
        context['no_parents'] = no_parents
        context['no_teachers'] = no_teachers
        context['setting'] = setting
    return render(request, template, context)

@login_required(login_url='/login/')   
def school_change_save(request, tenant_id):
    from .forms import UpdateSchoolForm
    if request.method == "POST":
        form = UpdateSchoolForm(request.POST)
        if form.is_valid():
            #tenant related data
            school_name = form.cleaned_data.get('school_name')
            subdomain = form.cleaned_data.get('subdomain')
            description = form.cleaned_data.get('description')
            on_trial = form.cleaned_data.get('ontrial')
            active_until = form.cleaned_data.get('active_until')

            # user related data
            admin_email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')
            phone = form.cleaned_data.get('phone')
            password = form.cleaned_data.get('password')
            user_id = form.cleaned_data.get('user_id')

            if Client.objects.filter(id=tenant_id).exists():
                tenant = Client.objects.get(id=tenant_id)
                tenant.name = school_name
                tenant.description = description
                if on_trial is not None:
                    tenant.on_trial = True
                else:
                    tenant.on_trial = False
                tenant.active_until = active_until

                with schema_context(tenant.schema_name):
                    admin = User.objects.get(id=user_id)
                    if password is not None:
                        admin.password=password
                    admin.email=admin_email
                    admin.phone=phone
                    admin.save()
                    tenant.school_admin=admin
                    tenant.save()

                    # update Domain
                    domain = Domain.objects.get(tenant_id=tenant_id)
                    if subdomain is not None:
                        domain.domain = '{}.bitpoint.com'.format(subdomain)
                    domain.tenant = tenant
                    domain.is_primary = True
                    domain.save()
                messages.success(request, 'Updated Successfully !')
                return redirect('school_change', tenant_id=tenant_id)
            else:
                print('Http404')
                raise Http404
        else:
            tenant = get_object_or_404(Client, id=tenant_id)
            form = UpdateSchoolForm(request.POST)
            template = "authenticated/school_change.html"
            message = form
            context =  {
                "form": form,
                "message": message,
                "tenant": tenant,
            }
            return render(request, template, context)
    else:
        print("get")
        return redirect('school_change', tenant_id=tenant_id)

def school_del(request, tenant_id):
    client = get_object_or_404(Client, id=tenant_id)
    
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