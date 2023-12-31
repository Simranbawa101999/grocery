# Generated by Django 4.2.5 on 2023-10-09 11:17

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mysite', '0021_alter_user_email_alter_user_phone_no'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='salt',
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone_no',
            field=models.CharField(max_length=50, validators=[django.core.validators.RegexValidator('^\\d{10}$', message='Phone number must be exactly 10 digits.')]),
        ),
    ]
