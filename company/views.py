import csv

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from company.serializers import CompanySerializer
from quiz_app.models import Result
from services.utils.average_value import calculate_average_score

from .models import Company
from .permissions import IsOwnerOrAdmin, IsOwnerOrReadOnly


class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    queryset = Company.objects.all()

    def get_permissions(self):
        if self.action in [
            'list',
            'retrieve',
            'create',
            'update',
            'partial_update',
            'destroy',
            'delete_member',
            'add_admin',
            'remove_admin',
            'user_average_score',
        ]:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        elif self.action in [
            'admin_export_global',
            'admin_export_user'
        ]:
            return [IsAuthenticated(), IsOwnerOrAdmin()]

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
            raise ValidationError({'detail': 'Must provide user_id in the request'})

        try:
            user_id = int(user_id)
        except ValueError:
            raise ValidationError({'detail': 'User id must be an integer'})

        try:
            user = get_user_model().objects.get(pk=user_id)
        except get_user_model().DoesNotExist:
            raise ValidationError({'detail': 'User not found'})

        if user_id == company.owner.id:
            raise ValidationError({'detail': 'The owner of the company cannot be removed'})

        if user in company.members.all():
            company.members.remove(user)
            if user in company.admins.all():
                company.admins.remove(user)
            return Response({'message': 'User has been deleted from the company'})
        raise ValidationError({'detail': 'The user is not a member of the company'})

    @action(detail=True, methods=['POST'], url_path='add-admin')
    def add_admin(self, request, pk=None):
        company = self.get_object()
        user_id = request.data.get('user_id')

        if user_id is None:
            raise ValidationError({'detail': 'Must provide user_id in the request'})

        try:
            user_id = int(user_id)
        except ValueError:
            raise ValidationError({'detail': 'User id must be an integer'})

        try:
            user = get_user_model().objects.get(pk=user_id)
        except get_user_model().DoesNotExist:
            raise ValidationError({'detail': 'User not found'})

        if user == company.owner:
            raise ValidationError({'detail': 'The owner cannot be assigned as an admin.'})

        if user in company.admins.all():
            return Response({'message': 'User is already an admin.'})

        company.admins.add(user)
        return Response({'message': 'User has been added as an admin'})

    @action(detail=True, methods=['POST'], url_path='remove-admin')
    def remove_admin(self, request, pk=None):
        company = self.get_object()
        user_id = request.data.get('user_id')

        if user_id is None:
            raise ValidationError({'detail': 'Must provide user_id in the request'})

        try:
            user_id = int(user_id)
        except ValueError:
            raise ValidationError({'detail': 'User id must be an integer'})

        try:
            user = get_user_model().objects.get(pk=user_id)
        except get_user_model().DoesNotExist:
            raise ValidationError({'detail': 'User not found'})

        if user in company.admins.all():
            company.admins.remove(user)
            return Response({'message': 'User has been removed as an admin'})
        else:
            raise ValidationError({'detail': 'The user is not an admin of the company'})

    @action(detail=True, methods=['GET'], url_path='user-average-score')
    def user_average_score(self, request, pk=None):
        company = self.get_object()
        user = request.user
        user_results = Result.objects.filter(user=user, quiz__company=company)
        average_score = calculate_average_score(user_results)
        return Response({"average_score": average_score}, status=status.HTTP_200_OK)

    @action(detail=True, url_path='admin-export-global', methods=['GET'])
    def admin_export_global(self, request, pk=None):
        company = self.get_object()
        results = Result.objects.filter(quiz__company=company)

        serialized_data = [
            {
                'id': result.id,
                'user': str(result.user),
                'company': result.quiz.company.name,
                'quiz': str(result.quiz.title),
                'score': result.current_average_value,
                'date passed': result.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            for result in results
        ]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{company.name}_quiz_results.csv"'

        writer = csv.DictWriter(response, fieldnames=['id', 'user', 'company', 'quiz', 'score', 'date passed'])
        writer.writeheader()
        writer.writerows(serialized_data)

        return response

    @action(detail=True, url_path='admin-export-user', methods=['POST'],
            permission_classes=[IsAuthenticated, IsOwnerOrAdmin])
    def admin_export_user(self, request, pk=None):
        company = self.get_object()
        user_id = request.data.get('user_id')

        if not user_id:
            return Response({'detail': 'User ID is required in the request'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = get_user_model().objects.get(pk=user_id)
        except get_user_model().DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        results = Result.objects.filter(user=user, quiz__company=company)

        serialized_data = [
            {
                'id': result.id,
                'user': str(result.user),
                'company': result.quiz.company.name,
                'quiz': str(result.quiz.title),
                'score': result.current_average_value,
                'date passed': result.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            for result in results
        ]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{user.username}_quiz_results.csv"'

        writer = csv.DictWriter(response, fieldnames=['id', 'user', 'company', 'quiz', 'score', 'date passed'])
        writer.writeheader()
        writer.writerows(serialized_data)

        return response
