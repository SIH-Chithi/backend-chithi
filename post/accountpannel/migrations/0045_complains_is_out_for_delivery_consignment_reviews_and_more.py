# Generated by Django 5.1.3 on 2024-11-30 18:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accountpannel', '0044_container_journey'),
    ]

    operations = [
        migrations.AddField(
            model_name='complains',
            name='is_out_for_delivery',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='consignment_reviews',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.FloatField()),
                ('consignment_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='accountpannel.consignment')),
            ],
        ),
        migrations.CreateModel(
            name='container_qr',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('barcode_url', models.URLField()),
                ('qr_url', models.URLField()),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('created_by_id', models.CharField(max_length=50)),
                ('container_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='accountpannel.container')),
            ],
        ),
    ]
