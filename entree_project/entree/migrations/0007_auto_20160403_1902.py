# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-03 19:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entree', '0006_auto_20160403_1841'),
    ]

    operations = [
        migrations.AddField(
            model_name='flickrpost',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=9),
        ),
        migrations.AddField(
            model_name='flickrpost',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=9),
        ),
    ]
