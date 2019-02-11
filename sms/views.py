from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .decorators import teacher_required, student_required, parent_required
from .models import *
from .constants import *
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import ranking
from django.core import serializers
from datetime import datetime
from .remark import getRemark, getGrade
from .forms import (AddStudentForm, 
					AddParentForm, 
					AddTeacherForm, 
					AddClassForm, 
					AddSubjectForm,
					AddSectionForm,
					SubjectAllocationForm,
					SectionAllocationForm,
					AttendanceListForm,
					AttendanceSaveForm,
					UpdateProfileForm,
					ExpenseForm,
					PaymentForm,
					SessionForm,
					SmsForm,
					SettingForm,
					)
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.core.mail import send_mail

from .send_message import ACCOUNT_SID, AUTH_TOKEN, client


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
	if request.user.is_student:
		student = Student.objects.get(user__pk=request.user.pk)
		current_session = Session.objects.get(current_session=True)
		p = Payment.objects.filter(student=student, session=current_session)
		no_students = Student.objects.filter(in_class__pk=student.in_class.pk).count()
		subjects = Subject.objects.filter(class__pk=student.pk)
		no_subjects = subjects.count()
		ncontext = {}
		context = {
		"no_students": no_students,
		"no_parents": no_parents,
		"no_subjects": no_subjects,
		"no_classes": no_classes,
		"no_teachers": no_teachers,
		"subjects": subjects, 
		"student": student,
		"p":p,
		}
	elif request.user.is_teacher:
		subjects = SubjectAssign.objects.filter(teacher__id=request.user.id)
		context = {
		"no_students": no_students,
		"no_parents": no_parents,
		"no_subjects": no_subjects,
		"no_classes": no_classes,
		"no_teachers": no_teachers,
		"subjects": subjects,
	}
	elif request.user.is_parent:
		wards = Parent.objects.filter(parent__pk=request.user.id)
		context = {
		"no_students": wards.count(),
		"no_parents": 1,
		"no_subjects": no_subjects,
		"no_classes": no_classes,
		"no_teachers": no_teachers,
		"wards": wards,
		}
	return render(request, 'sms/home.html', context)



@login_required
@teacher_required
def expenditure_graph(request):
	total_payments = 0
	total_spendings = 0
	target = 0
	current_session = Session.objects.get(current_session=True)
	expenditures = Expense.objects.filter(session=current_session)
	for expenditure in expenditures:
		total_spendings += expenditure.amount

	payments = Payment.objects.filter(session=current_session)
	for payment in payments:
		total_payments += payment.paid_amount

	classes = Class.objects.all()
	for clss in classes:
		if not clss.amount_to_pay == None:
			target += clss.amount_to_pay

	current_session = Session.objects.get(current_session=True)
	labels = ["Income", "Expensediture", "Target"]
	data = [total_payments, total_spendings, target]
	data = {
		"labels": labels,
		"data_to_send": data,
		"current_session": current_session.name,
		}
	return JsonResponse(data)



@login_required
@teacher_required
def students_view(request):
	classes = Class.objects.all()
	context = {"classes": classes}
	return render(request, 'sms/student/students.html', context)


@login_required
@teacher_required
def delete_user(request, id):
	user = User.objects.get(pk=id)
	if user:
		user_name = user.get_full_name()
		if user.is_student:
			student = Student.objects.get(user__pk=user.pk)
			class_id = student.in_class.pk
			user.delete()
			messages.success(request, user_name + ' Successfully deleted !')
			return redirect('students_list_view', id=class_id)
		elif user.is_teacher:
			user.delete()
			messages.success(request, user_name + ' Successfully deleted !')
			return redirect('teachers_list')
		elif user.is_parent:
			user.delete()
			messages.success(request, user_name + ' Successfully deleted !')
			return redirect('parents_list')
		else:
			user.delete()
			messages.success(request, user_name + ' Successfully deleted !')
			return redirect('home')
	else:
		messages.error(request,' Please dont trick me, nothing is deleted !')
		return redirect('teachers_list')


@login_required
@teacher_required
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
@teacher_required
def section_view(request):
	sections = Section.objects.all()
	context = {"sections": sections}
	return render(request, 'sms/section/section.html', context)

@login_required
@teacher_required
def assign_teacher_view(request):
	context = {}
	if request.method == "POST":
		if not request.POST['term'] in ['First', 'Second', 'Third']:
			messages.error(request, ' ERROR: please select a term !')
			return redirect('assign_teacher_list')
		else:
			term = request.POST['term']
			current_session = Session.objects.get(current_session=True)
			assigned_teachers = SubjectAssign.objects.filter(term=term, session=current_session)
			subjects = Subject.objects.all()
			context = {
			"term": term,
			"subjects": subjects,
			"assigned_teachers": assigned_teachers,
			}
	return render(request, 'sms/teacher/assign_teacher.html', context)


