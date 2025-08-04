from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from accounts.models import CustomUser
from orders.models import Order, OrderItem
from products.models import Product


class TestOrderViewSet(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = CustomUser.objects.create_user(
            email='user@gmail.com',
            password='testpass123'
        )
        self.admin_user = CustomUser.objects.create_superuser(
            email='admin@gmail.com',
            password='adminpass123'
        )
        self.other_user = CustomUser.objects.create_user(
            email='other@gmail.com',
            password='otherpass123'
        )

        self.product = Product.objects.create(
            name='Test Product',
            price=10.00,
            description='Test description'
        )

        self.order = Order.objects.create(user=self.user)
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2
        )

        self.order_list_url = reverse('orders-list')
        self.order_detail_url = lambda pk: reverse('orders-detail', kwargs={'pk': pk})

    def test_unauthorized_access(self):
        response = self.client.get(self.order_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "order_items": [
                {"product": self.product.id, "quantity": 3}
            ]
        }
        response = self.client.post(self.order_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.filter(user=self.user).count(), 2)

    def test_list_own_orders(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.order_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_own_order(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.order_detail_url(self.order.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_retrieve_others_order(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.order_detail_url(self.order.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_see_all_orders(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.order_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), Order.objects.count())

    def test_user_can_delete_own_order(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.order_detail_url(self.order.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(pk=self.order.pk).exists())

    def test_user_cannot_delete_others_order(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.order_detail_url(self.order.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_delete_any_order(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.order_detail_url(self.order.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(pk=self.order.pk).exists())
