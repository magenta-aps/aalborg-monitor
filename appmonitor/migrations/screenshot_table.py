# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appmonitor', '0002_add_testmeasureconfig'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScreenShot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('measure_name', models.TextField()),
                ('file_name', models.TextField()),
                ('run_id', models.ForeignKey(to='appmonitor.TestRun')),
            ],
        ),
    ]
