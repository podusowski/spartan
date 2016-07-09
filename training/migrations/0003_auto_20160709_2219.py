# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0002_auto_20160708_1242'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='TrainingSession',
            new_name='Workout',
        ),
        migrations.RenameField(
            model_name='excercise',
            old_name='training_session',
            new_name='workout',
        ),
    ]
