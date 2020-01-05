from django.db import models
from sms.models import Section


class PromotionCriteria(models.Model):
	description	= models.CharField(max_length=50)
	minimum_avg	= models.FloatField(max_length=5)

	def __str__(self):
		return self.description

class SectionPromotionCriteria(models.Model):
	section 			= models.ForeignKey(Section, on_delete=models.CASCADE)
	promotion_criteria	= models.ForeignKey(PromotionCriteria, null=True, on_delete=models.SET_NULL)

	def __str__(self):
		return self.section