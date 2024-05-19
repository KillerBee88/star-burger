import json
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
            return Response({"error": f"Field '{field}' is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    product_list = order_params.get('products', [])
    if not isinstance(product_list, list) or not product_list:
        return Response({"error": "Field 'products' must be a non-empty list"}, status=status.HTTP_400_BAD_REQUEST)
    
    for product_item in product_list:
        if 'product' not in product_item or 'quantity' not in product_item:
            return Response({"error": "Each product must contain 'product' and 'quantity' fields"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product_id = int(product_item['product'])
            quantity = int(product_item['quantity'])
            if quantity <= 0:
                raise ValueError
        except ValueError:
            return Response({"error": "Product ID and quantity must be positive integers"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not Product.objects.filter(pk=product_id).exists():
            return Response({"error": f"Product with id {product_id} does not exist"}, status=status.HTTP_400_BAD_REQUEST)

    order = Order.objects.create(
        firstname=order_params['firstname'],
        lastname=order_params['lastname'],
        phonenumber=order_params['phonenumber'],
        address=order_params['address']
    )
    
    for product_item in product_list:
        product = Product.objects.get(pk=product_item['product'])
        OrderItem.objects.create(
            order=order,
            product_name=product.name,
            quantity=product_item['quantity'],
            price=product.price
        )
    
    return Response({"message": "Order created successfully", "order_id": order.id}, status=status.HTTP_201_CREATED)
