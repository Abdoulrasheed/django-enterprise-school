from datetime import datetime

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core import serializers
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Min, Sum, CharField, Value, Q
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy

from django.shortcuts import (
	get_object_or_404, 
	redirect, 
	render, 
	render_to_response
	)

from django.template import Context
from django.template.loader import get_template
from .decorators import (teacher_required, 
						student_required, 
						parent_required,
						admin_required)
from .models import *
from constants import *
from django.db import IntegrityError

from . sms_sender import send_sms

from django.views.decorators.http import require_http_methods

import asyncio

from .remark import getRemark, getGrade
from frontend.models import OnlineAdmission
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
					ChangePasswordForm,
					NoticeForm,
					EditStudentForm,
					EditUserForm,
					EditClassForm,
					EditSubjectForm,
					EditSectionForm,
					EditSectionAllocationForm,
					EditExpenseForm,
					EditSessionForm,
					SetParentForm,
					ProfilePictureForm,
					EmailMessageForm,)

from django.template.loader import render_to_string


INDEX = lambda items, key, item: list(items.values_list(key, flat=True)).index(item)+1

def get_item_index(items, key, item):
	try:
		return INDEX(items, key, item)
	except Exception as e:
		return 0

import logging
DB_LOGGER = logging.getLogger(__name__)
def get_subject_report_data(grades, subjects, student, student_grades):
	result = []
	for subject in subjects:
		sub_grades = grades.filter(subject=subject)
		sub_student_grades = student_grades.filter(subject=subject)
		if sub_student_grades.exists():
			#DB_LOGGER.error('%r===%r='%(sub_grades.values_list('total',flat=True), student_grades.filter(subject=subject).first().total))

			# print ('#'*10,sub_grades.values_list('total',flat=True), student_grades.filter(subject=subject).first().total)
			sub_rank = get_item_index(sub_grades, 'total', student_grades.filter(subject=subject).first().total)
			#DB_LOGGER.error('%r===%r='%(student, sub_rank))

			# sub_rank = get_item_index(sub_grades, 'total', sub_student_grades.first().pk)
			sub_student_grades = sub_student_grades.annotate(rank=Value(sub_rank, output_field=CharField()))
			result+=sub_student_grades.values()
	return result



@admin_required
@login_required
def report_student(request):
	data = request.POST
	obj_id = data.get('pk') or None
	template ='sms/student/report_student.html'
	class_id = data.get('class')
	term = data.get('term')
	if not any([class_id, term]):
		messages.success(request, 'Missing data class %s in term %r '%(class_id, term))
		return redirect('create_report_student')
	clss = get_object_or_404(Class, pk=class_id)
	current_session = Session.objects.get(current_session=True)
	students = Student.objects.filter(in_class=clss, session=current_session)
	if not students.exists():
		messages.success(request, 'No students exists for class %s in term %r '%(clss, term))
		return redirect('create_report_student')

	subjects = clss.subjects.all()

	if not subjects.exists():
		messages.success(request, 'No subjects exists for class %s in term %r '%(clss, term))
		return redirect('create_report_student')

	grades = Grade.objects.filter(term=term, student__in_class=clss,session=current_session).order_by('-total')
	if not grades.exists():
		messages.success(request, 'No grades exists for class %s in term %r '%(clss, term))
		return redirect('create_report_student')


	grades_ordered= grades\
	.values('student')\
	.annotate(total_mark=Sum('total'))\
	.order_by('-total_mark')
	total_marks = [i.get('total_mark') for i in grades_ordered]
	records = {}
	highest = grades_ordered.first()['total_mark']
	lowest = grades_ordered.last()['total_mark']
	count = 0
	for student in students:
		try:
			total_mark = (grades_ordered.get(student=student.pk)['total_mark'])
			setattr(student, 'total_mark', total_mark)
			student_rank = total_marks.index(total_mark)+1
			setattr(student, 'student_rank', student_rank)
			count += 1
			student_grades = grades.filter(student=student)
			data = get_subject_report_data(grades, subjects, student, student_grades)
			records[student.id] = (student,data)

		except Exception as e:
			DB_LOGGER.error('=====================%r'%(e))
	if not count:
		messages.success(request, 'No reports exists for class %s in term %r '%(clss, term))
		return redirect('create_report_student')

	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename="report.pdf"'
	# return render(request, template, context)
	setting = Setting.objects.first()
	scale = GradeScale.objects.all().order_by('grade')
	se_tion = Session.objects.get(current_session=True)
	context = {'results':records,'term':term,'setting':setting, 'highest':highest, 'lowest':lowest, 'number_of_student': grades_ordered.count(), 'gradeScale': scale, 'se_tion': se_tion}

	from weasyprint import HTML, CSS
	template = get_template(template)
	html = template.render(context)

	css_string = """@page {
		size: a4 portrait;
		margin: 1mm;
		counter-increment: page;
	}"""

	pdf_file = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(
			stylesheets=[CSS(string=css_string)],presentational_hints=True)


	response = HttpResponse(pdf_file, content_type='application/pdf')
	response['Content-Disposition'] = 'filename="home_page.pdf"'
	return response
	return HttpResponse(response.getvalue(), content_type='application/pdf')


@login_required
@admin_required
def create_report_student(request):
	classes = Class.objects.all()
	context = {"classes": classes}
	return render(request, 'sms/student/create_report_student.html', context)

@login_required
def home(request):
	context = {}
	no_classes = Class.objects.all().count()
	no_subjects = Subject.objects.all().count()
	no_parents = User.objects.filter(is_parent=True).count()
	no_students = User.objects.filter(is_student=True).count()
	no_teachers = User.objects.filter(is_teacher=True).count()
	current_session = Session.objects.get(current_session=True)
	
	if request.user.is_superuser:
		sms_unit = Setting.objects.first().sms_unit
		target_income = 0
		classes = Class.objects.all()
		for clss in classes:
			if clss.amount_to_pay is not None:
				target_income += clss.amount_to_pay

		context["no_students"] = no_students
		context["no_parents"] = no_parents
		context["no_subjects"] = no_subjects
		context["no_classes"] = no_classes
		context["no_teachers"] = no_teachers
		context["target_income"] = int(target_income)
		context['sms_unit'] = sms_unit
		context['colxl'] = 2

	elif request.user.is_student:
		student = Student.objects.get(user__pk=request.user.pk, session=current_session)
		p = Payment.objects.filter(student=student, session=current_session)
		no_students = Student.objects.filter(in_class__pk=student.in_class.pk, session=current_session).count()
		subjects_q = get_object_or_404(Class, pk=student.in_class.pk).subjects
		subjects = subjects_q.all
		no_subjects = subjects_q.count()
		context = {
		"no_students": no_students,
		"no_parents": no_parents,
		"no_subjects": no_subjects,
		"no_classes": no_classes,
		"no_teachers": no_teachers,
		"subjects": subjects,
		"student": student,
		"p":p,
		"colxl": 3,
		}
	elif request.user.is_teacher:
		# Get all the subjects assigned to the teacher
		subjects = SubjectAssign.objects.filter(teacher__id=request.user.id, session=current_session, term=get_terms())
		
		# show number of those students in any class that
		# the teacher is being assigned a subject

		# then, count the parents of those students
		
		no_students = 0
		no_parents = 0

		# also skip those students with no parent.

		parent_ids = ()
		for clss in subjects:
			no_students += Student.objects.filter(in_class__pk=clss.clss.id, session=current_session).count()
			
			if Parent.objects.filter(student__in_class__pk=clss.clss.id).exists():
				if not Parent.objects.filter(student__in_class__pk=clss.clss.id).first().id in parent_ids:
					no_parents += Parent.objects.filter(student__in_class__pk=clss.clss.id).count()
					parent_ids += (Parent.objects.filter(student__in_class__pk=clss.clss.id).first().id,)

		context = {
		"no_students": no_students,
		"no_parents": len(parent_ids),
		"no_subjects": subjects.count(),
		"no_teachers": no_teachers,
		"allocated_subjects": subjects,
		"colxl": 3,
	}
	elif request.user.is_parent:
		no_classes = Class.objects.all().count()
		no_subjects = Subject.objects.all().count()
		no_teachers = User.objects.filter(is_teacher=True).count()
		parent = Parent.objects.get(parent__pk=request.user.id)
		context = {
		"no_students": parent.student.filter(session=current_session).count(),
		"no_parents": 1,
		"no_subjects": no_subjects,
		"no_classes": no_classes,
		"no_teachers": no_teachers,
		"students": parent.student.filter(session=current_session),
		"colxl": 3,
		}
	return render(request, 'sms/home.html', context)