@login_required
@teacher_required
def add_assign_teacher(request):
	context = {}
	classes = Class.objects.all()
	teachers = User.objects.filter(is_teacher=True)
	subjects = Subject.objects.all()

	if request.method == "POST":
		form = SubjectAllocationForm(request.POST)
		if form.is_valid():
			class_id = form.cleaned_data.get('clss')
			term = form.cleaned_data.get('term')
			teacher = form.cleaned_data.get('teacher')
			subjects = form.cleaned_data.get('subjects')

			class_id = Class.objects.get(pk=class_id)
			teacher = User.objects.get(is_teacher=True, pk=teacher)
			current_session = Session.objects.get(current_session=True)

			record, created = SubjectAssign.objects.update_or_create(clss=class_id, term=term, teacher=teacher, session=current_session)
			if not created:
				record = SubjectAssign.objects.get(clss=class_id, session=current_session, term=term, teacher=teacher)
				ids = ()
				for i in range(0, len(subjects)):
					ids += (subjects[i].name,)
					record.subjects.add(subjects[i])
					record.save()
				Notification(user=teacher, title="Subject Allocation !", body="Admin just updated the subjects allocated to you ! ", message_type=SUCCESS).save()
				messages.success(request, 'Subjects were successfully allocated updated')
			else:
				record = SubjectAssign(clss=class_id, session=current_session, term=term, teacher=teacher)
				record.save()
				ids = ()
				for i in range(0, len(subjects)):
					ids += (subjects[i].name,)
					record.subjects.add(subjects[i])
					Notification(user=teacher, title="Subject Allocation !", body="You've been assigned to teach "+str(subjects[i]), message_type=SUCCESS).save()
				messages.success(request, 'Subject was successfully allocated ')
				return HttpResponseRedirect(reverse_lazy('assign_teacher_list'))
		else:
			form = SubjectAllocationForm(request.POST)
			message = form
			context =  {
				"form": form, 
				"message": message,
				"classes": classes,
				"subjects": subjects,
				"teachers": teachers,
			}
	else:
		context = {
		"classes": classes,
		"subjects": subjects,
		"teachers": teachers,
		}
	return render(request, 'sms/teacher/allocate_subject.html', context)

@login_required
@teacher_required
def section_allocation(request):
	if request.method == "POST":
		print(request.POST)
	else:
		sections = SectionAssign.objects.all()
		subjects = Subject.objects.all()
		context = {
		"subjects": subjects,
		"sections": sections,
}
	return render(request, 'sms/section/section_allocation.html', context)


@login_required
@teacher_required
def add_section_allocation(request):
	sections = Section.objects.all()
	teachers = User.objects.filter(is_teacher=True)
	context = {
		"teachers": teachers,
		"sections": sections,
	}
	if request.method == "POST":
		form = SectionAllocationForm(request.POST, request.FILES)
		if form.is_valid():
			section = form.cleaned_data.get('section')
			section_head = form.cleaned_data.get('section_head')
			placeholder = form.cleaned_data.get('placeholder')
			signature = form.cleaned_data.get('signature')
			 
			if SectionAssign.objects.filter(section=section).exists():
				check = SectionAssign.objects.get(section=section)
				section_name = check.section_head.get_full_name()
				section_head = check.section.name
				messages.info(request, "You've already allocated "+str(section_head)+" Section to "+ str(section_name) + " <a href='/section-allocation/update/"+str(check.pk)+"'/>Click here to edit this information</a>")
				return redirect('add_assign_section')
			else:
				section = Section.objects.get(pk=section)
				section_head = User.objects.get(pk=section_head)
				SectionAssign.objects.create(
					section=section, 
					section_head=section_head, 
					placeholder=placeholder, 
					signature=signature)
				Notification(user=section_head, message_type=SUCCESS, title="Section Allocation !", body="You've been allocated as the "+ str(placeholder)  +" of " +str(section)+" Section.").save()
				messages.success(request, "Successfully allocated "+str(section)+" Section to "+ str(section_head.get_full_name()))
				return redirect('section_allocation')
		else:
			form = SectionAllocationForm(request.POST, request.FILES)
			message = form
			context =  {
				"form": form, 
				"message": message,
				"teachers": teachers,
				"sections": sections,
			}
	else:
		return render(request, 'sms/section/new_section_allocation.html', context)
	return render(request, 'sms/section/new_section_allocation.html', context)


@login_required
@teacher_required
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

			if not '' in [parent_username, parent_password] and existing_parent not in ['', None]:
				messages.error(request, 'You cannot select an existing parent and create a new one at same time !')
				return redirect('add_student')
			elif Student.objects.filter(user__username=stud_username).exists():
				messages.error(request, 'A student with that username already exist !')
				return redirect('add_student')
				if User.objects.filter(username=parent_username).exists():
					messages.error(request, 'A parent with that username already exist !')
					return redirect('add_student')
			elif Student.objects.filter(roll_number=stud_roll_number).exists():
				messages.error(request, 'A student with the entered roll number already exist !')
				return redirect('add_student')
			else:
				if existing_parent in ['', None]:
					if '' in [parent_username, parent_password] or None in [parent_username, parent_password]:
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
				stud = Student.objects.get(user__username=stud_username)
				if existing_parent in ['', None]:
					par = User.objects.get(username=parent_username, first_name=parent_fname, last_name=parent_sname)
				else:
					par = User.objects.get(username=parent)
				Parent.objects.create(student=stud, parent=par)
				messages.success(request, stud_fname + " " + stud_sname +' Was Successfully Recorded! ')
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
@teacher_required
def add_parent(request):
	context = {}
	if request.method == "POST":
		form = AddParentForm(request.POST, request.FILES)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			firstname = form.cleaned_data.get('firstname')
			surname = form.cleaned_data.get('surname')
			othername = form.cleaned_data.get('othername')
			state = form.cleaned_data.get('state')
			phone = form.cleaned_data.get('phone')
			email = form.cleaned_data.get('email')
			address = form.cleaned_data.get('address')
			picture = form.cleaned_data['picture']

			if User.objects.filter(username=username).exists():
				messages.success(request, "A user with username "+ username + " had already exists !")
				return HttpResponseRedirect(reverse_lazy('add_parent'))
			User.objects.create(
				username=username, 
				password=make_password(password), 
				first_name=firstname,
				last_name=surname,
				other_name=othername,
				address=address,
				state=state,
				phone=phone,
				email=email,
				picture=picture,
				is_parent=True,
				)
			messages.success(request, firstname + " " + surname +' Was Successfully Recorded! ')
			return HttpResponseRedirect(reverse_lazy('add_parent'))
		else:
			form = AddParentForm(request.POST, request.FILES)
			context =  {
				"form": form, 
				}
	return render(request, 'sms/parent/add_parent.html', context)


