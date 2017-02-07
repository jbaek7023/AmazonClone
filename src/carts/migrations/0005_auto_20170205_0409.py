# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0004_cart_line_item_total'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='line_item_total',
        ),
        migrations.AddField(
            model_name='cartitem',
            name='line_item_total',
            field=models.DecimalField(default=19.99, max_digits=10, decimal_places=2),
        ),
    ]
