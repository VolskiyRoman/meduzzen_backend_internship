from rest_framework import permissions

from company.models import Company


class IsCompanyAdminOrOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'create':
            company_id = request.data.get('company')
            if company_id:
                try:
                    company = Company.objects.get(id=company_id)
                except Company.DoesNotExist:
                    company = None

                if company:
                    return company.owner == request.user or request.user in company.admins.all()
            return False
        return True

    def has_object_permission(self, request, view, obj):
        if obj.company:
            return obj.company.owner == request.user or request.user in obj.company.admins.all()

        return True
