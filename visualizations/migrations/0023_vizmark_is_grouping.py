# Generated by Django 2.2.10 on 2020-07-23 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visualizations', '0022_auto_20200717_1132'),
    ]

    operations = [
        migrations.AddField(
            model_name='vizmark',
            name='is_grouping',
            field=models.BooleanField(default=False),
        ),
    ]
