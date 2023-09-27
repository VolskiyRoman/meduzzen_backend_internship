from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import User


class UserAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {'name': 'Test User', 'description': 'Test Description'}

    def test_create_user(self):
        url = reverse('user-list')
        response = self.client.post(url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().name, 'Test User')

    def test_retrieve_user(self):
        user = User.objects.create(name='Test User', description='Test Description')
        url = reverse('user-detail', args=[user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test User')


