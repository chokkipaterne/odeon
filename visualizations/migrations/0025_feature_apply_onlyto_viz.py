# Generated by Django 2.2.10 on 2020-08-05 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visualizations', '0024_auto_20200728_1049'),
    ]

    operations = [
        migrations.AddField(
            model_name='feature',
            name='apply_onlyto_viz',
            field=models.TextField(blank=True, null=True),
        ),
    ]
