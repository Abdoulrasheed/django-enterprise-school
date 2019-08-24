from django.db import models
from django.conf import settings
from authentication.models import User
from constants import *
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from django.utils.translation import ugettext_lazy as _

from django.template.defaultfilters import slugify

from django.core.mail import EmailMessage as EMessage

from datetime import date

import asyncio

import re

from django.utils import timezone as tz

from django.db.models import Sum

def get_terms():
	term = 'First'
	now = tz.now()
	date = tz.localtime(now).date()
	setting = Setting.objects.first()

	if setting:
		st_begins, st_ends = setting.st_begins, setting.st_ends
		tt_begins, tt_ends = setting.tt_begins, setting.tt_ends
		if (st_begins and st_begins) and (date >= st_begins) and (date <=st_ends):
			term = 'Second'
		if (tt_begins and tt_ends) and (date >= tt_begins) and (date <=tt_ends):
			term = 'Third'
	return term

class Session(models.Model):
	name = models.CharField(max_length=100)
	note = models.CharField(max_length=200, blank=True, null=True)
	current_session = models.BooleanField()
	created_on = models.DateTimeField(auto_now_add=True)

	def get_current_session():
		return Session.objects.get(current_session=True).name

	def __str__(self):
		return self.name


class Section(models.Model):
	name = models.CharField(max_length=100, unique=True)
	note = models.CharField(max_length=200, blank=True, null=True)


	def __str__(self):
		return self.name



class Subject(models.Model):
	name = models.CharField(max_length=200, unique=True)


	def __str__(self):
		return self.name

class Class(models.Model):
	name = models.CharField(max_length=100)
	section = models.ForeignKey(Section, on_delete=models.CASCADE)
	subjects = models.ManyToManyField(Subject)
	amount_to_pay = models.FloatField(blank=True, null=True)


	def __str__(self):
		return self.name

	class Meta:
		verbose_name_plural = 'classes'

def get_current_session():
    return Session.objects.get(current_session=True).id

class Student(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	in_class = models.ForeignKey(Class, on_delete=models.CASCADE)
	session = models.ForeignKey(Session, default=get_current_session, on_delete=models.CASCADE)
	year_of_admission = models.CharField(max_length=100, blank=True, null=True)
	roll_number = models.CharField(max_length=50)

	def __str__(self):
		return self.user.get_full_name()

class Parent(models.Model):
	parent = models.ForeignKey(User, on_delete=models.CASCADE)
	student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="childrens")

	def __str__(self):
		return self.parent.get_full_name()


class SubjectAssign(models.Model):
	session = models.ForeignKey(Session, on_delete=models.CASCADE)
	term = models.CharField(choices=TERM, max_length=7)
	clss = models.ForeignKey(Class, on_delete=models.CASCADE)
	teacher = models.ForeignKey(User, on_delete=models.CASCADE)
	subjects = models.ManyToManyField(Subject, blank=True)



class SectionAssign(models.Model):
	section_head = models.ForeignKey(User, on_delete=models.CASCADE)
	section = models.ForeignKey(Section, on_delete=models.CASCADE)
	placeholder = models.CharField(max_length=100)
	signature = models.ImageField(upload_to="school_signature/", blank=True, null=True)

class Grade(models.Model):
	session = models.ForeignKey(Session, on_delete=models.CASCADE)
	term = models.CharField(choices=TERM, max_length=7)
	student = models.ForeignKey(Student, on_delete=models.CASCADE)
	subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
	fca = models.CharField(max_length=10)
	sca = models.CharField(max_length=10)
	exam = models.CharField(max_length=10)
	total = models.FloatField(blank=True, null=True)
	grade = models.CharField(choices=GRADE, max_length=1, blank=True, null=True)
	remark = models.CharField(max_length=50, blank=True, null=True)

	def compute_position(self, term):
		cs = Session.objects.get(current_session=True)
		total = 0
		all_score = Grade.objects.filter(student__id=self.student.id)
		for i in all_score:
			if i.total == None:
				total += 0
			else:
				total += float(i.total)
		try:
			r = Ranking.objects.get(session=cs, term=term, student=self.student)
			r.cumulative=total
			r.save()
		except Ranking.DoesNotExist:
			a = Ranking.objects.create(
				session=cs,
				term=term,
				student=self.student,
				cumulative=total,
				)


