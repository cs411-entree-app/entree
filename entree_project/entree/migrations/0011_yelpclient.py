# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-17 18:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entree', '0010_flickrpost_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='YelpClient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('consumer_key', models.CharField(max_length=32)),
                ('consumer_secret', models.CharField(max_length=32)),
                ('token', models.CharField(max_length=32)),
                ('token_secret', models.CharField(max_length=32)),
            ],
        ),
    ]
