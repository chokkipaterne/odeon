# Generated by Django 2.2.10 on 2021-10-08 12:33

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('visualizations', '0062_auto_20211008_1152'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='published_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='project',
            name='show_in_mobile_apps',
            field=models.BooleanField(default=False),
        ),
    ]
