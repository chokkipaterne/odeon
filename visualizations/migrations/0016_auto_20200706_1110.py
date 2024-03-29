# Generated by Django 2.2.10 on 2020-07-06 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visualizations', '0015_auto_20200702_1016'),
    ]

    operations = [
        migrations.AddField(
            model_name='vizinput',
            name='value',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vizinputfeature',
            name='formula',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='feature',
            name='formula',
            field=models.TextField(blank=True, null=True),
        ),
    ]
