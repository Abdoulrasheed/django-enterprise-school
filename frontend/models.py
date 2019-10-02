from django.db import models
from constants import RELIGION, GENDER
from sms.models import Session

ADMISSION_STATUS = (
	('Waiting', 'Waiting'),
	('Approved', 'Approved'),
	('Declined', 'Declined')
	)


class OnlineAdmission(models.Model):
	admission_id = models.CharField(max_length=10)
	student_fname = models.CharField(max_length=20)
	student_lname = models.CharField(max_length=20)
	student_oname = models.CharField(max_length=20, blank=True, null=True)
	student_gender = models.CharField(choices=GENDER, max_length=7)
	student_address = models.CharField(max_length=200)
	student_religion = models.CharField(choices=RELIGION, max_length=13)
	student_dob = models.DateField()
	student_clss = models.CharField(max_length=50)
	applicant_phone_no = models.CharField(max_length=11)
	student_email = models.EmailField(blank=True, null=True)
	date_of_application = models.DateTimeField(auto_now_add=True)
	student_passport = models.ImageField(upload_to="admission/")
	status = models.CharField(max_length=20, default='Waiting', choices=ADMISSION_STATUS)
	session = models.ForeignKey(Session, on_delete=models.CASCADE)

	def get_applicant_full_name(self):
		return "{} {} {}".format(self.student_fname or '', self.student_lname or '', self.student_oname or '')
