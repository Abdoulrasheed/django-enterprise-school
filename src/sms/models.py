import re
import urllib
from utils.constants import *
from datetime import date
from django.db import models
from django.conf import settings
from django.db.models import Sum
from django.contrib import messages
from authentication.models import User
from django.utils import timezone as tz
#from markdownx.models import MarkdownxField
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.core.mail import EmailMessage as EMessage
#from markdownx.utils import markdownify # deprecated
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import datetime

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


class SessionQuerySet(models.QuerySet):
    def get_current_session(self):
        return self.filter(current_session=True).first() or None

class Session(models.Model):
	name 			= models.CharField(_('session name'), max_length=100)
	note 			= models.CharField(_('short note'), max_length=200, blank=True, null=True)
	current_session = models.BooleanField(_('is current session'))
	created_on 		= models.DateTimeField(_('date Created'), auto_now_add=True)

	objects = SessionQuerySet.as_manager()

	def __str__(self):
		return self.name

	class Meta:
		verbose_name 		= _("Session")
		verbose_name_plural = _("Sessions")


class Section(models.Model):
	name = models.CharField(max_length=100, unique=True)
	note = models.CharField(max_length=200, blank=True, null=True)


	def __str__(self):
		return self.name


	class Meta:
		verbose_name 		= _("Section")
		verbose_name_plural = _("Sections")


class Subject(models.Model):
	short_name	= models.CharField(_('subject short name'), max_length=50)
	name 		= models.CharField(_('subject name'), max_length=200)
	section 	= models.ForeignKey(Section, verbose_name=_('section'), on_delete=models.CASCADE)
	subject_type= models.CharField(_('subject type'), max_length=30, choices=SUBJECT_TYPE)
	
	def __str__(self):
		return self.name

	def get_absolute_url(self):
		return reverse('subjects_list')

class Class(models.Model):
	name = models.CharField(max_length=100)
	section = models.ForeignKey(Section, on_delete=models.CASCADE)


	class Meta:
		verbose_name 		= _('Student Class')
		verbose_name_plural = _('Student classes')

	def __str__(self):
		return self.name

	def get_absolute_url(self):
		return reverse('class_list')


class Batch(models.Model):
	name = models.CharField(_('Batch Name'), max_length=50)
	capacity = models.PositiveIntegerField()
	subjects = models.ManyToManyField(Subject)
	clss = models.ForeignKey(Class, on_delete=models.CASCADE, verbose_name=_('Class'))

	class Meta:
		verbose_name = _("Batch")
		verbose_name_plural = _("Batches")

	def __str__(self):
		return f'{_(self.name)}'

	def get_absolute_url(self):
		return reverse('batch_list')

class Student(models.Model):
	roll_number	= models.CharField(_('Roll Number'), max_length=50)
	user 		= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('Student'))
	optional_subjects = models.ManyToManyField(Subject, blank=True, verbose_name=_('Optional Subjects'))
	year_of_admission= models.ForeignKey(Session, related_name='year_of_admission', on_delete=models.SET_NULL, verbose_name=_('Session of Admission'),max_length=100, blank=True, null=True)
	in_class 	= models.ForeignKey(Class, null=True, on_delete=models.SET_NULL, verbose_name=_('Class'))
	batch 		= models.ForeignKey(Batch, null=True, on_delete=models.SET_NULL, verbose_name=_('Batch'))
	session 	= models.ForeignKey(Session, on_delete=models.PROTECT)

	def __str__(self):
		return self.user.get_full_name()

class Parent(models.Model):
	parent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	title = models.CharField(max_length=30, choices=TITLES)
	student = models.ManyToManyField(Student, related_name="guardians")

	def __str__(self):
		return self.parent.get_full_name()


