# Generated by Django 3.2.15 on 2024-05-08 11:02

from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0037_auto_20210125_1833'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstname', models.CharField(max_length=100, verbose_name='имя')),
                ('lastname', models.CharField(max_length=100, verbose_name='фамилия')),
                ('phonenumber', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None, verbose_name='номер телефона')),
                ('address', models.CharField(max_length=255, verbose_name='адрес')),
            ],
            options={
                'verbose_name': 'заказ',
                'verbose_name_plural': 'заказы',
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=100, verbose_name='название продукта')),
                ('quantity', models.PositiveIntegerField(verbose_name='количество')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='цена')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='foodcartapp.order', verbose_name='заказ')),
            ],
            options={
                'verbose_name': 'позиция заказа',
                'verbose_name_plural': 'позиции заказов',
            },
        ),
    ]