# Generated by Django 3.0.2 on 2020-02-20 12:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repo', '0015_scenario_customers'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scenario',
            name='customers',
        ),
    ]
