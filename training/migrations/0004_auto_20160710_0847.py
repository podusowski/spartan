# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0003_auto_20160709_2219'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reps',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('reps', models.IntegerField()),
            ],
        ),
        migrations.RemoveField(
            model_name='excercise',
            name='sets',
        ),
        migrations.AddField(
            model_name='reps',
            name='excercise',
            field=models.ForeignKey(to='training.Excercise'),
        ),
    ]
