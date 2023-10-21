from enum import Enum

from django.db import models

from services.utils.models import TimeStampedModel
from users.models import User


class InvitationStatus(Enum):
    invited = 'Invited'
    revoke = "Revoked"
    requested = 'Requested'
    rejected = 'Rejected'
    declined = 'Declined'
    removed = 'Removed'
    left = 'Left'

    member = 'Member'
    owner = 'Owner'


class Actions(TimeStampedModel):
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, related_name="actions", db_column="company_id")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20)
