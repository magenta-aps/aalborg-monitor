# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appmonitor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestMeasureConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('failure_threshold', models.IntegerField(default=None, null=True, blank=True)),
                ('test_suite', models.ForeignKey(to='appmonitor.TestSuite')),
            ],
        ),
        migrations.AddField(
            model_name='testmeasure',
            name='config',
            field=models.ForeignKey(blank=True, to='appmonitor.TestMeasureConfig', null=True),
        ),
    ]
