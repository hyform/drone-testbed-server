# Generated by Django 3.0.2 on 2020-02-19 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repo', '0011_scenario_cusomters'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CustomerList',
            new_name='CustomerScenario',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='cusomters',
        ),
        migrations.AddField(
            model_name='scenario',
            name='customers',
            field=models.ManyToManyField(through='repo.CustomerScenario', to='repo.Customer'),
        ),
    ]
