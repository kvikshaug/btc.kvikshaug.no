# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_currentrate'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='price',
            options={'ordering': ['-datetime']},
        ),
    ]
