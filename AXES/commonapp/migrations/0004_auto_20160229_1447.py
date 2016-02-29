# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commonapp', '0003_auto_20160226_1602'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='permission',
            name='project',
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='permission',
            field=models.ManyToManyField(to='systemmanage.Game', blank=True),
        ),
        migrations.DeleteModel(
            name='Permission',
        ),
    ]
