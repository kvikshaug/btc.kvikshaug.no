# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20150531_0224'),
    ]

    operations = [
        migrations.AddField(
            model_name='price',
            name='_rate_buy',
            field=models.DecimalField(decimal_places=2, max_digits=3, null=True),
        ),
        migrations.AddField(
            model_name='price',
            name='_rate_sell',
            field=models.DecimalField(decimal_places=2, max_digits=3, null=True),
        ),
        migrations.AddField(
            model_name='price',
            name='_usdbtc',
            field=models.DecimalField(decimal_places=8, max_digits=14, null=True),
        ),
        migrations.AddField(
            model_name='price',
            name='_usdnok',
            field=models.DecimalField(decimal_places=8, max_digits=12, null=True),
        ),
    ]
