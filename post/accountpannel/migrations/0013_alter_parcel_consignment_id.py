# Generated by Django 5.1.3 on 2024-11-22 19:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accountpannel', '0012_consignment_consignment_pickup_consignment_qr_parcel_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parcel',
            name='consignment_id',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='accountpannel.consignment'),
        ),
    ]