@login_required
@teacher_required
def add_teacher(request):
	context = {}
	if request.method == "POST":
		form = AddTeacherForm(request.POST, request.FILES)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			firstname = form.cleaned_data.get('firstname')
			surname = form.cleaned_data.get('surname')
			othername = form.cleaned_data.get('othername')
			state = form.cleaned_data.get('state')
			phone = form.cleaned_data.get('phone')
			email = form.cleaned_data.get('email')
			address = form.cleaned_data.get('address')
			picture = form.cleaned_data['picture']

			if User.objects.filter(username=username).exists():
				messages.success(request, "A user with username "+ username + " had already exists !")
				return HttpResponseRedirect(reverse_lazy('add_teacher'))
			User.objects.create(
				username=username, 
				password=make_password(password), 
				first_name=firstname,
				last_name=surname,
				other_name=othername,
				address=address,
				state=state,
				phone=phone,
				email=email,
				picture=picture,
				is_teacher=True,
				)
			messages.success(request, firstname + " " + surname +' Was successfully added! ')
			return HttpResponseRedirect(reverse_lazy('add_teacher'))
		else:
			form = AddParentForm(request.POST, request.FILES)
			context =  {
				"form": form, 
				}
	return render(request, 'sms/teacher/add_teacher.html', context)



@login_required
@teacher_required
def add_class(request):
	if request.method == "POST":
		sections = Section.objects.all()
		subjects = Subject.objects.all()
		form = AddClassForm(request.POST)
		if form.is_valid():
			name = form.cleaned_data.get('name')
			section_id = form.cleaned_data.get('section')
			selected_subjects = form.cleaned_data.get('subjects')
			if Class.objects.filter(name=name).exists():
				class_id = str(Class.objects.get(name=name).pk)
				messages.error(request, name + ' Already exists! <a href="/class/update/'+class_id+'/">click here to update its subjects</a>')
				return HttpResponseRedirect(reverse_lazy('add_class'))
			else:
				ids = ()
				section = Section.objects.get(pk=section_id)
				new_class = Class.objects.create(name=name, section=section)
				for i in range(0, len(selected_subjects)):
					ids += (selected_subjects[i].name,)
					new_class.subjects.add(selected_subjects[i])
				messages.success(request, new_class.name +' Was successfully added, don\'t forget adding a payment setting for this class')
				return HttpResponseRedirect(reverse_lazy('class_list'))
		else:
			form = AddParentForm(request.POST)
			context =  {
				"form": form, 
				}
		context = {
			"sections": sections,
			"subjects": subjects,
			}
	else:
		sections = Section.objects.all()
		subjects = Subject.objects.all()
		context = {
			"sections": sections,
			"subjects": subjects,
			}
	return render(request, 'sms/class/add_class.html', context)

@login_required
@teacher_required
def delete_class(request, id):
	selected_class = Class.objects.get(pk=id)
	class_name = selected_class.name
	selected_class.delete()
	messages.success(request, "Successfully deleted "+ class_name)
	return HttpResponseRedirect(reverse_lazy('class_list'))


@login_required
@teacher_required
def delete_subject(request, id):
	selected_subject = Subject.objects.get(pk=id)
	subject_name = selected_subject.name
	selected_subject.delete()
	messages.success(request, "Successfully deleted "+ subject_name)
	return HttpResponseRedirect(reverse_lazy('subjects_list'))


@login_required
@teacher_required
def delete_section(request, id):
	selected_section = Section.objects.get(pk=id)
	section_name = selected_section.name
	selected_section.delete()
	messages.success(request, "Successfully deleted "+ str(selected_section))
	return HttpResponseRedirect(reverse_lazy('sections_list'))

@login_required
@teacher_required
def delete_all_allocated_subjects(request, id):
	subjects = SubjectAssign.objects.get(pk=id)
	teacher = subjects.teacher
	notification = Notification.objects.filter(user__pk=subjects.teacher.pk, title__icontains='Subject Allocation')
	notification.delete()
	subjects.delete()
	messages.success(request, "Successfully deleted all subjects allocated to "+ str(teacher))
	return HttpResponseRedirect(reverse_lazy('assign_teacher_list'))


