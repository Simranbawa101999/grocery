# Generated by Django 4.2.5 on 2023-10-02 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mysite', '0004_alter_product_price_alter_product_stock_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productcategory',
            name='createdby',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='productcategory',
            name='datedeleted',
            field=models.DateTimeField(null=True),
        ),
    ]
