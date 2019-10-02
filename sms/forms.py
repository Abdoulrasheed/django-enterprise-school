from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from .models import *
from constants import *
from django.forms import BaseModelFormSet
from markdownx.fields import MarkdownxFormField


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
    stud_phone_number = forms.CharField(max_length=11, min_length=11, label="Phone number", required=False)
    stud_year_of_admission = forms.CharField(max_length=4, label="Year of admission", required=False)
    parent_username = forms.CharField(max_length=50, label="Parent username", required=False)
    parent_password = forms.CharField(max_length=100, label="Parent password", required=False)
    parent_fname = forms.CharField(max_length=50, label="Parent firstname", required=False)
    parent_sname = forms.CharField(max_length=50, label="Parent surname", required=False)
    parent_oname = forms.CharField(max_length=50, label="Parent othername", required=False)
    parent_phone_number = forms.CharField(max_length=11, min_length=11, label="Parent Phone number", required=False)
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
    phone = forms.CharField(max_length=11, min_length=11, required=False, label="Phone number")
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
    phone = forms.CharField(max_length=11, min_length=11, required=False, label="Phone number")
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
    clss = forms.CharField(max_length=50, label="Class")
    term = forms.CharField(max_length=100, label="Term")
    teacher =forms.CharField(max_length=100, label="Teacher")
    subjects = forms.ModelMultipleChoiceField(queryset=Subject.objects.all())

class SectionAllocationForm(forms.Form):
    section = forms.CharField(max_length=50, label="Section")
    section_head = forms.CharField(max_length=50, label="Section Head")
    placeholder = forms.CharField(max_length=100, label="placeholder")
    signature = forms.ImageField(label="Signature", required=False)

class AttendanceListForm(forms.Form):
    selected_class = forms.ModelChoiceField(queryset=Class.objects.all(), label="class")
    selected_term = forms.CharField(widget=forms.Select(choices=TERM), label="term")

class AttendanceSaveForm(forms.Form):
    selected_term = forms.CharField(widget=forms.Select(choices=TERM), label="Term")
    selected_date = forms.DateField(label="Date")

class UpdateProfileForm(forms.Form):
    username = forms.CharField(max_length=100)
    email = forms.EmailField(label="Email Address", required=False)
    phone = forms.CharField(max_length=11, min_length=11, label="Phone number", required=False)
    firstname = forms.CharField(max_length=30, label="Firstname", required=False)
    surname = forms.CharField(max_length=30, label="Firstname", required=False)
    address = forms.CharField(max_length=120, label="Address", required=False)
    othername = forms.CharField(max_length=50, label="Othername", required=False)
    religion = forms.CharField(widget=forms.Select(choices=RELIGION), label="Religion", required=False)


class ExpenseForm(forms.Form):
    item = forms.CharField(max_length=100, min_length=3, label="Item")
    amount = forms.FloatField(label="Amount")
    description = forms.CharField(max_length=150, label="Description", required=False)
    term = forms.CharField(widget=forms.Select(choices=TERM), label="Term")

class PaymentForm(forms.Form):
    student = forms.CharField(max_length=100, label="Student")
    paid_amount = forms.CharField(max_length=150, label="Amount")
    payment_method = forms.CharField(widget=forms.Select(choices=PAYMENT_METHOD), label="Payment method")
    term = forms.CharField(widget=forms.Select(choices=TERM), label="Term")
    tnumber = forms.CharField(max_length=100, label="Teller number", required=False)

class SessionForm(forms.Form):
    name = forms.CharField(max_length=20, label="Session")
    note = forms.CharField(max_length=50, label="Note")

class SmsForm(forms.Form):
    title = forms.CharField(max_length=100, label="Message title")
    body = forms.CharField(max_length=250, label="Message Body")
    to_user = forms.CharField(max_length=10)

