from django.db import models

from services.utils.models import TimeStampedModel
from users.models import User
from enum import auto
from strenum import StrEnum


class UserStatus(StrEnum):
    MEMBER = auto()
    OWNER = auto()

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class InviteStatus(StrEnum):
    INVITED = auto()
    REVOKED = auto()
    DECLINED = auto()

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class RequestStatus(StrEnum):
    REQUESTED = auto()
    CANCELED = auto()
    REJECTED = auto()
    APPROVED = auto()

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class Action(TimeStampedModel):
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, related_name="actions", db_column="company_id")
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class UserAction(Action):
    status = models.CharField(choices=UserStatus.choices())


class InvitationAction(Action):
    status = models.CharField(choices=UserStatus.choices())


class RequestAction(Action):
    status = models.CharField(choices=UserStatus.choices())