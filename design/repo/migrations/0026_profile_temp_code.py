# Generated by Django 3.0.5 on 2020-04-23 03:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repo', '0025_auto_20200320_0348'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='temp_code',
            field=models.TextField(default=''),
        ),
    ]
