# Generated by Django 4.2.16 on 2024-10-22 17:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('forums', '0001_initial'),
        ('pnds', '0002_scheduledpump_exchange'),
    ]

    operations = [
        migrations.AddField(
            model_name='scheduledpump',
            name='message',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='forums.message'),
            preserve_default=False,
        ),
    ]