@login_required
@teacher_required
def delete_section_allocation(request, id):
	allocated_section = SectionAssign.objects.get(pk=id)
	section_name = allocated_section.section
	notification = Notification.objects.filter(user__pk=allocated_section.section_head.pk ,body__icontains=section_name)
	notification.delete()
	allocated_section.delete()
	messages.success(request, "You've Successfully deallocated "+str(allocated_section.section)+" Section from "+ str(allocated_section.section_head.get_full_name()))
	return HttpResponseRedirect(reverse_lazy('section_allocation'))


@login_required
@teacher_required
def delete_attendance(request, id):
	attendance = Attendance.objects.get(pk=id)
	student = attendance.student
	date = attendance.date
	attendance.delete()
	messages.success(request, "You've successfully deleted "+ str(student) +" from attendance of " + str(date))
	return HttpResponseRedirect(reverse_lazy('attendance_list'))


@login_required
@teacher_required
def add_subject(request):
	classes = Class.objects.all()
	context = {"classes": classes}
	if request.method == "POST":
		form = AddSubjectForm(request.POST)
		if form.is_valid():
			name = form.cleaned_data.get('subject')
			if Subject.objects.filter(name=name).exists():
				messages.info(request, name + " Already exists !")
				return HttpResponseRedirect(reverse_lazy('add_subject'))
			else:
				subject = Subject(name=name).save()
				messages.success(request, "Successfully added "+ name)
				return HttpResponseRedirect(reverse_lazy('subjects_list'))
		context =  {"form": form,}
	return render(request, 'sms/subject/add_subject.html', context)



@login_required
@teacher_required
def add_section(request):
	context = {}
	if request.method == "POST":
		form = AddSectionForm(request.POST)
		if form.is_valid():
			section_name = form.cleaned_data.get('section').title()
			section_note = form.cleaned_data.get('note')
			if Section.objects.filter(name=section_name).exists():
				messages.info(request, section_name + " Section Already exists !")
				return HttpResponseRedirect(reverse_lazy('add_section'))
			elif "Section" in section_name:
				messages.info(request, " You don't need to include the word 'Section' in section name, just write <code>"+ section_name.replace('Section', '') +"</code>")
				return HttpResponseRedirect(reverse_lazy('add_section'))
			else:
				Section(name=section_name, note=section_note).save()
				messages.success(request, "Successfully added "+ section_name)
				return HttpResponseRedirect(reverse_lazy('sections_list'))
		else:
			context =  {"form": form,}
	return render(request, 'sms/section/add_section.html', context)


@login_required
@teacher_required
def system_admin(request):
	users = User.objects.filter(is_superuser=True)
	return render(request, 'sms/users/user.html', { "users": users })

@login_required
@teacher_required
def add_system_admin(request):
	context = {}
	if request.method == "POST":
		form = AddParentForm(request.POST, request.FILES)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			firstname = form.cleaned_data.get('firstname')
			surname = form.cleaned_data.get('surname')
			othername = form.cleaned_data.get('othername')
			state = form.cleaned_data.get('state')
			phone = form.cleaned_data.get('phone')
			email = form.cleaned_data.get('email')
			address = form.cleaned_data.get('address')
			picture = form.cleaned_data['picture']

			if User.objects.filter(username=username).exists():
				messages.success(request, "A user with username "+ username + " had already exists !")
				return HttpResponseRedirect(reverse_lazy('add_system_admin'))
			User.objects.create(
				username=username, 
				password=make_password(password), 
				first_name=firstname,
				last_name=surname,
				other_name=othername,
				address=address,
				state=state,
				phone=phone,
				email=email,
				picture=picture,
				is_superuser=True,
				)
			messages.success(request, firstname + " " + surname +' Was Successfully Recorded! ')
			return HttpResponseRedirect(reverse_lazy('add_system_admin'))
		else:
			form = AddParentForm(request.POST, request.FILES)
			context =  {
				"form": form, 
				}
	return render(request, 'sms/users/add_user.html', context)


@login_required
@teacher_required
def teachers_view(request):
	teachers = User.objects.filter(is_teacher=True)
	context = {
		'teachers': teachers,
	}
	return render(request, 'sms/teacher/teachers.html', context)


@login_required
def profile(request, user):
	user = User.objects.get(username=user)
	context = {"user": user}
	if request.method == "POST":
		date = request.POST['dob']
		if date == '':
			date = None
		form = UpdateProfileForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			email = form.cleaned_data.get('email')
			phone = form.cleaned_data.get('phone')
			firstname = form.cleaned_data.get('firstname')
			surname = form.cleaned_data.get('surname')
			address = form.cleaned_data.get('address')
			othername = form.cleaned_data.get('othername')
			religion = form.cleaned_data.get('religion')
			user = User.objects.get(username=username)
			user.email = email
			user.phone = phone
			user.firstname = firstname
			user.surname = surname
			user.address = address
			user.dob = date
			user.other_name = othername
			user.religion = religion
			user.save()
			messages.success(request, "Your profile was successfully edited !")
			return redirect("profile", user=user)
		else:
			user = User.objects.get(username=user)
			form = UpdateProfileForm(request.POST)
			context = {
				"user": user,
				"form": form,
			}
	return render(request, 'sms/users/profile.html', context)


@login_required
@teacher_required
def parents_view(request):
	parents = User.objects.filter(is_parent=True)
	context = {
		'parents': parents,
	}
	return render(request, 'sms/parent/parents.html', context)

