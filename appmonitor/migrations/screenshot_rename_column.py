# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appmonitor', 'screenshot_table'),
    ]

    operations = [
        migrations.RenameField(
            model_name='screenshot',
            old_name='run_id',
            new_name='test_run',
        ),
    ]
