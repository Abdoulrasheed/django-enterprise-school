import os
import csv
import json
from .forms import *
from .models import *
from utils.constants import *
from datetime import datetime
from django.views import View
from django.contrib import messages
from django.urls import reverse_lazy
from utils.helper import BulkCreateManager
from .remark import getRemark, get_grade
from frontend.models import OnlineAdmission
from django.views.generic import CreateView, TemplateView, UpdateView, DeleteView, ListView, FormView
from django.template.loader import render_to_string
from django.contrib.auth.hashers import make_password
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils import timezone as tz

from django.shortcuts import (
		get_object_or_404, 
		redirect, 
		render, 
		render_to_response
	)

from utils.decorators import (teacher_required, 
		student_required, 
		parent_required,
		admin_required
	)



import asyncio # not used

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
			if clss is not None:
				target_income += 88

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
	return render(request, 'home.html', context)



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



def load_students_in_class(request):
	if request.is_ajax():
		clss = request.GET.get('clss')
		clss = Class.objects.get(id=clss)
		students = Student.objects.filter(in_class=clss)
		ct = {"students": students}
		template_name = ""
		return render(request, template_name, ct)


@login_required
@admin_required
def section_view(request):
	sections = Section.objects.all()
	context = {"sections": sections}
	return render(request, 'section/section.html', context)


@method_decorator(admin_required, name='dispatch')
class SubjectAllocationList(ListView):
	model = SubjectAllocation
	template_name = 'subject_allocation/allocation_list.html'


@login_required
@admin_required
def assign_teacher_view(request):
	if not request.GET.get('term') in ['First', 'Second', 'Third']:
		messages.error(request, ' ERROR: please select a term !')
		return redirect('subject_allocation_list')
	else:
		term = request.GET.get('term')
		print(dir(SubjectAllocation))
		assigned_teachers = SubjectAllocation.objects.filter(
			term=term, 
			session=Session.objects.get_current_session())

		subjects = Subject.objects.all()
		context = {
		"term": term,
		"subjects": subjects,
		"assigned_teachers": assigned_teachers,
		}
	return render(request, 'subject_allocation/allocation_list.html', context)



@method_decorator(admin_required, name='dispatch')
class AddSubjectAllocation(CreateView):
	model = SubjectAllocation
	form_class = SubjectAllocationForm
	template_name = 'subject_allocation/allocation_form.html'

	def get_success_url(self):
		return reverse('subject_allocation_list')

	def form_valid(self, form):
		obj = form.save(commit=False)
		subjects = form.cleaned_data.get('subjects')
		current_session = Session.objects.get_current_session()
		sa, created = SubjectAllocation.objects.get_or_create(session=current_session,
			teacher=obj.teacher, term=obj.term,
			clss=obj.clss, batch=obj.batch)
		if not created:
			sa.subjects.clear()
			for s in subjects:
				sa.subjects.add(s)
		else:
			for s in subjects:
				sa.subjects.add(s)
		return HttpResponseRedirect(self.get_success_url())

@login_required
@admin_required
def section_allocation(request):
	sections = SectionAssign.objects.all()
	subjects = Subject.objects.all()
	context = {
		"subjects": subjects,
		"sections": sections,
		}
	return render(request, 'section/section_allocation.html', context)


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
		return render(request, 'section/new_section_allocation.html', context)
	return render(request, 'section/new_section_allocation.html', context)


@login_required
def load_batches(request):
    class_id = request.GET.get('class')
    if class_id:
    	batches = Batch.objects.filter(clss_id=class_id)
    else:
    	batches = Batch.objects.none()
    return render(request, 'ajax/batch_dropdown_list_options.html', {'batches': batches})


@method_decorator(login_required, name='dispatch')
class AddClass(CreateView):
	model = Class
	form_class = AddClassForm
	template_name = 'class/add_class.html'

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
	return render(request, 'class/new_class_list.html', context)


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
	return render(request, 'subject/new_subjects_list.html', context)


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
	return render(request, 'section/new_section_list.html', context)

