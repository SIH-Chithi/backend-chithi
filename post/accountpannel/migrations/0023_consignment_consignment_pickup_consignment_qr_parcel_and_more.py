# Generated by Django 5.1.3 on 2024-11-23 17:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accountpannel', '0022_remove_consignment_qr_consignment_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='consignment',
            fields=[
                ('consignment_id', models.AutoField(primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[('Document', 'Document'), ('Parcel', 'Parcel')], max_length=50)),
                ('created_place', models.CharField(max_length=10)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('created_time', models.TimeField(auto_now_add=True)),
                ('Amount', models.FloatField()),
                ('is_pickup', models.BooleanField(default=False)),
                ('is_payed', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='consignment_pickup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pickup_date', models.DateTimeField()),
                ('pickup_time', models.TimeField()),
                ('pickup_amount', models.FloatField()),
                ('pickup_status', models.BooleanField(default=False)),
                ('consignment_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accountpannel.consignment')),
            ],
        ),
        migrations.CreateModel(
            name='consignment_qr',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('barcode_url', models.URLField()),
                ('qr_url', models.URLField()),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.CharField(max_length=50)),
                ('created_by_id', models.CharField(max_length=50)),
                ('consignment_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='accountpannel.consignment')),
            ],
        ),
        migrations.CreateModel(
            name='parcel',
            fields=[
                ('parcel_id', models.AutoField(primary_key=True, serialize=False)),
                ('weight', models.FloatField()),
                ('length', models.FloatField()),
                ('breadth', models.FloatField()),
                ('height', models.FloatField()),
                ('price', models.FloatField()),
                ('consignment_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='accountpannel.consignment')),
            ],
        ),
        migrations.CreateModel(
            name='receiver_details',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('pincode', models.IntegerField()),
                ('address', models.TextField()),
                ('city_district', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=50)),
                ('country', models.CharField(max_length=50)),
                ('phone_number', models.CharField(max_length=10)),
                ('consignment_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accountpannel.consignment')),
            ],
        ),
        migrations.CreateModel(
            name='senders_details',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('pincode', models.IntegerField()),
                ('address', models.TextField()),
                ('city_district', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=50)),
                ('country', models.CharField(max_length=50)),
                ('phone_number', models.CharField(max_length=10)),
                ('consignment_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accountpannel.consignment')),
            ],
        ),
    ]
