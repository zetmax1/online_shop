from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from products.models import Product, Category, ProductCategory

User = get_user_model()

class ProductAPITestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='adminpass123',
            is_staff=True,
            is_superuser=True
        )

        self.regular_user = User.objects.create_user(
            email='user@test.com',
            password='userpass123'
        )

        self.unauthenticated_client = APIClient()
        self.category1 = Category.objects.create(name="Electronics")
        self.category2 = Category.objects.create(name="Books")

        self.product1 = Product.objects.create(
            name="Test Product 1",
            price=Decimal('99.99'),
            description="Test description",
            count=10
        )

        self.product2 = Product.objects.create(
            name="Test Product 2",
            price=Decimal('149.99'),
            description="Another test description",
            count=5
        )

        ProductCategory.objects.create(product=self.product1, category=self.category1)

    def test_get_products_list_authenticated_user_success(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('products-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2)

    def test_get_products_list_unauthenticated_user_forbidden(self):
        response = self.unauthenticated_client.get(reverse('products-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_single_product_authenticated_user_success(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('products-detail', kwargs={'pk': self.product1.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.product1.name)
        self.assertEqual(float(response.data['price']), float(self.product1.price))

    def test_get_single_product_not_found(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('products-detail', kwargs={'pk': 9999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_product_admin_user_success(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('products-list')
        data = {
            'name': 'New Product',
            'price': '199.99',
            'description': 'New product description',
            'count': 15,
            # 'category_ids': [self.category1.id, self.category2.id]
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Product')
        self.assertEqual(Product.objects.count(), 3)

    def test_create_product_regular_user_forbidden(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('products-list')
        data = {
            'name': 'New Product',
            'price': '199.99',
            'description': 'New product description',
            'count': 15
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_product_unauthenticated_user_unauthorized(self):
        url = reverse('products-list')
        data = {
            'name': 'New Product',
            'price': '199.99',
            'description': 'New product description',
            'count': 15
        }
        response = self.unauthenticated_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_product_invalid_data_bad_request(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('products-list')

        data = {
            'name': '',
            'price': '199.99',
            'description': 'Test description',
            'count': 15
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            'name': 'Test Product',
            'price': 'invalid_price',
            'description': 'Test description',
            'count': 15
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_description_too_long_bad_request(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('products-list')
        data = {
            'name': 'Test Product',
            'price': '199.99',
            'description': 'a' * 5001,
            'count': 15
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_product_admin_user_success(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('products-detail', kwargs={'pk': self.product1.pk})
        data = {
            'name': 'Updated Product',
            'price': '299.99',
            'description': 'Updated description',
            'count': 20,
            'category_ids': [self.category2.id]
        }
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Product')
        updated_product = Product.objects.get(pk=self.product1.pk)
        self.assertEqual(updated_product.name, 'Updated Product')

    def test_partial_update_product_admin_user_success(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('products-detail', kwargs={'pk': self.product1.pk})
        data = {
            'price': '399.99'
        }
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['price']), 399.99)

    def test_update_product_regular_user_forbidden(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('products-detail', kwargs={'pk': self.product1.pk})
        data = {
            'name': 'Updated Product',
            'price': '299.99'
        }
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_nonexistent_product_not_found(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('products-detail', kwargs={'pk': 9999})
        data = {
            'name': 'Updated Product',
            'price': '299.99'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_product_admin_user_success(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('products-detail', kwargs={'pk': self.product1.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(pk=self.product1.pk).exists())

    def test_delete_product_regular_user_forbidden(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('products-detail', kwargs={'pk': self.product1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_nonexistent_product_not_found(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('products-detail', kwargs={'pk': 9999})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CategoryAPITestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            email='admin@gmail.com',
            password='adminpass123',
            is_staff=True
        )

        self.regular_user = User.objects.create_user(
            email='regularuser@gmail.com',
            password='userpass123'
        )

        self.category = Category.objects.create(name="Test Category")

    def test_get_categories_list_authenticated_success(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('category-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_category_admin_success(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('category-list')
        data = {'name': 'New Category'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Category')

    def test_create_category_regular_user_forbidden(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('category-list')
        data = {'name': 'New Category'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_category_admin_success(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('category-detail', kwargs={'pk': self.category.pk})
        data = {'name': 'Updated Category'}
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Category')

    def test_delete_category_admin_success(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('category-detail', kwargs={'pk': self.category.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
