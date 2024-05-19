import json
import re
import logging

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

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


@api_view(['POST'])
def register_order(request):
    order_params = request.data

    print(json.dumps(order_params, indent=4, ensure_ascii=False))

    required_fields = ['firstname', 'lastname', 'phonenumber', 'address', 'products']

    for field in required_fields:
        if field not in order_params:
            return Response({"error": f"{field} is required"}, status=status.HTTP_400_BAD_REQUEST)

    if not isinstance(order_params['firstname'], str) or not order_params['firstname'].strip():
        return Response({"error": "Firstname must be a non-empty string"}, status=status.HTTP_400_BAD_REQUEST)
    if not isinstance(order_params['lastname'], str) or not order_params['lastname'].strip():
        return Response({"error": "Lastname must be a non-empty string"}, status=status.HTTP_400_BAD_REQUEST)
    if not isinstance(order_params['phonenumber'], str) or not order_params['phonenumber'].strip():
        return Response({"error": "Phonenumber must be a non-empty string"}, status=status.HTTP_400_BAD_REQUEST)
    if not isinstance(order_params['address'], str) or not order_params['address'].strip():
        return Response({"error": "Address must be a non-empty string"}, status=status.HTTP_400_BAD_REQUEST)
    if not isinstance(order_params['products'], list):
        return Response({"error": "Products must be a list"}, status=status.HTTP_400_BAD_REQUEST)
    
    phone_regex = re.compile(r'^\+79\d{9}$')
    if not phone_regex.match(order_params['phonenumber']):
        return Response({"error": "Phonenumber is invalid"}, status=status.HTTP_400_BAD_REQUEST)


    products = order_params['products']
    if not products:
        return Response({"error": "Products list cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)

    product_ids = []
    for product_item in products:
        if 'product' not in product_item or 'quantity' not in product_item:
            return Response({"error": "Each product item must contain 'product' and 'quantity' fields"}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(product_item['product'], int):
            return Response({"error": "Product ID must be an integer"}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(product_item['quantity'], int) or product_item['quantity'] <= 0:
            return Response({"error": "Quantity must be a positive integer"}, status=status.HTTP_400_BAD_REQUEST)
        product_ids.append(product_item['product'])

    if len(product_ids) != len(set(product_ids)):
        return Response({"error": "Duplicate products are not allowed"}, status=status.HTTP_400_BAD_REQUEST)

    if not Product.objects.filter(id__in=product_ids).exists():
        return Response({"error": "One or more products do not exist"}, status=status.HTTP_400_BAD_REQUEST)

    order = Order.objects.create(
        firstname=order_params['firstname'],
        lastname=order_params['lastname'],
        phonenumber=order_params['phonenumber'],
        address=order_params['address']
    )
    
    for product_item in products:
        product = Product.objects.get(pk=product_item['product'])
        OrderItem.objects.create(
            order=order,
            product_name=product.name,
            quantity=product_item['quantity'],
            price=product.price
        )
    
    return Response({"message": "Order created successfully", "order_id": order.id}, status=status.HTTP_201_CREATED)
