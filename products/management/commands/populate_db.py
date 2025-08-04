import io
import random

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from faker import Faker
from PIL import Image

from products.models import Category, Product, ProductCategory, ProductImage

fake = Faker()

class Command(BaseCommand):
    help = 'Populates the database with fake product data'

    def handle(self, *args, **kwargs):
        self.create_categories(10)
        self.create_products(20)

    def create_categories(self, count):
        for _ in range(count):
            Category.objects.create(name=fake.unique.word().capitalize())

        self.stdout.write(self.style.SUCCESS(f'{count} categories created'))

    def create_products(self, count):
        categories = list(Category.objects.all())

        for _ in range(count):
            product = Product.objects.create(
                name=fake.unique.word().capitalize(),
                price=round(random.uniform(10, 1000), 2),
                description=fake.text(max_nb_chars=500),
                count=random.randint(1, 20)
            )

            assigned_categories = random.sample(categories, random.randint(1, 3))
            for category in assigned_categories:
                ProductCategory.objects.create(product=product, category=category)

            for _ in range(random.randint(1, 3)):
                image_file = self.generate_fake_image()
                ProductImage.objects.create(product=product, image=image_file)

        self.stdout.write(self.style.SUCCESS(f'{count} products created with images and categories'))

    def generate_fake_image(self):

        image = Image.new('RGB', (300, 300), color=(random.randint(0,255), random.randint(0,255), random.randint(0,255)))
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG')
        return ContentFile(buffer.getvalue(), name=fake.slug() + '.jpg')
