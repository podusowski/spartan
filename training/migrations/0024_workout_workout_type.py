# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-18 13:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0023_auto_20160906_1856'),
    ]

    operations = [
        migrations.AddField(
            model_name='workout',
            name='workout_type',
            field=models.CharField(default='strength', max_length=20),
        ),
    ]