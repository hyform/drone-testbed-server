# Generated by Django 3.0.5 on 2020-04-28 22:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repo', '0026_profile_temp_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='temp_code',
        ),
    ]
