# Generated by Django 3.0.8 on 2020-09-09 09:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('exper', '0015_auto_20200907_1752'),
    ]

    operations = [
        migrations.AddField(
            model_name='study',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='exper.Organization'),
        ),
    ]
