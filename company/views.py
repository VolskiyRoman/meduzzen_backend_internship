from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from actions.models import Actions, InvitationStatus
from company.serializers import CompanySerializer

from .models import Company
from .permissions import IsOwnerOfCompany


class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, IsOwnerOfCompany]
    queryset = Company.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        print(serializer.data)

        company_id = serializer.data.get('id')

        try:
            company = Company.objects.get(pk=company_id)
        except Company.DoesNotExist:
            return Response({'error': 'Company does not exist'}, status=status.HTTP_404_NOT_FOUND)

        action = Actions(user=request.user, company=company, status=InvitationStatus.owner.value)
        action.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        if self.action == 'list':
            return Company.objects.filter(is_hidden=False)
        return Company.objects.all()
