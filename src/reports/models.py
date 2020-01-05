from django.db import models
from sms.models import Section


class ReportTemplate(models.Model):
	report_card_template_name	= models.CharField(max_length=50)
	transcript_template_name	= models.CharField(max_length=50)

	def __str__(self):
		return self.report_card_template_name


class ReportCardSheet(models.Model):
	section 			= models.ForeignKey(Section, null=True, blank=True, on_delete=models.SET_NULL)
	show_attendance_info= models.BooleanField(default=True)
	show_class_vg		= models.BooleanField(default=True)
	show_final_avg		= models.BooleanField(default=True)
	show_final_grade	= models.BooleanField(default=True)
	show_final_position	= models.BooleanField(default=True)
	show_class_name		= models.BooleanField(default=True)
	show_highest_total	= models.BooleanField(default=True)
	show_lowest_total	= models.BooleanField(default=True)
	show_school_motto	= models.BooleanField(default=True)
	show_number_in_class= models.BooleanField(default=True)
	show_next_term_begin= models.BooleanField(default=True)
	show_no_student_col= models.BooleanField(default=True)
	show_student_id		= models.BooleanField(default=True)
	show_student_picture= models.BooleanField(default=True)
	show_total_score	= models.BooleanField(default=True)

	# comments, label n footer

	form_teacher_lbl 	= models.CharField(max_length=100)
	guiding_n_concil_lbl= models.CharField(max_length=100)
	overall_comment_lbl = models.CharField(max_length=100)

	show_form_teacher_com = models.BooleanField(default=True)
	show_extra_comment	  = models.BooleanField(default=True)
	show_guiding_n_council_com = models.BooleanField(default=True)
	show_promotion_status = models.BooleanField(default=True)
	use_auto_comment	  = models.BooleanField(default=False)

	# cognitive domain

	result_decimal_places = models.IntegerField(default=2)
	show_class_avg_for_subject_col = models.BooleanField(default=True)
	show_remark_column	  = models.BooleanField(default=True)
	show_previous_term_info = models.BooleanField(default=True)
	show_subject_lowes_col= models.BooleanField(default=True)
	show_percent_symbol	  = models.BooleanField(default=True)
	show_grade_column	  = models.BooleanField(default=True)
	show_subject_position = models.BooleanField(default=True)
	use_ordinal_position  = models.BooleanField(default=True)

	def __str__(self):
		return self.section