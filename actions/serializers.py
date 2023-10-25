from rest_framework import serializers

from .models import UserAction, InvitationAction, RequestAction


class InvitatationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvitationAction
        fields = '__all__'
        read_only_fields = ['status']


class AcceptCancelSerializer(serializers.Serializer):
    is_owner = serializers.BooleanField()
    id = serializers.IntegerField()


# class RequestSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Actions
#         fields = ['company']
#
#
# class LeaveFromCompany(serializers.Serializer):
#     id = serializers.IntegerField()
#
#
# class MemberListSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Actions
#         fields = ['company']
#
#
# class MyInvitesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Actions
#         fields = '__all__'
#
#
# class MyRequestsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Actions
#         fields = '__all__'