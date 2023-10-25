from rest_framework import permissions
from rest_framework.permissions import BasePermission

from actions.models import UserStatus, UserAction


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.company.owner == request.user


class IsOwnerOfCompany(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        action = UserAction.objects.filter(user=request.user, company=obj).first()
        return action.status == UserStatus.OWNER.value


class IsRecipientOfInvitation(BasePermission):
    def has_permission(self, request, view):
        invitation = view.get_object()
        return request.user.email == invitation.recipient_email
