# Generated by Django 2.2.10 on 2020-06-04 14:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('visualizations', '0003_auto_20200604_1535'),
    ]

    operations = [
        migrations.RenameField(
            model_name='uploadfile',
            old_name='url',
            new_name='file_link',
        ),
    ]