class SettingForm(forms.Form):
    school_name = forms.CharField(max_length=150, label="School name")
    school_logo = forms.ImageField(label="School logo", required=False)
    school_address = forms.CharField(max_length=150, label="School address", required=False)
    school_slogan = forms.CharField(max_length=200, label="Motto / Slogan", required=False)
    business_phone1 = forms.CharField(max_length=200, label="Business Phone", required=False)
    business_phone2 = forms.CharField(max_length=200, label="Alternate Phone Number", required=False)
    business_email = forms.EmailField(label="Business Email", required=False)
    social_link1 = forms.CharField(max_length=200, label="Social Link #1", required=False)
    social_link2 = forms.CharField(max_length=200, label="Social Link #2", required=False)
    social_link3 = forms.CharField(max_length=200, label="Social Link #3", required=False)
    ft_begins = forms.DateField(required=False)
    ft_ends  = forms.DateField(required=False)
    st_begins = forms.DateField(required=False)
    st_ends = forms.DateField(required=False)
    tt_begins = forms.DateField(required=False)
    tt_ends = forms.DateField(required=False)
    school_town = forms.CharField(max_length=20, label="Town", required=False)

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput, label="Old Password")
    new_password = forms.CharField(widget=forms.PasswordInput, label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

class NoticeForm(forms.Form):
    post_title = forms.CharField(max_length=200)
    post_body = forms.CharField(max_length=500)
    posted_to = forms.CharField(max_length=100)


class EditStudentForm(forms.ModelForm):
    year_of_admission = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Year of admission',
            'class': 'form-control mb-4',
            'name': 'stud_year_of_admission',
            })
    )
    roll_number = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Roll number',
            'class': 'form-control mb-4',
            'name': 'stud_roll_number',
            })
    )
    in_class = forms.ModelChoiceField(
        queryset=Class.objects.all(),
        label="class")
    class Meta:
        model = Student
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['in_class'].widget.attrs.update({'class': 'mdb-select md-form'})


class EditUserForm(forms.ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Firstname',
            'class': 'form-control mb-4',
            'name': 'stud_fname',
            })
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Last name',
            'class': 'form-control mb-4',
            'name': 'stud_fname',
            })
    )
    phone = forms.CharField(
        max_length=11, min_length=11,
        required=False,
        widget=forms.TextInput(attrs={
            'type':'number',
            'placeholder': 'Phone number',
            'class': 'form-control mb-4',
            'name': 'stud_phone_number',
            'max_length': '11',
            'min_length':'11',
            })
    )

    address = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'type':'text',
            'placeholder': 'Address',
            'class': 'form-control mb-4',
            'name': 'stud_address',
            })
    )
    email = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'type':'text',
            'placeholder': 'Email',
            'class': 'form-control mb-4',
            'name': 'stud_email',
            })
    )
    other_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'type':'text',
            'placeholder': 'Othername',
            'class': 'form-control mb-4',
            'name': 'stud_oname',
            })
    )
    dob = forms.CharField(
        label="Date of birth",
        widget=forms.TextInput(attrs={
            'type':'date',
            'class': 'form-control mb-4',
            'name': 'stud_dob',
            })
    )
    gender = forms.CharField(
        required=False,
        widget=forms.Select(choices=GENDER,
        attrs={
            'placeholder': 'Gender',
            'class': 'mdb-select md-form',
            'name': 'stud_gender',
            })
    )

    religion = forms.CharField(
        required=False,
        widget=forms.Select(choices=RELIGION,
        attrs={
            'placeholder': 'Religion',
            'class': 'mdb-select md-form',
            'name': 'stud_religion',
            })
    )
    state = forms.CharField(
        required=False,
        widget=forms.Select(
            choices=STATE,
        attrs={
            'type':'text',
            'placeholder': 'State',
            'class': 'mdb-select mb-4',
            'name': 'stud_state',
            })
    )
    class Meta:
        model = User
        exclude = (
            'password',
            'username',
            'last_login',
            'date_joined',
            'is_student',
            'is_teacher',
            'is_parent',
            'is_staff',
            'is_superuser',
            'groups',
            'user_permissions',
            'is_active')

