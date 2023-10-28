from rest_framework import permissions
from rest_framework.exceptions import ValidationError

from actions.models import InviteStatus, RequestStatus
from company.models import Company
from users.models import User


class InvitationPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        company_id = request.data.get('company')
        user_id = request.data.get('user')
        company = Company.objects.filter(pk=company_id).first()
        user = User.objects.filter(pk=user_id).first()

        if not company:
            raise ValidationError({'company': ['Company not found']})

        if not user:
            raise ValidationError({'user': ['User not found']})

        if company.owner != request.user:
            raise ValidationError({'user': ['User is not the owner of the company']})

        return True


class InviteInteractionPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        invitation = view.get_object()

        if invitation.status != InviteStatus.PENDING.value:
            raise ValidationError({'detail': 'This invitation can no longer be interacted with'})

        return True


class RequestPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        company_id = request.data.get('company')
        company = Company.objects.filter(pk=company_id).first()

        if not company:
            raise ValidationError({'company': ['Company not found']})

        return True


class RequestInteractionPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        request = view.get_object()

        if request.status != RequestStatus.PENDING.value:
            raise ValidationError({'detail': 'This invitation can no longer be interacted with'})

        return True
