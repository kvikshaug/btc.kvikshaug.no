# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20150531_0211'),
    ]

    operations = [
        migrations.RenameField(
            model_name='price',
            old_name='price',
            new_name='price_usd',
        ),
        migrations.AddField(
            model_name='price',
            name='usdnok',
            field=models.PositiveIntegerField(default=None),
            preserve_default=False,
        ),
    ]