@login_required
@admin_required
@require_http_methods(["GET"])
def expenditure_graph(request):
	current_session = Session.objects.get(current_session=True)
	
	expenditures = Expense.objects.filter(session=current_session, term=get_terms())
	expenditures_by_month = [0] * 12
	for month in range(1, 13):
		for expenditure in expenditures.filter(timestamp__month=month):
			m = expenditure.timestamp.month
			if expenditures_by_month[m-1] in expenditures_by_month:
				expenditures_by_month[m-1] += expenditure.amount
			else:
				expenditures_by_month[m-1] = expenditure.amount

	payments = Payment.objects.filter(session=current_session, term=get_terms())
	payments_by_month = [0] * 12
	for month in range(1, 13):
		for payment in payments.filter(date_paid__month=month):
			m = payment.date_paid.month
			if payments_by_month[m-1] in payments_by_month:
				payments_by_month[m-1] += payment.paid_amount
			else:
				payments_by_month[m-1] = payment.paid_amount

	data = {
		"expenditure": expenditures_by_month,
		"income": payments_by_month,
		"current_session": current_session.name,
		}
	return JsonResponse(data)



@login_required
@teacher_required
def students_view(request):
	classes = Class.objects.all()
	# if teacher, then show only classes
	# that he/she is been assigned a subject in.
	# for current academic year, and current term
	if request.user.is_teacher:
		current_session = Session.objects.get(current_session=True)
		classes = SubjectAssign.objects.filter(
			teacher__id=request.user.id, 
			session=current_session, 
			term=get_terms())
	context = {"classes": classes}
	return render(request, 'sms/student/students.html', context)


@login_required
@admin_required
def delete_user(request, id):
	user = User.objects.get(pk=id)
	if user:
		user_name = user.get_full_name()
		if user.is_student:
		    current_session = Session.objects.get(current_session=True)
		    student = Student.objects.get(user__pk=user.pk, session=current_session)
		    class_id = student.in_class.pk
		    student.delete()
		    new_students_list = Student.objects.filter(in_class__pk=class_id, session=current_session)
		    context = {'students': new_students_list,}
		    return render(request, 'sms/student/new_students_list.html', context)
		elif user.is_teacher:
			user.delete()
			new_teachers_list = User.objects.filter(is_teacher=True)
			context = {'teachers': new_teachers_list,}
			return render(request, 'sms/teacher/new_teachers_list.html', context)
		elif user.is_parent:
			user.delete()
			new_parents_list = User.objects.filter(is_parent=True)
			context = {
				'parents': new_parents_list,
			}
			return render(request, 'sms/parent/new_parents_list.html', context)
		else:
			user.delete()
			messages.success(request, user_name + ' Successfully deleted !')
			return redirect('home')
	else:
		messages.error(request,' Please dont trick me, nothing is deleted !')
		return HttpResponse('nothing deleted')



@login_required
@teacher_required
def students_list_view(request, id):
    current_session = Session.objects.get(current_session=True)
    students = Student.objects.filter(in_class__pk=id, session=current_session)
    selected_class = Class.objects.get(pk=id)
    classes = Class.objects.all()

    # if teacher, then show only classes
	# that he/she is been assigned a subject in.
	# for current academic year, and current term

    if request.user.is_teacher:
    	current_session = Session.objects.get(current_session=True)
    	classes = SubjectAssign.objects.filter(
    		teacher__id=request.user.id, 
			session=current_session, 
			term=get_terms())
    context = {
        "selected_class": selected_class,
        "students": students,
        "classes": classes,
        }
    return render(request, 'sms/student/students_list.html', context)

@login_required
@admin_required
def section_view(request):
	sections = Section.objects.all()
	context = {"sections": sections}
	return render(request, 'sms/section/section.html', context)

@login_required
@admin_required
def assign_teacher_list(request):
	return render(request, 'sms/teacher/assign_list.html', {})


@login_required
@admin_required
def assign_teacher_view(request):
	if not request.GET.get('term') in ['First', 'Second', 'Third']:
		messages.error(request, ' ERROR: please select a term !')
		return redirect('assign_teacher_list')
	else:
		term = request.GET.get('term')
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
@admin_required
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

			try:
				record = SubjectAssign.objects.get(clss=class_id, session=current_session, term=term, teacher=teacher)
				ids = ()
				record.subjects.clear()
				for i in range(0, len(subjects)):
					ids += (subjects[i].name,)
					record.subjects.add(subjects[i])
					record.save()
				Notification(user=teacher, title="Subject Allocation !", body="Admin just updated the subjects allocated to you ! ", message_type=SUCCESS).save()
				
				sms_body = "Hello {}, \
							the school administrator just updated \
							the list of subjects allocated to you. \
							! Login now for details".format(teacher.get_full_name())
				send_sms(teacher.phone, sms_body)
				
				messages.success(request, 'Subjects were successfully updated')
				return HttpResponseRedirect(reverse_lazy('assign_teacher_list'))
			except SubjectAssign.DoesNotExist:
				record = SubjectAssign.objects.create(clss=class_id, session=current_session, term=term, teacher=teacher)
				ids = ()
				for i in range(0, len(subjects)):
					ids += (subjects[i].name,)
					record.subjects.add(subjects[i])
					record.save()
				Notification(user=teacher, title="Subject Allocation !", body="Admin just updated the subjects allocated to you ! ", message_type=SUCCESS).save()
				
				sms_body = "An admin just updated \
							the subjects allocated \
							to you !".format(teacher.get_full_name())
				send_sms(teacher.phone, sms_body)
				
				messages.success(request, 'Subjects were successfully allocated')
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
@admin_required
def section_allocation(request):
	sections = SectionAssign.objects.all()
	subjects = Subject.objects.all()
	context = {
		"subjects": subjects,
		"sections": sections,
		}
	return render(request, 'sms/section/section_allocation.html', context)


@login_required
@admin_required
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
				messages.info(request, "You've already allocated "+str(section_head)+" Section to "+ str(section_name) + " <a href='/section-allocation/edit/"+str(check.pk)+"'/>Click here to edit this information</a>")
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
@admin_required
def add_student(request):
	classes = Class.objects.all()
	general_setting = Setting.objects.first()
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

			stud_picture = form.cleaned_data['stud_picture']
			parent_picture = form.cleaned_data['parent_picture']

			existing_parent = form.cleaned_data.get('existing_parent')
			selected_class = Class.objects.get(pk=stud_class)

			if User.objects.filter(username=stud_username).exists():
				messages.error(request, 'A student with that username already exist !')
				return redirect('add_student')

			if Student.objects.filter(roll_number=stud_roll_number).exists():
				messages.error(request, 'A student with the entered roll number already exist !')
				return redirect('add_student')

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
				dob = stud_dob,
				address = stud_address,
				phone = stud_phone_number,
				picture = stud_picture,
				is_student = True,
				)

			student = Student.objects.create(
				user=user,
				in_class=selected_class,
				year_of_admission=stud_year_of_admission,
				roll_number = stud_roll_number,
				)

			if not any([parent_username, parent_password, existing_parent]):
				pass
			elif parent_username and parent_password:
				parent = User.objects.create(
					username = parent_username,
					password = make_password(parent_password),
					first_name = parent_fname,
					last_name = parent_sname,
					other_name = parent_oname,
					email = parent_email,
					state = parent_state,
					address = parent_address,
					phone = parent_phone_number,
					picture = parent_picture,
					is_parent = True,
					)

				par = Parent.objects.create(parent=parent)
				par.student.add(student)
				if parent_picture:
					fs = FileSystemStorage()
					fs.save(parent_picture.name, parent_picture)
			else:
				parent = Parent.objects.get(parent__username=existing_parent)
				parent.student.add(student)

			sms_body = "Hello {0}, \nWelcome to {1}. \
						Your login details are: \
						username: {2}\
						password: {3}\
						link: {4}".format(
							parent_fname, 
							general_setting.school_name, 
							parent_username, 
							parent_password, 
							request.META['HTTP_HOST']
							)

			send_sms(parent_phone_number, sms_body)

			if stud_picture:
				fs = FileSystemStorage()
				fs.save(stud_picture.name, stud_picture)
			messages.success(request, stud_fname + " " + stud_sname +' Was Successfully Recorded! ')
			return HttpResponseRedirect(reverse_lazy('add_student'))
		else:
			form = AddStudentForm(request.POST, request.FILES)
			context =  {
				"form": form,
				"parents": parents,
				"classes": classes,
				}
			return render(request, 'sms/student/add_student.html', context)

	else:
		context = {"classes": classes, "parents": parents,}
		return render(request, 'sms/student/add_student.html', context)



