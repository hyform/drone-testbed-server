# Generated by Django 3.1.4 on 2021-10-19 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ai', '0004_auto_20211019_1942'),
    ]

    operations = [
        migrations.AddField(
            model_name='designerbot',
            name='bot_user_name',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='opsbot',
            name='bot_user_name',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
