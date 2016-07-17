# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0007_reps_time_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='excercise',
            name='time_finished',
            field=models.DateTimeField(null=True, default=None),
        ),
        migrations.AddField(
            model_name='excercise',
            name='time_started',
            field=models.DateTimeField(null=True, default=None),
        ),
        migrations.AddField(
            model_name='excercise',
            name='time_updated',
            field=models.DateTimeField(null=True, default=None),
        ),
    ]
