# Generated by Django 5.1.3 on 2024-11-21 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accountpannel', '0009_remove_spo_telephone_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='HPO',
            fields=[
                ('hpo_id', models.AutoField(primary_key=True, serialize=False)),
                ('ho_pincode', models.IntegerField(unique=True)),
                ('office_name', models.CharField(max_length=100)),
                ('region_name', models.CharField(max_length=50)),
                ('division_name', models.CharField(max_length=50)),
                ('circle_name', models.CharField(max_length=50)),
                ('district_name', models.CharField(max_length=50)),
                ('state_name', models.CharField(max_length=50)),
                ('spo', models.ManyToManyField(related_name='hpos', to='accountpannel.spo')),
            ],
        ),
    ]
