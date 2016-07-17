# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0006_auto_20160715_1252'),
    ]

    operations = [
        migrations.AddField(
            model_name='reps',
            name='time_created',
            field=models.DateTimeField(default=None, null=True),
        ),
    ]
