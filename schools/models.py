from django.db import models
from authentication.models import User
from django_tenants.models import TenantMixin, DomainMixin
from sms.models import Setting


class Client(TenantMixin):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=200)
    created_on = models.DateField(auto_now_add=True)
    on_trial = models.BooleanField(default=True)
    active_until = models.DateField()
    school_admin = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)
    auto_drop_schema = True
    force_drop = True
    
    def __str__(self):
    	return self.name



class Domain(DomainMixin):
    pass
