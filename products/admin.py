from django.contrib import admin

from products.models import Category, Product, ProductCategory, ProductImage


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price',)
    search_fields = ('name', 'description')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class ProductPhotoAdmin(admin.ModelAdmin):
    list_display = ('product', 'image',)
    search_fields = ('product',)


class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'category',)


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(ProductImage, ProductPhotoAdmin)
admin.site.register(Category, CategoryAdmin)
