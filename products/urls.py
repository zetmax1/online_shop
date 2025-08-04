from django.urls import path
from rest_framework.routers import DefaultRouter

from products.views import (CategoryViewSet, ProductCategoryViewSet,
                            ProductViewSet)

router = DefaultRouter()

router.register('product-categories', ProductCategoryViewSet, basename='product-categories')
router.register('products', ProductViewSet, basename='products')
router.register('category', CategoryViewSet, basename='category')

urlpatterns = router.urls
