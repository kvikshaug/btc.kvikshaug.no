# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20150602_0128'),
    ]

    operations = [
        migrations.RenameField(
            model_name='price',
            old_name='usdbtc',
            new_name='btcusd',
        ),
    ]
