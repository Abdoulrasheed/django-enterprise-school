from django.contrib.auth.models import User
from django.db.utils import DatabaseError
from django.views.generic import FormView, TemplateView, CreateView, UpdateView, DeleteView
from .forms import GenerateUsersForm
from .models import Client
from random import choice

from django_tenants.urlresolvers import reverse_lazy

from django.conf import settings
from django.db import utils

from django_tenants.utils import remove_www
from schools.models import Client, Domain
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django_tenants.utils import schema_context, schema_exists
from authentication.models import User
from sms.models import *
from django.contrib import messages
from .forms import UpdateSchoolForm, SchoolDeleteForm, SchoolAddForm
from django.contrib.auth.hashers import check_password, make_password
from .decorators import site_su_required
from django.utils.decorators import method_decorator



@method_decorator(site_su_required, name='dispatch')
class Dashboard(TemplateView):
    template_name = 'schools/dashboard.html'

    def get_context_data(self, **kwargs):
        tenants = Client.objects.exclude(schema_name='public')
        students_count = 0
        for tenant in tenants:
            with schema_context(tenant.schema_name):
                students_count += User.objects.filter(is_student=True).count()

        target = 500 * students_count # N500 times Number of students in all tenants

        context = super().get_context_data(**kwargs)
        context["tenants_count"]  = tenants.count()
        context['students_count'] = students_count
        context['tenants_list']   = tenants
        return context


@method_decorator(site_su_required, name='dispatch')
class SchoolList(TemplateView):
    template_name = 'schools/schools_list.html'

    def get_context_data(self, **kwargs):
        tenants_list = Client.objects.exclude(schema_name='public')
        context = super().get_context_data(**kwargs)
        context['object_list'] = tenants_list
        return context


@login_required(login_url='/login/')
@site_su_required
def school_add(request):
    template = 'schools/schools_add.html'
    return render(request, template, {})

import re
def special_match(strg, search=re.compile(r'[^a-z0-9.]').search):
    return not bool(search(strg))


@method_decorator(site_su_required, name='dispatch')
class SchoolAddView(CreateView):
    model = Client
    form_class = UpdateSchoolForm
    template_name_suffix = '_form'

@login_required(login_url='/login/')
@site_su_required
def school_add_save(request):
    if request.is_ajax():
        print(request.POST)
        if request.method == "POST":
            form = SchoolAddForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                #tenant related data
                school_name = data.get('name')
                subdomain = data.get('domain')
                description = data.get('description')
                on_trial = data.get('ontrial')
                active_until = data.get('active_until')

                # user related data
                admin_email = data.get('email')
                phone = data.get('phone')
                username = data.get('username')
                password = data.get('password')

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
                    domain.domain = subdomain
                    domain.tenant = tenant
                    domain.is_primary = True
                    domain.save()
                    return HttpResponse('success')
            else:
                form = SchoolAddForm(request.POST)
                template = "schools/ajax/school_add_form_not_valid.html"
                context =  {
                    "form": form,
                }
                return render(request, template, context)
        else:
            return HttpResponse('Get')



@method_decorator(site_su_required, name='dispatch')
class SchoolChangeView(UpdateView):
    template_name_suffix = '_form'
    model = Client
    form_class = UpdateSchoolForm

@login_required(login_url='/login/')
@site_su_required
def schools_view(request, tenant_id):
    context = {}
    template = 'schools/school_view.html'
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
@site_su_required
def schools_sms_sub_update(request):
    if request.is_ajax():
        tenant_id = request.GET.get('tenant_id')
        added_unit = request.GET.get('sms_unit')
        tenant = Client.objects.get(id=tenant_id)
        with schema_context(tenant.schema_name):
            from sms_notification.models import SMS_Configuration
            obj, created = SMS_Configuration.objects.update_or_create(available_unit=added_unit)
            if created:
                obj.save()
        return HttpResponse(obj.available_unit)


@method_decorator(site_su_required, name="dispatch")
class SchoolSMSUnitView(TemplateView):
    model = Client
    template_name = 'schools/schools_sms_sub.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = Client.objects.exclude(schema_name='public')
        return context


@login_required(login_url='/login/')
@site_su_required
def site_backup(request, tenant_id):
    # TODO, Not working yet
    from django.contrib.contenttypes.models import ContentType
    import csv
    tenant = get_object_or_404(Client, id=tenant_id)
    with schema_context(tenant.schema_name):
        # Backup individual table as excel
        content_types = ContentType.objects.filter(app_label='sms')
        for model in content_types:
            model_objects = model.model_class().objects.all() # eg User.objects.all()
            if model_objects:
                fields = []
                print('================================{}=================='.format(model.model))
                # get list of fields (columns) for each model (table)
                # eg for class table will data like below 
                # ['student', 'subjectassign', 'feetype', 'id', 'name', 'section', 'amount_to_pay', 'subjects']
                fields = [field.name for field in model_objects.first()._meta.get_fields()]
                values = [value for value in model_objects.all()]
                print(values)
                response = HttpResponse(model_objects , content_type='application/vnd.ms-excel;charset=utf-8')
                response['Content-Disposition'] = 'attachment; filename="{}.xls"'.format(model.model)

                writer = csv.writer(response, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(fields[3:])
                for data in model_objects:
                    writer.writerow(values)
        return response



@method_decorator(site_su_required, name='dispatch')
class SchoolDeleteView(DeleteView):
    model = Client
    def delete(self, request, *args, **kwargs):
        password = request.POST.get('password', None)
        #if check_password(request.user.password, password): not working, issue with hashers
        if password:
            self.get_object().delete()
            tenants = Client.objects.exclude(schema_name='public')
            ct = {'object_list': tenants}
            return render(request, 'schools/ajax/update_schools_table.html', ct)
        else:
            return HttpResponse('incorrect_password')


class TenantViewFileUploadCreate(CreateView):
    pass
#     template_name = "upload_file.html"
#     model = UploadFile
#     fields = ['filename']
#     success_url = reverse_lazy('upload_file')

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['tenants_list'] = Client.objects.all()
#         context['upload_files'] = UploadFile.objects.all()
#         return context

