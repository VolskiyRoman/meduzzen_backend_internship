from enum import StrEnum, auto

from django.db import models

from company.models import Company
from services.utils.models import TimeStampedModel
from users.models import User


class InviteStatus(StrEnum):
    PENDING = auto()
    REVOKED = auto()
    DECLINED = auto()
    APPROVED = auto()

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class RequestStatus(StrEnum):
    PENDING = auto()
    CANCELED = auto()
    REJECTED = auto()
    APPROVED = auto()

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class InvitationAction(TimeStampedModel):
    status = models.CharField(choices=InviteStatus.choices())
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="invitation_actions",
                                db_column="company_id")
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class RequestAction(TimeStampedModel):
    status = models.CharField(choices=RequestStatus.choices())
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="request_actions",
                                db_column="company_id")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
