# Generated by Django 3.2.15 on 2024-05-24 08:09

from decimal import Decimal
import django.core.validators
from django.db import migrations, models

def set_fixed_price_for_existing_order_items(apps, schema_editor):
    OrderItem = apps.get_model('foodcartapp', 'OrderItem')
    for item in OrderItem.objects.all():
        item.fixed_price = item.price
        item.save()

class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0039_rename_product_name_orderitem_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='fixed_total_price',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='зафиксированная стоимость'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='fixed_price',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))]),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))]),
        ),
        migrations.RunPython(set_fixed_price_for_existing_order_items),
    ]