@login_required
@admin_required
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
			full_name = firstname+" "+surname
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
			if picture:
				fs = FileSystemStorage()
				fs.save(picture.name, picture)
			messages.success(request, firstname + " " + surname +' Was Successfully Recorded! ')
			
			sms_body="Hello {0}, \
					You can now access any of your child's school \
					record right from your mobile or pc device!\nLogin \
					using the link and the credentials below and we recommend \
					you change your password immediately.\
					username: {1}\
					password: {2}\
					link: {3}".format(
						full_name, 
						username, 
						password, 
						request.META['HTTP_HOST']
						)

			send_sms(phone, sms_body)

			return HttpResponseRedirect(reverse_lazy('add_parent'))
		else:
			form = AddParentForm(request.POST, request.FILES)
			context =  {
				"form": form,
				}
	return render(request, 'sms/parent/add_parent.html', context)


@login_required
@admin_required
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
			if picture:
				fs = FileSystemStorage()
				fs.save(picture.name, picture)
			messages.success(request, firstname + " " + surname +' Was successfully added! ')
			
			sms_body="Hello {0},\
					We are proud to have you as teacher. \
					Your login details are: \
					username: {1}\
					password: {2}\
					link: {3}".format(
						firstname, 
						username, 
						password, 
						request.META['HTTP_HOST']
					)
			send_sms(phone, sms_body)
			return HttpResponseRedirect(reverse_lazy('add_teacher'))
		else:
			form = AddParentForm(request.POST, request.FILES)
			context =  {
				"form": form,
				}
	return render(request, 'sms/teacher/add_teacher.html', context)



@login_required
@admin_required
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
			    ids = ()
			    section = Section.objects.get(pk=section_id)
			    clss = Class.objects.get(name=name)
			    clss.subjects.clear()
			    for i in range(0, len(selected_subjects)):
			        ids += (selected_subjects[i].name,)
			        clss.subjects.add(selected_subjects[i])
			    messages.success(request, clss.name +' Was successfully updated')
			    return HttpResponseRedirect(reverse_lazy('class_list'))
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
@admin_required
def delete_class(request, id):
	selected_class = Class.objects.get(pk=id)
	class_name = selected_class.name
	selected_class.delete()
	new_class_list = Class.objects.all()
	context = {
		'classes': new_class_list,
	}
	return render(request, 'sms/class/new_class_list.html', context)


@login_required
@admin_required
def delete_subject(request, id):
	selected_subject = Subject.objects.get(pk=id)
	subject_name = selected_subject.name
	selected_subject.delete()
	new_subjects_list = Subject.objects.all()
	context = {
		'subjects': new_subjects_list,
	}
	return render(request, 'sms/subject/new_subjects_list.html', context)


@login_required
@teacher_required
def delete_section(request, id):
	selected_section = Section.objects.get(pk=id)
	section_name = selected_section.name
	selected_section.delete()
	new_section_list = Section.objects.all()
	context = {
		'sections': new_section_list,
	}
	return render(request, 'sms/section/new_section_list.html', context)

@login_required
@admin_required
def delete_all_allocated_subjects(request, id):
	subjects = SubjectAssign.objects.get(pk=id)
	teacher = subjects.teacher
	notification = Notification.objects.filter(user__pk=subjects.teacher.pk, title__icontains='Subject Allocation')
	notification.delete()
	subjects.delete()
	messages.success(request, "Successfully deleted all subjects allocated to "+ str(teacher))
	return HttpResponseRedirect(reverse_lazy('assign_teacher_list'))


@login_required
@admin_required
def delete_section_allocation(request, id):
	allocated_section = SectionAssign.objects.get(pk=id)
	section_name = allocated_section.section
	notification = Notification.objects.filter(user__pk=allocated_section.section_head.pk ,body__icontains=section_name)
	notification.delete()
	allocated_section.delete()
	messages.success(request, "You've Successfully deallocated "+str(allocated_section.section)+" Section from "+ str(allocated_section.section_head.get_full_name()))
	return HttpResponseRedirect(reverse_lazy('section_allocation'))


@login_required
@admin_required
def delete_attendance(request, id):
	attendance = Attendance.objects.get(pk=id)
	student = attendance.student
	date = attendance.date
	attendance.delete()
	messages.success(request, "You've successfully deleted "+ str(student) +" from attendance of " + str(date))
	return HttpResponseRedirect(reverse_lazy('attendance_list'))


@login_required
@admin_required
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
@admin_required
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
@admin_required
def system_admin(request):
	users = User.objects.filter(is_superuser=True)
	return render(request, 'sms/users/user.html', { "users": users })

@login_required
@admin_required
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
def profile(request, user_id):
	user = get_object_or_404(User, id=user_id)
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
			return redirect("profile", user_id=user.id)
		else:
			user = get_object_or_404(User, id=user_id)
			form = UpdateProfileForm(request.POST)
			context = {
				"user": user,
				"form": form,
			}
	return render(request, 'sms/users/profile.html', context)


@login_required
@admin_required
def parents_view(request):
	parents = User.objects.filter(is_parent=True)
	context = {
		'parents': parents,
	}
	return render(request, 'sms/parent/parents.html', context)

@login_required
@admin_required
def class_view(request):
	classes = Class.objects.all()
	context = {
		'classes': classes,
	}
	return render(request, 'sms/class/class.html', context)


@login_required
@admin_required
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
			students = Student.objects.filter(in_class=selected_class, session=session)
			ids = ()
			for i in students:
				ids += (i.user.pk,)
			q = Attendance.objects.filter(date=date, student__user__pk__in=ids, term=term, session=session)
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
			students = Student.objects.filter(in_class__pk=class_id, session=current_session)
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


@login_required
@teacher_required
def save_attendance(request):
	if request.method == 'POST':
		session = Session.objects.get(current_session=True)
		term = request.POST.get('selected_term')
		date = request.POST.get('selected_date')

		stud_id = list(request.POST.getlist('student_id'))
		status = list(request.POST.getlist('status'))
		is_late = list(request.POST.getlist('is_late'))
		duration = list(request.POST.getlist('duration'))

		if len(is_late) < len(stud_id):
			for i in range(0, len(stud_id)):
				is_late.append(False)

		if len(status) < len(stud_id):
			for i in range(0, len(stud_id)):
				status.append(False)

		for i in range(0, len(stud_id)):
			student = Student.objects.get(pk=stud_id[i])
			d = duration[i]
			if status[i] == 'on':
				s = True
			else:
				s = False

			if is_late[i] == 'on':
				is_l = True
			else:
				is_l = False

			try:
				a = Attendance.objects.get(student=student, term=term, session=session, date=date)
				a.is_late = is_l
				a.is_present = s
				a.is_late_for = d
				a.save()
			except Attendance.DoesNotExist:
				Attendance(
					student=student,
					term=term,
					session=session,
					is_present=s,
					is_late=is_l,
					date=date,
					is_late_for=d
					).save()
		messages.success(request, "Successfully saved")
		return redirect('add_attendance')
	else:
		messages.error(request, "There's an error while creating an attendance record")
		return redirect('add_attendance')


