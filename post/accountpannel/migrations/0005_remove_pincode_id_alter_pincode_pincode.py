# Generated by Django 5.1.3 on 2024-11-21 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accountpannel', '0004_pincode'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pincode',
            name='id',
        ),
        migrations.AlterField(
            model_name='pincode',
            name='pincode',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
