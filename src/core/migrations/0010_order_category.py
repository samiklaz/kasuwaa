# Generated by Django 2.2.8 on 2021-04-17 19:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20210417_1147'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Category'),
        ),
    ]