@login_required
@teacher_required
def class_view(request):
	classes = Class.objects.all()
	context = {
		'classes': classes,
	}
	return render(request, 'sms/class/class.html', context)


@login_required
@teacher_required
def subjects_view(request):
	subjects = Subject.objects.all()
	context = {
		'subjects': subjects,
	}
	return render(request, 'sms/subject/subjects.html', context)

@login_required
@teacher_required
def attendance_view(request):
	current_session = Session.objects.all(current_session=True)
	select_class = Class.objects.filter(id=id)
	context = {"in_class": select_class}
	return render(request, 'sms/student/attendance.html', context)


@login_required
@teacher_required
def attendance_list(request):
	session = Session.objects.get(current_session=True)
	all_class = Class.objects.all()
	if request.method == "POST":
		date = request.POST['date']
		if date == '':
			messages.info(request, "Please select class, term and date in order to view attendance")
			return HttpResponseRedirect(reverse_lazy('attendance_list'))
		date = datetime.strptime(date, '%d %B, %Y')
		form = AttendanceListForm(request.POST)
		if form.is_valid():
			term = form.cleaned_data.get('selected_term')
			selected_class = form.cleaned_data.get('selected_class')
			students = Student.objects.filter(in_class=selected_class)
			ids = ()
			for i in students:
				ids += (i.user.pk,)
			q = Attendance.objects.filter(date=date, student__user__pk__in=ids, term=term, session=session)
			print("query: " + str(q))
			context = {
				"students": students,
				"classes": all_class,
				"attendance": q,
				"selected_class": selected_class,
				"selected_term": term,
				"selected_date": date,
			}
		else:
			context =  {
				"form": form,
				"classes": all_class,
			}
	else:
		context = {"classes": all_class}
	return render(request, 'sms/student/attendance_list.html', context)

@login_required
@teacher_required
def add_attendance(request):
	current_session = Session.objects.get(current_session=True)
	if request.method == "POST":
		in_class = Class.objects.all()
		data = request.POST.copy()
		data.pop('csrfmiddlewaretoken')
		data.pop('submit')
		try:
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
		except:
			messages.info(request, "Please select class, term and date in order to add attendance")
			return HttpResponseRedirect(reverse_lazy('add_attendance'))
	else:
		in_class = Class.objects.all()
		context = {
			"classes": in_class,
		}
	return render(request, 'sms/student/add_attendance.html', context)


# TODO -------------FIX
@login_required
@teacher_required
def save_attendance(request):
	if request.method == "POST":
		data = request.POST.copy()
		data.pop('csrfmiddlewaretoken')
		data.pop('submit')
		term = data['selected_term']
		date = data['selected_date']
		data.pop('selected_term')
		data.pop('selected_date')
		print(data.lists)
		# form = AttendanceSaveForm(request.POST)
		# if form.is_valid():
		# 	session = Session.objects.get(current_session=True)
		# 	term = form.cleaned_data.get('selected_term')
		# 	date = form.cleaned_data.get('selected_date')
		# 	attendance = form.cleaned_data.get('status')
		# 	is_late = form.cleaned_data.get('is_late')
		# 	duration = form.cleaned_data.get('duration')
		# 	student_ids = request.POST['student_ids']
		# 	print('session: '+ str(session))
		# 	print('term: '+ str(term))
		# 	print('date: '+ str(date))
		# 	print('attendance: '+ str(attendance))
		# 	print('is_late: '+ str(is_late))
		# 	print('duration: '+ str(duration))
		# 	print('student_ids: '+ str(request.POST['student_ids']))
		messages.error(request, "There's an error while creating an attendance record")
		return HttpResponseRedirect(reverse_lazy('add_attendance'))
		# else:
		# messages.error(request, "There's an error while creating an attendance record")
		# return HttpResponseRedirect(reverse_lazy('add_attendance'))


@login_required
@teacher_required
def toggle_session(request, id):
	selected_session = Session.objects.get(pk=id)
	current_session = Session.objects.get(current_session=True)
	current_session.current_session = False
	current_session.save()
	selected_session.current_session = True
	selected_session.save()
	return HttpResponse(
		"<script type='text/javascript'>\
			history.go(-1); \
			location.reload(true);\
		</script>")


@login_required
@teacher_required
def load_subjects(request):
	class_id = request.GET.get('class')
	clss = Class.objects.get(pk=class_id)
	subjects = clss.subjects.all()
	if request.user.is_teacher:
		sub = SubjectAssign.objects.filter(teacher__id=request.user.id)
		for i in sub:
			clss = i.clss
			subjects = i.subjects.filter(subjectassign__clss=clss)
	return render(request, 'sms/mark/subject_dropdown_list_options.html', {'subjects': subjects})


@login_required
@teacher_required
def score_list(request):
	current_session = Session.objects.filter(current_session=True)
	classes = Class.objects.all()
	context = {"classes": classes}
	if request.user.is_teacher:
		assigned_subjects = SubjectAssign.objects.filter(teacher__id=request.user.id)
		context = {"assigned_subjects": assigned_subjects}
		for i in assigned_subjects:
			print(i.clss)
	return render(request, 'sms/mark/get_score_list.html', context)


