from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import InvitationAction, InviteStatus, RequestAction, RequestStatus
from .permissions import InvitationPermission, InviteInteractionPermission, RequestInteractionPermission, RequestPermission
from .serializers import InvitationSerializer, RequestSerializer


class InvitationViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    serializer_class = InvitationSerializer
    queryset = InvitationAction.objects.all()

    def get_permissions(self):
        if self.action in [
            'list',
            'retrieve'
        ]:
            return [IsAuthenticated()]
        elif self.action in [
            'accept_invitation',
            'cancel_invitation',
            'revoke_invitation'
        ]:
            return [IsAuthenticated(), InviteInteractionPermission()]
        return [IsAuthenticated(), InvitationPermission()]

    def perform_create(self, serializer):
        company = serializer.validated_data['company']
        invited_user = serializer.validated_data['user']

        if company.members.filter(id=invited_user.id).exists():
            raise ValidationError({'user': ['User already in company']})

        if InvitationAction.objects.filter(user=invited_user, status=InviteStatus.PENDING.value):
            raise ValidationError({'user': ['User already invited in company']})

        pending_request = RequestAction.objects.filter(user=invited_user, status=RequestStatus.PENDING.value,
                                                       company=company).first()

        if pending_request:
            pending_request.status = RequestStatus.APPROVED.value
            pending_request.save()
            company.members.add(pending_request.user)
            return Response({'message': 'This member added to company'}, status=200)


        status = InviteStatus.PENDING.value
        serializer.save(status=status, company=company)

    @action(detail=True, url_path='accept', methods=['POST']
        , permission_classes=[IsAuthenticated, InviteInteractionPermission])
    def accept_invitation(self, request, pk=None):
        invite = self.get_object()
        user = request.user
        recipient = invite.user

        if user != recipient:
            raise ValidationError({'user': ['You cannot interact with this invitation']})

        invite.status = InviteStatus.APPROVED.value
        invite.save()

        company = invite.company
        company.members.add(user)

        return Response({'message': 'You added to company'}, status=200)

    @action(detail=True, url_path='decline', methods=['POST']
        , permission_classes=[IsAuthenticated, InviteInteractionPermission])
    def cancel_invitation(self, request, pk=None):
        invite = self.get_object()
        user = request.user
        recipient = invite.user

        if user != recipient:
            raise ValidationError({'user': ['You cannot interact with this invitation']})

        invite.status = InviteStatus.DECLINED.value
        invite.save()

        return Response({'message': 'You declined company invitation'}, status=200)

    @action(detail=True, url_path='revoke', methods=['POST'],
            permission_classes=[IsAuthenticated, InviteInteractionPermission])
    def revoke_invitation(self, request, pk=None):
        invite = self.get_object()
        user = request.user
        owner = invite.company.owner

        if user != owner:
            raise ValidationError({'user': ['You cannot interact with this invitation']})

        invite.status = InviteStatus.REVOKED.value
        invite.save()

        return Response({'message': 'Invitation revoked successfully'}, status=200)


class RequestViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    serializer_class = RequestSerializer
    queryset = RequestAction.objects.all()

    def get_permissions(self):
        if self.action in [
            'list',
            'retrieve'
        ]:
            return [IsAuthenticated()]
        elif self.action in [
            'approve_request',
            'reject_request',
            'cancel_request'
        ]:
            return [IsAuthenticated(), RequestInteractionPermission()]
        return [IsAuthenticated(), RequestPermission()]

    def perform_create(self, serializer):
        company = serializer.validated_data['company']
        user = self.request.user

        if company.members.filter(id=user.id).exists():
            raise ValidationError({'user': ['You are already in company']})

        pending_invite = InvitationAction.objects.filter(user=user, status=RequestStatus.PENDING.value,
                                                         company=company).first()
        if pending_invite:
            pending_invite.status = RequestStatus.APPROVED.value
            pending_invite.save()
            company.members.add(pending_invite.user)
            return Response({'message': 'You are added to this company'}, status=200)

        if InvitationAction.objects.filter(user=user, status=InviteStatus.PENDING.value):
            raise ValidationError({'user': ['User already invited in company']})

        status = InviteStatus.PENDING.value
        serializer.save(status=status, company=company, user=self.request.user)

    @action(detail=True, url_path='approve', methods=['POST'],
            permission_classes=[IsAuthenticated, RequestInteractionPermission])
    def approve_request(self, request, pk=None):
        instance = self.get_object()
        owner = instance.company.owner

        if request.user != owner:
            raise ValidationError({'user': ['You cannot interact with this invitation']})

        instance.status = RequestStatus.APPROVED.value
        instance.save()

        company = instance.company
        company.members.add(instance.user)

        return Response({'message': 'You added this user to company'}, status=200)

    @action(detail=True, url_path='reject', methods=['POST'],
            permission_classes=[IsAuthenticated, RequestInteractionPermission])
    def reject_request(self, request, pk=None):
        instance = self.get_object()
        owner = instance.company.owner

        if request.user != owner:
            raise ValidationError({'user': ['You cannot interact with this invitation']})

        instance.status = RequestStatus.REJECTED.value
        instance.save()

        company = instance.company
        company.members.add()

        return Response({'message': 'You rejected this request'}, status=200)

    @action(detail=True, url_path='cancel', methods=['POST'],
            permission_classes=[IsAuthenticated, RequestInteractionPermission])
    def cancel_request(self, request, pk=None):
        instance = self.get_object()

        if instance.user != self.request.user:
            raise ValidationError({'user': ['You cannot interact with this invitation']})

        instance.status = RequestStatus.CANCELED.value
        instance.save()

        return Response({'message': 'Request canceled successfully'}, status=200)
