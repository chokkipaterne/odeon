# Generated by Django 2.2.10 on 2021-10-31 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visualizations', '0069_auto_20211030_1446'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='is_popular',
            field=models.BooleanField(default=False),
        ),
    ]