@login_required
@teacher_required
def score_entry(request):
	if request.method == 'POST':
		session = Session.objects.get(current_session=True)
		term = request.POST.get('term')
		subject = request.POST.get('subject')
		subject = Subject.objects.get(pk=subject)
		ca1 = list(request.POST.getlist('ca1'))
		ca2 = list(request.POST.getlist('ca2'))
		exam = list(request.POST.getlist('exam'))
		stud_id = list(request.POST.getlist('student_id'))

		for i in range(0, len(stud_id)):
			student = Student.objects.get(pk=stud_id[i])
			if ca1[i] == '' and ca2[i] == '':
				total = int(exam[i])
			elif ca2[i] == '' and exam[i] == '':
				total = int(ca1[i])
			elif exam[i] == '' and ca1[i] == '':
				total = int(ca2[i])
			elif ca1[i] == '':
				total = int(ca2[i]) + int(exam[i])
			elif ca2[i] == '':
				total = int(ca1[i]) + int(exam[i])
			elif exam[i] == '':
				total = ca1[i] + ca2[i]
			else:
				total = int(ca1[i]) + int(ca2[i]) + int(exam[i])
			grade, created = Grade.objects.get_or_create(session=session, term=term, student=student, subject=subject)
			if not created:
					grade.fca=ca1[i]
					grade.sca=ca2[i]
					grade.exam=exam[i]
					grade.total=total
					grade.grade=getGrade(total)
					grade.remark=getRemark(total)
					grade.compute_position(term)
					grade.save()
			else:
				a = Grade.objects.get(
				session=session, 
				term=term, 
				student=student, 
				subject=subject)
				a.fca=ca1[i]
				a.sca=ca2[i]
				a.exam=str(exam[i])
				a.total=total
				a.remark = getRemark(total)
				a.grade = getGrade(total)
				a.compute_position(term)
				a.save()
		messages.success(request, "Score Successfully Recorded !")
	classes = Class.objects.all()
	context = {"classes": classes}
	selected_class = request.GET.get('class')
	selected_term = request.GET.get('term')
	selected_subject = request.GET.get('subject')
	if request.user.is_superuser:
		if not None in [selected_class, selected_term, selected_subject]:
			selected_class = Class.objects.get(pk=selected_class)
			current_session = Session.objects.filter(current_session=True)
			students = Student.objects.filter(in_class__name=selected_class)
			context = {
				"classes": classes,
				"selected_subject": selected_subject,
				"selected_class": selected_class,
				"selected_term": selected_term,
				"students": students,
				}
			return render(request, 'sms/mark/load_score_table.html', context)
	elif request.user.is_teacher:
		if not None in [selected_term, selected_subject]:
			selected_class_name = request.GET.get('scid')
			selected_class_name = selected_class_name[-7:-1]
			selected_class = Class.objects.get(name=selected_class_name)
			current_session = Session.objects.filter(current_session=True)
			students = Student.objects.filter(in_class__name=selected_class)
			gr = Grade.objects.filter(student__in_class__pk=selected_class.pk)
			gr = zip(students, gr)
			context = {
				"classes": classes,
				"selected_subject": selected_subject,
				"selected_class": selected_class,
				"selected_term": selected_term,
				"students": students,
				"gr":gr,
				}
			return render(request, 'sms/mark/load_score_table.html', context)
	return render(request, 'sms/mark/get_score_list.html', context)


@login_required
@teacher_required
def view_score(request):
	classes = Class.objects.all().order_by('name')
	context = {
		"classes": classes
		}
	return render(request, 'sms/mark/view_scores.html', context)


@login_required
@teacher_required
def load_score_table(request):
	if request.is_ajax:
		class_id = request.GET.get('class')
		subject_id = request.GET.get('subject_id')
		term = request.GET.get('term')

		clss = Class.objects.get(pk=class_id).pk
		subject = Subject.objects.get(pk=subject_id)
		current_session = Session.objects.get(current_session=True)

		grades = Grade.objects.filter(
			student__in_class__pk=clss,
			session=current_session,
			term=term,
			subject=subject
			)
		print(grades)
		return render(request, 'sms/mark/load_view_score.html', {'grades': grades})

@login_required
def get_student_position(request):
	current_session = Session.objects.get(current_session=True)
	students = Student.objects.filter(in_class__pk=1)
	overall_total = []
	all_ids = []
	for student in students:
		total = 0
		grades = Grade.objects.filter(student__pk=student.id, term="First", session=current_session)
		for i in grades:
			total += float(i.total)
		overall_total.append(total)
		all_ids.append(student.id)
	print(sorted(overall_total, reverse=True))
	print(sorted(all_ids, reverse=True))
	total_scores = sorted(overall_total, reverse=True)
	positions = ranking.Ranking(total_scores, start=1)
	return HttpResponse(positions)


@login_required
@teacher_required
def add_expenditure(request):
	if request.method == "POST":
		form = ExpenseForm(request.POST)
		if form.is_valid():
			term = form.cleaned_data.get('term')
			session = Session.objects.get(current_session=True)
			item = form.cleaned_data.get('item')
			amount = form.cleaned_data.get('amount')
			description = form.cleaned_data.get('description')
			Expense(
				term=term,
				session=session,
				item=item,
				description=amount,
				amount=amount,
				).save()
			messages.success(request, str(item) +' was successfully added')
			return HttpResponseRedirect(reverse_lazy('view_expenses'))
		else:
			form = ExpenseForm(request.POST)
			return render(request, 'sms/expenses/add_expense.html', {"form": form})
	else:
		return render(request, 'sms/expenses/add_expense.html', {})


