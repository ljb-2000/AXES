# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('systemmanage', '__first__'),
        ('commonapp', '0002_auto_20160223_1940'),
    ]

    operations = [
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('host', models.CharField(max_length=255)),
            ],
        ),
        migrations.RemoveField(
            model_name='role',
            name='project',
        ),
        migrations.AddField(
            model_name='permission',
            name='project',
            field=models.ManyToManyField(to='systemmanage.Game'),
        ),
    ]