class Attendance(models.Model):
	""" Attendance have some deprecated fields that i need to remove
		instead of is_present, is_absent etc, we'll have a status field 
		that takes a value of either A (Absent), P (Present)
	"""
	student = models.ForeignKey(Student, on_delete=models.CASCADE)
	session = models.ForeignKey(Session, on_delete=models.CASCADE)
	term = models.CharField(choices=TERM, max_length=7)
	date = models.DateField()
	is_present = models.BooleanField(default=False)
	is_late = models.BooleanField(blank=True, null=True)
	is_late_for = models.CharField(max_length=4, blank=True, null=True)


	def __str__(self):
		return self.student.user.get_full_name()

class FeeType(models.Model):
	name = models.CharField(max_length=100)
	for_class = models.ManyToManyField(Class)
	amount = models.FloatField()
	session = models.ForeignKey(Session, on_delete=models.CASCADE)
	term = models.CharField(choices=TERM, max_length=7)

	def __str__(self):
		return self.name

class Payment(models.Model):
	student = models.ForeignKey(Student, on_delete=models.CASCADE)
	paid_amount = models.FloatField()
	due_amount = models.FloatField()
	date_paid = models.DateTimeField(auto_now_add=True)
	payment_method = models.CharField(choices=PAYMENT_METHOD, max_length=50)
	payment_status = models.CharField(choices=PAYMENT_STATUS, max_length=50)
	term = models.CharField(choices=TERM, max_length=7)
	session = models.ForeignKey(Session, on_delete=models.CASCADE)
	teller_number = models.CharField(max_length=100, blank=True, null=True)

	def __str__(self):
		return self.student.roll_number

class Expense(models.Model):
	item = models.CharField(max_length=100)
	description = models.CharField(max_length=500, blank=True, null=True)
	timestamp = models.DateTimeField(auto_now_add=True)
	session = models.ForeignKey(Session, on_delete=models.CASCADE)
	term = models.CharField(choices=TERM, max_length=7)
	amount = models.FloatField()


	def __str__(self):
		return self.item

class Setting(models.Model):
	school_name = models.CharField(max_length=100)
	school_logo = models.ImageField(upload_to="pictures/", blank=True, null=True)
	school_address = models.CharField(max_length=300, blank=True, null=True)
	school_town = models.CharField(max_length=100, blank=True, null=True)
	school_slogan = models.CharField(max_length=200, blank=True, null=True)
	business_email = models.EmailField(blank=True, null=True)
	business_phone1 = models.CharField(max_length=11, blank=True, null=True)
	business_phone2 = models.CharField(max_length=11, blank=True, null=True)
	social_link1 = models.CharField(max_length=200, blank=True, null=True)
	social_link2 = models.CharField(max_length=200, blank=True, null=True)
	social_link3 = models.CharField(max_length=200, blank=True, null=True)
	ft_begins = models.DateField(blank=True, null=True)
	ft_ends = models.DateField(blank=True, null=True)
	st_begins = models.DateField(blank=True, null=True)
	st_ends = models.DateField(blank=True, null=True)
	tt_begins = models.DateField(blank=True, null=True)
	tt_ends = models.DateField(blank=True, null=True)
	sms_unit = models.IntegerField(default=200)

	def get_logo(self):
		no_logo = settings.STATIC_ROOT + '/static/img/logo.png'
		try:
			return self.school_logo.url
		except:
			return no_logo

class Notification(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	title = models.CharField(max_length=100)
	body = models.CharField(max_length=300)
	unread = models.BooleanField(default=False)
	time = models.DateTimeField(auto_now_add=True)
	message_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE)

class GradeScale(models.Model):
	grade = models.CharField(choices=GRADE, max_length=100, unique=True)
	mark_from = models.IntegerField(unique=True)
	mark_upto = models.IntegerField(unique=True)
	remark = models.CharField(max_length=20, unique=True)


class Sms(models.Model):
	to_user = models.CharField(max_length=10)
	title = models.CharField(max_length=100)
	date_send = models.DateTimeField(auto_now_add=True)
	body = models.CharField(max_length=250)
	status = models.CharField(max_length=1, choices=STATUS, default=PENDING)

