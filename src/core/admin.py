from django.contrib import admin
from .models import *


class ItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'category', 'quantity_type']


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'item', 'quantity', 'ordered']


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'ordered', 'delivered', 'received', 'refund_requested', 'refund_granted']
    list_filter = ['user', 'ordered', 'delivered', 'received', 'refund_requested', 'refund_granted']
    search_fields = ['user__username', 'ref_code']


class BillingAddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'street_address', 'apartment_address', 'country']


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'stripe_charge_id']


admin.site.register(Item, ItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Category)
admin.site.register(BillingAddress, BillingAddressAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Coupon)



