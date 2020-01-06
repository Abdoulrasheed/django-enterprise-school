from .models import ScorePermission, Teacher, SubjectAllocation, Score, Grade
from authentication.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from sms_notification.send_message import SMS
from sms_notification.models import Setting
from django.utils.timesince import timesince, timeuntil
from django.db.models import Sum
from .remark import get_grade

@receiver(post_save, sender=ScorePermission)
def notify_teachers(sender, instance, **kwargs):
	teachers = Teacher.objects.filter(section_id=instance.pk)
	recipients = [t.user.phone for t in teachers]
	sms = SMS()
	sms.send(recipients=recipients,
		message=f"Score entry permission for {instance} \
		section just got updated, it is set to auto close in \
		{timeuntil(instance.end_time)} from now\nHurry and get \
		your score entry done !")


@receiver(post_save, sender=SubjectAllocation)
def notify_teacher(sender, instance, **kwargs):
	teacher_id = instance.teacher.pk
	teacher = Teacher.objects.get(pk=teacher_id)
	subject_allocation = teacher.subjectallocation_set.first()
	subjects = subject_allocation.subjects.all()
	subjects = [f"{s.name}," for s in subjects]
	subjects = "".join(subjects)
	message = f"Hello {instance.teacher.user.get_full_name()}\
		\nYou've been assigned to teach {subjects} in {instance.term} term of {instance.session} academic session\nGoodLuck !"
	instance.teacher.user.send_sms(message=message)


@receiver(post_save, sender=Score)
def save_grade(sender, instance, **kwargs):
	total = Score.objects.filter(
		student=instance.student_id, term=instance.term, 
		session=instance.session, subject=instance.subject).aggregate(Sum('score'))['score__sum']
	grade_data = get_grade(total=total, section=instance.mark_percentage.section)
	Grade.objects.update_or_create(student=instance.student, term=instance.term, session=instance.session,
		subject=instance.subject, defaults={"total": total, "grade": grade_data[0], "remark": grade_data[1]})