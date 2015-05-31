# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20150531_1146'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='price',
            name='rate_buy',
        ),
        migrations.RemoveField(
            model_name='price',
            name='rate_sell',
        ),
        migrations.RemoveField(
            model_name='price',
            name='usdbtc',
        ),
        migrations.RemoveField(
            model_name='price',
            name='usdnok',
        ),
    ]
