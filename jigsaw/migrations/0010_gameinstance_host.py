# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-17 07:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jigsaw', '0009_gameinstance_system'),
    ]

    operations = [
        migrations.AddField(
            model_name='gameinstance',
            name='host',
            field=models.CharField(blank=True, max_length=150),
        ),
    ]
