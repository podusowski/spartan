# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0015_gpxtrackpoint'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gpxtrackpoint',
            old_name='log',
            new_name='lon',
        ),
    ]
