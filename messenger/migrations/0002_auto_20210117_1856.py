# Generated by Django 3.1.5 on 2021-01-17 16:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('messenger', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='messgage_content',
            new_name='message_content',
        ),
    ]
