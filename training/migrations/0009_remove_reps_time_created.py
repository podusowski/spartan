# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0008_auto_20160717_1917'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reps',
            name='time_created',
        ),
    ]
