# Generated by Django 4.2.5 on 2023-10-10 05:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mysite', '0023_alter_user_phone_no'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='datedeleted',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='dateupdate',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]