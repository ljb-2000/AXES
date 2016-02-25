# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commonapp', '0004_userprofile_host'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='permission',
            field=models.ManyToManyField(to='commonapp.Permission', blank=True),
        ),
    ]
