from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from company.models import Company
from users.models import User

from .models import UserStatus, InviteStatus, RequestStatus, UserAction, InvitationAction, RequestAction
from .serializers import (
    # AcceptCancelSerializer,
    InvitatationSerializer,
    # LeaveFromCompany,
    # MemberListSerializer,
    # MyInvitesSerializer,
    # MyRequestsSerializer,
    # RequestSerializer,
)


class CreateInvitation(APIView):
    queryset = InvitationAction.objects.all()
    serializer_class = InvitatationSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        sender = request.user
        company_id = data.get('company')
        recipient_id = data.get('user')

        recipient = User.objects.get(pk=recipient_id)
        company = Company.objects.get(pk=company_id)

        recipient_member = UserAction.objects.filter(company=company, user=recipient).first()

        if not company:
            return Response({'error': 'Company not found'}, status=404)

        if not recipient:
            return Response({'error': 'Recipient not found'}, status=404)

        if recipient_member:
            return Response({'error': 'User already in company'}, status=400)

        if company.owner() == sender:
            recipient_invite = InvitationAction.objects.filter(company=company, user=recipient).first()
            recipient_request = RequestAction.objects.filter(company=company, user=recipient).first()

            if not recipient_invite:
                if recipient_request:
                    recipient_request.status = RequestStatus.APPROVED.value
                    recipient_request.save()

                    recipient_member = UserAction(company=company, user=recipient, status=UserStatus.MEMBER.value)
                    recipient_member.save()

                    return Response({'message': 'This member added to company'}, status=200)
                else:
                    created_invite = InvitationAction(company=company, user=recipient, status=InviteStatus.INVITED.value)
                    created_invite.save()
                    return Response({'message': 'Invitation sent successfully'}, status=200)
            else:
                return Response({'error': 'User already invited'}, status=400)
        else:
            return Response({'error': 'You are not the owner of this company'}, status=400)


# class InvitationViewSet(viewsets.ModelViewSet):
#
# my invites
#     user = request.user
#     user_owner_actions = UserAction.objects.filter(status=UserStatus.OWNER.value, user=user)
#     companies = [action.company for action in user_owner_actions]
#     actions = InvitationAction.objects.filter(status=InviteStatus.INVITED.value, company__in=companies)
#     serializer = ActionsSerializer(actions, many=True)
#     return Response(serializer.data)

# class CreateRequest(APIView):
#     queryset = Actions.objects.all()
#     serializer_class = RequestSerializer
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request, *args, **kwargs):
#         data = request.data
#         user = request.user
#         company_id = data.get('company')
#
#         company = Company.objects.get(pk=company_id)
#
#         if not company:
#             return Response({'error': 'Company not found'}, status=404)
#
#         action = Actions.objects.filter(company=company, user=user).first()
#         if action:
#             if action.status == RequestStatus.REQUESTED.value:
#                 return Response({'error': 'User already requested'}, status=400)
#             elif action.status in [UserStatus.MEMBER.value, UserStatus.OWNER.value]:
#                 return Response({'error': 'User already in company'}, status=400)
#             elif action.status in [InviteStatus.INVITED.value]:
#                 action.status = UserStatus.MEMBER.value
#                 action.save()
#                 return Response({'message': 'You added to company'}, status=200)
#         else:
#             action = Actions(company=company, user=user, status=RequestStatus.REQUESTED.value)
#             action.save()
#         return Response({'message': 'Request sent successfully'}, status=200)
#
#     def get(self, request):
#         user = request.user
#         user_owner_actions = Actions.objects.filter(status=UserStatus.OWNER.value, user=user)
#         companies = [action.company for action in user_owner_actions]
#         actions = Actions.objects.filter(status=RequestStatus.REQUESTED.value, company__in=companies)
#         serializer = ActionsSerializer(actions, many=True)
#         return Response(serializer.data)
#
#


