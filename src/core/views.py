from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.base import View
from .models import *
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckoutForm, RefundForm
import random
import string


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def product(request):
    items = Item.objects.all().exclude(quantity_type='Bags')[0:4]
    item_secondList = Item.objects.all()[4:12]
    items_bags = Item.objects.filter(quantity_type='Bags')[0:4]
    items_beverages = Item.objects.filter(category__name='Beverages')[0:4]
    items_rubber = Item.objects.filter(category__name='Rubber')[0:4]
    items_bottle = Item.objects.filter(category__name='Bottle')[0:4]
    context = {
        'items': items,
        'item_secondList': item_secondList,
        # for the footer menu
        'items_bags': items_bags,
        'items_beverages': items_beverages,
        'items_rubber': items_rubber,
        'items_bottle': items_bottle,
    }
    return render(request, "core/product.html", context)


def category(request, slug):
    query = get_object_or_404(Category, slug=slug)
    result = query.item_set.all()
    context = {
        'result': result,
        'category': Category.objects.all(),
        'category_qs': query.item_set.all()[0:4],
        'products_in_category': query.item_set.all(),
    }

    return render(request, 'core/categories.html', context)


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(item=item, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # checking if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order_summary")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart")
            return redirect("core:product")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info("This item was created and added to your cart")
        return redirect("core:product")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the item
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False).first()
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "The item was removed from the cart")
            return redirect("core:product")
        else:
            # add a message showing that the user doesn't have the order
            messages.info(request, "The item was not in your cart")
            return redirect("core:order_summary")
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product")


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the item
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False).first()

            if order_item.quantity > 1:
                order_item.quantity -= 1
            else:
                order.items.remove(order_item)
                order_item.delete()
            order_item.save()
            messages.info(request, "The item quantity was updated")
            return redirect("core:order_summary")
        else:
            # add a message showing that the user doesn't have the order
            messages.info(request, "The item was not in your cart")
            return redirect("core:order_summary")
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:order_summary")


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order,
            }
            return render(self.request, 'core/cart.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect('/')


class CheckoutView(View):

    def get(self, *args, **kwargs):
        form = CheckoutForm()
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            "form": form,
            "order": order,
        }
        return render(self.request, "core/checkout.html", context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                print(form.cleaned_data)
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                # same_shipping_address = form.cleaned_data.get('same_shipping_address')
                # save_info = form.cleaned_data.get('save_info')

                billing_address, created = BillingAddress.objects.get_or_create(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                # Add a redirect to the selected payment option
            else:
                messages.warning(self.request, "Failed Checkout")
            return redirect('core:payment')
        except ObjectDoesNotExist:
            messages.error(self.request, "You don't have an active order")
            redirect("core:order_summary")


class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'order': order,
        }
        return render(self.request, 'core/payment.html', context)

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        return redirect('')


class AddCouponView(View):

    def post(self, *args, **kwargs):
        code = self.request.POST.get('code')
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            coupon = coupon = Coupon.objects.get(code=code)
            order.coupons = coupon
            order.save()
            messages.success(self.request, "Successfully added Coupon")
            return redirect("core:order_summary")
        except ObjectDoesNotExist:
            messages.info(self.request, "Coupon does not exist")
            return redirect("core:order_summary")

        return redirect("core:order_summary")


def add_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        try:
            order = Order.objects.get(user=request.user, ordered=False)
            coupon = coupon = Coupon.objects.get(code=code)
            order.coupons = coupon
            order.save()
            messages.success(request, "Successfully added Coupon")
            return redirect("core:order_summary")
        except ObjectDoesNotExist:
            messages.info(request, "Coupon does not exist")
            return redirect("core:order_summary")
    return redirect("core:order_summary")


class RequestRefundView(View):

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()
                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()
                messages.info(self.request, "Your request was received")
                return redirect('core:request-refund')
            except ObjectDoesNotExist:
                messages.info(self.request, "This Order does not exist")
                return redirect('core:request-refund')