@login_required
@admin_required
def delete_all_allocated_subjects(request, id):
	subjects = SubjectAssign.objects.get(pk=id)
	teacher = subjects.teacher
	notification = Notification.objects.filter(user__pk=subjects.teacher.pk, title__icontains='Subject Allocation')
	notification.delete()
	subjects.delete()
	messages.success(request, "Successfully deleted all subjects allocated to "+ str(teacher))
	return HttpResponseRedirect(reverse_lazy('subject_allocation_list'))


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

@method_decorator(login_required, name='dispatch')
class SubjectListView(ListView):
	model = Subject
	template_name = 'subject/subject_listview.html'


@method_decorator(login_required, name='dispatch')
class SubjectAddView(CreateView):
	model = Subject
	form_class = AddSubjectForm
	template_name = 'subject/add_subject.html'


@method_decorator(login_required, name='dispatch')
class BatchList(ListView):
	model = Batch
	template_name_suffix = '_list'
	ordering = ['-clss']


@method_decorator(login_required, name='dispatch')
class AddBatch(CreateView):
	model = Batch
	form_class = AddBatchForm
	template_name_suffix = '_form'


@method_decorator(login_required, name='dispatch')
class DeleteBatch(DeleteView):
	model = Batch

	def delete(self, request, *args, **kwargs):
		self.get_object().delete()
		batches = Batch.objects.all()
		ct = {'object_list': batches}
		return render(request, 'batch_list.html', ct)

class UpdateBatch(UpdateView):
	model = Batch
	form_class = AddBatchForm
	template_name_suffix = '_form'


@login_required
def load_subjects_by_section(request):
	template_name = 'mark/subject_dropdown_list_options.html'
	subjects = Class.objects.get(pk=request.GET.get('class')).section.subject_set.all()
	ct = {'subjects': subjects}
	return render(request, template_name, ct)


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
	return render(request, 'section/add_section.html', context)


@method_decorator(login_required, name='dispatch')
class ClassView(ListView):
	model = Class
	template_name = 'class/class.html'


@login_required
@admin_required
def subjects_view(request):
	subjects = Subject.objects.all()
	context = {
		'subjects': subjects,
	}
	return render(request, 'subject/subjects.html', context)


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
	template_name = 'mark/subject_dropdown_list_options.html'
	batch_id = request.GET.get('batch_id')
	subjects = Batch.objects.get(pk=batch_id).subjects.all()
	if request.user.is_teacher: 
		sub = SubjectAssign.objects.filter(teacher__id=request.user.id)
		for i in sub:
			clss = i.clss
			subjects = i.subjects.filter(subjectassign__clss=clss)
	ct = {'subjects': subjects}
	return render(request, template_name, ct)



@method_decorator(login_required, name='dispatch')
class MarkPercentageView(TemplateView):
	template_name = 'markpercentage/mark_percentage.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['mark_percentages'] = MarkPercentage.objects.all().order_by('section')
		return context


@method_decorator(login_required, name='dispatch')
class AddMarkPercentageView(CreateView):
	model = MarkPercentage
	form_class = AddMarkPercentageForm
	template_name = 'markpercentage/markpercentage_form.html'


@method_decorator(login_required, name='dispatch')
class UpdateMarkPercentageView(UpdateView):
	model = MarkPercentage
	fields = '__all__'


@method_decorator(login_required, name='dispatch')
class DeleteMarkPercentageView(DeleteView):
	model = MarkPercentage

	def delete(self, request, *args, **kwargs):
		self.get_object().delete()
		mark_percentages = MarkPercentage.objects.all()
		ct = {'mark_percentages': mark_percentages}
		return render(request, 'mark_percentage_data_table.html', ct)


