# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-03-12 09:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0033_auto_20161223_1050'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='workout',
            options={'ordering': ['-started']},
        ),
    ]