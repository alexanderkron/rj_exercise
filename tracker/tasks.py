# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task

from .models import Cart, Item


@shared_task
def add_item_to_cart(cart_id, product_id, name=None, price=None):
    cart, _created = Cart.objects.get_or_create(pk=cart_id)

    if Item.objects.filter(cart_id=cart.id, product_id=product_id).exists():
        return

    Item.objects.create(
        cart_id=cart.id,
        product_id=product_id,
        name=name,
        price=price
    )
