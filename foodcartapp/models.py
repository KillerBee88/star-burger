from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Sum
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class Order(models.Model):
    ACCEPTED = 'accepted'
    IN_PROCESS = 'in_process'
    IN_DELIVERY = 'in_delivery'
    RECEIVED = 'received'

    STATUSES = [
        (ACCEPTED, 'Принят'),
        (IN_PROCESS, 'Собирается'),
        (IN_DELIVERY, 'В пути'),
        (RECEIVED, 'Получен'),
    ]

    firstname = models.CharField('имя', max_length=100)
    lastname = models.CharField('фамилия', max_length=100)
    phonenumber = PhoneNumberField('номер телефона')
    address = models.CharField('адрес', max_length=255)
    fixed_total_price = models.DecimalField(
        'зафиксированная стоимость',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00')
    )
    status = models.CharField(max_length=20, choices=STATUSES, default=ACCEPTED, db_index=True)

    _price_updated = False

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f"{self.firstname} {self.lastname}"

    def calculate_total_price(self):
        return self.items.aggregate(
            total=Sum(F('fixed_price') * F('quantity'))
        )['total'] or Decimal('0.00')

    def update_total_price(self):
        self.fixed_total_price = self.calculate_total_price()
        self._price_updated = True
        self.save(update_fields=['fixed_total_price'])

    def save(self, *args, **kwargs):
        if not self._price_updated:
            super().save(*args, **kwargs)
            self.update_total_price()
        else:
            super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name='items', on_delete=models.CASCADE, verbose_name="заказ")
    product = models.CharField('название продукта', max_length=100)
    quantity = models.PositiveIntegerField('количество')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[
                                MinValueValidator(Decimal('0.00'))])
    fixed_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))], default=Decimal('0.00'))

    class Meta:
        verbose_name = 'позиция заказа'
        verbose_name_plural = 'позиции заказов'

    def __str__(self):
        return f"{self.product} x {self.quantity}"

    def save(self, *args, **kwargs):
        if not self.fixed_price or self.fixed_price == Decimal('0.00'):
            self.fixed_price = self.price
        super().save(*args, **kwargs)
        self.order.update_total_price()
