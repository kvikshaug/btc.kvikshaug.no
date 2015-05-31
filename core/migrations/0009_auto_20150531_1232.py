# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20150531_1152'),
    ]

    operations = [
        migrations.RenameField(
            model_name='price',
            old_name='rate_buy',
            new_name='buy_rate',
        ),
        migrations.RenameField(
            model_name='price',
            old_name='rate_sell',
            new_name='sell_rate',
        ),
    ]
