# Generated by Django 5.1.3 on 2024-11-24 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accountpannel', '0028_complains_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('Employee_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('password', models.CharField(max_length=128)),
                ('type', models.CharField(choices=[('spo', 'spo'), ('hpo', 'hpo'), ('ich', 'ich'), ('nsh', 'nsh')], max_length=50)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('address', models.TextField()),
                ('pincode', models.IntegerField()),
                ('city_district', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=50)),
                ('office_id', models.IntegerField()),
            ],
        ),
    ]
