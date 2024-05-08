import json
import logging

from django.http import JsonResponse
from django.templatetags.static import static
from django.views.decorators.http import require_http_methods

from .models import Order, OrderItem, Product

logger = logging.getLogger(__name__)


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@require_http_methods(["POST"])
def register_order(request):
    data = json.loads(request.body.decode('utf-8'))

    order = Order.objects.create(
        firstname=data['firstname'],
        lastname=data['lastname'],
        phonenumber=data['phonenumber'],
        address=data['address']
    )

    for product_info in data['products']:
        product = Product.objects.get(pk=product_info['product'])
        OrderItem.objects.create(
            order=order,
            product_name=product.name,
            quantity=product_info['quantity'],
            price=product.price
        )

    return JsonResponse({"message": "Order created successfully"}, status=201)
