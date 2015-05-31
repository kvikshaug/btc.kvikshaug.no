# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import decimal

from django.db import models, migrations

def forwards(apps, schema_editor):
    CurrentRate = apps.get_model("core", "CurrentRate")
    cr = CurrentRate(buy_rate=decimal.Decimal('0.99'), sell_rate=decimal.Decimal('1.02'))
    cr.save()

def backwards(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20150531_1232'),
    ]

    operations = [
        migrations.CreateModel(
            name='CurrentRate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('buy_rate', models.DecimalField(max_digits=3, decimal_places=2, null=True)),
                ('sell_rate', models.DecimalField(max_digits=3, decimal_places=2, null=True)),
            ],
        ),
        migrations.RunPython(forwards, backwards),
    ]
