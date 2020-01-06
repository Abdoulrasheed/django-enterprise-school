from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from .models import *
from utils.constants import *
from django.forms import BaseModelFormSet
from django.contrib.auth.models import Group, Permission
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Row, Column


class AddMarkPercentageForm(forms.ModelForm):
    class Meta:
        model = MarkPercentage
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(AddMarkPercentageForm, self).__init__(*args, **kwargs)
        self.fields['percentage'].widget.attrs['max'] = 100
        self.fields['percentage'].widget.attrs['min'] = 0
        self.fields['section'].widget.attrs['class'] = 'browser-default custom-select'

class AddGradeScaleForm(forms.ModelForm):
    class Meta:
        model = GradeScale
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(AddGradeScaleForm, self).__init__(*args, **kwargs)
        self.fields['section'].widget.attrs['class'] = 'browser-default custom-select'
        self.fields['grade'].widget.attrs['class'] = 'browser-default custom-select'

class AddMarkPermissionForm(forms.ModelForm):
    class Meta:
        model = ScorePermission
        fields = ['start_time', 'end_time']

    def __init__(self, *args, **kwargs):
        super(AddMarkPermissionForm, self).__init__(*args, **kwargs)
        self.fields['start_time'].widget.attrs['id'] = 'startingDate'
        self.fields['end_time'].widget.attrs['id'] = 'endingDate'

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

class AddClassForm(forms.ModelForm):
    class Meta:
      model = Class
      fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(AddClassForm, self).__init__(*args, **kwargs)
        self.fields['section'].widget.attrs['class'] = 'browser-default custom-select'


class AddSubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(AddSubjectForm, self).__init__(*args, **kwargs)
        self.fields['section'].widget.attrs['class'] = 'browser-default custom-select'
        self.fields['subject_type'].widget.attrs['class'] = 'browser-default custom-select'

class AddBatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ['name','capacity','clss','subjects']

    def __init__(self, *args, **kwargs):
        super(AddBatchForm, self).__init__(*args, **kwargs)
        self.fields['subjects'].widget.attrs['class'] = 'browser-default multiple custom-select'
        self.fields['clss'].widget.attrs['class'] = 'browser-default custom-select'
        self.fields['subjects'].queryset = Subject.objects.none()

        if 'clss' in self.data:
            try:
                class_id = int(self.data.get('clss'))
                self.fields['subjects'].queryset = Class.objects.get(pk=class_id).section.subject_set.all()
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty subjects queryset
        elif self.instance.pk:
            self.fields['subjects'].queryset = self.instance.clss.section.subject_set.order_by('name')


class AddSectionForm(forms.Form):
    section = forms.CharField(max_length=50, label="Section name")
    note = forms.CharField(max_length=100, label="Section Description", required=False)

class SubjectAllocationForm(forms.ModelForm):
    batch = forms.ModelChoiceField(queryset=Batch.objects.none())
    subjects = forms.ModelMultipleChoiceField(queryset=Subject.objects.none())
    
    class Meta:
        model = SubjectAllocation
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            Fieldset(
                'Subject Allocation',
                Row(
                    Column('session', css_class='form-group col-md-2 mb-0'),
                    Column('term', css_class='form-group col-md-2 mb-0'),
                    Column('teacher', css_class='form-group col-md-2 mb-0'),
                    Column('clss', css_class='form-group col-md-2 mb-0'),
                    Column('batch', css_class='form-group col-md-2 mb-0'),
                    Column('subjects', css_class='form-group col-md-2 mb-0'),
                    css_class='form-row'
                ),
            )
        )
        if 'batch' in self.data:
            try:
                batch_id = int(self.data.get('batch'))
                subjects = int(self.data.get('subjects'))
                class_id = int(self.data.get('clss'))
                self.fields['subjects'].queryset = Batch.objects.get(pk=batch_id).subjects.all()
                self.fields['batch'].queryset = Batch.objects.filter(clss=class_id)
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty subjects queryset
        elif self.instance.pk:
            self.fields['subjects'].queryset = self.instance.batch.subjects.all()
            self.fields['batch'].queryset = Batch.objects.filter(clss=self.clss)
        else:
            self.fields['batch'].queryset = Batch.objects.none()
            self.fields['subjects'].queryset = Subject.objects.none()


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
        model = SectionAllocation
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
    message = forms.CharField()
    image = forms.ImageField(required=False)
    class Meta:
        model = EmailMessage
        fields = ["recipients", "title", "message", 'image']

class ImportForm(forms.Form):
    csv_file = forms.FileField(widget=forms.FileInput(attrs={'accept': ".csv"}))


class RoleAddForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name',]