# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20150531_0218'),
    ]

    operations = [
        migrations.RenameField(
            model_name='price',
            old_name='price_usd',
            new_name='usdbtc',
        ),
        migrations.AddField(
            model_name='price',
            name='rate_buy',
            field=models.PositiveIntegerField(default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='price',
            name='rate_sell',
            field=models.PositiveIntegerField(default=None),
            preserve_default=False,
        ),
    ]
