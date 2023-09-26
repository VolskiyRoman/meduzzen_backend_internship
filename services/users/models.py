from django.db import models
from services.utils.models import TimeStampedModel


class AbstractUser(TimeStampedModel):
    name = models.CharField(max_length=100)
    description = models.TextField()

    class Meta:
        abstract = True