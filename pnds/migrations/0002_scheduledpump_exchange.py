# Generated by Django 4.2.16 on 2024-10-04 21:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pnds', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='scheduledpump',
            name='exchange',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='schduled', to='market.exchange'),
        ),
    ]