class Ranking(models.Model):
	student = models.ForeignKey(Student, on_delete=models.CASCADE)
	term = models.CharField(max_length=12, choices=TERM)
	session = models.ForeignKey(Session, on_delete=models.CASCADE)
	cumulative = models.FloatField()
	rank = models.CharField(max_length=5, blank=True, null=True)

class NoticeBoard(models.Model):
    post_title = models.CharField(max_length=100, blank=True, null=True)
    post_body = models.TextField(blank=True, null=True)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    posted_to = models.CharField(max_length=100, blank=True, null=True)
    posted_on = models.DateTimeField(auto_now_add=True)


class EmailQuerySet(models.query.QuerySet):
    """Personalized queryset created to improve model usability"""

    def get_delivered(self):
        """Returns only the delivered items in the current queryset."""
        return self.filter(status="S")

    def get_drafts(self):
        """Returns only the items marked as DRAFT in the current queryset."""
        return self.filter(status="D")

    def get_pendings(self):
        """Returns only the items marked as DRAFT in the current queryset."""
        return self.filter(status="P")


class EmailMessage(models.Model):
    admin = models.ForeignKey(
        User, null=True, related_name="author",
        on_delete=models.SET_NULL)
    image = models.ImageField(
        _('Featured image'), null=True, upload_to='articles_pictures/%Y/%m/%d/')
    timestamp = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255, null=False)
    slug = models.SlugField(max_length=80, null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS, default=PENDING)
    content = MarkdownxField()
    recipients = models.ManyToManyField(User)
    objects = EmailQuerySet.as_manager()

    class Meta:
        verbose_name = _("Mail")
        verbose_name_plural = _("Mails")
        ordering = ("-timestamp",)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.admin.username}-{self.title}")

        super().save(*args, **kwargs)

    def get_markdown(self):
        return markdownify(self.content)


    async def deliver_mail(self, recipients, content):
    	audience = self.recipients.all()
    	for i in audience:
    		content = re.sub('==fullname==', i.get_full_name(), content)
    		content = re.sub('==fname==', i.first_name, content)
    		content = re.sub('==sname==', i.last_name, content)
    		content = re.sub('==gender==', i.gender or '', content)
    		content = re.sub('==lga==', i.lga or '', content)
    		content = re.sub('==session==', Session.get_current_session(), content)
    		content = re.sub('==state==', i.state, content)
    		content = re.sub('==address==', i.address, content)
    		content = re.sub('==scname==', Setting.objects.first().school_name, content)
    		amount = Expense.objects.aggregate(Sum('amount'))
    		amount = str(amount['amount__sum'])
    		content = re.sub('==expnse==', amount , content)
    		
    		if i.is_student:
    			student = Student.objects.get(user__id=i.id)
    			content = re.sub('==clss==', student.in_class.name, content)
    			content = re.sub('==section==', student.in_class.section.name, content)

    			sq = student.in_class.subjects.all()
    			s = '<p>Subject(s)</p><ol>'

    			for each_sub in sq:
    				s += f'<li style="color: green">{each_sub.name}</li>'
    			s += '</ol>'
    			content = re.sub('==clssub==', s, content)
    			g = Grade.objects.filter(
    				student=student, 
    				session=Session.objects.filter(current_session=True).first().id, 
    				term=get_terms())
    			e = '<p><span>Subject</span> <span id="grade" style="margin-left: 35vw;">Grade</span></p><ol>'

    			for k in g:
    				e += f'<li style="color: green"><span>{k.subject}</span> <span id="grade" style="margin-left: 35vw;">{k.grade}</span></li>'
    			e += '</ol>'
    			content = re.sub('==grades==', e, content)

    			pq = Payment.objects.filter(
    				student=student, 
    				session=Session.objects.filter(current_session=True).first().id, 
    				term=get_terms()).first().paid_amount
    			pq = str(pq)

    			content = re.sub('==amount==', pq, content)


    			a = None
    			if Attendance.objects.filter(
    				student=student, 
    				session=Session.objects.filter(current_session=True).first().id, 
    				term=get_terms(), 
    				date=date.today()).exists():

	    			a = Attendance.objects.filter(
	    				student=student, 
	    				session=Session.objects.filter(current_session=True).first().id, 
	    				term=get_terms(), 
	    				date=date.today()).first().is_present
    			
    			if a is not True:
    				a = 'Absent'
    			else:
    				a = 'Present'
    			content = re.sub('==attnd==', a, content)

    			# due amount
    			due_amount = Payment.objects.filter(
    				student=student, 
    				session=Session.objects.filter(current_session=True).first().id, 
    				term=get_terms()).first().due_amount
    			due_amount = str(due_amount)
    			content = re.sub('==damnt==', due_amount, content)

    			content = re.sub('==tno==', Payment.objects.filter(
    				student=student, 
    				session=Session.objects.filter(current_session=True).first().id, 
    				term=get_terms()).first().teller_number, content)

    		if i.is_teacher:
    			# allocated subjects
    			allocated_s = SubjectAssign.objects.get(
					session=Session.objects.filter(current_session=True).first().id,
					term=get_terms(),
					teacher=i)
    			subject_string = '<p>Subject(s)</p><ol>'
    			for subject in allocated_s.subjects.all():
    				subject_string += f'<li style="color: #85144b">{subject} ({allocated_s.clss})</li>'
    			subject_string += '</ol>'
    			content = re.sub('==allsub==', subject_string, content)
    		if i.is_parent:
    			# Get all his childrens
    			# Get the pattern and replace with their actual:
    			#	subjects for the current class
    			#	School Fee Paid Amount for the current term and session
    			#	School Fee Due Amount for the current term and session
    			#	Today's Attendance and
    			#	Grades for the current term and session
    			
    			childrens = Parent.objects.filter(parent__pk=request.user.id)

    			for child in childrens:
    				subjects = child.student.in_class.subjects.all()

    				# First thing first after getting all subjects above
    				# Create a Header for the subjects, like
    				# Subject
    				# 1. English
    				# 2. Mathematics
    				# 3. ...
    				header = '<p>Subject(s)</p><ol>'

	    			for subject in subjects:
	    				header += f'<li style="color: green">{subject.name}</li>'
	    			header += '</ol>'

	    			# now find and subtitude class subjects 
	    			# i.e ==clssub== with the header value

	    			content = re.sub('==clssub==', header, content)

	    			# secondly handle paid amount
	    			# re.sub espects string and so the q
	    			# should be str

	    			p_amount = str(Payment.objects.filter(
    				student=child, 
    				session=Session.objects.filter(current_session=True).first().id, 
    				term=get_terms()).first().paid_amount or 0)

    				# replace ==amount== with the actual amount.
	    			content = re.sub('==amount==', p_amount, content)

	    			# thirdly, due amount
	    			# due amount
	    			d_amount = str(Payment.objects.filter(
	    				student=child, 
	    				session=Session.objects.filter(current_session=True).first().id, 
	    				term=get_terms()).first().due_amount or 0)

	    			# again, replace
	    			content = re.sub('==damnt==', d_amount, content)

	    			# Student attendance
	    			a_status = Attendance.objects.filter(
	    				student=student, 
	    				session=Session.objects.filter(current_session=True).first().id, 
	    				term=get_terms(), 
	    				date=date.today()).first().is_present or 'Absent'

	    			if a_status is not 'Absent':
	    				a_status = 'Present'

	    			# replace
	    			content = re.sub('==attnd==', a_status, content)

	    			# Get and replace grades
	    			grades = Grade.objects.filter(
	    				student=child, 
	    				session=Session.objects.filter(current_session=True).first().id, 
	    				term=get_terms())

	    			header = '<p><span>Subject</span> <span id="grade" style="margin-left: 35vw;">Grade</span></p><ol>'

	    			for grade in grades:
	    				header += f'<li style="color: green"><span>{grade.subject}</span> <span id="grade" style="margin-left: 35vw;">{grade.grade}</span></li>'
	    			header += '</ol>'

	    			# replace
	    			content = re.sub('==grades==', header, content)

    	msg = EMessage(self.title, content, "support@bitpoint.com", recipients)
    	msg.content_subtype = 'html'
    	msg.send()
    	self.status = DELIVERED
