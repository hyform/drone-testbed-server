# Generated by Django 3.0.5 on 2020-04-29 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repo', '0026_profile_temp_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='temp_code',
            field=models.TextField(blank=True, default=''),
        ),
    ]
