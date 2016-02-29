# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commonapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='role',
            name='role',
            field=models.IntegerField(null=True),
        ),
    ]
