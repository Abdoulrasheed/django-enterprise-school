from constants import *
from django.db import models
from django.conf import settings
from .validators import ASCIIUsernameValidator
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_parent = models.BooleanField(default=False)
    phone = models.CharField(max_length=60, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    picture = models.ImageField(upload_to="pictures/", blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    other_name = models.CharField(max_length=100, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(choices=GENDER, max_length=6, blank=True, null=True)
    religion = models.CharField(choices=RELIGION, max_length=12, blank=True, null=True)
    state = models.CharField(choices=STATE, max_length=100, blank=True, null=True)
    lga = models.CharField(choices=LGA, max_length=100, blank=True, null=True)



    username_validator = ASCIIUsernameValidator()

    def get_picture(self):
        no_picture = settings.STATIC_URL + 'img/img_avatar.png'
        try:
            return self.picture.url
        except:
            return no_picture

    def get_full_name(self):
        full_name = self.username
        if self.first_name and self.last_name:
            full_name = self.first_name + " " + self.last_name
            if self.other_name:
            	full_name = self.first_name + " " + self.last_name + " " + self.other_name
        return full_name