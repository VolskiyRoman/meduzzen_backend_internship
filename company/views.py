from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from company.serializers import CompanySerializer

from .models import Company


class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    queryset = Company.objects.all()

    def get_queryset(self):
        if self.action == 'list':
            return Company.objects.filter(is_hidden=False)
        return Company.objects.all()
