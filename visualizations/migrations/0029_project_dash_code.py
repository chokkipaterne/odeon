# Generated by Django 2.2.10 on 2020-09-12 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visualizations', '0028_auto_20200821_1003'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='dash_code',
            field=models.CharField(blank=True, editable=False, max_length=8),
        ),
    ]
