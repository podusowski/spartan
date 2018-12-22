# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0012_auto_20160731_0705'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gpx',
            name='user',
        ),
        migrations.AddField(
            model_name='gpx',
            name='workout',
            field=models.ForeignKey(to='training.Workout', default=None, on_delete=models.CASCADE),
            preserve_default=False,
        ),
    ]
