# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commonapp', '0003_auto_20160224_1033'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='host',
            field=models.ManyToManyField(to='commonapp.Host', blank=True),
        ),
    ]
