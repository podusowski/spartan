# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='trainingsession',
            name='finished',
            field=models.DateTimeField(null=True, default=None),
        ),
        migrations.AddField(
            model_name='trainingsession',
            name='started',
            field=models.DateTimeField(null=True, default=None),
        ),
    ]
