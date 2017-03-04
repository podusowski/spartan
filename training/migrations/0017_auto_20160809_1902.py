# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0016_auto_20160807_1728'),
    ]

    operations = [
        migrations.AddField(
            model_name='gpxtrackpoint',
            name='cad',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='gpxtrackpoint',
            name='hr',
            field=models.IntegerField(default=None, null=True),
        ),
    ]
