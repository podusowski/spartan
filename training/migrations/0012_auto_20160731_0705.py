# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0011_gpxworkout_gpx'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='GpxWorkout',
            new_name='Gpx',
        ),
    ]
