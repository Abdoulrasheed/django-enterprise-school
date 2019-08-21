from django import forms 


class UpdateSchoolForm(forms.Form):
	school_name = forms.CharField(max_length=50, min_length=4)
	subdomain = forms.RegexField (
        label = "Subdomain", 
        max_length = 30,
        regex = r"^[\w'\.\-@]+$",
        help_text = "Required. 30 characters or fewer. Letters, apostrophes, periods, hyphens and at signs.")
	phone = forms.CharField(max_length=11, min_length=11)
	description = forms.CharField(max_length=200, min_length=10)
	email = forms.EmailField()
	password = forms.CharField(max_length=16, min_length=4, required=False)
	ontrial = forms.BooleanField(required=False)
	active_until = forms.DateField()
	user_id = forms.IntegerField()

class SchoolAddForm(UpdateSchoolForm):
	"""docstring for SchoolAddForm"""
	user_id = forms.IntegerField(required=False)
	username = forms.CharField(max_length=50, min_length=4)
		

class SchoolDeleteForm(forms.Form):
	password = forms.CharField()
	school_id = forms.IntegerField()