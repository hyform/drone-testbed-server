# Generated by Django 3.1.4 on 2021-10-19 18:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('exper', '0025_session_is_tutorial'),
        ('ai', '0002_designer1_velocity'),
    ]

    operations = [
        migrations.CreateModel(
            name='OpsBot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('iter_time', models.FloatField(blank=True, default=0, null=True)),
                ('command', models.CharField(blank=True, max_length=500, null=True)),
                ('command_type', models.CharField(blank=True, max_length=50, null=True)),
                ('referenced_obj', models.CharField(blank=True, max_length=500, null=True)),
                ('profit_dir', models.CharField(blank=True, max_length=10, null=True)),
                ('profit_value', models.FloatField(blank=True, null=True)),
                ('cost_dir', models.CharField(blank=True, max_length=10, null=True)),
                ('cost_value', models.FloatField(blank=True, null=True)),
                ('customers_dir', models.CharField(blank=True, max_length=10, null=True)),
                ('customers_value', models.FloatField(blank=True, null=True)),
                ('config', models.CharField(blank=True, max_length=5000, null=True)),
                ('ask_profit', models.BooleanField(blank=True, default=True, null=True)),
                ('ask_cost', models.BooleanField(blank=True, default=True, null=True)),
                ('ask_customers', models.BooleanField(blank=True, default=True, null=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exper.session')),
            ],
        ),
        migrations.CreateModel(
            name='DesignerBot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('iter_time', models.FloatField(blank=True, default=0, null=True)),
                ('command', models.CharField(blank=True, max_length=500, null=True)),
                ('command_type', models.CharField(blank=True, max_length=50, null=True)),
                ('referenced_obj', models.CharField(blank=True, max_length=500, null=True)),
                ('range_dir', models.CharField(blank=True, max_length=10, null=True)),
                ('range_value', models.FloatField(blank=True, default=10, null=True)),
                ('capacity_dir', models.CharField(blank=True, max_length=10, null=True)),
                ('capacity_value', models.FloatField(blank=True, default=5, null=True)),
                ('cost_dir', models.CharField(blank=True, max_length=10, null=True)),
                ('cost_value', models.FloatField(blank=True, default=3470, null=True)),
                ('config', models.CharField(blank=True, default='aMM0+++++*bNM2+++*cMN1+++*dLM2+++*eML1+++^ab^ac^ad^ae,5,3', max_length=5000, null=True)),
                ('ask_range', models.BooleanField(blank=True, default=True, null=True)),
                ('ask_capacity', models.BooleanField(blank=True, default=True, null=True)),
                ('ask_cost', models.BooleanField(blank=True, default=True, null=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exper.session')),
            ],
        ),
    ]
