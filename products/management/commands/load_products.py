import csv
from django.core.management.base import BaseCommand
from products.models import Product

class Command(BaseCommand):
    help = 'Load products from products_data.csv'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', nargs='?', default='products_data.csv')

    def handle(self, *args, **options):
        path = options['csv_path']
        Product.objects.all().delete()
        count = 0
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            batch = []
            for row in reader:
                batch.append(Product(
                    id=int(row['id']),
                    product_name=row['product_name'],
                    product_description=row['product_description'],
                    category=row['category'],
                    tags=row['tags'],
                ))
                count += 1
                if len(batch) >= 200:
                    Product.objects.bulk_create(batch)
                    batch = []
            if batch:
                Product.objects.bulk_create(batch)
        self.stdout.write(self.style.SUCCESS(f'Loaded {count} products.'))
