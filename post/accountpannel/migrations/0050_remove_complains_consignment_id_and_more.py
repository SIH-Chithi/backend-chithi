# Generated by Django 5.1.3 on 2024-12-05 14:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accountpannel', '0049_complain_journey'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='complains',
            name='consignment_id',
        ),
        migrations.RemoveField(
            model_name='complains',
            name='user',
        ),
        migrations.DeleteModel(
            name='complain_journey',
        ),
        migrations.DeleteModel(
            name='complains',
        ),
    ]
