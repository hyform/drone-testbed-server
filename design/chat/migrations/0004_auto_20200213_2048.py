# Generated by Django 3.0.2 on 2020-02-13 20:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('exper', '0001_initial'),
        ('chat', '0003_auto_20200207_1824'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChannelPosition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.RemoveField(
            model_name='channel',
            name='configuration',
        ),
        migrations.RemoveField(
            model_name='channel',
            name='team',
        ),
        migrations.AddField(
            model_name='channel',
            name='structure',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='exper.Structure'),
        ),
        migrations.DeleteModel(
            name='ChannelGroup',
        ),
        migrations.AddField(
            model_name='channelposition',
            name='channel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chat.Channel'),
        ),
        migrations.AddField(
            model_name='channelposition',
            name='position',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='exper.Position'),
        ),
    ]
