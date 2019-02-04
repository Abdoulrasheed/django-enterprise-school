from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from .models import *
from .constants import *
from django.forms import BaseModelFormSet


class AddStudentForm(forms.Form):
    stud_username = forms.CharField(max_length=50)
    stud_password = forms.CharField(max_length=100)
    dob = forms.DateField(required=False)
    stud_fname = forms.CharField(max_length=50, label="Firstname")
    stud_sname = forms.CharField(max_length=50, label="Surname")
    stud_oname = forms.CharField(max_length=50, required=False, label="Othername")
    stud_religion = forms.CharField(widget=forms.Select(choices=RELIGION),max_length=14, 
        label="Religion", required=False)
    stud_address = forms.CharField(max_length=200,label="Address", required=False)
    stud_class = forms.CharField(max_length=20, label="Class")
    stud_gender = forms.CharField(widget=forms.Select(choices=GENDER), label="Gender" , required=False)
    stud_state = forms.CharField(max_length=100, label="State", required=False)
    stud_email = forms.EmailField(required=False, label="Student Email Address")
    stud_lga = forms.CharField(max_length=150, label="Local Govt.", required=False)
    stud_blood_group = forms.CharField(max_length=2, label="Blood Group", required=False)
    stud_roll_number = forms.CharField(max_length=50, label="Roll number")
    stud_phone_number = forms.CharField(max_length=15, label="Phone number", required=False)
    stud_year_of_admission = forms.CharField(max_length=4, label="Year of admission", required=False)
    parent_username = forms.CharField(max_length=50, label="Parent username", required=False)
    parent_password = forms.CharField(max_length=100, label="Parent password", required=False)
    parent_fname = forms.CharField(max_length=50, label="Parent firstname", required=False)
    parent_sname = forms.CharField(max_length=50, label="Parent surname", required=False)
    parent_oname = forms.CharField(max_length=50, label="Parent othername", required=False)
    parent_phone_number = forms.CharField(max_length=15, label="Parent Phone number", required=False)
    parent_state = forms.CharField(max_length=50, label="Parent state of origin", required=False)
    parent_address = forms.CharField(max_length=200, label="Parent Address", required=False)
    parent_email = forms.EmailField(required=False, label="Parent email address")
    parent_lga = forms.CharField(max_length=30, required=False, label="Parent Local Govt.")

    stud_picture = forms.ImageField(required=False, label="Student picture")
    parent_picture = forms.ImageField(required=False, label="Parent picture")

    existing_parent = forms.CharField(max_length=100, required=False, label="Existing parent")


class AddParentForm(forms.Form):
    username = forms.CharField(max_length=50, label="Username")
    password = forms.CharField(max_length=40, label="Password")
    firstname = forms.CharField(max_length=50, label="Firstname")
    surname = forms.CharField(max_length=50, label="Surname")
    othername = forms.CharField(max_length=50, required=False, label="Othername")
    state = forms.CharField(max_length=50, required=False, label="State")
    phone = forms.CharField(max_length=50, required=False, label="Phone number")
    email = forms.CharField(max_length=120, required=False, label="Email Address")
    address = forms.CharField(max_length=500, required=False, label="Home / Office Address")
    picture = forms.ImageField(required=False, label="Picture")


class AddTeacherForm(forms.Form):
    username = forms.CharField(max_length=50, label="Username")
    password = forms.CharField(max_length=40, label="Password")
    firstname = forms.CharField(max_length=50, label="Firstname")
    surname = forms.CharField(max_length=50, label="Surname")
    othername = forms.CharField(max_length=50, required=False, label="Othername")
    state = forms.CharField(max_length=50, required=False, label="State")
    phone = forms.CharField(max_length=50, required=False, label="Phone number")
    email = forms.CharField(max_length=120, required=False, label="Email Address")
    address = forms.CharField(max_length=500, required=False, label="Home / Office Address")
    picture = forms.ImageField(required=False, label="Picture")

class AddClassForm(forms.Form):
    name = forms.CharField(max_length=50, label="Class Name")
    section = forms.CharField(max_length=100, label="Section")
    subjects = forms.ModelMultipleChoiceField(queryset=Subject.objects.all())

class AddSubjectForm(forms.Form):
    subject = forms.CharField(max_length=100, label="Subject name")

class AddSectionForm(forms.Form):
    section = forms.CharField(max_length=50, label="Section name")
    note = forms.CharField(max_length=100, label="Section Description", required=False)

class SubjectAllocationForm(forms.Form):
    session = forms.CharField(max_length=50, label="Session")
    term = forms.CharField(max_length=100, label="Term")
    teacher =forms.CharField(max_length=100, label="Teacher")
    subjects = forms.ModelMultipleChoiceField(queryset=Subject.objects.all())

class SectionAllocationForm(forms.Form):
    section = forms.CharField(max_length=50, label="Section")
    section_head = forms.CharField(max_length=50, label="Section Head")
    placeholder = forms.CharField(max_length=100, label="placeholder")
    signature = forms.ImageField(label="Signature", required=False)

class AttendanceListForm(forms.Form):
    selected_class = forms.ModelChoiceField(queryset=Class.objects.all())
    selected_term = forms.CharField(widget=forms.Select(choices=TERM))