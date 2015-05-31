# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20150531_1152'),
    ]

    operations = [
        migrations.RenameField(
            model_name='price',
            old_name='_rate_buy',
            new_name='rate_buy',
        ),
        migrations.RenameField(
            model_name='price',
            old_name='_rate_sell',
            new_name='rate_sell',
        ),
        migrations.RenameField(
            model_name='price',
            old_name='_usdbtc',
            new_name='usdbtc',
        ),
        migrations.RenameField(
            model_name='price',
            old_name='_usdnok',
            new_name='usdnok',
        ),
    ]
