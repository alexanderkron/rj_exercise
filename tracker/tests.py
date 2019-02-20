import uuid
from mock import patch
from django.http.cookie import SimpleCookie
from django.test import TestCase
from django.test.utils import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from .tasks import add_item_to_cart
from .models import Cart, Item

PRODUCT_ID = 'prodid'
NAME = 'pants'
PRICE = 50

COOKIE_CART_ID = uuid.uuid4()
BODY_CART_ID = uuid.uuid4()
GENERATED_CART_ID = uuid.uuid4()


class ItemsTest(APITestCase):

    URL = '/items/'

    def test_product_id_is_required(self):
        data = {}
        response = self.client.post(self.URL, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['error'], 'missing parameter: product_id'
        )

    @patch('tracker.tasks.add_item_to_cart.delay')
    def test_cookie_cart_id_is_used(self, add_item_to_cart):
        self.client.cookies = SimpleCookie({'cart_id': COOKIE_CART_ID})
        data = {
            'product_id': PRODUCT_ID,
            'name': NAME,
            'price': PRICE
        }
        self.client.post(self.URL, data, format='json')

        add_item_to_cart.assert_called_with(
            COOKIE_CART_ID, PRODUCT_ID, NAME, PRICE
        )

    @patch('tracker.tasks.add_item_to_cart.delay')
    def test_cookie_cart_id_is_preferred_over_body(self, add_item_to_cart):
        self.client.cookies = SimpleCookie({'cart_id': COOKIE_CART_ID})
        data = {
            'cart_id': BODY_CART_ID,
            'product_id': PRODUCT_ID,
            'name': NAME,
            'price': PRICE
        }
        self.client.post(self.URL, data, format='json')

        add_item_to_cart.assert_called_with(
            COOKIE_CART_ID, PRODUCT_ID, NAME, PRICE
        )

    @patch('tracker.tasks.add_item_to_cart.delay')
    def test_body_cart_id_is_used_when_cookie_absent(self, add_item_to_cart):
        data = {
            'cart_id': BODY_CART_ID,
            'product_id': PRODUCT_ID,
            'name': NAME,
            'price': PRICE
        }
        self.client.post(self.URL, data, format='json')

        add_item_to_cart.assert_called_with(
            BODY_CART_ID, PRODUCT_ID, NAME, PRICE
        )

    @patch('tracker.tasks.add_item_to_cart.delay')
    @patch('uuid.uuid4')
    def test_cart_id_is_generated_when_missing(self, uuid4, add_item_to_cart):
        uuid4.return_value = GENERATED_CART_ID
        data = {
            'product_id': PRODUCT_ID,
            'name': NAME,
            'price': PRICE
        }
        self.client.post(self.URL, data, format='json')
        add_item_to_cart.assert_called_with(
            GENERATED_CART_ID, PRODUCT_ID, NAME, PRICE
        )

    def test_sets_cart_id_cookie(self):
        data = {
            'cart_id': BODY_CART_ID,
            'product_id': PRODUCT_ID,
            'name': NAME,
            'price': PRICE
        }
        self.client.post(self.URL, data, format='json')
        self.assertEqual(
            self.client.cookies['cart_id'].value, str(BODY_CART_ID)
        )

    def test_responds_with_cart_id(self):
        data = {
            'cart_id': BODY_CART_ID,
            'product_id': PRODUCT_ID,
            'name': NAME,
            'price': PRICE
        }
        response = self.client.post(self.URL, data, format='json')
        self.assertEqual(response.data['cart_id'], BODY_CART_ID)


class TasksTest(TestCase):
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_add_item_to_cart_creates_cart_if_necessary(self):
        add_item_to_cart.delay(
            GENERATED_CART_ID, PRODUCT_ID, NAME, PRICE
        ).get()
        cart = Cart.objects.get(pk=GENERATED_CART_ID)
        self.assertIsNotNone(cart)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_add_item_to_cart_finds_existing_cart(self):
        cart = Cart.objects.create(pk=GENERATED_CART_ID)
        add_item_to_cart.delay(
            GENERATED_CART_ID, PRODUCT_ID, NAME, PRICE
        ).get()
        cart = Cart.objects.get(pk=GENERATED_CART_ID)
        self.assertIsNotNone(cart)

        carts = Cart.objects.all()
        self.assertEqual(carts.count(), 1)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_add_item_to_cart_persists_item(self):
        cart = Cart.objects.create()
        add_item_to_cart.delay(
            cart.id, PRODUCT_ID, NAME, PRICE
        ).get()
        item = cart.items.get(product_id=PRODUCT_ID)
        self.assertIsNotNone(item)
        self.assertEqual(item.product_id, PRODUCT_ID)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_add_item_to_cart_updates_attributes_for_existing_keys(self):
        cart = Cart.objects.create()
        Item.objects.create(
            cart_id=cart.id,
            product_id=PRODUCT_ID,
            name=NAME,
            price=PRICE
        )
        self.assertEqual(cart.items.all().count(), 1)

        updated_name = 'shirt'
        updated_price = 20
        add_item_to_cart.delay(
            cart.id, PRODUCT_ID, updated_name, updated_price
        ).get()

        items = Item.objects.all()
        self.assertEqual(items.count(), 1)

        self.assertEqual(items[0].name, updated_name)
        self.assertEqual(items[0].price, updated_price)
