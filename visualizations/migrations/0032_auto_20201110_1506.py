# Generated by Django 2.2.10 on 2020-11-10 14:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('visualizations', '0031_auto_20201110_1445'),
    ]

    operations = [
        migrations.RenameField(
            model_name='viztype',
            old_name='code',
            new_name='graph_function',
        ),
    ]