from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from company.models import Company
from users.models import User

from .models import Actions, InvitationStatus
from .serializers import (
    AcceptCancelSerializer,
    ActionsSerializer,
    LeaveFromCompany,
    MemberListSerializer,
    MyInvitesSerializer,
    MyRequestsSerializer,
    RequestSerializer,
)


class CreateInvitation(APIView):
    queryset = Actions.objects.all()
    serializer_class = ActionsSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        sender = request.user
        company_id = data.get('company')
        user_id = data.get('user')

        recipient = User.objects.get(pk=user_id)
        company = Company.objects.get(pk=company_id)

        if not company:
            return Response({'error': 'Company not found'}, status=404)

        if not recipient:
            return Response({'error': 'Recipient not found'}, status=404)

        if company.owner() == sender:
            action = Actions.objects.filter(company=company, user=recipient).first()
            if action:
                if action.status == InvitationStatus.invited.value:
                    return Response({'error': 'User already invited'}, status=400)
                elif action.status in [InvitationStatus.member.value, InvitationStatus.owner.value]:
                    return Response({'error': 'User already in company'}, status=400)
                elif action.status in InvitationStatus.requested.value:
                    action.status = InvitationStatus.member.value
                    action.save()
                    return Response({'message': 'This member added to company'}, status=200)
                action.status = InvitationStatus.invited.value
                action.save()
                return Response({'message': 'Invitation sent successfully'}, status=201)
            else:
                action = Actions(company=company, user=recipient, status=InvitationStatus.invited.value)
                action.save()
            return Response({'message': 'Invitation sent successfully'}, status=201)
        else:
            return Response({'error': 'You are not the owner of this company'}, status=403)

    def get(self, request):
        user = request.user
        user_owner_actions = Actions.objects.filter(status=InvitationStatus.owner.value, user=user)
        companies = [action.company for action in user_owner_actions]
        actions = Actions.objects.filter(status=InvitationStatus.invited.value, company__in=companies)
        serializer = ActionsSerializer(actions, many=True)
        return Response(serializer.data)

class CreateRequest(APIView):
    queryset = Actions.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        user = request.user
        company_id = data.get('company')

        company = Company.objects.get(pk=company_id)

        if not company:
            return Response({'error': 'Company not found'}, status=404)

        action = Actions.objects.filter(company=company, user=user).first()
        if action:
            if action.status == InvitationStatus.requested.value:
                return Response({'error': 'User already requested'}, status=400)
            elif action.status in [InvitationStatus.member.value, InvitationStatus.owner.value]:
                return Response({'error': 'User already in company'}, status=400)
            elif action.status in InvitationStatus.invited.value:
                action.status = InvitationStatus.member.value
                action.save()
                return Response({'message': 'You added to company'}, status=200)
        else:
            action = Actions(company=company, user=user, status=InvitationStatus.requested.value)
            action.save()
        return Response({'message': 'Request sent successfully'}, status=200)

    def get(self, request):
        user = request.user
        user_owner_actions = Actions.objects.filter(status=InvitationStatus.owner.value, user=user)
        companies = [action.company for action in user_owner_actions]
        actions = Actions.objects.filter(status=InvitationStatus.requested.value, company__in=companies)
        serializer = ActionsSerializer(actions, many=True)
        return Response(serializer.data)


class CancelInvitation(APIView):
    queryset = Actions.objects.all()
    serializer_class = AcceptCancelSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        sender = request.user
        action_id = data.get('id')
        is_owner = data.get('is_owner', None)
        action = Actions.objects.filter(pk=action_id).first()
        if not action:
            return Response({'error': 'No such action exist'}, status=400)

        if is_owner is None:
            return Response({'error': 'You must specify who is making this cancellation'}, status=400)

        if action.status == InvitationStatus.revoke.value:
            return Response({'error': 'This invitation already revoked'}, status=400)

        if action.status == InvitationStatus.declined.value:
            return Response({'error': 'This invitation already declined'}, status=400)

        if action.status == InvitationStatus.member.value:
            return Response({'error': 'This invitation already accepted'}, status=400)

        if is_owner:
            if sender == action.company.owner():
                action.status = InvitationStatus.revoke.value
                action.save()
                return Response({'message': 'Invitation revoked'}, status=200)
            return Response({'error': 'You are not owner of this company'}, status=400)
        else:
            if sender == action.user:
                action.status = InvitationStatus.declined.value
                action.save()
                return Response({'message': 'This invitation is declined'}, status=200)
            return Response({'error': 'You cannot interact with this invitation '}, status=400)


