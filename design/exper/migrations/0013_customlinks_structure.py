# Generated by Django 3.0.6 on 2020-06-09 00:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('exper', '0012_auto_20200608_1638'),
    ]

    operations = [
        migrations.AddField(
            model_name='customlinks',
            name='structure',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='exper.Structure'),
        ),
    ]