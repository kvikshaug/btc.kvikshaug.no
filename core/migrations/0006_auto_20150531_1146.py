# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import decimal

from django.db import models, migrations

def forwards(apps, schema_editor):
    Price = apps.get_model("core", "Price")
    for p in Price.objects.all():
        p._usdbtc = p.usdbtc / decimal.Decimal(1000)
        p._usdnok = p.usdnok / decimal.Decimal(1000)
        p._rate_buy = p.rate_buy / decimal.Decimal(100)
        p._rate_sell = p.rate_sell / decimal.Decimal(100)
        p.save()

def backwards(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20150531_1146'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
