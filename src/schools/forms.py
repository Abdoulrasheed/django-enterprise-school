from django import forms
from .models import Client, Domain

class GenerateUsersForm(forms.Form):
    pass

class UpdateSchoolForm(forms.ModelForm):
	domain = forms.CharField(max_length=100)

	class Meta:
		model = Client
		exclude = ['schema_name']

	def __init__(self, *args, **kwargs):
		super(UpdateSchoolForm, self).__init__(*args, **kwargs)
		try:
			domain = Domain.objects.get(tenant_id=self.instance.id)
			if self.data:
				domain.domain = self['domain'].value()
				domain.save()
			self.fields['domain'].widget.attrs['value'] = domain.domain
		except:
			pass

	field_order = ['name', 'domain', 'description', 'created_on', 'on_trial', 'school_package', 'active_until']

class SchoolAddForm(UpdateSchoolForm):
	"""docstring for SchoolAddForm"""
	user_id = forms.IntegerField(required=False)
	username = forms.CharField(max_length=50, min_length=4)
		

class SchoolDeleteForm(forms.Form):
	password = forms.CharField()
	school_id = forms.IntegerField()