from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .decorators import teacher_required, student_required, parent_required
from .models import *
from django.core import serializers
from datetime import datetime
from .forms import AddStudentForm
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.core.mail import send_mail


@login_required
def home(request):
	no_classes = Class.objects.all().count()
	no_subjects = Subject.objects.all().count()
	no_parents = User.objects.filter(is_parent=True).count()
	no_students = User.objects.filter(is_student=True).count()
	no_teachers = User.objects.filter(is_teacher=True).count()
	context = {
		"no_students": no_students,
		"no_parents": no_parents,
		"no_subjects": no_subjects,
		"no_classes": no_classes,
		"no_teachers": no_teachers,
	}
	return render(request, 'sms/home.html', context)

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
	return render(request, 'sms/student/students.html', context)


def delete_student(request, id):
	user = User.objects.get(pk=id)
	student = Student.objects.get(user__pk=user.pk)
	class_id = student.in_class.pk
	stud_name = student.user.get_full_name()
	user.delete()
	messages.success(request, stud_name + ' Successfully deleted !')
	return redirect('students_list_view', id=class_id)

@login_required
def students_list_view(request, id):
	students = Student.objects.filter(in_class__pk=id)
	selected_class = Class.objects.get(pk=id)
	classes = Class.objects.all()
	context = {
		"selected_class": selected_class,
		"students": students,
		"classes": classes,
	}
	return render(request, 'sms/student/students_list.html', context)

@login_required
def section_view(request):
	sections = Section.objects.all()
	context = {"sections": sections}
	return render(request, 'sms/section/section.html', context)

@login_required
def assign_teacher_view(request):
	assigned_teachers = SubjectAssign.objects.all()
	subjects = Subject.objects.all()
	context = {
	"subjects": subjects,
	"assigned_teachers": assigned_teachers,
	}
	return render(request, 'sms/teacher/assign_teacher.html', context)


@login_required
def add_assign_teacher(request):
	teachers = User.objects.filter(is_teacher=True)
	subjects = Subject.objects.all()
	context = {
	"subjects": subjects,
	"teachers": teachers,
	}
	return render(request, 'sms/teacher/add_assign_teacher.html', context)

@login_required
def assign_section_view(request):
	assigned_sections = SectionAssign.objects.all()
	subjects = Subject.objects.all()
	context = {
	"subjects": subjects,
	"assigned_sections": assigned_sections,
	}
	return render(request, 'sms/section/assign_section.html', context)


@login_required
def add_assign_section(request):
	sections = Section.objects.all()
	teachers = User.objects.filter(is_teacher=True)
	context = {
		"teachers": teachers,
		"sections": sections,
	}
	return render(request, 'sms/section/add_assign_section.html', context)


@login_required
def add_student(request):
	classes = Class.objects.all()
	parents = User.objects.filter(is_parent=True)
	if request.method == "POST":
		form = AddStudentForm(request.POST, request.FILES)
		if form.is_valid():
			stud_username = form.cleaned_data.get('stud_username')
			stud_password = form.cleaned_data.get('stud_password')
			stud_fname = form.cleaned_data.get('stud_fname')
			stud_sname = form.cleaned_data.get('stud_sname')
			stud_oname = form.cleaned_data.get('stud_oname')
			stud_year_of_admission = form.cleaned_data.get('stud_year_of_admission')
			stud_religion = form.cleaned_data.get('stud_religion')
			stud_address = form.cleaned_data.get('stud_address')
			stud_class = form.cleaned_data.get('stud_class')
			stud_gender = form.cleaned_data.get('stud_gender')
			stud_state = form.cleaned_data.get('stud_state')
			stud_email = form.cleaned_data.get('stud_email')
			stud_phone_number = form.cleaned_data.get('stud_phone_number')
			stud_lga = form.cleaned_data.get('stud_lga')
			stud_blood_group = form.cleaned_data.get('stud_blood_group')
			stud_roll_number = form.cleaned_data.get('stud_roll_number')
			stud_dob = form.cleaned_data.get('dob')
			parent_username = form.cleaned_data.get('parent_username')
			parent_password = form.cleaned_data.get('parent_password')
			parent_fname = form.cleaned_data.get('parent_fname')
			parent_sname = form.cleaned_data.get('parent_sname')
			parent_oname = form.cleaned_data.get('parent_oname')
			parent_phone_number = form.cleaned_data.get('parent_phone_number')
			parent_state = form.cleaned_data.get('parent_state')
			parent_address = form.cleaned_data.get('parent_address')
			parent_email = form.cleaned_data.get('parent_email')
			parent_lga = form.cleaned_data.get('parent_lga')

			stud_picture = form.cleaned_data['stud_picture']
			parent_picture = form.cleaned_data['parent_picture']

			existing_parent = form.cleaned_data.get('existing_parent')

			if not '' in [parent_username, parent_password] and not existing_parent == '':
				messages.error(request, 'You cannot select an existing parent and create a new one at same time !')
				return redirect('add_student')
			elif User.objects.filter(username=stud_username):
				messages.error(request, 'A student with that username already exist !')
				return redirect('add_student')
				if User.objects.filter(username=parent_username).exists():
					messages.error(request, 'A parent with that username already exist !')
					return redirect('add_student')
			else:
				if existing_parent == '':
					if '' in [parent_username, parent_password]:
						messages.error(request, 'You need to select a parent or create a new one')
						return redirect('add_student')
					else:
						parent = User.objects.create(
						username = parent_username, 
						password = make_password(parent_password),
						first_name = parent_fname,
						last_name = parent_sname,
						other_name = parent_oname,
						email = parent_email,
						state = parent_state,
						lga =stud_lga,
						address = parent_address,
						phone = parent_phone_number,
						picture = parent_picture,
						is_parent = True,
						)
						send_mail(
						    'Welcome to cosmotech',
						    'we are happy to have you join our school',
						    'noreply@cosmotech.com',
						    ['abdlrasheedibrahim47@gmail.com'],
						    fail_silently=False,
						)
				else:
					parent = existing_parent
					user = User.objects.create(
					username = stud_username, 
					password = make_password(stud_password),
					first_name = stud_fname,
					last_name = stud_sname,
					other_name = stud_oname,
					gender = stud_gender,
					email = stud_email,
					religion = stud_religion,
					state = stud_state,
					lga =stud_lga,
					dob = stud_dob,
					address = stud_address,
					phone = stud_phone_number,
					picture = stud_picture,
					is_student = True,
					)
				selected_class = Class.objects.get(pk=stud_class)
				student = Student.objects.create(
				user=user, 
				in_class=selected_class, 
				year_of_admission=stud_year_of_admission,
				roll_number = stud_roll_number,
				)
				messages.success(request, stud_fname +' Successfully Recorded! ')
				return HttpResponseRedirect(reverse_lazy('add_student'))
				
		else:
			form = AddStudentForm(request.POST)
			message = form
			context =  {
				"form": form, 
				"message": message,
				"parents": parents,
				"classes": classes,
				}
			return render(request, 'sms/student/add_student.html', context)

	else:
		context = {"classes": classes, "parents": parents,}
		return render(request, 'sms/student/add_student.html', context)


