from django.db import models

from services.utils.models import TimeStampedModel
from users.models import User


class Company(TimeStampedModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_hidden = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Companies"
