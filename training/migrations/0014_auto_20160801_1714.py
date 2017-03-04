# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0013_auto_20160731_0710'),
    ]

    operations = [
        migrations.AddField(
            model_name='gpx',
            name='activity_type',
            field=models.CharField(max_length=20, default='RUNNING'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gpx',
            name='length_2d',
            field=models.IntegerField(default=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gpx',
            name='length_3d',
            field=models.IntegerField(default=11),
            preserve_default=False,
        ),
    ]