# class CancelInvitation(APIView):
#     queryset = InvitationAction.objects.all()
#     serializer_class = AcceptCancelSerializer
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request, *args, **kwargs):
#         data = request.data
#         sender = request.user
#         action_id = data.get('id')
#         is_owner = data.get('is_owner', None)
#         action = Actions.objects.filter(pk=action_id).first()
#         if not action:
#             return Response({'error': 'No such action exist'}, status=400)
#
#         if is_owner is None:
#             return Response({'error': 'You must specify who is making this cancellation'}, status=400)
#
#         if action.status == InviteStatus.REVOKED.value:
#             return Response({'error': 'This invitation already revoked'}, status=400)
#
#         if action.status == InviteStatus.DECLINED.value:
#             return Response({'error': 'This invitation already declined'}, status=400)
#
#         if action.status == UserStatus.MEMBER.value:
#             return Response({'error': 'This invitation already accepted'}, status=400)
#
#         if is_owner:
#             if sender == action.company.owner():
#                 action.status = InviteStatus.REVOKED.value
#                 action.save()
#                 return Response({'message': 'Invitation revoked'}, status=200)
#             return Response({'error': 'You are not owner of this company'}, status=400)
#         else:
#             if sender == action.user:
#                 action.status = InviteStatus.DECLINED.value
#                 action.save()
#                 return Response({'message': 'This invitation is declined'}, status=200)
#             return Response({'error': 'You cannot interact with this invitation '}, status=400)
#
#
# class AcceptInvitation(APIView):
#     queryset = InvitationAction.objects.all()
#     serializer_class = AcceptCancelSerializer
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request):
#         data = request.data
#         sender = request.user
#         action_id = data.get('id')
#         is_owner = data.get('is_owner', None)
#         action = Actions.objects.filter(pk=action_id).first()
#         if not action:
#             return Response({'error': 'No such action exist'}, status=400)
#
#         if is_owner is None:
#             return Response({'error': 'You must specify who is making this cancellation'}, status=400)
#
#         if action.status == InviteStatus.REVOKED.value:
#             return Response({'error': 'This invitation already revoked'}, status=400)
#         elif action.status == UserStatus.MEMBER.value:
#             return Response({'error': 'This invitation already accepted'}, status=400)
#         elif action.status == InviteStatus.DECLINED.value:
#             return Response({'error': 'This invitation already declined'}, status=400)
#
#         if is_owner:
#             if sender == action.company.owner():
#                 if action.status == UserStatus.OWNER.value:
#                     return Response({'error': 'You are owner of this company'}, status=400)
#                 action.status = UserStatus.MEMBER.value
#                 action.save()
#                 return Response({'message': 'Invitation accepted'}, status=200)
#             return Response({'error': 'You are not owner of this company'}, status=400)
#         else:
#             if sender == action.user:
#                 action.status = UserStatus.MEMBER.value
#                 action.save()
#                 return Response({'message': 'This invitation is accepted'}, status=200)
#             return Response({'error': 'You cannot interact with this invitation '}, status=400)
#
#
# class RemoveUser(APIView):
#     queryset = Actions.objects.all()
#     serializer_class = LeaveFromCompany
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request, *args, **kwargs):
#         data = request.data
#         user = request.user
#
#         action_id = data.get('id')
#         action = Actions.objects.filter(pk=action_id).first()
#
#         if not action:
#             return Response({'error': 'There is no such action'}, status=400)
#
#         if user == action.company.owner():
#             if action.status == DeletedUserStatus.REMOVED.value:
#                 return Response({'error': 'This invitation already removed'}, status=400)
#             if action.status == UserStatus.MEMBER.value:
#                 action.status = DeletedUserStatus.REMOVED.value
#                 action.save()
#                 return Response({'message': 'This user is removed'}, status=200)
#             return Response({'error': 'This member is not a member in your company'}, status=200)
#         else:
#             return Response({'error': 'You are not the owner of this company'}, status=400)
#
#
# class LeaveFromCompany(APIView):
#     queryset = Actions.objects.all()
#     serializer_class = LeaveFromCompany
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request, *args, **kwargs):
#         data = request.data
#         user = request.user
#
#         action_id = data.get('id')
#         action = Actions.objects.filter(pk=action_id).first()
#
#         if not action:
#             return Response({'error': 'There is no such action'}, status=400)
#
#         if user == action.user:
#             if action.status == DeletedUserStatus.LEFT.value:
#                 return Response({'error': 'You have already left the company'}, status=400)
#             if action.status == UserStatus.MEMBER.value:
#                 action.status = DeletedUserStatus.LEFT.value
#                 action.save()
#                 return Response({'message': 'You left the company'}, status=200)
#         return Response({'error': 'You are not a member in the company'}, status=200)
#
#
# class MemberList(APIView):
#     queryset = Actions.objects.all()
#     serializer_class = MemberListSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request):
#         user = request.user
#         user_owner_actions = Actions.objects.filter(status=UserStatus.OWNER.value, user=user)
#         companies = [action.company for action in user_owner_actions]
#         actions = Actions.objects.filter(status=UserStatus.MEMBER.value, company__in=companies)
#         serializer = ActionsSerializer(actions, many=True)
#         return Response(serializer.data)
#
#
# class MyInvites(APIView):
#     queryset = Actions.objects.all()
#     serializer_class = MyInvitesSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request):
#         user = request.user
#         filtered_actions = Actions.objects.filter(status=InviteStatus.INVITED.value, user=user)
#         serializer = ActionsSerializer(filtered_actions, many=True)
#         return Response(serializer.data)
#
#
# class MyRequests(APIView):
#     queryset = Actions.objects.all()
#     serializer_class = MyRequestsSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request):
#         user = request.user
#         filtered_actions = Actions.objects.filter(status=RequestStatus.REQUESTED.value, user=user)
#         serializer = ActionsSerializer(filtered_actions, many=True)
#         return Response(serializer.data)
