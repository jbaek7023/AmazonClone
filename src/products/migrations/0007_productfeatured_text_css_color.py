# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_productfeatured_make_image_background'),
    ]

    operations = [
        migrations.AddField(
            model_name='productfeatured',
            name='text_css_color',
            field=models.CharField(null=True, max_length=120, blank=True),
        ),
    ]
