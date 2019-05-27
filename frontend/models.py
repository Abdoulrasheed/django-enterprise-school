from django.db import models
from sms.constants import RELIGION, GENDER


class OnlineAdmission(models.Model):
	admission_id = models.CharField(max_length=10)
	student_fname = models.CharField(max_length=20)
	student_lname = models.CharField(max_length=20)
	student_oname = models.CharField(max_length=20, blank=True, null=True)
	gender = models.CharField(choices=GENDER, max_length=7)
	address = models.CharField(max_length=200)
	religion = models.CharField(choices=RELIGION, max_length=13)
	date_of_birth = models.DateTimeField()
	clss = models.CharField(max_length=50)
	phone = models.CharField(max_length=11)
	email = models.EmailField(blank=True, null=True)
	date_of_application = models.DateTimeField(auto_now_add=True)
	passport = models.ImageField(upload_to="admission/")
