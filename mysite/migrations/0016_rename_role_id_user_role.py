# Generated by Django 4.2.5 on 2023-10-03 09:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mysite', '0015_rename_city_id_address_city_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='role_id',
            new_name='role',
        ),
    ]