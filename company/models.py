from django.db import models

from actions.models import UserAction, UserStatus
from services.utils.models import TimeStampedModel


class Company(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    is_hidden = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Companies"

    def owner(self):
        action = UserAction.objects.filter(company=self, status=UserStatus.OWNER.value).first()
        return action.user

    def __str__(self):
        return self.name
