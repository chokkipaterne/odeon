# Generated by Django 2.2.10 on 2020-07-17 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visualizations', '0020_auto_20200716_0952'),
    ]

    operations = [
        migrations.AddField(
            model_name='vizoutput',
            name='code',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
    ]