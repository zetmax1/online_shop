from datetime import timedelta

import jwt
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import PasswordResetCode

User = get_user_model()


class AuthenticationTestMixin:

    
    def get_jwt_token(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }

    def authenticate_user(self, user):
        tokens = self.get_jwt_token(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        return tokens


class CustomTokenObtainPairAPITests(APITestCase, AuthenticationTestMixin):
    def setUp(self):
        self.url = reverse('token_obtain_pair')
        self.user = User.objects.create_user(
            email='test@gmail.com',
            password='TestPass@123',
            first_name='Test',
            last_name='User'
        )

    def test_obtain_token_with_valid_credentials(self):
        data = {
            'email': 'test@gmail.com',
            'password': 'TestPass@123'
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        token = response.data['access']
        decoded = jwt.decode(token, options={"verify_signature": False})
        self.assertEqual(decoded['email'], 'test@gmail.com')

    def test_obtain_token_with_invalid_email(self):
        data = {
            'email': 'wrong@gmail.com',
            'password': 'TestPass@123'
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access', response.data)

    def test_obtain_token_with_invalid_password(self):
        data = {
            'email': 'test@gmail.com',
            'password': 'wrongpassword'
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_obtain_token_with_missing_fields(self):
        data = {'password': 'TestPass@123'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = {'email': 'test@gmail.com'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_obtain_token_with_empty_data(self):
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AccountsViewSetAPITests(APITestCase, AuthenticationTestMixin):

    def setUp(self):
        self.list_url = reverse('accounts-list')

        self.user1 = User.objects.create_user(
            email='user1@gmail.com',
            password='TestPass@123',
            first_name='User',
            last_name='One',
            phone_number='+998901234567'
        )

        self.user2 = User.objects.create_user(
            email='user2@gmail.com',
            password='TestPass@123',
            first_name='User',
            last_name='Two',
            phone_number='+998901234568'
        )

        # Admin user
        self.admin_user = User.objects.create_superuser(
            email='admin@gmail.com',
            password='AdminPass@123'
        )

    def get_detail_url(self, user_id):
        return reverse('accounts-detail', kwargs={'pk': user_id})

    def test_list_users_without_authentication(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_users_with_authentication(self):
        self.authenticate_user(self.user1)

        response = self.client.get(self.list_url)


        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # 2 user + 1 admin

        self.assertIsInstance(response.data, list)
        for user_data in response.data:
            self.assertIn('id', user_data)
            self.assertIn('email', user_data)
            self.assertIn('first_name', user_data)
            self.assertNotIn('password', user_data)  

    def test_create_user_without_authentication(self):
        data = {
            'email': 'new@gmail.com',
            'password': 'NewPass@123',
            'first_name': 'New',
            'last_name': 'User',
            'phone_number': '+998901234569'
        }

        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_user_with_valid_data(self):
        self.authenticate_user(self.admin_user)

        data = {
            'email': 'new@gmail.com',
            'password': 'NewPass@123',
            'first_name': 'New',
            'last_name': 'User',
            'phone_number': '+998901234569'
        }

        response = self.client.post(self.list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertIn('data', response.data)
        self.assertIn('status', response.data)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['status'], status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'User created successfully')

        self.assertTrue(User.objects.filter(email='new@gmail.com').exists())

        new_user = User.objects.get(email='new@gmail.com')
        self.assertTrue(new_user.check_password('NewPass@123'))

    def test_create_user_with_invalid_password(self):
        self.authenticate_user(self.admin_user)

        test_cases = [
            {
                'password': '123',
                'expected_error': 'Password should be 8 characters at least'
            },
            {
                'password': '12345678',
                'expected_error': 'Password should include one letter (A–Z or a–z) at least'
            },
            {
                'password': 'abcdefgh',
                'expected_error': 'Password should include one number at least'
            },
            {
                'password': 'abcdefg1',
                'expected_error': 'Password should include one specific character(!@#$ etc) at least'
            }
        ]

        for case in test_cases:
            data = {
                'email': f'test{case["password"]}@gmail.com',
                'password': case['password'],
                'first_name': 'Test',
                'last_name': 'User'
            }

            response = self.client.post(self.list_url, data, format='json')

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('password', response.data)
            self.assertIn(case['expected_error'], str(response.data['password']))

    def test_create_user_with_duplicate_email(self):
        self.authenticate_user(self.admin_user)

        data = {
            'email': 'user1@gmail.com',
            'password': 'NewPass@123',
            'first_name': 'Duplicate',
            'last_name': 'User'
        }

        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_create_user_with_missing_required_fields(self):
        self.authenticate_user(self.admin_user)

        data = {
            'password': 'NewPass@123',
            'first_name': 'Test'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_retrieve_user_without_authentication(self):
        url = self.get_detail_url(self.user1.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_user_with_authentication(self):
        self.authenticate_user(self.user1)

        url = self.get_detail_url(self.user1.id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'user1@gmail.com')
        self.assertEqual(response.data['first_name'], 'User')
        self.assertNotIn('password', response.data)

    def test_retrieve_nonexistent_user(self):
        self.authenticate_user(self.user1)

        url = self.get_detail_url(99999)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_user_without_authentication(self):
        url = self.get_detail_url(self.user1.id)
        data = {'first_name': 'Updated'}

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_partial_update_user(self):
        self.authenticate_user(self.user1)

        url = self.get_detail_url(self.user1.id)
        data = {'first_name': 'Partially Updated'}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'User updated successfully')

        self.user1.refresh_from_db()
        self.assertEqual(self.user1.first_name, 'Partially Updated')
        self.assertEqual(self.user1.last_name, 'One')

    def test_update_user_with_invalid_email(self):
        self.authenticate_user(self.user1)

        url = self.get_detail_url(self.user1.id)
        data = {
            'email': 'invalid-email',
            'first_name': 'Test'
        }

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_delete_user_without_authentication(self):
        url = self.get_detail_url(self.user1.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_user_with_authentication(self):
        self.authenticate_user(self.admin_user)

        url = self.get_detail_url(self.user1.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIn('status', response.data)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'User deleted successfully')

        self.assertFalse(User.objects.filter(id=self.user1.id).exists())

    def test_delete_nonexistent_user(self):
        self.authenticate_user(self.admin_user)

        url = self.get_detail_url(99999)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class SendPasswordResetCodeAPITests(APITestCase):

    def setUp(self):
        self.url = reverse('send-reset-code')
        self.user = User.objects.create_user(
            email='test@gmail.com',
            password='TestPass@123',
            first_name='Test',
            last_name='User'
        )

    def test_send_reset_code_with_valid_email(self):
        data = {'email': 'test@gmail.com'}

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Code has been sent to your email')

        self.assertTrue(
            PasswordResetCode.objects.filter(email='test@gmail.com').exists()
        )

        reset_code = PasswordResetCode.objects.filter(email='test@gmail.com').first()
        self.assertEqual(len(reset_code.code), 4)
        self.assertTrue(reset_code.code.isdigit())

    def test_send_reset_code_with_invalid_email(self):
        data = {'email': 'nonexistent@gmail.com'}

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertIn('There is no active user with this email', str(response.data['email']))

    def test_send_reset_code_with_malformed_email(self):
        data = {'email': 'invalid-email'}

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_send_reset_code_without_email(self):
        data = {}

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_multiple_reset_codes_for_same_email(self):
        data = {'email': 'test@gmail.com'}

        response1 = self.client.post(self.url, data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        response2 = self.client.post(self.url, data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        codes_count = PasswordResetCode.objects.filter(email='test@gmail.com').count()
        self.assertEqual(codes_count, 2)


class ResetPasswordAPITests(APITestCase):

    def setUp(self):
        self.url = reverse('reset-password')
        self.user = User.objects.create_user(
            email='test@gmail.com',
            password='OldPass@123',
            first_name='Test',
            last_name='User'
        )

        self.reset_code = PasswordResetCode.objects.create(
            email='test@gmail.com',
            code='1234'
        )

    def test_reset_password_with_valid_data(self):
        data = {
            'email': 'test@gmail.com',
            'code': '1234',
            'new_password': 'NewPass@123'
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Password has been successfully changed')

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPass@123'))
        self.assertFalse(self.user.check_password('OldPass@123'))

        self.assertFalse(
            PasswordResetCode.objects.filter(email='test@gmail.com', code='1234').exists()
        )

    def test_reset_password_with_invalid_code(self):
        data = {
            'email': 'test@gmail.com',
            'code': '9999',
            'new_password': 'NewPass@123'
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('code', response.data)
        self.assertIn('Invalid code', str(response.data['code']))

    def test_reset_password_with_expired_code(self):
        old_time = timezone.now() - timedelta(seconds=500)
        self.reset_code.created_at = old_time
        self.reset_code.save()

        data = {
            'email': 'test@gmail.com',
            'code': '1234',
            'new_password': 'NewPass@123'
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('code', response.data)
        self.assertIn('The code is expired', str(response.data['code']))

    def test_reset_password_with_nonexistent_email(self):
        data = {
            'email': 'nonexistent@gmail.com',
            'code': '1234',
            'new_password': 'NewPass@123'
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('code', response.data)

    def test_reset_password_with_short_password(self):
        data = {
            'email': 'test@gmail.com',
            'code': '1234',
            'new_password': '123'
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('new_password', response.data)

    def test_reset_password_with_missing_fields(self):
        test_cases = [
            {'code': '1234', 'new_password': 'NewPass@123'},
            {'email': 'test@gmail.com', 'new_password': 'NewPass@123'},
            {'email': 'test@gmail.com', 'code': '1234'}, ]

        for data in test_cases:
            response = self.client.post(self.url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
