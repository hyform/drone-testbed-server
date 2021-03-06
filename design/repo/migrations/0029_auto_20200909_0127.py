# Generated by Django 3.0.8 on 2020-09-09 01:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('exper', '0015_auto_20200907_1752'),
        ('repo', '0028_profile_user_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='experiment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='exper.Experiment'),
        ),
        migrations.AddField(
            model_name='profile',
            name='study',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='exper.Study'),
        ),
    ]
