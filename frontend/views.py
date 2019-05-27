from django.shortcuts import render
from sms.views import Setting
from django.core.files.storage import FileSystemStorage
from .models import OnlineAdmission
from sms.models import Class, Section
from django.http import HttpResponse
from .forms import OnlineAdmissionForm
from django.shortcuts import redirect

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
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.SystemRandom().choice(chars) for _ in range(size))

def process_online_admission(request):
	setting = Setting.objects.first()
	if request.method == "POST":
		form =  OnlineAdmissionForm(request.POST, request.FILES)
		print(form)
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
				
			admission_id = id_generator()
			print(admission_id)
			return HttpResponse(admission_id)
		else:
			form = OnlineAdmissionForm(request.POST, request.FILES)
			context = {
				'form': form,
				'setting': setting,
			}
			return render(request, 'frontend/home.html', context)
	else:
		return redirect('frontend_home')