@login_required
@teacher_required
def expenditure(request):
	expenses = Expense.objects.all().order_by('item')
	return render(request, 'sms/expenses/expense.html', {"expenses": expenses})

@login_required
@teacher_required
def delete_expenditure(request, id):
	expense = Expense.objects.get(pk=id)
	expense.delete()
	messages.success(request, str(expense.item) + ' was successfully deleted')
	return HttpResponseRedirect(reverse_lazy('view_expenses'))


@login_required
@teacher_required
def add_payment(request):
	if request.method == "POST":
		students = Student.objects.all()
		form = PaymentForm(request.POST)
		if form.is_valid():
			student = form.cleaned_data.get('student')
			student = Student.objects.get(pk=student)
			payment_method = form.cleaned_data.get('payment_method')
			session = Session.objects.get(current_session=True)
			term = form.cleaned_data.get('term')
			paid_amount = form.cleaned_data.get('paid_amount')
			teller_number = form.cleaned_data.get('tnumber')
			damount = student.in_class.amount_to_pay
			if damount == None or damount == '':
				messages.success(request, ' You have to create a payment setting for the student\'s class, Account > Set Payment')
				classes = Class.objects.all().order_by('name')
				return render(request, 'sms/payments/add_payment.html', {"students": students, "classes": classes})
			paid_amount = float(paid_amount)
			due_amount = damount - paid_amount
			if due_amount == 0:
				payment_status = PAID
			elif paid_amount == 0:
				payment_status = NOT_PAID
			else:
				payment_status = PARTIALLY_PAID

			if payment_method == 'Bank' and teller_number in [None, '']:
				messages.success(request, ' Please provide the bank teller number')
				classes = Class.objects.all().order_by('name')
				return render(request, 'sms/payments/add_payment.html', {"students": students, "classes": classes})
			p = Payment.objects.filter(student__pk=student.pk, term=term, session=session)
			prevAmount = 0
			for i in p:
				prevAmount += i.paid_amount
			e = prevAmount + paid_amount
			if e > damount:
				classes = Class.objects.all().order_by('name')
				messages.success(request,' Please check the due amount of this student for ' + term + " term, " + str(session))
				return render(request, 'sms/payments/add_payment.html', {"students": students, "classes":classes})
			pay, updated = Payment.objects.update_or_create(
				student=student,
				due_amount=float(due_amount),
				payment_status=payment_status,
				paid_amount=float(paid_amount),
				payment_method =payment_method,
				teller_number=teller_number,
				session=session,
				term=term)
			if not updated:
				pay.save()
			messages.success(request, str(student) +'\'s payment was successfully added')
			return HttpResponseRedirect(reverse_lazy('view_payments'))
		else:
			form = PaymentForm(request.POST)
			return render(request, 'sms/payments/add_payment.html', {"form": form, "students": students})
	else:
		students = Student.objects.all()
		classes = Class.objects.all().order_by('name')
		context = {
			"classes": classes,
			"students":students
		}
		return render(request, 'sms/payments/add_payment.html', context)


@login_required
@teacher_required
def payment(request):
	students = Student.objects.all().order_by('name')
	payments = Payment.objects.all().order_by('student')
	classes = Class.objects.all().order_by('name')
	context = {
		"classes": classes,
		"payments": payments
		}
	return render(request, 'sms/payments/payment.html',context )


@login_required
@teacher_required
def set_payment(request):
	if request.method == "POST":
		class_id = request.POST['class']
		amount_to_pay = request.POST['amount_to_pay']
		print(class_id)
		print(amount_to_pay)
		clss = Class.objects.get(id=class_id)
		clss.amount_to_pay = amount_to_pay=amount_to_pay
		clss.save()
		messages.success(request, ' Payment setting was successfully updated ')
		return HttpResponseRedirect(reverse_lazy('set_payment'))
	classes = Class.objects.all()
	context = {"classes": classes}
	return render(request, 'sms/settings/payment_setting.html', context)


@login_required
@teacher_required
def delete_payment(request, id):
	payment = Payment.objects.get(pk=id)
	payment.delete()
	messages.success(request, str(payment.student) + ' payment information was successfully deleted')
	return HttpResponseRedirect(reverse_lazy('view_payments'))


@login_required
@teacher_required
def load_payment_table(request):
	session = Session.objects.get(current_session=True)
	term = request.GET.get('term')
	class_id = request.GET.get('class')
	payments = Payment.objects.filter(
		student__in_class__pk=class_id, 
		term=term, 
		session=session)
	print("payments"+str(payments))
	return render(request, 'sms/payments/ajax_load_payment.html', {"payments": payments})


@login_required
@teacher_required
def load_students_of_class(request):
	class_id = request.GET.get('class')
	students = Student.objects.filter(in_class__pk=class_id).order_by('-id')
	return render(request, 'sms/payments/ajax_load_students.html', {"students": students})

@login_required
@teacher_required
def session_view(request):
	sessions = Session.objects.all()
	return render(request, 'sms/academic_year/session.html', {"sessions": sessions})


