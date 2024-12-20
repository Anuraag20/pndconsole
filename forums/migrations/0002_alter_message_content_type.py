# Generated by Django 4.2.16 on 2024-12-07 15:35

from django.db import migrations, models
import django.db.models.deletion
import forums.models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('forums', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='content_type',
            field=models.ForeignKey(limit_choices_to=forums.models.get_contenttype_choices, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
    ]
