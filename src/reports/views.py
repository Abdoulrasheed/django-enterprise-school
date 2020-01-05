from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from utils.decorators import admin_required
from django.db.models import Sum, CharField, Value

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
			sub_rank = get_item_index(sub_grades, 'total', student_grades.filter(subject=subject).first().total)
			sub_student_grades = sub_student_grades.annotate(rank=Value(sub_rank, output_field=CharField()))
			result+=sub_student_grades.values()
	return result

@login_required
@admin_required
def report_card_sheet_view(request):
	classes = Class.objects.all()
	context = {"classes": classes}
	return render(request, 'reports_view/reportcard_sheet_view.html', context)


@admin_required
@login_required
def report_student(request):
	data = request.POST
	obj_id = data.get('pk') or None
	template ='reports/reportcard_sheet.html'
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
		messages.success(request, 'No grades exists for class %s in %r term'%(clss, term))
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
			DB_LOGGER.error(e)
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
		margin: 2mm;
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