class Teacher(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	branch = models.CharField(max_length=50, blank=True, null=True)
	qualification = models.CharField(max_length=150, blank=True, null=True)
	next_of_kin = models.CharField(_("Next of kin"), max_length=30, blank=True, null=True)
	section = models.ForeignKey(Section, verbose_name=_('Section'), null=True, on_delete=models.SET_NULL)

	def __str__(self):
		return self.teacher


	def __str__(self):
		return self.user.get_full_name()


class SubjectAllocation(models.Model):
	session 	= models.ForeignKey(Session, verbose_name=_('session'), on_delete=models.CASCADE)
	term 		= models.CharField(_('term'), choices=TERM, max_length=7)
	clss 		= models.ForeignKey(Class, verbose_name=_('class'), on_delete=models.CASCADE)
	batch 		= models.ForeignKey(Batch, verbose_name=_('batch'), on_delete=models.CASCADE)
	teacher 	= models.ForeignKey(Teacher, verbose_name=_('teacher'), on_delete=models.CASCADE)
	subjects 	= models.ManyToManyField(Subject, verbose_name=_('subjects'), blank=True)

	class Meta:
		verbose_name 		= _("Subject Allocation")
		verbose_name_plural = _("Subject Allocations")

	def __str__(self):
		return f"{self.teacher}"

class SectionAllocation(models.Model):
	section_head 	= models.ForeignKey(Teacher, verbose_name=_('section head'), on_delete=models.CASCADE)
	section 		= models.ForeignKey(Section, verbose_name=_('section'), on_delete=models.CASCADE)
	placeholder 	= models.CharField(_('placeholder'), max_length=100)
	signature 		= models.ImageField(_('signature'), upload_to="section_signatures/", blank=True, null=True)
	
	class Meta:
		verbose_name 		= _("section allocation")
		verbose_name_plural = _("section allocations")
	
	def __str__(self):
		return self.section_head

class MarkPercentage(models.Model):
	section  = models.ForeignKey(Section, verbose_name=_('section'), on_delete=models.CASCADE)
	name = models.CharField(_('name'), max_length=10)
	percentage = models.PositiveIntegerField(_('percentage'), validators=[
            MaxValueValidator(100),
            MinValueValidator(1)])


	def __str__(self):
		return f"{self.percentage} - {self.section}"

	def get_absolute_url(self):
	    return reverse('mark_percentage')


class Score(models.Model):
	student 	= models.ForeignKey(Student, verbose_name=_('student'), on_delete=models.CASCADE)
	mark_percentage = models.ForeignKey(MarkPercentage, verbose_name=_('mark percentage'), null=True, on_delete=models.SET_NULL)
	subject 	= models.ForeignKey(Subject, verbose_name=_('subject'), null=True, on_delete=models.SET_NULL)
	score 		= models.FloatField(_('score'))
	term 		= models.CharField(_('term'), choices=TERM, max_length=7)
	session 	= models.ForeignKey(Session, verbose_name=_('session'), null=True, on_delete=models.SET_NULL)

	def __str__(self):
		return f"{self.student} {self.score}"

class Grade(models.Model):
	score = models.ForeignKey(Score, verbose_name=_('score'), on_delete=models.CASCADE)
	remark= models.CharField(_('remark'), max_length=50, blank=True, null=True)
	grade = models.CharField(_('grade'), choices=GRADE, max_length=1, blank=True, null=True)
	total = models.FloatField(_('total'), blank=True, null=True)

	class Meta:
		verbose_name 		= _("Grade")
		verbose_name_plural = _("Grades")
	
	def __str__(self):
		return f"{self.grade} - {self.student}"

	def get_total_score(self):
		pass

class ScoreModificationLog(models.Model):
	score 		= models.ForeignKey(Score, verbose_name=_('score'), null=True, on_delete=models.SET_NULL)
	old_score	= models.FloatField(_('old score'))
	new_score	= models.FloatField(_('new score'))
	date_modified = models.DateTimeField(_('modified date'), auto_now_add=True)

	def __str__(self):
		return self.score.score

class ScorePermission(models.Model):
	session = models.ForeignKey(Session, verbose_name=_('session'), on_delete=models.CASCADE)
	section = models.ForeignKey(Section, verbose_name=_('section'), on_delete=models.CASCADE)
	start_time =models.DateTimeField(_('opens from'), default=tz.now)
	end_time =models.DateTimeField(_('closes on'), default=tz.now)

	def __str__(self):
		return self.section.name

class PerfomanceComment(models.Model):
	student = models.ForeignKey(Student, verbose_name=_('student'), on_delete=models.CASCADE)
	session = models.ForeignKey(Session, verbose_name=_('term'), on_delete=models.CASCADE)
	term 	= models.CharField(_('term'), max_length=15)
	form_teacher_comment = models.TextField(_('form teacher comment'))
	principal_comment = models.TextField(_('principal comment'))
	guiding_and_council_comment = models.TextField(_('guiding and council comment'))

	def __str__(self):
		return f"{self.student} - {self.form_teacher_comment}"


class Psychomotor(models.Model):
	student 	= models.ForeignKey(Student, verbose_name=_('student'), on_delete=models.CASCADE)
	neatness 	= models.IntegerField(_('neatness'), default=3)
	politeness	= models.IntegerField(_('politeness'), default=3)
	initiative	= models.IntegerField(_('initiative'), default=3)
	cop_with_others= models.IntegerField(_('corporation with others'), default=3)
	leadership= models.IntegerField(_("leadership Trait"), default=3)
	helping_others	= models.IntegerField(_('helping others'), default=3)
	emotional_stability = models.IntegerField(_('emotional stability'), default=3)
	health				= models.IntegerField(_('health'), default=3)
	att_to_school_work	= models.IntegerField(_('attentive to school work'), default=3)
	attentive 			= models.IntegerField(_('attentive'), default=3)
	perseverance		= models.IntegerField(_('perseverance'), default=3)
	relationship_with_teachers = models.IntegerField(_('relationship with teachers'), default=3)
	punctuality			= models.IntegerField(_('punctuality'), default=3)
	handwriting			= models.IntegerField(_('handwriting'), default=3)
	verbal 				= models.IntegerField(_('verbal'), default=3)
	games				= models.IntegerField(_('games'), default=3)
	sport				= models.IntegerField(_('sport'), default=3)
	hand_tool			= models.IntegerField(_('hand_tool'), default=3)
	drawing_and_painting= models.IntegerField(_('drawing and painting'), default=3)
	music_skills		= models.IntegerField(_('music skills'), default=3)

	def __str__(self):
		return self.student


class AbsentReason(models.Model):
	reason	= models.CharField(max_length=50)

	def __str__(self):
		return self.reason

class Attendance(models.Model):
	date 		= models.DateField()
	status 		= models.BooleanField(default=False)
	late 		= models.BooleanField(blank=True, null=True)
	term 		= models.CharField(choices=TERM, max_length=7)
	session 	= models.ForeignKey(Session, on_delete=models.CASCADE)
	student 	= models.ForeignKey(Student, on_delete=models.CASCADE)
	absent_reason = models.ForeignKey(AbsentReason, null=True, on_delete=models.SET_NULL)

	def __str__(self):
		return self.student.user.get_full_name()

	def get_todays_attendance(self):
		return _("Present") if self.status else _("Absent")

	def notify_parents(self):
		parent = Parent.objects.filter(student__in=[self.student,]).first()
		parent.notify_attendance()

class FeeType(models.Model):
	name 		= models.CharField(max_length=100)
	for_class 	= models.ManyToManyField(Class)
	amount 		= models.FloatField()
	session 	= models.ForeignKey(Session, on_delete=models.CASCADE)
	term 		= models.CharField(choices=TERM, max_length=7)

	def __str__(self):
		return self.name

class AutoComment(models.Model):
	section 	= models.ForeignKey(Section, on_delete=models.CASCADE)
	avg_from	= models.FloatField(unique=True)
	avg_upto	= models.FloatField(unique=True)
	comment 	= models.CharField(max_length=100)
	commenter	= models.CharField(max_length=100)


class Payment(models.Model):
	student 		= models.ForeignKey(Student, on_delete=models.CASCADE)
	paid_amount 	= models.FloatField()
	due_amount 		= models.FloatField()
	date_paid 		= models.DateTimeField(auto_now_add=True)
	payment_method 	= models.CharField(choices=PAYMENT_METHOD, max_length=50)
	payment_status 	= models.CharField(choices=PAYMENT_STATUS, max_length=50)
	term 			= models.CharField(choices=TERM, max_length=7)
	session 		= models.ForeignKey(Session, on_delete=models.CASCADE)
	teller_number 	= models.CharField(max_length=100, blank=True, null=True)

	def __str__(self):
		return self.student.roll_number

class Expense(models.Model):
	item 		= models.CharField(max_length=100)
	description = models.CharField(max_length=500, blank=True, null=True)
	timestamp 	= models.DateTimeField(auto_now_add=True)
	session 	= models.ForeignKey(Session, on_delete=models.CASCADE)
	term 		= models.CharField(choices=TERM, max_length=7)
	amount 		= models.FloatField()

	def __str__(self):
		return self.item

class Setting(models.Model):
	school_name 	= models.CharField(max_length=100)
	school_logo 	= models.ImageField(upload_to="pictures/", blank=True, null=True)
	school_address 	= models.CharField(max_length=300, blank=True, null=True)
	school_town 	= models.CharField(max_length=100, blank=True, null=True)
	school_slogan 	= models.CharField(max_length=200, blank=True, null=True)
	business_email 	= models.EmailField(blank=True, null=True)
	business_phone1 = models.CharField(max_length=11, blank=True, null=True)
	business_phone2 = models.CharField(max_length=11, blank=True, null=True)
	social_link1 	= models.CharField(max_length=200, blank=True, null=True)
	social_link2 	= models.CharField(max_length=200, blank=True, null=True)
	social_link3 	= models.CharField(max_length=200, blank=True, null=True)
	ft_begins 		= models.DateField(blank=True, null=True)
	ft_ends 		= models.DateField(blank=True, null=True)
	st_begins 		= models.DateField(blank=True, null=True)
	st_ends 		= models.DateField(blank=True, null=True)
	tt_begins 		= models.DateField(blank=True, null=True)
	tt_ends 		= models.DateField(blank=True, null=True)
	sms_unit 		= models.IntegerField(default=200)

	def __str__(self):
		return self.school_name

	def get_logo(self):
		no_logo = settings.STATIC_ROOT + '/static/img/logo.png'
		return self.school_logo.url if self.school_logo else no_logo


	class Meta:
		verbose_name 		= _("School Configuration")
		verbose_name_plural = _("School Configurations")

class Notification(models.Model):
	""" DEPRECATED """
	user 	= models.ForeignKey(User, on_delete=models.CASCADE)
	title 	= models.CharField(max_length=100)
	body 	= models.CharField(max_length=300)
	unread 	= models.BooleanField(default=False)
	time 	= models.DateTimeField(auto_now_add=True)
	message_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE)

	def __str__(self):
		return self.user

