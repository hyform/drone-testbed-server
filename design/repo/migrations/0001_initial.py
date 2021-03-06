# Generated by Django 2.2.7 on 2019-11-26 22:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x', models.FloatField()),
                ('z', models.FloatField()),
                ('region', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.IntegerField()),
                ('payload', models.CharField(max_length=20)),
                ('weight', models.FloatField()),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='repo.Address')),
            ],
        ),
        migrations.CreateModel(
            name='DesignTeam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('initialscore', models.FloatField(default=0.0)),
                ('currentscore', models.FloatField(default=0.0)),
            ],
        ),
        migrations.CreateModel(
            name='OpsPlanDemo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('xmlstring', models.TextField()),
                ('tag', models.CharField(max_length=50)),
                ('team', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Path',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('leavetime', models.FloatField(default=0.0)),
                ('returntime', models.FloatField(default=0.0)),
            ],
        ),
        migrations.CreateModel(
            name='PlayDemo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('xmlstring', models.TextField()),
                ('tag', models.CharField(max_length=50)),
                ('team', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='ScenarioDemo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('xmlstring', models.TextField()),
                ('tag', models.CharField(max_length=50)),
                ('team', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='VehicleDemo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('xmlstring', models.TextField()),
                ('tag', models.CharField(max_length=50)),
                ('team', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Waypoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deliverytime', models.FloatField()),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='repo.Customer')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='repo.DesignTeam')),
            ],
        ),
        migrations.CreateModel(
            name='Warehouse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='repo.Address')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='repo.DesignTeam')),
            ],
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=100)),
                ('config', models.TextField()),
                ('result', models.CharField(max_length=100)),
                ('range', models.FloatField()),
                ('velocity', models.FloatField()),
                ('cost', models.FloatField()),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='repo.DesignTeam')),
            ],
        ),
        migrations.CreateModel(
            name='Target',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('selected', models.BooleanField(default=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='repo.Customer')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='repo.DesignTeam')),
            ],
        ),
        migrations.CreateModel(
            name='Scenario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=100)),
                ('nodes', models.ManyToManyField(to='repo.Target')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='repo.DesignTeam')),
                ('warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='repo.Warehouse')),
            ],
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=100)),
                ('pathss', models.ManyToManyField(to='repo.Path')),
                ('scenario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='repo.Scenario')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='repo.DesignTeam')),
            ],
        ),
        migrations.AddField(
            model_name='path',
            name='customers',
            field=models.ManyToManyField(to='repo.Target'),
        ),
        migrations.AddField(
            model_name='path',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='repo.DesignTeam'),
        ),
        migrations.AddField(
            model_name='path',
            name='vehicle',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='repo.Vehicle'),
        ),
        migrations.AddField(
            model_name='path',
            name='warehouse',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='repo.Warehouse'),
        ),
    ]
