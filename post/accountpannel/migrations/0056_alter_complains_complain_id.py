# Generated by Django 5.1.3 on 2024-12-07 21:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accountpannel', '0055_alter_consignment_consignment_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='complains',
            name='complain_id',
            field=models.CharField(editable=False, max_length=12, primary_key=True, serialize=False),
        ),
    ]
