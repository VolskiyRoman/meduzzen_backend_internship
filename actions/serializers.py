from rest_framework import serializers

from .models import InvitationAction, RequestAction


class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvitationAction
        fields = '__all__'
        read_only_fields = ['status']


class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestAction
        fields = '__all__'
        read_only_fields = ['status', 'user']
