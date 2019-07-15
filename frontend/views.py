from django.shortcuts import render
from sms.views import Setting
from django.core.files.storage import FileSystemStorage
from .models import OnlineAdmission
from sms.models import Class, Section, Session
from django.http import HttpResponse
from .forms import OnlineAdmissionForm
from django.shortcuts import redirect
from sms.sms_sender import send_sms
from django.contrib import messages

def frontend(request):
	setting = Setting.objects.first()
	classes = Class.objects.all()
	sections = Section.objects.all()
	context = {
		'setting': setting, 
		'sections': sections,
	}
	return render(request, 'frontend/home.html', context)


def get_filtered_classes(request):
	section = request.GET.get('section')
	classes = Class.objects.filter(section=section)
	return render(request, 'frontend/filtered_classes.html', {'classes': classes})


import string
import random
def admissionNumberCodeGen():
	counter = OnlineAdmission.objects.count()
	admission_no = "{0:05}".format(counter+1)
	return admission_no


def process_online_admission(request):
	setting = Setting.objects.first()
	current_session = Session.objects.get(current_session=True)
	if request.method == "POST":
		form =  OnlineAdmissionForm(request.POST, request.FILES)
		if form.is_valid():
			student_fname = form.cleaned_data.get('student_fname')
			student_lname = form.cleaned_data.get('student_lname')
			student_oname = form.cleaned_data.get('student_oname')
			student_gender = form.cleaned_data.get('student_gender')
			student_address = form.cleaned_data.get('student_address')
			applicant_phone_no = form.cleaned_data.get('applicant_phone_no')
			student_clss = form.cleaned_data.get('student_clss')
			student_email = form.cleaned_data.get('student_email')
			student_passport = form.cleaned_data.get('student_passport')
			student_religion = form.cleaned_data.get('student_religion')
			student_dob = form.cleaned_data.get('student_dob')

			if student_passport:
				fs = FileSystemStorage()
				pic = fs.save(student_passport.name, student_passport)

			admission_no = admissionNumberCodeGen()

			OnlineAdmission.objects.create(
				admission_id=admission_no,
				student_fname=student_fname,
				student_lname=student_lname,
				student_oname=student_oname,
				student_gender=student_gender,
				student_address=student_address,
				student_religion=student_religion,
				student_dob=student_dob,
				student_clss=student_clss,
				applicant_phone_no=applicant_phone_no,
				student_email=student_email,
				student_passport=student_passport,
				session=current_session
			)

			sms_body = 'Hello {} {},\
						your admission request number is {}.\
				 		thank you for applying.'.format(
				 			student_fname, 
				 			student_lname,
				 			admission_no
			)
			send_sms(applicant_phone_no, sms_body)
			messages.success(
				request, 
				'Thank you for applying, we will get back to you soon'
			)
			request.session['code'] = admission_no
			return redirect('/#success')
		else:
			form = OnlineAdmissionForm(request.POST, request.FILES)
			context = {
				'form': form,
				'setting': setting,
			}
			return render(request, 'frontend/home.html', context)
	else:
		return redirect('frontend_home')


def search_admission_status(request):
	if request.is_ajax():
		admission_id = request.GET.get('admission_id')
		admission_id = OnlineAdmission.objects.filter(admission_id=admission_id) or None
		return render(request, 'frontend/search_status.html', {'admission_id': admission_id})