@method_decorator(login_required, name='dispatch')
class MarkPermissionCreateView(View):
	template_name = 'scorepermission_create_form.html'
	parent_template_name = 'scorepermission_list_view.html'
	model = ScorePermission
	form_class = AddMarkPermissionForm

	def get(self, request):
		sections = Section.objects.all()
		ct = {'form': self.form_class, 'sections': sections}

		first_section = Section.objects.first().pk

		section_id = request.GET.get('pk', first_section)
		session_id = Session.objects.get_current_session().pk

		obj, created = ScorePermission.objects.get_or_create(
			section_id=section_id,
			session_id=session_id
		)

		if not created:
			ct['selected_section'] = obj.section_id or first_section
			ct['form'] = self.form_class(instance=obj)
		else:
			ct['selected_section'] = obj.section_id
		
		if request.is_ajax():
			return render(request, self.template_name, ct)
		return render(request, self.parent_template_name, ct)

	def post(self, request):
		form = self.form_class(request.POST)
		if form.is_valid():
			section_id = request.POST.get('section')
			section_id = Section.objects.get(pk=section_id).pk
			session_id = Session.objects.get_current_session().pk
			perm, created = ScorePermission.objects.update_or_create(
				section_id=section_id,
				session_id=session_id,
				defaults={**form.cleaned_data}
			)
			if created:
				print('created')

			messages.success(request, 'permissions successfully set')
			return redirect('mark_permission')
		else:
			sections = Section.objects.all()
			ct =  {'form': self.form_class(request.POST), 'sections': sections}
			return render(request, self.parent_template_name, ct)



@method_decorator(teacher_required, name='dispatch')
class ScoreListView(View):
	template_name = 'mark/score_list.html'
	model = Score

	def get(self, request):
		sections = Section.objects.all()
		term = get_terms()
		ct = {'sections': sections, 'term': term}
		g = Group.objects.get(name='teacher')
		if request.user.groups.filter(name='teacher').exists():
			assigned_subjects = SubjectAllocation.objects.filter(
				teacher__user__id=request.user.id, 
				session=Session.objects.get_current_session(),
				term=term
			)
			print(assigned_subjects)
			ct = {"assigned_subjects": assigned_subjects}
		return render(request, self.template_name, ct)


@login_required
def get_section_classes(request):
	if request.is_ajax():
		section = request.GET.get('section')
		if section:
			classes = Class.objects.filter(section_id=section).order_by('-name')
			template_name = 'mark/class_dropdown_options.html'
			return render(request, template_name, {'classes': classes})
		else:
			return HttpResponse('Provide Section')

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
	return render(request, 'mark/get_score_list.html', context)


@method_decorator(login_required, name='dispatch')
class ScoreEntry(View):
	def get(self, request):
		class_id = request.GET.get('class')
		batch_id = request.GET.get('batch')
		subject_id = request.GET.get('subject')
		subject = Subject.objects.get(pk=subject_id)
		section_id = Class.objects.get(pk=class_id).section_id

		grade_scale = GradeScale.objects.filter(section_id=section_id).values('mark_from', 'mark_upto', 'grade')
		mark_percentages = MarkPercentage.objects.filter(section_id=section_id)
		score_permission = ScorePermission.objects.get(
			session=Session.objects.get_current_session(),
			section_id=section_id,
			)
		batch = Batch.objects.get(pk=batch_id)
		students = batch.student_set.all() if not subject.subject_type == OPTIONAL else batch.student_set.filter(optional_subjects__pk__in=subject_id)

		ct = {
			'mark_percentages':mark_percentages, 'students': students, 
			'score_permission': score_permission, 'today': tz.now(), 
			'grade_scale': grade_scale, 'subject': subject, 'section': section_id}
		return render(request, 'mark/load_score_table.html', ct)

	def post(self, request):
		subject = request.POST.get('subject')
		subject = Subject.objects.get(pk=subject)
		score_list = request.POST.getlist('score')
		section_id = request.POST.get('section')
		stud_id = request.POST.getlist('student_id')

		mp = MarkPercentage.objects.filter(section_id=section_id)
		term = get_terms()

		session = Session.objects.get_current_session()
		students_list = Student.objects.filter(id__in=stud_id)

		score_list = []

		for i in mp:
			key = f'score-{i.id}'
			score_list = request.POST.getlist(key)

			for c, s in enumerate(students_list): # counter, student
				obj, created = Score.objects.get_or_create(
					session=session, term=term, 
					student=s, subject=subject, mark_percentage=i)
				if not created:
					obj.score = score_list[c] or 0
					obj.save()
				else:
					obj = Score.objects.get(
					session=session, term=term, 
					student=s, subject=subject, mark_percentage=i)
					obj.score = score_list[c] or 0
					obj.save()
		return HttpResponse('success')



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
		return render(request, 'mark/parent_view_scores.html', context)
	elif request.user.is_student:
		student = Student.objects.get(user__pk=request.user.id, session=session)
		#subjects = student.in_class.subjects.all()
		scores = Grade.objects.filter(student=student.id, session=session, term=get_terms())
		context = {
			"scores": scores,
			"term": get_terms(),
		}
		return render(request, 'mark/student_view_score.html', context)
	elif request.user.is_teacher:
		term = get_terms()
		teacher = User.objects.get(pk=request.user.id)
		classes = SubjectAssign.objects.filter(teacher=teacher.pk, session=session, term=term)
		context = {
			"classes": classes
			}
		return render(request, 'mark/view_scores.html', context)
	else:
		classes = Class.objects.all().order_by('name')
		context = {
			"classes": classes
			}
		return render(request, 'mark/view_scores.html', context)