@login_required
@admin_required
def toggle_session(request, id):
	selected_session = Session.objects.get(pk=id)
	current_session = Session.objects.get(current_session=True)
	current_session.current_session = False
	current_session.save()
	selected_session.current_session = True
	selected_session.save()
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


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
	current_session = Session.objects.filter(current_session=True).first()
	term=get_terms()
	classes = Class.objects.all()
	context = {"classes": classes, 'term': term}
	if request.user.is_teacher:
		assigned_subjects = SubjectAssign.objects.filter(teacher__id=request.user.id, session=current_session, term=term)
		context.update({"assigned_subjects": assigned_subjects})
	return render(request, 'sms/mark/get_score_list.html', context)

@login_required
@teacher_required
def score_entry(request):
	session = Session.objects.get(current_session=True)
	classes = Class.objects.all()
	term = get_terms()
	context = {"classes": classes, 'term':get_terms()}

	if request.method == 'POST':
		term = request.POST.get('term')
		subject = request.POST.get('subject')
		subject = Subject.objects.get(pk=subject)
		ca1 = list(request.POST.getlist('ca1'))
		ca2 = list(request.POST.getlist('ca2'))
		exam = list(request.POST.getlist('exam'))
		stud_id = list(request.POST.getlist('student_id'))

		for i in range(0, len(stud_id)):
			student = Student.objects.get(pk=stud_id[i])
			total = int(ca1[i] or '0') + int(ca2[i] or '0') + int(exam[i] or '0')
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
		return redirect('score_list')

	selected_class = request.GET.get('class')
	selected_term = request.GET.get('term')
	selected_subject = request.GET.get('subject')
	if request.user.is_superuser:
		if not None in [selected_class, selected_term, selected_subject]:
			selected_class = Class.objects.get(pk=selected_class)
			current_session = session
			students = Student.objects.filter(in_class__name=selected_class, session=session)

			student_data = []
			for student in students:
				term = request.GET.get('term')
				subject = request.GET.get('subject')
				subject = Subject.objects.get(pk=subject)
				# grade, created = Grade.objects.get_or_create(session=session, term=term, student=student, subject=subject)
				grade_obj = Grade.objects.filter(
				session=current_session,
				term=term,
				student=student,
				subject=subject).first() or Grade.objects.none()

				student_data += [(student, grade_obj)]
			context.update({
				"classes": classes,
				"selected_subject": selected_subject,
				"selected_class": selected_class,
				"selected_term": selected_term,
				"students": students,
				"student_data":student_data
				})
			return render(request, 'sms/mark/load_score_table.html', context)
	elif request.user.is_teacher:
		if not None in [selected_term, selected_subject]:
			selected_class_id = request.GET.get('scid')
			selected_class = Class.objects.get(id=selected_class_id)
			selected_class_name = selected_class.name
			current_session = Session.objects.get(current_session=True)
			students = Student.objects.filter(in_class__name=selected_class, session=current_session)

			subject = request.GET.get('subject')
			subject = Subject.objects.get(pk=subject)
			student_data = []
			for student in students:
				term = request.GET.get('term')
				grade_obj = Grade.objects.filter(
					session=current_session,
					term=term,
					student=student,
					subject=subject).first() or Grade.objects.none()

				student_data += [(student, grade_obj)]

			context.update({
				"classes": classes,
				"selected_subject": selected_subject,
				"selected_class_name": selected_class_name,
				"selected_term": selected_term,
				"students": students,
				"student_data":student_data})
		return render(request, 'sms/mark/load_score_table.html', context)
	return render(request, 'sms/mark/get_score_list.html', context)




@login_required
def view_score(request):
	session = Session.objects.get(current_session=True)
	if request.user.is_parent:

		# Get all the current sesssion students related 
		# to the parent that  fired the request
		
		students = Parent.objects.get(
			parent__pk=request.user.pk).student.filter(
			session=session)
		
		context = {
			"students": students,
			"term": get_terms(),
		}
		return render(request, 'sms/mark/parent_view_scores.html', context)
	elif request.user.is_student:
		student = Student.objects.get(user__pk=request.user.id, session=session)
		#subjects = student.in_class.subjects.all()
		scores = Grade.objects.filter(student=student.id, session=session, term=get_terms())
		context = {
			"scores": scores,
			"term": get_terms(),
		}
		return render(request, 'sms/mark/student_view_score.html', context)
	elif request.user.is_teacher:
		term = get_terms()
		teacher = User.objects.get(pk=request.user.id)
		classes = SubjectAssign.objects.filter(teacher=teacher.pk, session=session, term=term)
		context = {
			"classes": classes
			}
		return render(request, 'sms/mark/view_scores.html', context)
	else:
		classes = Class.objects.all().order_by('name')
		context = {
			"classes": classes
			}
		return render(request, 'sms/mark/view_scores.html', context)


@login_required
def load_score_table(request):
	if request.is_ajax():
		if request.user.is_parent:
			current_session = Session.objects.get(current_session=True)
			stud_id = request.GET.get('stud_id')
			grades = Grade.objects.filter(student__pk=stud_id, session=current_session, term=get_terms())
			context = {"grades": grades}
			return render(request, 'sms/mark/load_view_score.html', context)
		else:
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
			return render(request, 'sms/mark/load_view_score.html', {'grades': grades})


@login_required
@admin_required
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
@admin_required
def expenditure(request):
	expenses = Expense.objects.all().order_by('item')
	return render(request, 'sms/expenses/expense.html', {"expenses": expenses})

@login_required
@admin_required
def delete_expenditure(request, id):
	expense = Expense.objects.get(pk=id)
	expense.delete()
	new_exp_list = Expense.objects.all()
	context = {'expenses': new_exp_list,}
	return render(request, 'sms/expenses/new_exp_list.html', context)


@login_required
@admin_required
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

			paid_amount = float(paid_amount)
			damount = student.in_class.amount_to_pay

			if damount == None or damount == '':
				messages.success(request, ' You have to create a payment setting for the student\'s class, Account > Set Payment')
				classes = Class.objects.all().order_by('name')
				return render(request, 'sms/payments/add_payment.html', {"students": students, "classes": classes})

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
				messages.success(request,'Invalid amount !')
				return render(request, 'sms/payments/add_payment.html', {"students": students, "classes":classes})

			due_amount = damount - paid_amount
			if e == damount:
				payment_status = PAID
			elif e == 0:
				payment_status = NOT_PAID
			else:
				payment_status = PARTIALLY_PAID

			try:
				pay = Payment.objects.get(student=student, session=session, term=term)
				pay.due_amount=float(damount - e)
				pay.payment_status=payment_status
				pay.paid_amount=float(e)
				pay.payment_method =payment_method
				pay.teller_number=teller_number
				pay.save()
				messages.success(request, str(student) +'\'s payment was successfully updated')
			except Payment.DoesNotExist:
				Payment.objects.create(
				student=student,
				due_amount=float(due_amount),
				payment_status=payment_status,
				paid_amount=float(paid_amount),
				payment_method =payment_method,
				teller_number=teller_number,
				session=session,
				term=term).save()
				messages.success(request, str(student) +'\'s payment was successfully added')
			return redirect('view_payments')
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
@admin_required
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
@admin_required
def set_payment(request):
	if request.method == "POST":
	    try:
	        class_id = request.POST['class'] or None
	        amount_to_pay = request.POST.get('amount_to_pay')
	    except:
	        messages.success(request, ' Please Select a class')
	        return redirect('set_payment')
	    if all([class_id, amount_to_pay]):
	        clss = Class.objects.get(id=class_id)
	        clss.amount_to_pay = amount_to_pay=amount_to_pay
	        clss.save()
	        messages.success(request, ' Payment setting was successfully updated ')
	        return HttpResponseRedirect(reverse_lazy('set_payment'))
	    else:
		    messages.info(request, ' All fields are required ')
		    return HttpResponseRedirect(reverse_lazy('set_payment'))
	classes = Class.objects.all()
	context = {"classes": classes}
	return render(request, 'sms/settings/payment_setting.html', context)


@login_required
@admin_required
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
	return render(request, 'sms/payments/ajax_load_payment.html', {"payments": payments})

