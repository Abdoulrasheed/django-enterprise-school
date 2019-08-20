from django import forms 


class UpdateSchoolForm(forms.Form):
	school_name = forms.CharField(max_length=50, min_length=4)
	subdomain = forms.CharField(max_length=50, min_length=2)
	phone = forms.CharField(max_length=11, min_length=11)
	description = forms.CharField(max_length=200, min_length=10)
	email = forms.EmailField()
	password = forms.CharField(max_length=16, min_length=4, required=False)
	ontrial = forms.BooleanField(required=False)
	active_until = forms.DateField()
	user_id = forms.IntegerField()