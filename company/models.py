from django.db import models

from actions.models import Actions, InvitationStatus
from services.utils.models import TimeStampedModel


class Company(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    is_hidden = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Companies"

    def owner(self):
        action = Actions.objects.filter(company=self, status=InvitationStatus.owner.value).first()
        return action.user

    def __str__(self):
        return self.name
