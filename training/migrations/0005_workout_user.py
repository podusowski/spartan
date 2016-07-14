# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('training', '0004_auto_20160710_0847'),
    ]

    operations = [
        migrations.AddField(
            model_name='workout',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL, default=None),
            preserve_default=False,
        ),
    ]
