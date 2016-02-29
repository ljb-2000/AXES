# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commonapp', '0002_role_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='Url',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='role',
            name='url',
            field=models.ManyToManyField(to='commonapp.Url', null=True, blank=True),
        ),
    ]
