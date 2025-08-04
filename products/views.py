from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from products.filters import ProductFilter
from products.models import Category, Product, ProductCategory, ProductImage
from products.pagination import CustomPagination
from products.permissions import IsAdminUser, IsAdminUserOrReadOnly
from products.serializers import (CategorySerializer,
                                  ProductCategorySerializer,
                                  ProductImageSerializer, ProductSerializer)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    pagination_class = CustomPagination
    filterset_class = ProductFilter
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )

    # def create(self, request, *args, ** kwargs):
    #     if not (request.user.is_staff or request.user.is_superuser):
    #         return Response({"detail": "You do not have permission to perform this action."},
    #                         status=status.HTTP_403_FORBIDDEN)
    #     return super().create(request, *args, **kwargs)
    #
    #
    # def update(self, request, *args, **kwargs):
    #     if not (request.user.is_staff or request.user.is_superuser):
    #         return Response({"detail": "You do not have permission to perform this action."},
    #                         status=status.HTTP_403_FORBIDDEN)
    #     return super().update(request, *args, **kwargs)
    #
    # def partial_update(self, request, *args, **kwargs):
    #     if not (request.user.is_staff or request.user.is_superuser):
    #         return Response({"detail": "You do not have permission to perform this action."},)
    #
    #     return super().partial_update(request, *args, **kwargs)
    #
    # def destroy(self, request, *args, **kwargs):
    #     if not (request.user.is_staff or request.user.is_superuser):
    #         return Response({"detail": "You do not have permission to perform this action."},
    #                         status=status.HTTP_403_FORBIDDEN)
    #     return super().destroy(request, *args, **kwargs)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUserOrReadOnly]
    pagination_class = CustomPagination


class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [IsAdminUserOrReadOnly]
    pagination_class = CustomPagination


