from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import User
from .serializers import UserSerializer


class UserSerializerTestCase(TestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'password': 'password123',
            'bio': 'Test bio',
            'rating': 5,
            'first_name': 'John',
            'last_name': 'Doe',
        }

    def test_user_serializer_valid(self):
        serializer = UserSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid())

    def test_user_serializer_create(self):
        serializer = UserSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertIsInstance(user, User)
        self.assertEqual(user.email, self.user_data['email'])


class CustomUserManagerTestCase(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(email='test@example.com', password='password123')
        self.assertIsInstance(user, User)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_create_superuser(self):
        User = get_user_model()
        superuser = User.objects.create_superuser(email='superuser@example.com', password='superpassword')
        self.assertIsInstance(superuser, User)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_active)