class AcceptInvitation(APIView):
    queryset = Actions.objects.all()
    serializer_class = AcceptCancelSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        sender = request.user
        action_id = data.get('id')
        is_owner = data.get('is_owner', None)
        action = Actions.objects.filter(pk=action_id).first()
        if not action:
            return Response({'error': 'No such action exist'}, status=400)

        if is_owner is None:
            return Response({'error': 'You must specify who is making this cancellation'}, status=400)

        if action.status == InvitationStatus.revoke.value:
            return Response({'error': 'This invitation already revoked'}, status=400)
        elif action.status == InvitationStatus.member.value:
            return Response({'error': 'This invitation already accepted'}, status=400)
        elif action.status == InvitationStatus.declined.value:
            return Response({'error': 'This invitation already declined'}, status=400)

        if is_owner:
            if sender == action.company.owner():
                if action.status == InvitationStatus.owner.value:
                    return Response({'error': 'You are owner of this company'}, status=400)
                action.status = InvitationStatus.member.value
                action.save()
                return Response({'message': 'Invitation accepted'}, status=200)
            return Response({'error': 'You are not owner of this company'}, status=400)
        else:
            if sender == action.user:
                action.status = InvitationStatus.member.value
                action.save()
                return Response({'message': 'This invitation is accepted'}, status=200)
            return Response({'error': 'You cannot interact with this invitation '}, status=400)


class RemoveUser(APIView):
    queryset = Actions.objects.all()
    serializer_class = LeaveFromCompany
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        user = request.user

        action_id = data.get('id')
        action = Actions.objects.filter(pk=action_id).first()

        if not action:
            return Response({'error': 'There is no such action'}, status=400)

        if user == action.company.owner():
            if action.status == InvitationStatus.removed.value:
                return Response({'error': 'This invitation already removed'}, status=400)
            if action.status == InvitationStatus.member.value:
                action.status = InvitationStatus.removed.value
                action.save()
                return Response({'message': 'This user is removed'}, status=200)
            return Response({'error': 'This member is not member in your company'}, status=200)
        else:
            return Response({'error': 'You are not the owner of this company'}, status=400)


class LeaveFromCompany(APIView):
    queryset = Actions.objects.all()
    serializer_class = LeaveFromCompany
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        user = request.user

        action_id = data.get('id')
        action = Actions.objects.filter(pk=action_id).first()

        if not action:
            return Response({'error': 'There is no such action'}, status=400)

        if user == action.user:
            if action.status == InvitationStatus.left.value:
                return Response({'error': 'You are already left the company'}, status=400)
            if action.status == InvitationStatus.member.value:
                action.status = InvitationStatus.left.value
                action.save()
                return Response({'message': 'You left the company'}, status=200)
        return Response({'error': 'You not member in company'}, status=200)


class MemberList(APIView):
    queryset = Actions.objects.all()
    serializer_class = MemberListSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_owner_actions = Actions.objects.filter(status=InvitationStatus.owner.value, user=user)
        companies = [action.company for action in user_owner_actions]
        actions = Actions.objects.filter(status=InvitationStatus.member.value, company__in=companies)
        serializer = ActionsSerializer(actions, many=True)
        return Response(serializer.data)


class MyInvites(APIView):
    queryset = Actions.objects.all()
    serializer_class = MyInvitesSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        filtered_actions = Actions.objects.filter(status=InvitationStatus.invited.value, user=user)
        serializer = ActionsSerializer(filtered_actions, many=True)
        return Response(serializer.data)


class MyRequests(APIView):
    queryset = Actions.objects.all()
    serializer_class = MyRequestsSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        filtered_actions = Actions.objects.filter(status=InvitationStatus.requested.value, user=user)
        serializer = ActionsSerializer(filtered_actions, many=True)
        return Response(serializer.data)
