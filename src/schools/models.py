from django.db import models
from sms.models import Setting
from django.urls import reverse
from authentication.models import User
from django.utils.translation import ugettext_lazy as _
from django_tenants.models import TenantMixin, DomainMixin


STARTER = 'Starter'
ULTIMATE = 'Ultimate'
REGULAR = 'Regular'



PACKAGES = (

    (STARTER, _("Starter")),
    (REGULAR, _("Regular")),
    (ULTIMATE, _("Ultimate")),

)


class Client(TenantMixin):
    name = models.CharField("School name", max_length=100)
    description = models.TextField(max_length=200, blank=True, null=True)
    created_on = models.DateField(auto_now_add=True)
    on_trial = models.BooleanField(default=True)
    active_until = models.DateField()
    school_package = models.CharField("Package", max_length=20, default=ULTIMATE, choices=PACKAGES)
    auto_drop_schema = True
    force_drop = True
    
    def __str__(self):
    	return self.name

    def get_absolute_url(self):
        return reverse('schools_list')

class Domain(DomainMixin):
    pass