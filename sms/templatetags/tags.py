from django import template
register = template.Library()
from sms.models import Subject
@register.simple_tag
def get_subject(pk):
	return Subject.objects.get(pk=int(pk))