@login_required
def add_parent(request):
	return render(request, 'sms/parent/add_parent.html', {})


@login_required
def add_teacher(request):
	return render(request, 'sms/teacher/add_teacher.html', {})

@login_required
def add_class(request):
	sections = Section.objects.all()
	return render(request, 'sms/class/add_class.html', {"sections": sections})

@login_required
def add_subject(request):
	classes = Class.objects.all()
	return render(request, 'sms/subject/add_subject.html', {"classes": classes})

@login_required
def add_section(request):
	return render(request, 'sms/section/add_section.html', {})


@login_required
def teachers_view(request):
	teachers = User.objects.filter(is_teacher=True)
	context = {
		'teachers': teachers,
	}
	return render(request, 'sms/teacher/teachers.html', context)


@login_required
def parents_view(request):
	parents = User.objects.filter(is_parent=True)
	context = {
		'parents': parents,
	}
	return render(request, 'sms/parent/parents.html', context)

@login_required
def class_view(request):
	classes = Class.objects.all()
	context = {
		'classes': classes,
	}
	return render(request, 'sms/class/class.html', context)


@login_required
def subjects_view(request):
	subjects = Subject.objects.all()
	context = {
		'subjects': subjects,
	}
	return render(request, 'sms/subject/subjects.html', context)

@login_required
def attendance_view(request):
	current_session = Session.objects.all(current_session=True)
	in_class = Class.objects.filter(id=id)
	context = {"in_class": classes}
	return render(request, 'sms/student/attendance.html', context)

def attendance_list(request):
	current_session = Session.objects.get(current_session=True)
	if request.method == "POST":
		in_class = Class.objects.all()
		data = request.POST.copy()
		data.pop('csrfmiddlewaretoken')
		data.pop('submit')
		date = data['date']
		term = data['term']
		class_id = data['class']
		date = datetime.strptime(date, '%d %B, %Y')
		students = Student.objects.filter(in_class__pk=class_id)
		ids = ()
		for i in students:
			ids = (i.user.pk,)
		q = Attendance.objects.filter(date=date, student__user__pk__in=ids, term=term, session=current_session)
		context = {
			"students": students,
			"classes": in_class,
			"attendance": q,
		}
	else:
		in_class = Class.objects.all()
		context = {
			"classes": in_class,
		}
	return render(request, 'sms/student/attendance_list.html', context)

@login_required
def add_attendance(request):
	current_session = Session.objects.get(current_session=True)
	if request.method == "POST":
		in_class = Class.objects.all()
		data = request.POST.copy()
		data.pop('csrfmiddlewaretoken')
		data.pop('submit')
		date = data['date']
		term = data['term']
		class_id = data['class']
		selected_class = Class.objects.get(pk=class_id)
		date = datetime.strptime(date, '%d %B, %Y')
		students = Student.objects.filter(in_class__pk=class_id)
		context = {
			"students": students,
			"classes": in_class,
			"selected_class": selected_class,
			"term": term,
			"date": date,
		}
	else:
		in_class = Class.objects.all()
		context = {
			"classes": in_class,
		}
	return render(request, 'sms/student/add_attendance.html', context)

@login_required
def score_list(request):
	if request.method == "POST":
		selected_class = request.POST['class']
		selected_term = request.POST['term']
		selected_subject = request.POST['subject']
		current_session = Session.objects.filter(current_session=True)
		classes = Class.objects.all()
		students = Student.objects.filter(in_class__name=selected_class)
		s = subjects.objects.filter(class__name=selected_class.id)
		context = {
			"classes": classes,
			#"subjects": subjects,
			"selected_class": selected_class,
			"selected_term": selected_term,
			#"students": students,
			}
	else:
		current_session = Session.objects.filter(current_session=True)
		classes = Class.objects.all()
		subjects = 	Subject.objects.all()
		context = {
			"classes": classes,
			"subjects": subjects,
			}
	return render(request, 'sms/mark/get_score_list.html', context)

@login_required
def score_entry(request):
	current_session = Session.objects.all(current_session=True)
	in_class = Class.objects.filter(id=id)
	context = {"in_class": classes}
	return render(request, 'sms/student/attendance.html', context)