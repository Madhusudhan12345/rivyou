from django.db import models

class Product(models.Model):
    product_name = models.CharField(max_length=255, db_index=True)
    product_description = models.TextField()
    category = models.CharField(max_length=100, db_index=True)
    tags = models.CharField(max_length=500)  # comma-separated

    class Meta:
        indexes = [
            models.Index(fields=['category']),
        ]

    def tags_list(self):
        return [t.strip().lower() for t in self.tags.split(',') if t.strip()]

    def __str__(self):
        return self.product_name
