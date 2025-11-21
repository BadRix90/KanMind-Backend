from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from auth_app.models import User


class RegistrationTests(TestCase):
    """Tests für User-Registrierung"""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_registration_success(self):
        data = {
            'fullname': 'Test User',
            'email': 'test@test.de',
            'password': 'test1234',
            'repeated_password': 'test1234'
        }
        response = self.client.post('/api/registration/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)
    
    def test_registration_password_mismatch(self):
        data = {
            'fullname': 'Test',
            'email': 'test@test.de',
            'password': 'test1234',
            'repeated_password': 'different'
        }
        response = self.client.post('/api/registration/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(TestCase):
    """Tests für User-Login"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@test.de',
            fullname='Test User',
            password='test1234'
        )
    
    def test_login_success(self):
        data = {'email': 'test@test.de', 'password': 'test1234'}
        response = self.client.post('/api/login/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
    
    def test_login_invalid_credentials(self):
        data = {'email': 'test@test.de', 'password': 'wrong'}
        response = self.client.post('/api/login/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class EmailCheckTests(TestCase):
    """Tests für Email-Check"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@test.de',
            fullname='Test User',
            password='test1234'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_email_exists(self):
        response = self.client.get(
            '/api/email-check/?email=test@test.de'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@test.de')
    
    def test_email_not_found(self):
        response = self.client.get(
            '/api/email-check/?email=notfound@test.de'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_email_check_no_auth(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(
            '/api/email-check/?email=test@test.de'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
class UserModelTests(TestCase):
   
    def test_user_str(self):
        user = User.objects.create_user(
            email='test@test.de',
            fullname='Test User',
            password='test1234'
        )
        self.assertEqual(str(user), 'test@test.de')
    
    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email='admin@test.de',
            fullname='Admin',
            password='admin123'
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)