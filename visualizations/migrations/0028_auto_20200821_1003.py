# Generated by Django 2.2.10 on 2020-08-21 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visualizations', '0027_vizoutput_mark_settings_str'),
    ]

    operations = [
        migrations.AddField(
            model_name='vizinput',
            name='insight',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vizinput',
            name='scores',
            field=models.TextField(blank=True, null=True),
        ),
    ]