@login_required
@teacher_required
def load_students_of_class(request):
    current_session = Session.objects.get(current_session=True)
    class_id = request.GET.get('class')
    students = Student.objects.filter(in_class__pk=class_id, session=current_session)
    return render(request, 'sms/payments/ajax_load_students.html', {"students": students})

@login_required
@teacher_required
def load_student_users(request):
    current_session = Session.objects.get(current_session=True)
    class_id = request.GET.get('class')
    students = Student.objects.filter(in_class__pk=class_id, session=current_session)
    return render(request, 'sms/ajax/ajax_load_student_users.html', {"students": students})

@login_required
@admin_required
def session_view(request):
	sessions = Session.objects.all()
	return render(request, 'sms/academic_year/session.html', {"sessions": sessions})


@login_required
@admin_required
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
@admin_required
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
@admin_required
def sms_list(request):
	sms = Sms.objects.all()
	return render(request, 'sms/sms/sms.html', {"sms":sms})

@login_required
@admin_required
def mail(request):
	if request.method == "POST":
		form = EmailMessageForm(request.POST)
		if form.is_valid():
			title = form.cleaned_data.get('title')
			message = form.cleaned_data.get('message')
			image = form.cleaned_data.get('image')
			recipients = form.cleaned_data.get('recipients')

			# get author of the email
			admin = request.user

			mail = EmailMessage.objects.create(
				title=title,
				content=message,
				admin=admin
			)
			mail.save()

			# prepare html templates
			template = 'email_template.html'
			setting = Setting.objects.first()
			context= {
				'setting': setting,
				'mail': mail
				}

			mail_message = render_to_string(template, context)
			
			# add recipients one after another
			for i in recipients:
				mail.recipients.add(i)
				

			# send the actual email and redirect
			asyncio.run(mail.deliver_mail(content=mail_message))
			messages.success(request, 'Emails Successfully Send !')
			return redirect('mail')
		else:
			form = EmailMessageForm(request.POST)
			context = {"form": form}
			template = 'sms/mail/mail_view.html'
			return render(request, template, context)

	draft_mails = EmailMessage.objects.filter(status=PENDING)
	delivered_emails = EmailMessage.objects.filter(status=DELIVERED)
	context = {
		'draft_mails': draft_mails,
		'delivered_emails': delivered_emails
	}
	template = 'sms/mail/mail_view.html'
	return render(request, template, context)

@login_required
@admin_required
def send_bulk_sms(request):
	sms = Sms.objects.all()
	if request.method == "POST":
		form = SmsForm(request.POST)
		if form.is_valid():
			title = form.cleaned_data.get('title')
			sms_body = form.cleaned_data.get('body')
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
				asyncio.run(send_sms(user.phone, '{}, {}'.format(title, sms_body)))

			Sms.objects.create(title=title, body=body, to_user=to_user)
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


@login_required
@admin_required
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

			school_business_phone = form.cleaned_data.get('business_phone1')
			alt_business_phone = form.cleaned_data.get('business_phone2')
			business_email = form.cleaned_data.get('business_email')
			school_town = form.cleaned_data.get('school_town')
			social_link1 = form.cleaned_data.get('social_link1')
			social_link2 = form.cleaned_data.get('social_link2')
			social_link3 = form.cleaned_data.get('social_link3')

			a, created = Setting.objects.get_or_create(id=1)
			if not created:
				s = Setting.objects.first()
				if school_logo == None:
					school_logo = a.school_logo
				s.school_name=school_name
				s.school_address=school_address
				s.school_slogan=school_slogan
				s.school_logo=school_logo
				s.ft_begins=ft_begins
				s.ft_ends=ft_ends
				s.st_begins=st_begins
				s.st_ends=st_ends
				s.tt_begins=tt_begins
				s.tt_ends=tt_ends
				s.business_email=business_email
				s.business_phone1=school_business_phone
				s.business_phone2=alt_business_phone
				s.social_link1=social_link1
				s.social_link2=social_link2
				s.social_link3=social_link3
				s.school_town=school_town
				s.save()

				fs = FileSystemStorage()
				name = fs.save(school_logo.name, school_logo)
				context['url'] = fs.url(name)
				context['s'] = Setting.objects.first()
			messages.success(request, 'School settings successfully updated !')
			return redirect('general_setting')
		else:
			s = Setting.objects.first()
			form = SettingForm(request.POST)
			return render(request, 'sms/settings/general_setting.html', {"form":form, "s":s})
	else:
		s = Setting.objects.first()
		return render(request, 'sms/settings/general_setting.html', {"s":s})



@login_required
@admin_required
def reset_users_password_view(request):
	if request.is_ajax():
		if request.method == 'POST':
			user = request.POST.get('selected_user')
			new_pass = request.POST.get('new_password')
			user = User.objects.get(username=user)
			user.password = make_password(new_pass)
			user.save()
	return render(request, 'sms/users_password/users_password.html', {})


@login_required
@admin_required
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




@login_required
@admin_required
def grade_scale(request):
	scales = GradeScale.objects.all().order_by('-grade')
	return render(request, 'sms/mark/grade_scale.html', {'gradeScales': scales})


@login_required
@admin_required
def set_grade_scale(request):
	if request.method == "POST":
		grade = request.POST.get('grade') or None
		remark = request.POST.get('remark') or None
		mark_from = request.POST.get('mark_from') or None
		mark_upto = request.POST.get('mark_upto') or None

		if not None in [grade, remark, mark_from, mark_upto]:
		    try:
		        gr = GradeScale.objects.get(grade=grade)
		        gr.grade = grade
		        gr.mark_from = mark_from
		        gr.mark_upto = mark_upto
		        gr.remark = remark
		        gr.save()
		        messages.success(request, ' Grade Scale setting was successfully updated ')
		        return HttpResponseRedirect(reverse_lazy('set_grade_scale'))

		    except GradeScale.DoesNotExist:
		        try:
		            gr = GradeScale.objects.create(
		                grade = grade,
		                mark_from = mark_from,
		                mark_upto = mark_upto,
		                remark = remark)
		            messages.success(request, ' Grade Scale setting was successfully recorded ')
		            return HttpResponseRedirect(reverse_lazy('set_grade_scale'))
		        except IntegrityError:
		            messages.success(request, ' The selected mark range had already been applied to another grade !')
		            return HttpResponseRedirect(reverse_lazy('set_grade_scale'))
		    except IntegrityError:
		        messages.success(request, ' The selected mark range had already been applied to another grade !')
		        return HttpResponseRedirect(reverse_lazy('set_grade_scale'))
		else:
		    messages.success(request, ' All the fields are required !')
		    return HttpResponseRedirect(reverse_lazy('set_grade_scale'))
	else:
		scales = GradeScale.objects.all()
		return render(request, 'sms/mark/grade_scale.html', {'gradeScales': scales})


@login_required
@admin_required
def promotion(request):
	classes = Class.objects.all()
	sessions = Session.objects.all()
	return render(request, 'sms/promotion/promote.html', {'sessions': sessions, 'classes': classes})


@login_required
@admin_required
def to_class_list(request):
	if request.is_ajax:
		from_class = request.GET.get('from_class')
		classes = Class.objects.exclude(id=from_class)
		return render(request, 'sms/promotion/to_class_list.html', {'classes': classes})



@login_required
@admin_required
def load_promotion_list(request):
	if request.is_ajax():
		from_class_id = request.GET.get('from_class_id')
		to_class_id = request.GET.get('to_class_id')
		current_session = Session.objects.get(current_session=True)
		to_session = request.GET.get('to_session')
		ranking = Student.objects.filter(in_class__pk=from_class_id, session=current_session)
		context = {
			'term': get_terms(),
			'current_session': current_session,
			'ranking': ranking,
 			'to_session': to_session,
          	'from_class_id': from_class_id,
          	'to_class_id': to_class_id,
		}
		return render(request, 'sms/promotion/load_promotion_list.html', context)


