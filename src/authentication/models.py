from utils.constants import *
from django.db import models
from django.conf import settings
from sms_notification.send_message import SMS
from .validators import ASCIIUsernameValidator
from django.contrib.auth.models import AbstractUser, Group, UserManager


BLOOD_GROUPS = (
    ("A+", "A+"),
    ("A-", "A-"),
    ("B+", "B+"),
    ("B-", "B-"),
    ("O+", "O+"),
    ("O-", "O-"),
    ("AB+", "AB+"),
    ("AB-", "AB-"),)

GENOTYPES = (
    ("AA", "AA"),
    ("AS", "AS"),
    ("SA", "SA"),
    ("SS", "SS"),)

class UserManager(UserManager):
    def get_student_users(self):
        role = Group.objects.get(name='student')
        students = role.user_set.all()
        return students

    def get_parent_users(self):
        role = Group.objects.get(name='parent')
        parents = role.user_set.all()
        return parents

    def get_teacher_users(self):
        role = Group.objects.get(name='teacher')
        teachers = role.user_set.all()
        return teachers

class User(AbstractUser):
    is_student  = models.BooleanField(default=False)
    is_teacher  = models.BooleanField(default=False)
    is_parent   = models.BooleanField(default=False)
    first_name  = models.CharField(max_length=100)
    last_name  = models.CharField(max_length=100)
    other_name  = models.CharField(max_length=100, blank=True, null=True)
    phone       = models.CharField(max_length=60, blank=True, null=True)
    address1     = models.CharField(max_length=200, blank=True, null=True)
    address2     = models.CharField(max_length=200, blank=True, null=True)
    picture     = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)
    dob         = models.DateField(blank=True, null=True)
    gender      = models.CharField(choices=GENDER, max_length=6, blank=True, null=True)
    religion    = models.CharField(choices=RELIGION, max_length=12, blank=True, null=True)
    state       = models.CharField(choices=STATE, max_length=100, blank=True, null=True)
    lga         = models.CharField(choices=LGA, max_length=100, blank=True, null=True)
    blood_group = models.CharField(max_length=10, blank=True, null=True, choices=BLOOD_GROUPS)
    genotype    = models.CharField(max_length=10, blank=True, null=True, choices=GENOTYPES)

    objects = UserManager()


    username_validator = ASCIIUsernameValidator()

    def save(self, *args, **kwargs):
        if self.phone:
            if self.phone[0] == '0' and len(self.phone) == 11:
                self.phone = f"+234{self.phone[1:]}"
        super(User, self).save(*args, **kwargs)

    def get_picture(self):
        no_picture = settings.STATIC_URL + 'img/img_avatar.png'
        return self.picture.url if self.picture else no_picture

    def get_full_name(self):
        return f"{self.first_name or ''} {self.last_name or ''} {self.other_name or ''}"

    def send_sms(self, message):
        if self.phone:
            sms = SMS()
            sms.send(message=message, recipients=[self.phone,])