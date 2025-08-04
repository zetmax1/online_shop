from django.core.validators import MaxLengthValidator
from django.db import models

from shared.models import BaseModel


class Product(BaseModel):
    name = models.CharField(max_length=150, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(validators=[MaxLengthValidator(5000)])
    count = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'products'
        verbose_name = 'product'
        verbose_name_plural = 'products'

class ProductImage(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"{self.product.name}'s image"

    class Meta:

        db_table = 'product_images'
        verbose_name = 'product image'
        verbose_name_plural = 'product images'


class Category(BaseModel):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'categories'
        verbose_name = 'category'
        verbose_name_plural = 'categories'


class ProductCategory(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_categories')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='product_categories')

    def __str__(self):
        return f"{self.category.name}'s products"

    class Meta:
        db_table = 'product_categories'
        verbose_name = 'product category'
        verbose_name_plural = 'product categories'
