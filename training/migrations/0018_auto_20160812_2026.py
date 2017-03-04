# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0017_auto_20160809_1902'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gpx',
            name='gpx',
        ),
        migrations.AlterField(
            model_name='gpxtrackpoint',
            name='cad',
            field=models.PositiveSmallIntegerField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='gpxtrackpoint',
            name='hr',
            field=models.PositiveSmallIntegerField(default=None, null=True),
        ),
    ]
