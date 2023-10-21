from rest_framework import status
from rest_framework.test import APITestCase

from company.models import Company
from users.models import User

from .models import Actions, InvitationStatus


class ActionsAPITestCase(APITestCase):
    def setUp(self):
        self.user_1_payload = {
            'email': 'user1@example.com',
            'password': 'testpassword'
        }

        self.user_2_payload = {
            'email': 'user2@example.com',
            'password': 'testpassword'
        }
        self.user1 = User.objects.create_user(**self.user_1_payload)
        self.user2 = User.objects.create_user(**self.user_2_payload)

        self.comp = Company.objects.create(name='testcomp1', description='testdesc', is_hidden=False)
        self.action = Actions.objects.create(status=InvitationStatus.owner.value, company=self.comp, user=self.user1)

    def test_create_invite(self):
        self.user1_token = self.client.post('/auth/jwt/create/', self.user_1_payload).data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user1_token)
        url = '/actions/invite'
        request_data = {"company": self.comp.id,
                   "user": self.user2.id}
        response = self.client.post(url, request_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Invitation sent successfully')

    def test_cancel_invite(self):
        Actions.objects.create(status=InvitationStatus.invited.value, company=self.comp, user=self.user2)

        self.user2_token = self.client.post('/auth/jwt/create/', self.user_2_payload).data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user2_token)

        url = '/actions/my/invites'
        response = self.client.get(url)
        invite_id = response.data[0]['id']

        url = '/actions/cancel'
        request_data = {"is_owner": False,
                        "id": invite_id}

        response = self.client.post(url, request_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['message'], 'This invitation is declined')

    def test_accept_invite(self):
        Actions.objects.create(status=InvitationStatus.invited.value, company=self.comp, user=self.user2)

        self.user2_token = self.client.post('/auth/jwt/create/', self.user_2_payload).data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user2_token)

        url = '/actions/my/invites'
        response = self.client.get(url)
        invite_id = response.data[0]['id']

        url = '/actions/accept'
        request_data = {"is_owner": False,
                        "id": invite_id}
        response = self.client.post(url, request_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'This invitation is accepted')

    def test_request(self):
        self.user2_token = self.client.post('/auth/jwt/create/', self.user_2_payload).data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user2_token)

        url = '/actions/request'
        request_data = {"company": self.comp.id}
        response = self.client.post(url, request_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Request sent successfully')

    def test_remove(self):
        member = Actions.objects.create(status=InvitationStatus.member.value, company=self.comp, user=self.user2)

        self.user1_token = self.client.post('/auth/jwt/create/', self.user_1_payload).data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user1_token)

        url = '/actions/remove'
        request_data = {"id": member.id}
        response = self.client.post(url, request_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'This user is removed')

    def test_leave(self):
        member = Actions.objects.create(status=InvitationStatus.member.value, company=self.comp, user=self.user2)

        self.user2_token = self.client.post('/auth/jwt/create/', self.user_2_payload).data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user2_token)

        url = '/actions/leave'
        request_data = {"id": member.id}
        response = self.client.post(url, request_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'You left the company')
