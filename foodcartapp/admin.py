from django.contrib import admin
from django.shortcuts import redirect, reverse
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.http import url_has_allowed_host_and_scheme

from .models import (Order, OrderItem, Product, ProductCategory, Restaurant,
                     RestaurantMenuItem)


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly, so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category__name',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html('<img src="{url}" style="max-height: 200px;"/>', url=obj.image.url)
    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html('<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>', edit_url=edit_url, src=obj.image.url)
    get_image_list_preview.short_description = 'превью'


@admin.register(ProductCategory)
class ProductAdmin(admin.ModelAdmin):
    pass


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ['product', 'quantity', 'price', 'fixed_price']
    extra = 1


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'firstname', 'lastname',
                    'phonenumber', 'address', 'fixed_total_price', 'status', 'comments', 'call_date', 'delivery_date', 'payment_method', 'restaurant']
    search_fields = ['firstname', 'lastname',
                     'phonenumber', 'address', 'comments']
    list_filter = ['fixed_total_price', 'status', 'payment_method']
    readonly_fields = ('created_at',)
    inlines = [OrderItemInline]

    fieldsets = (
        (None, {
            'fields': ('firstname', 'lastname', 'phonenumber', 'address', 'status', 'comments', 'restaurant', 'fixed_total_price', 'payment_method')
        }),
    )

    def save_model(self, request, obj, form, change):
        if 'restaurant' in form.changed_data:
            obj.status = 'собирается'
        super().save_model(request, obj, form, change)

    def response_change(self, request, obj):
        next_url = request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            return redirect(next_url)
        return super().response_change(request, obj)

    def display_payment_method(self, obj):
        return obj.get_payment_method_display()

    display_payment_method.short_description = 'Способ оплаты'


admin.site.register(Order, OrderAdmin)
