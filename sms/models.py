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
	student = models.ManyToManyField(Student, related_name="guardians")

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


    async def deliver_mail(self, content):
    	audience = self.recipients.all()
    	setting = Setting.objects.first()
    	current_session = Session.objects.get(
    		current_session=True)
    	recipients = ()

    	for i in audience:
    		recipients += (i.email,)
    		total_expenditure = Expense.objects.aggregate(
    			Sum('amount'))['amount__sum']

    		default_user_replacements = [
    			('==fullname==', i.get_full_name()),
    			('==fname==', i.first_name),
    			('==sname==', i.last_name),
    			('==gender==', i.gender or ''),
    			('==session==', str(current_session)),
    			('==state==', i.state or ''),
    			('==address==', i.address or ''),
    			('==expnse==', str(total_expenditure)),
    			('==scname==', str(setting.school_name)),
    		]
    		for old, new in default_user_replacements:
    			content = re.sub(old, new, content)

    		if i.is_student:
    			student = Student.objects.get(
    				user__id=i.id,
    				session=current_session)
    			
    			subject_q = student.in_class.subjects.all()

    			subjects_html_with_header = '<p>Subject(s)</p><ol>'

    			for subject_obj in subject_q:
    				subjects_html_with_header += f'<li style="color: green">\
    					{subject_obj.name}\
    					</li>'

    			subjects_html_with_header += '</ol>'
    			grades_q = Grade.objects.filter(
    				student=student,
    				session=current_session,
    				term=get_terms())
    			grades_html_with_header = '<p><span>Subject</span> \
    				<span id="grade" style="margin-left: 35vw;">Grade</span>\
    				</p><ol>'

    			for grade_obj in grades_q:
    				grades_html_with_header += f'<li style="color: green"><span>{grade_obj.subject}</span>\
    					<span id="grade" style="margin-left: 35vw;">\
    						{grade_obj.grade}\
    						</span></li>'


    			grades_html_with_header += '</ol>'

    			payment_q = Payment.objects.filter(
    				student=student,
    				session=current_session,
    				term=get_terms()).first().paid_amount

    			paid_amount = str(payment_q)

    			due_amount_q = Payment.objects.filter(
    				student=student,
    				session=current_session,
    				term=get_terms()).first() or '<i>No outstanding fee</i>'

    			due_amount = str(due_amount_q)

    			payment_t_number_q = Payment.objects.filter(
    				student=student,
    				session=current_session,
    				term=get_terms()).first()

    			payment_teller_number = payment_t_number_q.teller_number or ''

    			attendance_status = Attendance.objects.filter(
    				student=student,
    				session=current_session,
    				term=get_terms(),
    				date=date.today()) or 'Absent'
    			
    			if attendance_status is not 'Absent':
    				attendance_status = 'Present'

    			student_replacements = [
    				('==clss==', student.in_class.name),
    				('==section==', student.in_class.section.name),
    				('==clssub==', subjects_html_with_header),
    				('==grades==', grades_html_with_header),
    				('==amount==', paid_amount),
    				('==attnd==', attendance_status),
    				('==damnt==', due_amount),
    				('==tno==', payment_teller_number),]

    			for old, new in student_replacements:
    				content = re.sub(old, new, content)
    		
    		if i.is_teacher:
    			allocated_subjects_q = SubjectAssign.objects.get(
    				session=current_session,
    				term=get_terms(),
    				teacher=i)

    			subjects_html_with_header = '<p>Subject(s)</p><ol>'

    			for subject in allocated_subjects_q.subjects.all():
    				subjects_html_with_header += f'<li style="color: #85144b">\
    					{subject} ({allocated_subjects_q.clss})\
    					</li>'

    			subjects_html_with_header += '</ol>'
    			teacher_replacements = [
    				('==allsub==', subjects_html_with_header),
    				]

    			for old, new in teacher_replacements:
    				content = re.sub(old, new, content)

    		if i.is_parent:
    			"""Get all his childrens
    				Get the pattern and replace with their actual:
	    				subjects for the current class
	    				School Fee Paid Amount for the current term and session
	    				School Fee Due Amount for the current term and session
	    				Today's Attendance and
	    				Grades for the current term and session
	    		"""

	    		childrens_q = Parent.objects.get(parent__pk=i.id)

	    		for child in childrens_q.student.all():
	    			subjects_in_class = child.in_class.subjects.all()

	    			subjects_html_with_header = f'{child.user.first_name}\'s <p>Subjects</p><ol>'

	    			for subject in subjects_in_class:
	    				subjects_html_with_header += f'<li style="color: green">\
	    				{subject.name}</li>'

	    			subjects_html_with_header += '</ol>'

	    			# paid amount and due amount

	    			paid_amount = f'{child.user.first_name} <i>Not paid</i>'
	    			due_amount = f'{child.user.first_name} <i>Not Paid</i>'
	    			teller_number = ''

	    			payment_q = Payment.objects.filter(
	    				student=child, 
	    				session=current_session,
	    				term=get_terms()).first()

	    			if payment_q:
	    				paid_amount = f'{child.user.first_name} has paid {payment_q.paid_amount} Naira'
	    				due_amount = f'{child.user.first_name}\'s due amount is {payment_q.due_amount} Naira'
	    				teller_number = payment_q.teller_number

	    			# Student attendance
	    			attendance_q = Attendance.objects.filter(
	    				student=child,
	    				session=current_session,
	    				term=get_terms(),
	    				date=date.today()).first()

	    			attendance_status = f'{child.user.first_name} is Absent today <small>({date.today()})</small>'

	    			if attendance_q:
	    				attendance_status = f'{child.user.first_name} is <b>Present</b> today <small>({date.today()})</small>'

	    			# Get and replace grades
	    			grades_q = Grade.objects.filter(
	    				student=child,
	    				session=current_session,
	    				term=get_terms()) or ''

	    			grades_html_with_header = f'<p>{child.user.first_name}\'s results</p><span>Subject</span> \
	    				<span id="grade" style="margin-left: 35vw;">\
	    				Grade</span></p><ol>'

	    			for grade in grades_q:
	    				grades_html_with_header += f'<li style="color: green">\
	    				<span>{grade.subject}</span> \
	    				<span id="grade" style="margin-left: 35vw;">\
	    				{grade.grade or "<small><i>Nill</i></small>"}</span></li>'

	    			grades_html_with_header += '</ol>'

	    			parent_replacements = [
	    				('==clssub==', subjects_html_with_header),
	    				('==grades==', grades_html_with_header),
	    				('==amount==', paid_amount),
	    				('==attnd==', attendance_status),
	    				('==damnt==', due_amount),
	    				('==tno==', teller_number),
	    				]
	    			for old, new in parent_replacements:
	    				content = re.sub(old, new, content)

    	content = re.sub('^==.*==$', ' ', content)
    	msg = EMessage(self.title, content, "noreply@bitpoint.com", recipients)
    	msg.content_subtype = 'html'
    	msg.send()
    	self.status = DELIVERED