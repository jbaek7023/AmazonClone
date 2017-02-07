# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0003_auto_20170203_1245'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='line_item_total',
            field=models.DecimalField(max_digits=10, decimal_places=2, default=19.99),
        ),
    ]
