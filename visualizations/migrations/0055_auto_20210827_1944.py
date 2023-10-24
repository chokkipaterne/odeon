# Generated by Django 2.2.10 on 2021-08-27 17:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('visualizations', '0054_auto_20210805_1044'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='nb_likes',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='project',
            name='user_request_type',
            field=models.CharField(choices=[('citizen', 'Citizen'), ('developer', 'Developer')], default='citizen', max_length=30),
        ),
        migrations.AddField(
            model_name='uploadfile',
            name='nb_likes',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address_ip', models.CharField(blank=True, editable=False, max_length=20)),
                ('file', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='visualizations.UploadFile')),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='visualizations.Project')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='likes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Like',
                'verbose_name_plural': 'Likes',
            },
        ),
    ]