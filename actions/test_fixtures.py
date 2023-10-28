from django.test import TestCase
from rest_framework.test import APIClient

from company.models import Company
from users.models import User


class FixturesForAPITests(TestCase):
    @staticmethod
    def get_user_token(user_payload):
        client = APIClient()
        user_token = client.post('/auth/jwt/create/', user_payload).data['access']
        return 'Bearer ' + user_token

    def user_login(self, user_payload):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.get_user_token(user_payload))
        return client

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

        self.comp = Company.objects.create(name='testcomp1', description='testdesc', is_hidden=False, owner=self.user1)
        self.comp.members.add(self.user1)
