from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .decorators import teacher_required, student_required, parent_required
from .models import *
from django.core import serializers

@login_required
def home(request):
	return render(request, 'sms/home.html', {})

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

def students_view(request):
	classes = Class.objects.all()
	context = {"classes": classes}
	return render(request, 'sms/students.html', context)

def students_list_view(request, id):
	students = ()
	if request.is_ajax():
		students = Student.objects.filter(in_class__pk=id)
		classes = Class.objects.all()
		ss = ()
		for i in students:
			ss += (i.user.first_name, i.user.get_picture(), i.user.last_name, i.roll_number, i.user.email, i.user.is_active)
		print(ss)
		context = {
			"classes": "classes",
			"students": ss,
		}
		return JsonResponse(context)

def teachers_view(request):
	teachers = User.objects.filter(is_teacher=True)
	context = {
		'teachers': teachers,
	}
	return render(request, 'sms/teachers.html', context)


def parents_view(request):
	parents = User.objects.filter(is_parent=True)
	context = {
		'parents': parents,
	}
	return render(request, 'sms/parents.html', context)

def class_view(request):
	classes = Class.objects.all()
	context = {
		'classes': classes,
	}
	return render(request, 'sms/class.html', context)

def subjects_view(request):
	subjects = Subject.objects.all()
	context = {
		'subjects': subjects,
	}
	return render(request, 'sms/subjects.html', context)