from django.db import models
from django.conf import settings
from authentication.models import User
from constants import *


class Session(models.Model):
	name = models.CharField(max_length=100)
	note = models.CharField(max_length=200, blank=True, null=True)
	current_session = models.BooleanField()
	created_on = models.DateTimeField(auto_now_add=True)

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
