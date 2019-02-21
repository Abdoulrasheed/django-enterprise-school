import math
from django import template

register = template.Library()
from sms.models import Subject

ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(math.floor(n/10)%10!=1)*(n%10<4)*n%10::4])

@register.simple_tag
def get_rank(rank):
	return ordinal(int(rank))

@register.simple_tag
def get_subject(pk):
	return Subject.objects.get(pk=int(pk))

