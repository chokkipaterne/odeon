# Generated by Django 2.2.10 on 2021-09-26 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visualizations', '0060_auto_20210926_1342'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectstatus',
            name='abbreviation',
            field=models.CharField(default='', max_length=5),
        ),
    ]
