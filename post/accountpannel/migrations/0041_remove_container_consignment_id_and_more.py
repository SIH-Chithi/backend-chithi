# Generated by Django 5.1.3 on 2024-11-27 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accountpannel', '0040_alter_container_going_to'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='container',
            name='consignment_id',
        ),
        migrations.AddField(
            model_name='container',
            name='consignments',
            field=models.ManyToManyField(related_name='containers', to='accountpannel.consignment'),
        ),
    ]
