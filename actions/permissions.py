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


class IsInviteOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.company.owner


class IsInviteRecipient(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user


class IsInviteStatusPending(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.status == InviteStatus.PENDING.value


class IsRequestStatusPending(permissions.BasePermission):
    def has_permission(self, request, view):
        request = view.get_object()

        if request.status != RequestStatus.PENDING.value:
            return False

        return True


class IsCompanyOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.company.owner


class IsRequestOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user
