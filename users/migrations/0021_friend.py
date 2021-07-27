# Generated by Django 3.2.5 on 2021-07-27 13:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0020_alter_profile_profile_cover'),
    ]

    operations = [
        migrations.CreateModel(
            name='Friend',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('side1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Side1', to=settings.AUTH_USER_MODEL)),
                ('side2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Side2', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('side1', 'side2')},
            },
        ),
    ]
