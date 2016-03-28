# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-17 18:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jigsaw', '0013_auto_20160317_0134'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoundReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.IntegerField(default=0, editable=False)),
                ('totalpoints', models.IntegerField(default=0, editable=False)),
                ('wordscorrect', models.TextField(blank=True, editable=False)),
                ('roundbonus', models.BooleanField(default=False, editable=False)),
                ('instance', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='jigsaw.GameInstance')),
                ('player', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='jigsaw.Player')),
                ('round', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='jigsaw.Round')),
            ],
        ),
    ]
