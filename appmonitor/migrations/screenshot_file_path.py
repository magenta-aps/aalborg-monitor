# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appmonitor', 'screenshot_rename_column'),
    ]

    operations = [
        migrations.AddField(
            model_name='screenshot',
            name='file_path',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