@login_required
def load_score_table(request):
	if request.is_ajax():
		if request.user.is_parent:
			current_session = Session.objects.get(current_session=True)
			stud_id = request.GET.get('stud_id')
			grades = Grade.objects.filter(student__pk=stud_id, session=current_session, term=get_terms())
			context = {"grades": grades}
			return render(request, 'mark/load_view_score.html', context)
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
			return render(request, 'mark/load_view_score.html', {'grades': grades})


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
			return render(request, 'expenses/add_expense.html', {"form": form})
	else:
		return render(request, 'expenses/add_expense.html', {})


@login_required
@admin_required
def expenditure(request):
	expenses = Expense.objects.all().order_by('item')
	return render(request, 'expenses/expense.html', {"expenses": expenses})

@login_required
@admin_required
def delete_expenditure(request, id):
	expense = Expense.objects.get(pk=id)
	expense.delete()
	new_exp_list = Expense.objects.all()
	context = {'expenses': new_exp_list,}
	return render(request, 'expenses/new_exp_list.html', context)


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
				return render(request, 'payments/add_payment.html', {"students": students, "classes": classes})

			if payment_method == 'Bank' and teller_number in [None, '']:
				messages.success(request, ' Please provide the bank teller number')
				classes = Class.objects.all().order_by('name')
				return render(request, 'payments/add_payment.html', {"students": students, "classes": classes})
			p = Payment.objects.filter(student__pk=student.pk, term=term, session=session)
			prevAmount = 0
			for i in p:
				prevAmount += i.paid_amount
			e = prevAmount + paid_amount

			if e > damount:
				classes = Class.objects.all().order_by('name')
				messages.success(request,'Invalid amount !')
				return render(request, 'payments/add_payment.html', {"students": students, "classes":classes})

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
			return render(request, 'payments/add_payment.html', {"form": form, "students": students})
	else:
		students = Student.objects.all()
		classes = Class.objects.all().order_by('name')
		context = {
			"classes": classes,
			"students":students
		}
		return render(request, 'payments/add_payment.html', context)


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
	return render(request, 'payments/payment.html',context )


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
	return render(request, 'settings/payment_setting.html', context)


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
	return render(request, 'payments/ajax_load_payment.html', {"payments": payments})

@login_required
@teacher_required
def load_students_of_class(request):
    current_session = Session.objects.get(current_session=True)
    class_id = request.GET.get('class')
    students = Student.objects.filter(in_class__pk=class_id, session=current_session)
    return render(request, 'payments/ajax_load_students.html', {"students": students})

@login_required
@teacher_required
def load_student_users(request):
    current_session = Session.objects.get(current_session=True)
    class_id = request.GET.get('class')
    students = Student.objects.filter(in_class__pk=class_id, session=current_session)
    return render(request, 'ajax/ajax_load_student_users.html', {"students": students})

