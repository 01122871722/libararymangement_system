# Generated by Django 4.2.16 on 2024-10-03 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lms_app', '0002_rename_rental_peroid_book_rental_period'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='totale_rental',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
    ]
