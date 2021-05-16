from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.shortcuts import reverse
from django_countries.fields import CountryField




CATEGORY_CHOICES = (
    ('Glocery', 'Glocery'),
    ('Beverages', 'Beverages'),
    ('Other Categories', 'Other Categories'),
)

QUANTITY = (
    ('Cups', 'Cups'),
    ('Bags', 'Bags'),
    ('Bottle', 'Bottle'),
    ('Rubber', 'Rubber'),
    ('undefined', 'undefined'),
)


def upload_location(instance, filename):
    file_path = 'product/{title}-{filename}'.format(
         title=str(instance.title), filename=filename)
    return file_path





class Category(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)

    def __str__(self):
        return self.name


def pre_save_cat_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.name)


pre_save.connect(pre_save_cat_post_receiver, sender=Category)


class Item(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=upload_location, null=True, blank=True)
    price = models.BigIntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    discount_price = models.BigIntegerField(blank=True, null=True)
    quantity_type = models.CharField(max_length=10, choices=QUANTITY, default='Cups')

    def __str__(self):
        return self.title

    class Meta:
        pass

    def get_absolute_url(self):
        return reverse("core:details", kwargs={'slug': self.slug})

    def get_add_to_cart_url(self):
        return reverse("core:add_to_cart", kwargs={'slug': self.slug})

    def get_remove_from_cart_url(self):
        return reverse("core:remove_from_cart", kwargs={'slug': self.slug})


@receiver(post_delete, sender=Item)
def submission_delete(sender, instance, **kwargs):
    instance.image.delete(False)


def pre_save_blog_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.title)


pre_save.connect(pre_save_blog_post_receiver, sender=Item)


class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    quantity = models.IntegerField(default=1)

    def get_total_item_price(self):
        return self.quantity * int(self.item.price)

    def get_total_item_discount_price(self):
        return self.quantity * int(self.item.discount_price)

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_item_discount_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_item_discount_price()
        else:
            return self.get_total_item_price()

    def __str__(self):
        return f"{self.quantity} quantity --- {self.item.title}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(blank=True, null=True)
    billing_address = models.ForeignKey('BillingAddress', on_delete=models.SET_NULL, null=True, blank=True)
    coupons = models.ForeignKey('Coupon', on_delete=models.SET_NULL, null=True, blank=True)
    ref_code = models.CharField(max_length=21, blank=True, null=True)
    ordered = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    '''
    1. Item added to the cart.
    2. Payment (Preprocessing, Processing, Packaging etc)
    3. Being delivered.
    4. Received.
    5. Refunds.
    '''

    def get_coupon(self):
        if self.coupons:
            return self.coupons.amount
        else:
            return None

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total

    def get_discount_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        total -= self.coupons.amount
        return total

    def __str__(self):
        return self.user.username


class BillingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)

    def __str__(self):
        return self.apartment_address


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.amount


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    reason = models.TextField()
    email = models.EmailField()

    def __str__(self):
        return self.reason