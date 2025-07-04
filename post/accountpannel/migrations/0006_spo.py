# Generated by Django 5.1.3 on 2024-11-21 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accountpannel', '0005_remove_pincode_id_alter_pincode_pincode'),
    ]

    operations = [
        migrations.CreateModel(
            name='SPO',
            fields=[
                ('spo_id', models.AutoField(primary_key=True, serialize=False)),
                ('office_name', models.CharField(max_length=100)),
                ('divsion_name', models.CharField(max_length=50)),
                ('circle_name', models.CharField(max_length=50)),
                ('district_name', models.CharField(max_length=50)),
                ('state_name', models.CharField(max_length=50)),
                ('region_name', models.CharField(max_length=50)),
                ('telephone_number', models.CharField(max_length=50)),
                ('pincode', models.ManyToManyField(to='accountpannel.pincode')),
            ],
        ),
    ]
