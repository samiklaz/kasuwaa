# Generated by Django 2.2.8 on 2021-04-17 19:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_category_slug'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='items',
            new_name='item',
        ),
    ]