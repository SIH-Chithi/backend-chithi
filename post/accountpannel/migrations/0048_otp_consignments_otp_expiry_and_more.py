# Generated by Django 5.1.3 on 2024-12-04 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accountpannel', '0047_alter_consignment_journey_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='otp_consignments',
            name='otp_expiry',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='otp_consignments',
            name='otp',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
    ]