@login_required
@admin_required
def promote(request, stud_id,  to_class_id, to_session_id):
	from_session = Session.objects.get(current_session=True)
	to_session = Session.objects.get(id=to_session_id)
	to_class = Class.objects.get(id=to_class_id)

	student = Student.objects.get(
		id=stud_id, 
		session=from_session)

	# get the parent of the student if exist
	parent = student.guardians.first() or student.guardians.none()

	# create copy of the student object 
	# changing only the session and the class of the student
	student.pk = None
	student.session = to_session
	student.in_class = to_class
	student.save()

	# connect the copied student with a parent
	parent.student.add(student)

	return HttpResponse('Promoted')

@login_required
def change_password(request):
    from django.contrib.auth import update_session_auth_hash
    if request.method == "POST":
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            old_pass = form.cleaned_data.get('old_password')
            new_pass = form.cleaned_data.get('new_password')
            confirm_password = form.cleaned_data.get('confirm_password')
            user = request.user
            old_p = user.password
            new_p = make_password(new_pass)
            if user.check_password(old_pass):
                if new_pass == confirm_password:
                    user.password = new_p
                    user.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, 'Your password was successfully updated!')
                    return redirect('change_password')
                else:
                    messages.success(request, 'New password and confirm password do not match !')
                    return redirect('change_password')
            else:
                messages.success(request, 'Old password is incorrect, you may contact the principal if this parsist !')
                return redirect('change_password')
        else:
            form = ChangePasswordForm(request.POST)
            return render(request, 'sms/users/change_password.html', {'form': form})
    else:
        return render(request, 'sms/users/change_password.html', {})

@login_required
def notice_board(request):
	if request.user.is_parent:
		notices = NoticeBoard.objects.filter(posted_to="Parent").order_by('-posted_on')
	elif request.user.is_teacher:
		notices = NoticeBoard.objects.filter(posted_to="Teacher").order_by('-posted_on')
	elif request.user.is_student:
		notices = NoticeBoard.objects.filter(posted_to="Student").order_by('-posted_on')
	else:
		notices = NoticeBoard.objects.all().order_by('-posted_on')
	return render(request, 'sms/notice/notice_board.html', {'notices': notices})


@login_required
@admin_required
def create_notice(request):
	if request.method == "POST":
		form = NoticeForm(request.POST)
		if form.is_valid():
			post_title = form.cleaned_data.get('post_title')
			post_body = form.cleaned_data.get('post_body')
			posted_by = request.user
			posted_to = form.cleaned_data.get('posted_to')
			NoticeBoard.objects.create(
				post_title=post_title,
				post_body=post_body,
				posted_by=posted_by,
				posted_to=posted_to,
				)
			messages.success(request, 'Successfully posted to all ' + posted_to + "s")
			return redirect('notice_board')
		else:
			form = NoticeForm(request.POST)
			return redirect('notice_board')
	else:
		return redirect('notice_board')


@login_required
@admin_required
def delete_notice(request, id):
	notice  = get_object_or_404(NoticeBoard, id=id)
	notice.delete()
	messages.success(request, 'Successfully deleted')
	return redirect('notice_board')


def handler404(request, exception, template_name="404.html"):
    response = render_to_response("404.html")
    response.status_code = 404
    return response

@login_required
@admin_required
def update_student(request, id):
	student = get_object_or_404(Student, id=id)
	user = get_object_or_404(User, id=student.user.id)
	if request.method == "POST":
		userForm = EditUserForm(request.POST, instance=user)
		studentForm = EditStudentForm(request.POST, instance=student)
		if all([userForm.is_valid(), studentForm.is_valid()]):
			user = userForm.save(commit=False)
			student = studentForm.save(commit=False)
			user.first_name = userForm.cleaned_data.get('first_name')
			user.last_name = userForm.cleaned_data.get('last_name')
			user.other_name = userForm.cleaned_data.get('other_name')
			user.religion = userForm.cleaned_data.get('religion')
			user.address = userForm.cleaned_data.get('address')
			user.gender = userForm.cleaned_data.get('gender')
			user.phone = userForm.cleaned_data.get('phone')
			User.email = userForm.cleaned_data.get('email')
			user.dob = userForm.cleaned_data.get('dob')
			user.state = userForm.cleaned_data.get('state')

			student.in_class = studentForm.cleaned_data.get('in_class')
			student.roll_number = studentForm.cleaned_data.get('roll_number')
			student.year_of_admission = studentForm.cleaned_data.get('year_of_admission')
			user.save()
			student.save()
			messages.success(request, 'Successfully updated {0}\'s information'.format(user.username))
			return redirect('edit_student', id=student.id)
		else:
			userForm = EditUserForm(request.POST, request.FILES)
			studentForm = EditStudentForm(request.POST)
			context = {
				'userForm':userForm,
				'studentForm': studentForm,
			}
			return render(request, 'sms/student/edit_student.html', context)
	else:
		userForm = EditUserForm(instance=user)
		studentForm = EditStudentForm(instance=student)
		context = {
				'userForm':userForm,
				'studentForm': studentForm,
		}
	return render(request, 'sms/student/edit_student.html', context)


@login_required
@admin_required
def update_user(request, id):
	user = get_object_or_404(User, id=id)
	if user.is_student:
		user_type = "Student"
	elif user.is_teacher:
		user_type = "Teacher"
	elif user.is_parent:
		user_type = "Parent"
	else:
		user_type = "Administrator"
	if request.method == "POST":
		form = EditUserForm(request.POST, instance=user)
		if form.is_valid():
			user = form.save(commit=False)
			user.first_name = form.cleaned_data.get('first_name')
			user.last_name = form.cleaned_data.get('last_name')
			user.other_name = form.cleaned_data.get('other_name')
			user.religion = form.cleaned_data.get('religion')
			user.address = form.cleaned_data.get('address')
			user.gender = form.cleaned_data.get('gender')
			user.phone = form.cleaned_data.get('phone')
			User.email = form.cleaned_data.get('email')
			user.dob = form.cleaned_data.get('dob')
			user.state = form.cleaned_data.get('state')
			user.save()
			messages.success(request, 'Successfully updated {0}\'s information '.format(user.username))
			return redirect('edit_user', id=user.id)
		else:
			form = EditUserForm(request.POST)
			context = {'form': form, 'user_type': user_type}
			return render(request, 'sms/users/edit_user.html', context)
	else:
		form = EditUserForm(instance=user)
		context = {'form': form, 'user_type': user_type}
		return render(request, 'sms/users/edit_user.html', context)


@login_required
@admin_required
def update_class(request, id):
	clss = get_object_or_404(Class, id=id)
	if request.method == "POST":
		form = EditClassForm(request.POST, instance=clss)
		if form.is_valid():
			form.save(commit=False)
			clss.name = form.cleaned_data.get('name')
			clss.section = form.cleaned_data.get('section')
			clss.amount_to_pay = form.cleaned_data.get('amount_to_pay')
			clss.save()
			messages.success(request, 'Class successfully updated')
			return redirect('class_list')
		else:
			form = EditClassForm(request.POST)
			return render(request, 'sms/class/edit_class.html', {'form': form})
	else:
		form = EditClassForm(instance=clss)
		return render(request, 'sms/class/edit_class.html', {'form': form})


@login_required
@admin_required
def update_subject(request, id):
	subject = get_object_or_404(Subject, id=id)
	if request.method == "POST":
		form = EditSubjectForm(request.POST, instance=subject)
		if form.is_valid():
			form.save(commit=False)
			subject.name = form.cleaned_data.get('name')
			subject.save()
			messages.success(request, 'Subject Successfully updated')
			return redirect('subjects_list')
		else:
			form = EditSubjectForm(request.POST, instance=subject)
			return render(request, 'sms/subject/edit_subject.html', {'form': form})
	else:
		form = EditSubjectForm(instance=subject)
		return render(request, 'sms/subject/edit_subject.html', {'form': form})


@login_required
@admin_required
def update_section(request, id):
	section = get_object_or_404(Section, id=id)
	if request.method == "POST":
		form = EditSectionForm(request.POST, instance=section)
		if form.is_valid():
			form.save(commit=False)
			section.name = form.cleaned_data.get('name')
			section.note = form.cleaned_data.get('note')
			section.save()
			messages.success(request, 'Section successfully updated')
			return redirect('sections_list')
		else:
			form = EditSectionForm(request.POST, instance=section)
			return render(request, 'sms/section/edit_section.html', {'form': form})
	else:
		form = EditSectionForm(instance=section)
		return render(request, 'sms/section/edit_section.html', {'form': form})

