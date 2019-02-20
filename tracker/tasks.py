# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task

from .models import Cart, Item


@shared_task
def add_item_to_cart(cart_id, product_id, name=None, price=None):
    cart, _created = Cart.objects.get_or_create(pk=cart_id)

    try:
        item = Item.objects.get(cart_id=cart.id, product_id=product_id)
    except Item.DoesNotExist:
        Item.objects.create(
            cart_id=cart.id,
            product_id=product_id,
            name=name,
            price=price
        )
        return

    if item.name != name or item.price != price:
        Item.objects.filter(
            cart_id=cart.id, product_id=product_id
        ).update(name=name, price=price)