class EditClassForm(forms.ModelForm):
    name = forms.CharField(
        label="Name",
        widget=forms.TextInput(attrs={
            'type':'text',
            'class': 'form-control mb-4',
            'name': 'name',
            })
    )
    section = forms.ModelChoiceField(queryset=Section.objects.all(), label="Select Section")
    amount_to_pay = forms.CharField(
        help_text = "the amount expected for the students of the above class to pay",
        label="Amount of School Fee",
        widget=forms.TextInput(attrs={
            'type':'text',
            'class': 'form-control mb-4',
            'name': 'amount_to_pay',
            })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['section'].widget.attrs.update({'class': 'mdb-select md-form'})

    class Meta:
        model = Class
        exclude = ('subjects',)

class EditSubjectForm(forms.ModelForm):
    name = forms.CharField(
        label="Name",
        widget=forms.TextInput(attrs={
            'type':'text',
            'class': 'form-control mb-4',
            'name': 'name',
            })
    )
    class Meta:
        model = Subject
        fields = ['name']

class EditSectionForm(forms.ModelForm):
    name = forms.CharField(
        label="Name",
        widget=forms.TextInput(attrs={
            'type':'text',
            'class': 'form-control mb-4',
            'name': 'name',
            })
    )
    note = forms.CharField(
        label="Note",
        widget=forms.TextInput(attrs={
            'type':'text',
            'class': 'form-control mb-4',
            'name': 'note',
            })
    )
    class Meta:
        model = Section
        fields = ['name', 'note']

class EditSectionAllocationForm(forms.ModelForm):
    section = forms.ModelChoiceField(queryset=Section.objects.all(), label="Select Section")
    section_head = forms.ModelChoiceField(queryset=User.objects.filter(is_teacher=True), label="Select Section")
    signature = forms.ImageField(label="Signature")
    placeholder = forms.CharField(
        label="placeholder",
        widget=forms.TextInput(attrs={
            'type':'text',
            'class': 'form-control mb-4',
            'name': 'placeholder',
            'placeholder': 'e.g Principal, head master etc'
            })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['section'].widget.attrs.update({'class': 'mdb-select md-form'})
        self.fields['section_head'].widget.attrs.update({'class': 'mdb-select md-form'})
        self.fields['signature'].widget.attrs.update({'class': 'custom-file-input', 'id': 'inputGroupFile01', 'aria-describedby': 'inputGroupFileAddon01', 'name': 'signature'})

    class Meta:
        model = SectionAssign
        fields = '__all__'

class EditExpenseForm(forms.ModelForm):
    session = forms.ModelChoiceField(queryset=Session.objects.all(), label="Select a Session")
    term = forms.CharField(widget=forms.Select(choices=TERM), label="term")
    item = forms.CharField(
        label="Item",
        widget=forms.TextInput(attrs={
            'type':'text',
            'class': 'form-control mb-4',
            'name': 'item',
            'placeholder': 'e.g Books'
            })
    )
    description = forms.CharField(
        required=False,
        label="Description",
        widget=forms.TextInput(attrs={
            'type':'text',
            'class': 'form-control mb-4',
            'name': 'description',
            'placeholder': 'Description'
            })
    )
    amount = forms.FloatField(
        label="Amount",
        widget=forms.TextInput(attrs={
            'type':'number',
            'class': 'form-control mb-4',
            'name': 'amount',
            'placeholder': 'e.g 25000'
            })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['session'].widget.attrs.update({'class': 'mdb-select md-form'})
        self.fields['term'].widget.attrs.update({'class': 'mdb-select md-form'})

    class Meta:
        model = Expense
        fields = '__all__'


class EditSessionForm(forms.ModelForm):
    name = forms.CharField(
        label="Session Name",
        widget=forms.TextInput(attrs={
            'type':'text',
            'class': 'form-control mb-4',
            'name': 'name',
            'placeholder': 'Session name'
            })
    )
    note = forms.CharField(
        required = False,
        label="Note",
        widget=forms.TextInput(attrs={
            'type':'text',
            'class': 'form-control mb-4',
            'name': 'note',
            'placeholder': 'Description'
            })
    )
    class Meta:
        model = Session
        exclude = ('current_session', 'created_on')


class SetParentForm(forms.Form):
    parent_id = forms.IntegerField()
    student_id = forms.IntegerField()

class ProfilePictureForm(forms.Form):
    picture = forms.ImageField()


class EmailMessageForm(forms.ModelForm):
    message = MarkdownxFormField()
    image = forms.ImageField(required=False)
    class Meta:
        model = EmailMessage
        fields = ["recipients", "title", "message", 'image']