from rest_framework import serializers
from .models import Order, OrderItem, Product

class OrderItemSerializer(serializers.Serializer):
    product = serializers.IntegerField()
    quantity = serializers.IntegerField()

class OrderSerializer(serializers.Serializer):
    firstname = serializers.CharField(max_length=100)
    lastname = serializers.CharField(max_length=100)
    phonenumber = serializers.RegexField(regex=r'^\+79\d{9}$')
    address = serializers.CharField(max_length=255)
    products = OrderItemSerializer(many=True)

    def validate_products(self, value):
        if not value:
            raise serializers.ValidationError("Products list cannot be empty")

        product_ids = [item['product'] for item in value]
        if len(product_ids) != len(set(product_ids)):
            raise serializers.ValidationError("Duplicate products are not allowed")
        
        if not Product.objects.filter(id__in=product_ids).exists():
            raise serializers.ValidationError("One or more products do not exist")

        return value

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        order = Order.objects.create(**validated_data)
        for product_data in products_data:
            product = Product.objects.get(pk=product_data['product'])
            OrderItem.objects.create(
                order=order,
                product_name=product.name,
                quantity=product_data['quantity'],
                price=product.price
            )
        return order