# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0014_auto_20160801_1714'),
    ]

    operations = [
        migrations.CreateModel(
            name='GpxTrackPoint',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('lat', models.DecimalField(decimal_places=8, max_digits=10)),
                ('log', models.DecimalField(decimal_places=8, max_digits=11)),
                ('time', models.DateTimeField()),
                ('gpx', models.ForeignKey(to='training.Gpx', on_delete=models.CASCADE)),
            ],
        ),
    ]
