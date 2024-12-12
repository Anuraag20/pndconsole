# Generated by Django 4.2.16 on 2024-12-11 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0007_ohlcvdata_interval'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ohlcvdata',
            name='is_pump_non_ml',
            field=models.BooleanField(help_text='This boolean value will either be set manually or programatically', null=True),
        ),
    ]
