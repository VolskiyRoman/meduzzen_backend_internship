from django.shortcuts import get_object_or_404
from rest_framework import permissions

from actions.models import InviteStatus, RequestStatus
from company.models import Company


class InvitationPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        company_id = request.data.get('company')
        company = get_object_or_404(Company, pk=company_id)

        if company.owner != request.user:
            return False

        return True


class InviteInteractionPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        invitation = view.get_object()

        if invitation.status != InviteStatus.PENDING.value:
            return False

        return True


class RequestInteractionPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        request = view.get_object()

        if request.status != RequestStatus.PENDING.value:
            raise False

        return True
