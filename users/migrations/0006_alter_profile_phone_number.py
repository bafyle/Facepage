# Generated by Django 3.2.5 on 2021-10-16 13:35

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_profile_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='phone_number',
            field=models.CharField(blank=True, default='', max_length=50, validators=[django.core.validators.RegexValidator('/01[0125][0-9]{8}$/g', 'only valid phone numbers are required')]),
        ),
    ]