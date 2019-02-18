import uuid

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from .tasks import add_item_to_cart


class Items(APIView):
    def post(self, request, format=None):
        product_id, name, price = self._get_product_args()
        if product_id is None:
            return Response(
                data={'error': 'missing parameter: product_id'},
                status=HTTP_400_BAD_REQUEST
            )

        cart_id = self._get_cart_id()
        try:
            cart_id = uuid.UUID(cart_id, version=4)
        except (TypeError, ValueError):
            cart_id = uuid.uuid4()

        add_item_to_cart.delay(cart_id, product_id, name, price)

        # Store cart ID in cookie
        response = Response({'cart_id': cart_id})
        response.set_cookie('cart_id', cart_id)
        return response

    def _get_cart_id(self):
        cart_id = self.request.COOKIES.get('cart_id', None)
        if cart_id is not None:
            return cart_id
        return self.request.data.get('cart_id', None)

    def _get_product_args(self):
        product_id = self.request.data.get('product_id', None)
        name = self.request.data.get('name', None)
        price = self.request.data.get('price', None)
        return (product_id, name, price)
