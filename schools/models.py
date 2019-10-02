from django.db import models
from django_tenants.models import TenantMixin, DomainMixin


class Client(TenantMixin):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=200)
    created_on = models.DateField(auto_now_add=True)
    on_trial = models.BooleanField(default=True)

    def __str__(self):
    	return self.name


class Domain(DomainMixin):
    pass
