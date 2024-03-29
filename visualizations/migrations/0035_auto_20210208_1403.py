# Generated by Django 2.2.10 on 2021-02-08 13:03

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('visualizations', '0034_project_has_vizs'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataPortal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('active', models.BooleanField(default=True)),
                ('more_details', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'DataPortal',
                'verbose_name_plural': 'DataPortals',
                'ordering': ['name'],
            },
        ),
        migrations.AlterField(
            model_name='datatyperule',
            name='user_type',
            field=models.CharField(choices=[('expert', 'Confident'), ('intermediate', 'Less confident'), ('non-expert', 'Not confident')], default='non-expert', max_length=30),
        ),
        migrations.AlterField(
            model_name='vizoutput',
            name='user_type',
            field=models.CharField(choices=[('expert', 'Confident'), ('intermediate', 'Less confident'), ('non-expert', 'Not confident')], default='non-expert', max_length=30),
        ),
        migrations.AlterField(
            model_name='viztypemark',
            name='user_type',
            field=models.CharField(choices=[('expert', 'Confident'), ('intermediate', 'Less confident'), ('non-expert', 'Not confident')], default='non-expert', max_length=30),
        ),
        migrations.AddField(
            model_name='uploadfile',
            name='portal',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='uploadfiles', to='visualizations.DataPortal'),
        ),
    ]