@login_required
@admin_required
def session_view(request):
	sessions = Session.objects.all()
	return render(request, 'academic_year/session.html', {"sessions": sessions})


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
			return render(request, 'academic_year/session.html', context)
	return render(request, 'academic_year/session.html', {"sessions": sessions})


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
	return render(request, 'academic_year/session.html', {"sessions":sessions})


@login_required
@admin_required
def subject_syllabus(request):
	classes = Class.objects.all()
	template = 'syllabus/syllabus_list.html'
	return render(request, template, {'classes': classes})


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
			return render(request, 'settings/general_setting.html', {"form":form, "s":s})
	else:
		s = Setting.objects.first()
		return render(request, 'settings/general_setting.html', {"s":s})



@method_decorator(login_required, name="dispatch")
class GradeScaleListView(ListView):
	template_name = 'mark/grade_scale.html'
	model = GradeScale


@method_decorator(login_required, name="dispatch")
class GradeScaleCreateView(CreateView):
	template_name = 'mark/grade_scale.html'
	model = GradeScale
	form_class = AddGradeScaleForm

	success_url = '/app/grade_scale/'

class GradeScaleUpdateView(UpdateView):
	model = GradeScale
	template_name = 'mark/grade_scale.html'
	form_class = AddGradeScaleForm

class GradeScaleDeleteView(DeleteView):
	model = GradeScale

	def delete(self, request, *args, **kwargs):
		self.get_object().delete()
		object_list = GradeScale.objects.all()
		ct = {'object_list': object_list}
		return redirect('grade_scale')

@login_required
def get_gradescale_form_modal(request):
	form = AddGradeScaleForm
	return render(request, 'grade_scale_modal.html', {"form": form})

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
	return render(request, 'notice/notice_board.html', {'notices': notices})


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
			return render(request, 'class/edit_class.html', {'form': form})
	else:
		form = EditClassForm(instance=clss)
		return render(request, 'class/edit_class.html', {'form': form})


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
			return render(request, 'subject/edit_subject.html', {'form': form})
	else:
		form = EditSubjectForm(instance=subject)
		return render(request, 'subject/edit_subject.html', {'form': form})


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
			return render(request, 'section/edit_section.html', {'form': form})
	else:
		form = EditSectionForm(instance=section)
		return render(request, 'section/edit_section.html', {'form': form})

@login_required
@admin_required
def online_admission_list(request):
	current_session = get_object_or_404(Session, current_session=True)
	applications = OnlineAdmission.objects.filter(session=current_session)
	context = {
			'applications': applications
	}
	return render(request, 'online_admission/online_admission_list.html', context)


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
			return render(request, 'section/edit_section_allocation.html', {'form': form})
	else:
		form = EditSectionAllocationForm(instance=section_allocation)
		return render(request, 'section/edit_section_allocation.html', {'form': form})


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
			return render(request, 'academic_year/edit_session.html', {'form': form})
	else:
		form = EditSessionForm(instance=session)
		return render(request, 'academic_year/edit_session.html', {'form': form})



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
			return render(request, 'expenses/edit_expense.html', {'form': form})
	else:
		form = EditExpenseForm(instance=expense)
		return render(request, 'expenses/edit_expense.html', {'form': form})


@login_required
@admin_required
def set_parent(request):
	if request.method == "POST":
		form = SetParentForm(request.POST)
		if form.is_valid():
			student_id = form.cleaned_data.get('student_id')
			parent_id = 1

			student = get_object_or_404(Student, id=student_id)
			parent = get_object_or_404(Parent, parent__pk=parent_id)

			parent.student.add(student)
			messages.success(request, "You've successfully set a parent for the selected student")
			return redirect('set_parent')
		else:
			form = SetParentForm(request.POST)
			return render(request, 'parent/set_parent.html', {'form': form})
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
		return render(request, 'parent/set_parent.html', {'students': students, 'parents': parents})


@login_required
@admin_required
def view_detail_applicant(request, pk):
	applicant = get_object_or_404(OnlineAdmission, pk=pk)
	return render(
		request, 
		'online_admission/online_admission_detail_view.html', 
		{"applicant": applicant}
	)

