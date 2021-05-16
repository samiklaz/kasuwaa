from django.urls import path
from .views import *

app_name = 'core'
urlpatterns = [
    path('order-summary/', OrderSummaryView.as_view(), name="order_summary"),
    path('', product, name='product'),
    path('category/<slug>/', category, name='category'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('add-to-cart/<slug>/', add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<slug>/', remove_from_cart, name='remove_from_cart'),
    path('remove_single_item_from_cart/<slug>/', remove_single_item_from_cart, name='remove_single_item_from_cart'),
    path('payment/', PaymentView.as_view(), name='payment'),
    path('add_coupon/', AddCouponView.as_view(), name='add_coupon'),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund')
]