@login_required
@admin_required
def online_admission_list(request):
	current_session = get_object_or_404(Session, current_session=True)
	applications = OnlineAdmission.objects.filter(session=current_session)
	context = {
			'applications': applications
	}
	return render(request, 'sms/online_admission/online_admission_list.html', context)


@login_required
@admin_required
def update_section_allocation(request, id):
	section_allocation = get_object_or_404(SectionAssign, id=id)
	if request.method == "POST":
		form = EditSectionAllocationForm(request.POST, request.FILES, instance=section_allocation)
		if form.is_valid():
			form.save(commit=False)
			signature = form.cleaned_data.get('signature')
			section_allocation.section = form.cleaned_data.get('section')
			section_allocation.section_head = form.cleaned_data.get('section_head')
			section_allocation.signature = signature
			section_allocation.placeholder = form.cleaned_data.get('placeholder')
			fs = FileSystemStorage()
			fs.save(signature.name, signature)
			section_allocation.save()
			messages.success(request, 'Section allocation successfully updated ')
			return redirect('section_allocation')
		else:
			form = EditSectionAllocationForm(request.POST, request.FILES, instance=section_allocation)
			return render(request, 'sms/section/edit_section_allocation.html', {'form': form})
	else:
		form = EditSectionAllocationForm(instance=section_allocation)
		return render(request, 'sms/section/edit_section_allocation.html', {'form': form})


@login_required
@admin_required
def update_session(request, id):
	session = get_object_or_404(Session, id=id)
	if request.method == "POST":
		form = EditSessionForm(request.POST, instance=session)
		if form.is_valid():
			form.save(commit=False)
			session.name = form.cleaned_data.get('name')
			session.note = form.cleaned_data.get('note')
			session.save()
			return redirect('session_list')
		else:
			form = EditSessionForm(request.POST, instance=session)
			return render(request, 'sms/academic_year/edit_session.html', {'form': form})
	else:
		form = EditSessionForm(instance=session)
		return render(request, 'sms/academic_year/edit_session.html', {'form': form})



@login_required
@admin_required
def toggle_user_status(request, id):
	user = get_object_or_404(User, id=id)
	if request.user.id == user.id:
		return HttpResponse('You cannot deactivate your self')
	elif user.is_active:
		user.is_active = False
		user.save()
		return HttpResponse('deactivated')
	else:
		user.is_active = True
		user.save()
		return HttpResponse('activated')


@login_required
@admin_required
def update_expense(request, id):
	expense = get_object_or_404(Expense, id=id)
	if request.method == "POST":
		form = EditExpenseForm(request.POST, instance=expense)
		if form.is_valid():
			form.save(commit=False)
			expense.item = form.cleaned_data.get('item')
			expense.session = form.cleaned_data.get('session')
			expense.term = form.cleaned_data.get('term')
			expense.description = form.cleaned_data.get('description')
			expense.amount = form.cleaned_data.get('amount')
			expense.save()
			messages.success(request, 'Expense successfully updated')
			return redirect('view_expenses')
		else:
			form = EditExpenseForm(request.POST, instance=expense)
			return render(request, 'sms/expenses/edit_expense.html', {'form': form})
	else:
		form = EditExpenseForm(instance=expense)
		return render(request, 'sms/expenses/edit_expense.html', {'form': form})


@login_required
@admin_required
def set_parent(request):
	if request.method == "POST":
		form = SetParentForm(request.POST)
		if form.is_valid():
			student_id = form.cleaned_data.get('student_id')
			parent_id = form.cleaned_data.get('parent_id')

			student = get_object_or_404(Student, id=student_id)
			parent = get_object_or_404(Parent, parent__pk=parent_id)

			parent.student.add(student)
			messages.success(request, "You've successfully set a parent for the selected student")
			return redirect('set_parent')
		else:
			form = SetParentForm(request.POST)
			return render(request, 'sms/parent/set_parent.html', {'form': form})
	else:
		already_set = Parent.objects.all()
 
		# exclude those students 
		# who already has parents them in our q

		stud_ids = ()
		for parent in already_set:
			for student in parent.student.all():
				stud_ids += (student.id,)
		
		current_session = Session.objects.get(current_session=True)
		students = Student.objects.filter(session=current_session).exclude(id__in=stud_ids)
		parents = User.objects.filter(is_parent=True)
		return render(request, 'sms/parent/set_parent.html', {'students': students, 'parents': parents})

@login_required
def upload_picture(request):
	if request.is_ajax():
		form = ProfilePictureForm(request.POST, request.FILES)
		if form.is_valid():
			picture = form.cleaned_data.get('picture')
			user = get_object_or_404(User, id=request.user.id)
			user.picture = picture
			user.save()
			fs = FileSystemStorage()
			fs.save(picture.name, picture)
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
		else:
			form = ProfilePictureForm(request.POST, request.FILES)
			messages.success(request, form.errors)
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
@admin_required
def class_member_report_view(request):
	classes = Class.objects.all()
	session = Session.objects.all()
	context = {
		"session": session,
		"classes": classes,
	}
	return render(request, 'sms/reports_view/class_members_report_view.html', context)


@login_required
@admin_required
def class_member_report(request):
	from weasyprint import HTML, CSS
	class_id = request.GET.get('class')
	session = request.GET.get('session')
	if not session:
		session = Session.objects.get(current_session=True)
	else:
		session = Session.objects.get(pk=session)
	class_members = Student.objects.filter(in_class__pk=class_id, session=session.pk)
	setting = Setting.objects.first()
	term = get_terms()
	_class = get_object_or_404(Class, id=class_id) 
	context = {
		"session": session,
		"term": term,
		"class": _class,
		"class_members": class_members,
		"setting": setting
			}
	template = "sms/reports/class_members.html"
	template = get_template(template)
	html = template.render(context)

	css_string = """@page {
		size: a4 portrait;
		margin: 1mm;
		counter-increment: page;
	}"""

	pdf_file = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(
			stylesheets=[CSS(string=css_string)],presentational_hints=True)


	response = HttpResponse(pdf_file, content_type='application/pdf')
	response['Content-Disposition'] = 'filename="class_members.pdf"'
	return response
	return HttpResponse(response.getvalue(), content_type='application/pdf')

@login_required
@admin_required
def subject_allocation_report_view(request):
	session = Session.objects.all()
	classes = Class.objects.all()
	context = {
		"classes": classes,
		"session": session,
	}
	return render(request, 'sms/reports_view/subject_allocation_report_view.html', context)

@login_required
@admin_required
def subject_allocation_report(request):
	from weasyprint import HTML, CSS
	setting = Setting.objects.first()
	if not request.GET.get('term') in ['First', 'Second', 'Third']:
		messages.error(request, ' ERROR: please select a term !')
		return redirect('subject_allocation_report_view')
	elif not request.GET.get('session'):
		messages.error(request, ' ERROR: please select a session !')
		return redirect('subject_allocation_report_view')
	elif not request.GET.get('class'):
		messages.error(request, ' ERROR: please select a class !')
		return redirect('subject_allocation_report_view')
	else:
		term = request.GET.get('term')
		clss = request.GET.get('class')
		session = request.GET.get('session')
		session = get_object_or_404(Session, pk=session)
		context = {}
		default = []
		if clss == "All":
			clss = Class.objects.all().order_by('name')
			for klass in clss:
				assigned_teachers = SubjectAssign.objects.filter(
					term=term, 
					session=session.pk, 
					clss=klass)
				default += assigned_teachers
			context['assign_teacher_len'] = assign_teacher_len = len(default)
			context['classes'] = clss
		else:
			clss = get_object_or_404(Class, id=clss)
			default = SubjectAssign.objects.filter(
				term=term, 
				session=session.pk, 
				clss=clss.id)

			context['class'] = clss 
		total_number_of_teachers = User.objects.filter(
			is_teacher=True).count()

		context["setting"] = setting
		context["term"] = term
		context["session"] = session
		context["assigned_teachers"] = default
		context["session"] = session
		context["total_number_of_teachers"] = total_number_of_teachers
	template = "sms/reports/subject_allocation_report.html"
	template = get_template(template)
	html = template.render(context)

	css_string = """@page {
		size: a4 portrait;
		margin: 1mm;
		counter-increment: page;
	}"""

	pdf_file = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(
			stylesheets=[CSS(string=css_string)],presentational_hints=True)


	response = HttpResponse(pdf_file, content_type='application/pdf')
	response['Content-Disposition'] = 'filename="subject_allocation.pdf"'
	return response
	return HttpResponse(response.getvalue(), content_type='application/pdf')


