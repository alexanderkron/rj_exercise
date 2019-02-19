import uuid

from django.db import models


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)


class Item(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)

    product_id = models.TextField()
    name = models.TextField(null=True)
    price = models.IntegerField(null=True)

    class Meta:
        unique_together = (('cart', 'product_id'),)
