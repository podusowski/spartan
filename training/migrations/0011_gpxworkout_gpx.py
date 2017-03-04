# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0010_gpxworkout'),
    ]

    operations = [
        migrations.AddField(
            model_name='gpxworkout',
            name='gpx',
            field=models.FileField(default=None, upload_to='gpx'),
            preserve_default=False,
        ),
    ]
