# Generated by Django 3.0.8 on 2020-09-09 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exper', '0019_auto_20200909_1005'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exercise',
            name='name',
            field=models.CharField(blank=True, max_length=250),
        ),
    ]
