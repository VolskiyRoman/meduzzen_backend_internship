from django.conf import settings
from django.db import models

from services.utils.models import TimeStampedModel


class Company(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    is_hidden = models.BooleanField(default=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_companies')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='companies_joined', blank=True)
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='companies_admins', blank=True)

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name
