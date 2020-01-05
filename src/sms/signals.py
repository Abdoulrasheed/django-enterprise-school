from .models import ScorePermission, Teacher, SubjectAllocation
from authentication.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from sms_notification.send_message import SMS
from sms_notification.models import Setting
from django.utils.timesince import timesince, timeuntil

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