@login_required
@admin_required
def ajax_get_all_classes(request):
	if request.is_ajax():
		classes = Class.objects.all()
		template = 'ajax/get_all_classes.html'
		context = {'classes': classes}
		return render(request, template, context)
	return HttpResponse('error')



@login_required
@admin_required
def ajax_seek_renewal(request):
	if request.is_ajax():
		phone = Setting.objects.first().business_phone1
		from django.core.mail import EmailMessage
		content = f'Hello, hope you are doing good \
							\n {request.tenant} just requested that they wants\
							to renew their subscription. \n Below is their contact\n \
							Phone: {phone}'
		recipients = ['abdulrasheedibrahim47@gmail.com', 'abdulrasheedibraheem47@yahoo.com']
		msg = EmailMessage(f'{request.tenant} [RENEWAL REQUEST]', content, "bot@bitpoint.com", recipients)
		msg.send()
		return HttpResponse('success')

@login_required
def import_scores(request):
	import codecs
	template = 'import/import_score_view.html'
	form = ImportForm(request.FILES)
	if request.method == "POST":
		#if form.is_valid():
		#file = form.cleaned_data.get('csv_file')

		file = request.FILES['csv_file']
		bulk_mgr = BulkCreateManager(chunk_size=20)
		reader = csv.reader(codecs.iterdecode(file, 'utf-8'))
		next(reader, None)  # skip the headers
		session = Session.objects.get(current_session=True)
		for row in reader:
			class_ = row[5]
			total = float(row[1] or 0) + float(row[2] or 0) + float(row[3] or 0)
			subject = Subject.objects.get(name=row[4])
			student = Student.objects.get(
				roll_number=row[0],
				session=session, 
				in_class__name=class_)
			bulk_mgr.add(
				Grade(
					session=session, 
					term=get_terms(),
					student=student,
					subject=subject,
					fca=row[1] or 0,
					sca=row[2] or 0,
					exam=row[3] or 0,
					total=total,
					grade=getGrade(total),
					remark=getRemark(total)
					))
			bulk_mgr.done()
		messages.success(request, 'Scores successfully recorded')
		return redirect('import_users')
	else:
		return render(request, template, {})


@method_decorator(login_required, name='dispatch')
class RoleView(View):
	template_name = "role/role_list_view.html"
	model = Group

	def get(self, request):
		object_list = Group.objects.all()
		ct = {"object_list": object_list}
		return render(request, self.template_name, ct)

	def post(self, request):
		form = RoleAddForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect("sms_roles_view")
		else:
			return render(request, self.template_name, {"form": form})


@method_decorator(login_required, name='dispatch')
class RoleAddView(View):
	template_name = "role/sms_role_add_view.html"
	form_class = RoleAddForm()

	def get(self, request):
		ct = { "form": self.form_class }
		return render(request, self.template_name, ct)


@method_decorator(login_required, name='dispatch')
class PermissionView(View):
	template_name = "role/sms_permission_list_view.html"
	model = Group

	def get(self, request):
		return render(
			request, 
			self.template_name, 
			{"roles": self.model.objects.all()}
		)

	def post(self, request):
		data = request.POST.copy()
		_group = data['group']
		del data['csrfmiddlewaretoken']
		del data['group']
		codenames = []
		group = Group.objects.get(id=_group)
		[codenames.append(i) for i in data]
		permissions = Permission.objects.filter(codename__in=codenames)
		group.permissions.add(*permissions)
		messages.success(
			request, f'Permissions has been successfully updated'
		)
		return redirect('sms_permissions_view')


@login_required
def loadpersmissions(request):
	role_id = request.GET.get('role_id')
	template_name = "ajax/load_permission.html"
	features = ContentType.objects.filter(app_label='sms')
	group = Group.objects.get(id=role_id)
	ct = {'features': features, 'group': group}
	return render(request, template_name, ct)


@login_required
def get_batch_optional_subjects(request):
	template_name = 'mark/subject_dropdown_list_options.html'
	batch_id = request.GET.get('batch_id')
	subjects = Batch.objects.get(pk=batch_id).subjects.filter(subject_type=OPTIONAL)
	ct = {"subjects": subjects}
	return render(request, template_name, ct)