@login_required
@admin_required
def subject_report_view(request):
	classes = Class.objects.all()
	context = {
		"classes": classes,
	}
	return render(request, 'sms/reports_view/subject_report_view.html', context)


@login_required
@admin_required
def subject_report(request):
	from weasyprint import HTML, CSS
	setting = Setting.objects.first()
	if not request.GET.get('term') in ['First', 'Second', 'Third']:
		messages.error(request, ' ERROR: please select a term !')
		return redirect('subject_report_view')
	elif not request.GET.get('subject'):
		messages.error(request, ' ERROR: please select a subject !')
		return redirect('subject_report_view')
	elif not request.GET.get('class'):
		messages.error(request, ' ERROR: please select a class !')
		return redirect('subject_report_view')
	else:
		session = Session.objects.get(current_session=True)
		term = request.GET.get('term')
		class_id = request.GET.get('class')
		subject = request.GET.get('subject')
		subjects = Subject.objects.filter(pk=subject)
		s = get_object_or_404(Subject, id=subject)
		subject_teacher = SubjectAssign.objects.filter(
			clss=class_id, 
			session=session, 
			term=term);
		for i in subject_teacher:
			for sub in i.subjects.all():
				if sub == s:
					subject_teacher = i.teacher
		clss = get_object_or_404(Class, pk=class_id)
		current_session = Session.objects.get(current_session=True)
		students = Student.objects.filter(in_class=clss, 
			session=current_session)
		if not students.exists():
			messages.success(request, 'No students exists for class {} in {} term'.format(clss, term))
			return redirect('subject_report_view')

		grades = Grade.objects.filter(term=term, student__in_class=clss,session=current_session).order_by('-total')
		class_avg = grades.filter(subject=subject)
		class_avg = class_avg.aggregate(class_avg=Sum('total')).get('class_avg') / class_avg.count()
		if not grades.exists():
			messages.success(request, 'No grades exists for class {} in {} term'.format(clss, term))
			return redirect('subject_report_view')

		records = ()
		count = 0
		for student in students:
			try:
				count += 1
				student_grades = grades.filter(student=student)
				data = get_subject_report_data(grades, subjects, student, student_grades)
				records += (data,)
			except Exception as e:
				DB_LOGGER.error('====================={}'.format(e))
		if not count:
			messages.success(request, '	Report for class {} in {} term does not exists'.format(clss, term))
			return redirect('subject_report_view')
		
		context = {'results':records,'term':term,'setting':setting }
		context['students'] = students
		context['session'] = session
		context['class'] = clss
		context['subject'] = s
		context['subject_teacher'] = subject_teacher
		context['class_avg'] = class_avg
		template = "sms/reports/subject_report.html"
		template = get_template(template)
		html = template.render(context)

		css_string = """@page {
			size: a4 portrait;
			margin: 1mm;
			counter-increment: page;
		}"""

		pdf_file = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(
				stylesheets=[CSS(string=css_string)],presentational_hints=True)


		response = HttpResponse(pdf_file, content_type='application/pdf')
		response['Content-Disposition'] = 'filename="subject_allocation.pdf"'
		return response
		return HttpResponse(response.getvalue(), content_type='application/pdf')

@login_required
@admin_required
def broadsheet_report_view(request):
	classes = Class.objects.all()
	session = Session.objects.all()
	context = {
		"session": session,
		"classes": classes,
	}
	return render(request, 'sms/reports_view/broadsheet_report_view.html', context)

@login_required
@admin_required
def broadsheet_report(request):
	from weasyprint import HTML, CSS
	setting = Setting.objects.first()
	if not request.GET.get('term') in ['First', 'Second', 'Third']:
		messages.error(request, ' ERROR: please select a term !')
		return redirect('broadsheet_report_view')
	elif not request.GET.get('session'):
		messages.error(request, ' ERROR: please select a session !')
		return redirect('broadsheet_report_view')
	elif not request.GET.get('class'):
		messages.error(request, ' ERROR: please select a class !')
		return redirect('broadsheet_report_view')
	else:
		session = request.GET.get('session')
		term = request.GET.get('term')
		class_id = request.GET.get('class')
		clss = get_object_or_404(Class, pk=class_id)
		session = get_object_or_404(Session, pk=session)
		subjects = get_object_or_404(Class, pk=class_id).subjects.all()
		grades = Grade.objects.filter(term=term, student__in_class=clss.pk, session=session.pk).order_by('-total')
		if not grades.exists():
			messages.success(request, 'No grades exists for class {} in term {} '.format(clss, term))
			return redirect('broadsheet_report_view')

		grades_ordered= grades\
		.values('student')\
		.annotate(total_mark=Sum('total'))\
		.order_by('-total_mark')
		total_marks = [i.get('total_mark') for i in grades_ordered]
		records = ()
		highest = grades_ordered.first()['total_mark']
		lowest = grades_ordered.last()['total_mark']
		students = Student.objects.filter(in_class=clss, session=session)
		count = 0
		for student in students:
			try:
				total_mark = (grades_ordered.get(student=student.pk)['total_mark'])
				setattr(student, 'total_mark', total_mark)
				student_rank = total_marks.index(total_mark)+1
				setattr(student, 'student_rank', student_rank)
				count += 1
				student_grades = grades.filter(student=student)
				data = get_subject_report_data(grades, subjects, student, student_grades)
				records += (data,)

			except Exception as e:
				DB_LOGGER.error('====================={}'.format(e))
		if not count:
			messages.success(request, 'No reports exists for class %s in term %r '%(clss, term))
			return redirect('broadsheet_report_view')
		additional_td = None
		for item in records:
			if len(item) < subjects.count():
				additional_td = subjects.count() - len(item)
		context = {
			"results": records,
			"term": term,
			"class": clss,
			"session": session,
			"setting": setting,
			"subjects": subjects,
			"additional_td": additional_td,
		}
		template = "sms/reports/broadsheet_report.html"
		template = get_template(template)
		html = template.render(context)

		css_string = """@page {
			size: a4 landscape;
			margin: 1mm;
			counter-increment: page;
		}"""

		pdf_file = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(
				stylesheets=[CSS(string=css_string)],presentational_hints=True)


		response = HttpResponse(pdf_file, content_type='application/pdf')
		response['Content-Disposition'] = 'filename="subject_allocation.pdf"'
		return response
		return HttpResponse(response.getvalue(), content_type='application/pdf')

@login_required
@admin_required
def view_detail_applicant(request, pk):
	applicant = get_object_or_404(OnlineAdmission, pk=pk)
	return render(
		request, 
		'sms/online_admission/online_admission_detail_view.html', 
		{"applicant": applicant}
	)

@login_required
@admin_required
def ajax_get_all_classes(request):
	if request.is_ajax():
		classes = Class.objects.all()
		template = 'sms/ajax/get_all_classes.html'
		context = {'classes': classes}
		return render(request, template, context)
	return HttpResponse('error')


@login_required
@admin_required
def ajax_get_users_list(request):
	if request.is_ajax():
		template = 'sms/ajax/get_filtered_user_list.html'
		user_type = request.GET.get('user_type')
		print(user_type)
		if user_type == 'parents':
			users = User.objects.filter(is_parent=True)
		elif user_type == 'admins':
			users = User.objects.filter(is_superuser=True)
		elif user_type == 'teachers':
			users = User.objects.filter(is_teacher=True)
		context = {'users': users}
		return render(request, template, context)
	return HttpResponse('error')