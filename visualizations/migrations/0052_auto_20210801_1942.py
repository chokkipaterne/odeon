# Generated by Django 2.2.10 on 2021-08-01 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visualizations', '0051_auto_20210801_1255'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='attach',
            field=models.FileField(blank=True, null=True, upload_to='feedbacks/'),
        ),
        migrations.DeleteModel(
            name='Attachment',
        ),
    ]
