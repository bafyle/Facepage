# Generated by Django 3.2.8 on 2021-10-29 20:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_newaccountactivationlinks'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newaccountactivationlinks',
            name='link',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]