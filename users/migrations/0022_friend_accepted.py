# Generated by Django 3.2.5 on 2021-08-07 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0021_friend'),
    ]

    operations = [
        migrations.AddField(
            model_name='friend',
            name='accepted',
            field=models.BooleanField(default=False),
        ),
    ]
