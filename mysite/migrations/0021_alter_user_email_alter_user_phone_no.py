# Generated by Django 4.2.5 on 2023-10-09 10:55

from django.db import migrations, models
import mysite.models


class Migration(migrations.Migration):

    dependencies = [
        ('mysite', '0020_alter_user_email_alter_user_phone_no'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.CharField(max_length=50, unique=True, validators=[mysite.models.User.is_valid_email]),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone_no',
            field=models.CharField(max_length=50, validators=[mysite.models.User.is_valid_phone_number]),
        ),
    ]