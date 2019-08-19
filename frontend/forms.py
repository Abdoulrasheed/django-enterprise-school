from django import forms
from constants import GENDER, RELIGION
from sms.models import Class
from .models import OnlineAdmission

class OnlineAdmissionForm(forms.ModelForm):
	student_fname = forms.CharField(max_length=20, label="Student first name")
	student_lname = forms.CharField(max_length=20, label="Student last name")
	student_oname = forms.CharField(max_length=20, label="Student Othername", required=False)
	student_gender = forms.CharField(widget=forms.Select(choices=GENDER), max_length=7, label="Gender")
	student_address = forms.CharField(max_length=200, label="Student address")
	applicant_phone_no = forms.CharField(max_length=11, label="Phone number")
	student_clss = forms.ModelChoiceField(queryset=Class.objects.all(), label="Class of admission")
	student_email = forms.EmailField(required=False, label="Email Address")
	student_passport = forms.ImageField(label="Student passport")
	student_religion = forms.CharField(widget=forms.Select(choices=RELIGION), max_length=13, label="Religion")
	student_dob = forms.DateTimeField(label="Date of birth")

	class Meta:
		model = OnlineAdmission
		exclude = ('admission_id', 'date_of_application', 'session')