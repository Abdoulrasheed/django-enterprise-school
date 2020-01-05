from django import forms
from sms.models import Parent, Student, Batch, Subject, Teacher
from authentication.models import User
from utils.constants import OPTIONAL
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset

class AddUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'other_name', 
                    'email','address1', 'address2', 'picture',
                    'dob', 'gender', 'religion', 'state', 'lga', 'blood_group', 'genotype', 'phone'] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            Fieldset(
                'Personal Information',
                Row(
                    Column('first_name', css_class='form-group col-md-4 mb-0'),
                    Column('last_name', css_class='form-group col-md-4 mb-0'),
                    Column('other_name', css_class='form-group col-md-4 mb-0'),
                    css_class='form-row'
                    ),
                Row(
                    Column('email', css_class='form-group col-md-4 mb-0'),
                    Column('phone', css_class='form-group col-md-4 mb-0'),
                    Column('picture', css_class='form-group col-md-4 mb-0'),
                    css_class='form-row'
                    ),
                Row(
                    Column('address1', css_class='form-group col-md-4 mb-0'),
                    Column('address2', css_class='form-group col-md-4 mb-0'),
                    Column('gender', css_class='form-group col-md-4 mb-0'),
                    css_class='form-row'
                    ),
                Row(
                    Column('state', css_class='form-group col-md-4 mb-0'),
                    Column('lga', css_class='form-group col-md-4 mb-0'),
                    Column('religion', css_class='form-group col-md-4 mb-0'),
                    css_class='form-row'
                    ),
                Row(
                    Column('dob', css_class='form-group col-md-4 mb-0'),
                    Column('blood_group', css_class='form-group col-md-4 mb-0'),
                    Column('genotype', css_class='form-group col-md-4 mb-0'),
                    css_class='form-row'
                    )
                )
            )
        self.fields['gender'].widget.attrs['class'] = 'browser-default custom-select'
        self.fields['religion'].widget.attrs['class'] = 'browser-default custom-select'
        self.fields['state'].widget.attrs['class'] = 'browser-default custom-select'
        self.fields['lga'].widget.attrs['class'] = 'browser-default custom-select'
        self.fields['blood_group'].widget.attrs['class'] = 'browser-default custom-select'
        self.fields['genotype'].widget.attrs['class'] = 'browser-default custom-select'

class AddStudentForm(forms.ModelForm):
    parent = forms.ModelChoiceField(
        required=False,
        queryset=Parent.objects.all())

    class Meta:
        model = Student
        fields = ['in_class', 'batch', 'optional_subjects', 'year_of_admission']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            Fieldset(
                'Academic Information',
                Row(
                    Column('in_class', css_class='form-group col-md-4 mb-0'),
                    Column('batch', css_class='form-group col-md-4 mb-0'),
                    Column('optional_subjects', css_class='form-group col-md-4 mb-0'),
                    css_class='form-row'
                    ),
                Row(
                    Column('year_of_admission', css_class='form-group col-md-12 mb-0'),
                    )
                )
            )
        self.fields['in_class'].widget.attrs['class'] = 'browser-default custom-select'
        self.fields['batch'].widget.attrs['class'] = 'browser-default custom-select'
        self.fields['optional_subjects'].widget.attrs['class'] = 'browser-default custom-select'
        self.fields['parent'].widget.attrs['class'] = 'browser-default custom-select'
        self.fields['year_of_admission'].widget.attrs['class'] = 'browser-default custom-select'

        if 'in_class' in self.data:
            try:
                class_id = int(self.data.get('in_class'))
                id_batch = int(self.data.get('id_batch'))
                self.fields['batch'].queryset = Batch.objects.filter(clss=class_id)
                self.fields['optional_subjects'].queryset = Batch.objects.filter(clss=class_id).subjects.filter(subject_type=OPTIONAL)
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty subjects queryset
        elif self.instance.pk:
            self.fields['optional_subjects'].queryset = self.instance.batch.subjects.filter(subject_type=OPTIONAL).order_by('name')
            self.fields['batch'].queryset = Batch.objects.filter(pk=self.instance.batch_id)
        else:
            self.fields['batch'].queryset = Batch.objects.none()
            self.fields['optional_subjects'].queryset = Subject.objects.none()

class AddTeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        exclude = ['user', 'next_of_kin']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            Fieldset(
                'Other Information',
                Row(
                    Column('branch', css_class='form-group col-md-6 mb-0'),
                    Column('qualification', css_class='form-group col-md-6 mb-0'),
                    Column('section', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                    )
                )
            )