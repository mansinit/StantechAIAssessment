from django.db import models

# Create your models here.
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    quantity_sold = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)
    review_Count = models.IntegerField(default=0)

    def __str__(self):
        return self.product_name