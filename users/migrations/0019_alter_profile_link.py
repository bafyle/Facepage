# Generated by Django 3.2.5 on 2021-07-17 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_alter_profile_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='link',
            field=models.SlugField(blank=True, max_length=100, unique=True),
        ),
    ]