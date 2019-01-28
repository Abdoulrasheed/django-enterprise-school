from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .decorators import teacher_required, student_required, parent_required
from .models import *
from django.core import serializers

@login_required
def home(request):
	return render(request, 'sms/home.html', {})

@login_required
def expenditure_graph(request):
	payments_received = 1000
	expenditure = 13233

	current_session = Session.objects.get(current_session=True)
	labels = ["Income", "Expensediture"]
	data = [payments_received, expenditure]
	data = {
		"labels": labels,
		"data_to_send": data,
		"current_session": current_session.name,
		}
	return JsonResponse(data)

@login_required
def students_view(request):
	classes = Class.objects.all()
	context = {"classes": classes}
	return render(request, 'sms/students.html', context)


@login_required
def students_list_view(request, id):
	students = ()
	if request.is_ajax():
		students = Student.objects.filter(in_class__pk=id)
		classes = Class.objects.all()
		record = ()
		for student in students:
			record += (student.user.get_full_name(), student.user.get_picture(), student.roll_number, student.user.email, student.user.is_active)
		context = {
			"classes": "classes",
			"students": record,
		}
		return JsonResponse(context)


@login_required
def add_student(request):
	classes = Class.objects.all()
	return render(request, 'sms/add_student.html', {"classes": classes})


@login_required
def teachers_view(request):
	teachers = User.objects.filter(is_teacher=True)
	context = {
		'teachers': teachers,
	}
	return render(request, 'sms/teachers.html', context)


@login_required
def parents_view(request):
	parents = User.objects.filter(is_parent=True)
	context = {
		'parents': parents,
	}
	return render(request, 'sms/parents.html', context)

@login_required
def class_view(request):
	classes = Class.objects.all()
	context = {
		'classes': classes,
	}
	return render(request, 'sms/class.html', context)


@login_required
def subjects_view(request):
	subjects = Subject.objects.all()
	context = {
		'subjects': subjects,
	}
	return render(request, 'sms/subjects.html', context)