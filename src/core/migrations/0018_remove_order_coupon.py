# Generated by Django 2.2.8 on 2021-04-23 19:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_coupon_amount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='coupon',
        ),
    ]