@login_required
@teacher_required
def add_session(request):
	sessions = Session.objects.all()
	if request.method == "POST":
		form = SessionForm(request.POST)
		if form.is_valid():
			name = form.cleaned_data.get('name')
			note = form.cleaned_data.get('note')
			if Session.objects.filter(name=name).exists():
				messages.success(request, 'this session already exists')
				return redirect('session_list')
			Session(name=name, note=note, current_session=False).save()
			messages.success(request, 'Session successfully added')
			return redirect('session_list')
		else:
			form = SessionForm(request.POST)
			context = {"sessions": sessions, "form": form}
			return render(request, 'sms/academic_year/session.html', context)
	return render(request, 'sms/academic_year/session.html', {"sessions": sessions})


@login_required
@teacher_required
def del_session(request, id):
	session = Session.objects.get(id=id)
	if session.current_session == True:
		messages.info(request, 'You cannot delete the active academic year')
		return HttpResponseRedirect(reverse_lazy('session_list'))
	else:
		session.delete()
		messages.success(request, 'Successfully deleted')
		sessions = Session.objects.all()
	return render(request, 'sms/academic_year/session.html', {"sessions":sessions})

@login_required
@teacher_required
def sms_list(request):
	sms = Sms.objects.all()
	return render(request, 'sms/mail_and_sms/sms.html', {"sms":sms})


@login_required
@teacher_required
def send_sms(request):
	sms = Sms.objects.all()
	if request.method == "POST":
		form = SmsForm(request.POST)
		if form.is_valid():
			title = form.cleaned_data.get('title')
			body = form.cleaned_data.get('body')
			to_user = form.cleaned_data.get('to_user')
			if to_user == "Admin":
				users = User.objects.filter(is_superuser=True)
			elif to_user == "Student":
				users = User.objects.filter(is_student=True)
			elif to_user == "Parent":
				users = User.objects.filter(is_parent=True)
			elif to_user == "Teacher":
				users = User.objects.filter(is_teacher=True)

			for user in users:
				if len(str(user.phone)) == 0:
					pass
				else:
					if str(user.phone)[0] == '0':
						if len(user.phone) != 10:
							phone = str(user.phone)[1:]
							phone = '+234'+phone
							message = client.messages.create(
						    	to=phone, 
						    	from_="+14026034086",
						    	body=title+" \n "+body)
							print(message.sid)

			Sms(title=title, body=body, to_user=to_user).save()
			context = {
				"sms": sms,
				"title": title,
				"body": body, 
				"to_user": to_user
			}
			messages.success(request, ' Messages delivered successfully')
			return render(request, 'sms/mail_and_sms/sms.html', context)
		else:
			form = SmsForm(request.POST)
			context = {"form": form}
			return render(request, 'sms/mail_and_sms/sms.html', context)
	else:
		context = {"sms":sms}
		return render(request, 'sms/mail_and_sms/sms.html', context)

def general_setting(request):
	context = {}
	if request.method == "POST":
		form = SettingForm(request.POST, request.FILES)
		if form.is_valid():
			school_name = form.cleaned_data.get('school_name')
			school_logo = form.cleaned_data.get('school_logo')
			school_address = form.cleaned_data.get('school_address')
			school_slogan = form.cleaned_data.get('school_slogan')
			ft_begins = form.cleaned_data.get('ft_begins')
			ft_ends = form.cleaned_data.get('ft_ends')
			st_begins = form.cleaned_data.get('st_begins')
			st_ends = form.cleaned_data.get('st_ends')
			tt_begins = form.cleaned_data.get('tt_begins')
			tt_ends = form.cleaned_data.get('tt_ends')

			a, created = Setting.objects.get_or_create(id=1)
			if not created:
				a = Setting.objects.get(id=1)
				if school_logo == None:
					school_logo = a.school_logo
				a = Setting.objects.filter(id=1).update(
				school_name=school_name,
				school_address=school_address,
				school_slogan=school_slogan,
				school_logo=school_logo,
				ft_begins=ft_begins,
				ft_ends=ft_ends,
				st_begins=st_begins,
				st_ends=st_ends,
				tt_begins=tt_begins,
				tt_ends=tt_ends)
				fs = FileSystemStorage()
				name = fs.save(school_logo.name, school_logo)
				context['url'] = fs.url(name)
				context['s'] = Setting.objects.all()[0]
			messages.success(request, 'School settings successfully updated !')
			return render(request, 'sms/settings/general_setting.html', context)
		else:
			s = Setting.objects.all()[0]
			form = SettingForm(request.POST)
			return render(request, 'sms/settings/general_setting.html', {"form":form, "s":s})
	else:
		s = Setting.objects.all()[0]
		return render(request, 'sms/settings/general_setting.html', {"s":s})


def reset_users_password_view(request):
	if request.is_ajax:
		if request.method == 'POST':
			user = request.POST.get('selected_user')
			new_pass = request.POST.get('new_password')
			user = User.objects.get(username=user)
			user.password = make_password(new_pass)
			user.save()
	return render(request, 'sms/users_password/users_password.html', {})


def reset_users_password(request):
	user_type = request.GET.get('user_type')
	if user_type == 'admin':
		users = User.objects.filter(is_superuser=True)
	elif user_type == 'student':
		users = User.objects.filter(is_student=True)
	elif user_type == 'parent':
		users = User.objects.filter(is_parent=True)
	elif user_type == 'teacher':
		users = User.objects.filter(is_teacher=True)
	context = {'users': users}
	return render(request, 'sms/users_password/load_users.html', context)