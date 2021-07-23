# Generated by Django 3.2.5 on 2021-07-23 15:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_like'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(default='', upload_to=''),
        ),
        migrations.AddField(
            model_name='post',
            name='original_post',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='posts.post'),
        ),
        migrations.AddField(
            model_name='post',
            name='shared_post',
            field=models.BooleanField(default=False),
        ),
    ]
