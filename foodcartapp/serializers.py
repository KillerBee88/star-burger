from django.db import transaction
from rest_framework import serializers

from .models import Order, OrderItem, Product


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    products = OrderItemSerializer(
        many=True,
        allow_empty=False,
        write_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id',
            'products',
            'firstname',
            'lastname',
            'phonenumber',
            'address'
        ]

    def validate_products(self, value):
        if not value:
            raise serializers.ValidationError("Products list cannot be empty")

        product_ids = [item['product'] for item in value]
        if len(product_ids) != len(set(product_ids)):
            raise serializers.ValidationError(
                "Duplicate products are not allowed")

        if not Product.objects.filter(id__in=product_ids).exists():
            raise serializers.ValidationError(
                "One or more products do not exist")

        return value

    def create(self, validated_data):
        products_data = validated_data.pop('products')

        try:
            with transaction.atomic():
                order = Order.objects.create(**validated_data)
                for product_data in products_data:
                    product = Product.objects.get(pk=product_data['product'])
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=product_data['quantity'],
                        price=product.price
                    )
                return order
        except Exception as e:
            raise serializers.ValidationError(f"Order creation failed: {e}")
