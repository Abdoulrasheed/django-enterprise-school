from django.db import models
from django.conf import settings
from .validators import ASCIIUsernameValidator
from django.contrib.auth.models import AbstractUser
from .constants import *

class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_parent = models.BooleanField(default=False)
    phone = models.CharField(max_length=60, blank=True, null=True)
    address = models.CharField(max_length=60, blank=True, null=True)
    picture = models.ImageField(upload_to="pictures/", blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    other_name = models.CharField(max_length=100, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(choices=GENDER, max_length=6, blank=True, null=True)
    religion = models.CharField(choices=RELIGION, max_length=12, blank=True, null=True)
    state = models.CharField(choices=STATE, max_length=100, blank=True, null=True)
    lga = models.CharField(choices=LGA, max_length=100, blank=True, null=True)
    


    username_validator = ASCIIUsernameValidator()

    def get_picture(self):
        no_picture = settings.STATIC_URL + 'img/img_avatar.png'
        try:
            return self.picture.url
        except:
            return no_picture

    def get_full_name(self):
        full_name = self.username
        if self.first_name and self.last_name:
            full_name = self.first_name + " " + self.last_name
            if self.other_name:
            	full_name = self.first_name + " " + self.last_name + " " + self.other_name
        return full_name



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


	def __str__(self):
		return self.name

	class Meta:
		verbose_name_plural = 'classes'


class Student(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	in_class = models.ForeignKey(Class, on_delete=models.CASCADE)
	year_of_admission = models.CharField(max_length=100, blank=True, null=True)
	roll_number = models.CharField(max_length=50, unique=True)

	def __str__(self):
		return self.user.get_full_name()

class Parent(models.Model):
	parent = models.ForeignKey(User, on_delete=models.CASCADE)
	student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="childrens")

	def __str__(self):
		return self.parent.get_full_name()


class SubjectAssign(models.Model):
	session = models.ForeignKey(Session, on_delete=models.CASCADE)
	term = models.CharField(choices=TERM, max_length=7)
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
	student = models.ForeignKey(User, on_delete=models.CASCADE)
	subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
	fca = models.FloatField()
	sca = models.FloatField()
	exam = models.FloatField()
	total = models.FloatField()
	grade = models.CharField(choices=GRADE, max_length=1)
	remark = models.CharField(max_length=50)


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
	section = models.ForeignKey(Section, on_delete=models.CASCADE)
	amount = models.FloatField()
	session = models.ForeignKey(Session, on_delete=models.CASCADE)
	term = models.CharField(choices=TERM, max_length=7)

	def __str__(self):
		return self.name

class Payment(models.Model):
	payment = models.ForeignKey(FeeType, on_delete=models.CASCADE)
	due_amount = models.FloatField()
	payment_status = models.CharField(choices=PAYMENT_STATUS, max_length=50)
	date_paid = models.DateTimeField(auto_now_add=True)
	payment_method = models.CharField(choices=PAYMENT_METHOD, max_length=50)
	session = models.ForeignKey(Session, on_delete=models.CASCADE)
	term = models.CharField(choices=TERM, max_length=7)

	def __str__(self):
		return self.payment

class Expense(models.Model):
	item = models.CharField(max_length=100)
	description = models.CharField(max_length=500, blank=True, null=True)
	session = models.ForeignKey(Session, on_delete=models.CASCADE)
	term = models.CharField(choices=TERM, max_length=7)

	def __str__(self):
		return self.item

class Setting(models.Model):
	school_name = models.CharField(max_length=100)
	school_logo = models.ImageField(upload_to="school/")
	school_address = models.CharField(max_length=150)
	school_slogan = models.CharField(max_length=200)
	ft_begins = models.DateField()
	ft_ends = models.DateField()
	st_begins = models.DateField()
	st_ends = models.DateField()
	tt_begins = models.DateField()
	tt_ends = models.DateField()