class GradeScale(models.Model):
	section 	= models.ForeignKey(Section, verbose_name=_('section'), on_delete=models.CASCADE)
	grade 		= models.CharField(_('grade'), choices=GRADE, max_length=100, unique=True)
	mark_from 	= models.IntegerField(_('mark from'), unique=True)
	mark_upto 	= models.IntegerField(_('mark upto'), unique=True)
	remark 		= models.CharField(_('remark'), max_length=20, unique=True)
	description = models.CharField(_('description'), max_length=50, blank=True, null=True)
	color		= models.CharField(_('color'), max_length=20, default="#008000") # green


	def __str__(self):
		return self.section.name


	def get_absolute_url():
		return reverse('grade_scale')


class NoticeBoard(models.Model):
    post_title = models.CharField(max_length=100, blank=True, null=True)
    post_body = models.TextField(blank=True, null=True)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    posted_to = models.CharField(max_length=100, blank=True, null=True)
    posted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
    	return self.post_title


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
    admin 	= models.ForeignKey(
        User, null=True, related_name="author",
        on_delete=models.SET_NULL)
    image 	= models.ImageField(
        _('Featured image'), null=True, upload_to='email_pictures/%Y/%m/%d/')
    timestamp 	= models.DateTimeField(auto_now_add=True)
    title 		= models.CharField(max_length=255, null=False)
    slug 		= models.SlugField(max_length=80, null=True, blank=True)
    status 		= models.CharField(max_length=1, choices=STATUS, default=PENDING)
    content 	= models.TextField()
    recipients 	= models.ManyToManyField(User)
    objects 	= EmailQuerySet.as_manager()

    class Meta:
        verbose_name 		= _("Mail")
        verbose_name_plural = _("Mails")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.admin}-{self.title}")

        super().save(*args, **kwargs)

    def get_markdown(self):
        return markdownify(self.content)


    def deliver_mail(self, content, request):
    	""" DEPRECATED """
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
    				term=get_terms()).first()

    			if payment_q:
    				paid_amount = str(payment_q.paid_amount)
    			else:
    				paid_amount = '0'

    			due_amount_q = Payment.objects.filter(
    				student=student,
    				session=current_session,
    				term=get_terms()).first() or '<i>No outstanding fee</i>'

    			due_amount = str(due_amount_q)

    			payment_t_number_q = Payment.objects.filter(
    				student=student,
    				session=current_session,
    				term=get_terms()).first()

    			if payment_t_number_q:
    				payment_teller_number = payment_t_number_q.teller_number
    			else:
    				payment_teller_number = '0'

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
    	try:
    		msg.send()
    		self.status = DELIVERED
    		self.save()
    		messages.success(request, 'Emails Successfully Send !')
    		print(self.status)
    	except urllib.error.URLError:
    		self.status = PENDING
    		self.save()
    		messages.error(request, 'Emails not send and saved in draft, check your internet connection !')
    		print('Emails not send and saved in draft, check your internet connection !')