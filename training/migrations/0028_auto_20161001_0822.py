# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-01 08:22
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0027_auto_20160928_1028'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gpx',
            old_name='length_2d',
            new_name='distance',
        ),
    ]