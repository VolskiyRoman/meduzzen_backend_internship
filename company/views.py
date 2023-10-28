from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from company.serializers import CompanySerializer

from .models import Company
from .permissions import IsOwnerOrReadOnly


class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    queryset = Company.objects.all()

    def perform_create(self, serializer):
        owner = self.request.user
        members = [owner]

        serializer.save(owner=owner, members=members)

    def get_queryset(self):
        if self.action == 'list':
            return Company.objects.filter(is_hidden=False)
        return Company.objects.all()

    @action(detail=True, url_path='delete-member', methods=['POST'])
    def delete_member(self, request, pk=None):
        company = self.get_object()
        user_id = request.data.get('user_id')

        if user_id is None:
            raise ValidationError({'detail': 'Must be entered user_id in request'})

        try:
            user_id = int(user_id)
        except ValueError:
            raise ValidationError({'detail': 'User id must be an integer'})

        try:
            user = get_user_model().objects.get(pk=user_id)
        except get_user_model().DoesNotExist:
            raise ValidationError({'detail': 'User not found'})

        if user == company.owner:
            raise ValidationError({'detail': 'The owner of the company cannot be removed'})

        if user in company.members.all():
            company.members.remove(user)

            return Response({'message': 'User has been deleted from company'})

        raise ValidationError({'detail': 'The user is not a member of the company'})
