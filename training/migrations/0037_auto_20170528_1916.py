# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-05-28 19:16
from __future__ import unicode_literals

from django.db import migrations, models


def set_field_values(apps, schema_editor):
    Workout = apps.get_model("training", "Workout")
    for workout in Workout.objects.all():
        if workout.gpx_set.count() > 0:
            workout.activity_type = "gps"
            workout.save()
        else:
            workout.activity_type = "strength"
            workout.save()


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0036_workout_activity_type'),
    ]

    operations = [
        migrations.RunPython(set_field_values),
        migrations.AlterField(
            model_name='workout',
            name='activity_type',
            field=models.CharField(max_length=200),
        ),
    ]
