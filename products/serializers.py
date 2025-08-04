from rest_framework import serializers

from products.models import Category, Product, ProductCategory, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')
        extra_kwargs = {
            "id": {"read_only": True},
        }


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'product')
        extra_kwargs = {
            "id": {"read_only": True},
            "image": {"write_only": True},
        }


class ProductCategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = ProductCategory
        fields = ('id', 'product', 'category')
        extra_kwargs = {
            "id": {"read_only": True},
        }


class ProductSerializer(serializers.ModelSerializer):
    product_images = ProductImageSerializer(source='images', many=True, read_only=True)
    category_names = serializers.SerializerMethodField()
    category_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.all(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'description', 'product_images', 'category_names', 'category_ids')
        extra_kwargs = {
            "id": {"read_only": True},
        }

    def get_category_names(self, obj):
        categories = Category.objects.filter(product_categories__product=obj)
        return CategorySerializer(categories, many=True).data

    def update(self, instance, validated_data):
        category_ids = validated_data.pop('category_ids', None)
        instance = super().update(instance, validated_data)

        if category_ids is not None:

            ProductCategory.objects.filter(product=instance).delete()
            for category in category_ids:
                ProductCategory.objects.create(product=instance, category=category)

        return instance

