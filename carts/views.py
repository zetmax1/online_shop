from rest_framework import viewsets

from carts.models import Cart
from carts.permissions import IsOwnerOrAdmin
from carts.serializers import CartSerializer


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(user=self.request.user)

    def get_permissions(self):
        return [permission() for permission in self.permission_classes]


