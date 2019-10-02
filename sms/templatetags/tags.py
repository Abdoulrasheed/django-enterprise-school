import math
from django import template
from schools.models import Client, Domain
from sms.models import Setting
from authentication.models import User
from django_tenants.utils import schema_context

register = template.Library()
from sms.models import Subject, Student, Grade, Class, Session
from django.db.models import Sum

ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(math.floor(n/10)%10!=1)*(n%10<4)*n%10::4])

@register.simple_tag
def get_rank(rank):
	return ordinal(int(rank))

@register.simple_tag
def get_subject(pk):
	return Subject.objects.get(pk=int(pk))

@register.simple_tag
def get_student_roll_no(pk):
	return Student.objects.get(pk=int(pk)).roll_number

@register.simple_tag
def get_student_fname(pk):
	return Student.objects.get(pk=int(pk)).user.first_name

@register.simple_tag
def get_student_lname(pk):
	return Student.objects.get(pk=int(pk)).user.last_name

@register.simple_tag
def get_student_oname(pk):
	return Student.objects.get(pk=int(pk)).user.other_name or "--"

@register.simple_tag
def get_student_full_name(pk):
	return Student.objects.get(pk=pk).user.get_full_name()

@register.simple_tag
def get_subject_total_score(subject, student):
	return Grade.objects.get(subject=subject, student=student).total

@register.simple_tag
def get_overall_total(student, term, session):
	return Grade.objects.filter(student=student, term=term, session=session).aggregate(overall=Sum('total')).get('overall')

@register.simple_tag
def calculate_avg(student, term, session, num_subjects):
	overall = get_overall_total(student, term, session)
	return (float(overall) / float(num_subjects))

@register.simple_tag
def get_student_rank(clss, session, term, student):
	student =  Student.objects.get(pk=student)
	grades = Grade.objects.filter(term=term, student__in_class=clss,session=session).order_by('-total')
	grades_ordered= grades\
	.values('student')\
	.annotate(total_mark=Sum('total'))\
	.order_by('-total_mark')
	total_marks = [i.get('total_mark') for i in grades_ordered]
	records = {}
	highest = grades_ordered.first()['total_mark']
	lowest = grades_ordered.last()['total_mark']
	try:
		total_mark = (grades_ordered.get(student=student.pk)['total_mark'])
		setattr(student, 'total_mark', total_mark)
		student_rank = total_marks.index(total_mark)+1
		return student_rank
	except Exception as e:
		DB_LOGGER.error('{}'.format(e))
		return None

@register.simple_tag
def get_class_avg(clss, session, term, no_of_students):
	clss = Class.objects.get(pk=clss)
	session = Session.objects.get(pk=session)
	grades = Grade.objects.filter(student__in_class=clss, session=session, term=term)
	print(grades.count())
	avg = grades.aggregate(overall=Sum('total')).get('overall') / float(no_of_students)
	return round(avg, 2)

@register.simple_tag
def get_subject_avg(subject_id, session, clss, no_of_students, term):
	return round(Grade.objects.filter(subject=subject_id, session=session.pk, term=term).aggregate(subject_avg=Sum('total')).get('subject_avg') / no_of_students, 2)


@register.simple_tag
def check_if_promoted(student, session):
	if Student.objects.filter(user__pk=student.user.pk, session=session).exists():
		return 1
	else:
		return 0

from ..remark import getGradeWithTotalApproximate
@register.simple_tag
def get_grade(total):
	if total > 100:
		return 'A'
	return getGradeWithTotalApproximate(total)

@register.simple_tag
def get_tenant_domain(tenant_id):
	tenant_domain = Domain.objects.get(tenant_id=tenant_id).domain
	return tenant_domain

@register.simple_tag
def get_tenant_data(data, tenant_id):
	tenant = Client.objects.get(id=tenant_id)
	with schema_context(tenant.schema_name):
		if data == 'sms_unit':
			unit = Setting.objects.first().sms_unit
			return unit
		if data == 'no_studs':
			students = User.objects.filter(is_student=True).count()
			return students
