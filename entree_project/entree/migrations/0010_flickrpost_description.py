# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-04 20:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entree', '0009_auto_20160403_1909'),
    ]

    operations = [
        migrations.AddField(
            model_name='flickrpost',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
