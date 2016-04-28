# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appmonitor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScreenShot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('measure_name', models.TextField()),
                ('file_name', models.TextField()),
                ('file_path', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='TestMeasureConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, db_index=True)),
                ('failure_threshold', models.FloatField(default=None, null=True, verbose_name='Alarmt\xe6rskel', blank=True)),
                ('alarm_status', models.IntegerField(default=0, choices=[(0, 'Normal'), (2, 'Fejlet \xe9n gang'), (1, 'Alarm')])),
            ],
            options={
                'verbose_name': 'indstillinger for m\xe5ling',
                'verbose_name_plural': 'indstillinger for m\xe5linger',
            },
        ),
        migrations.AlterModelOptions(
            name='configurationvalue',
            options={'verbose_name': 'konfigurationsv\xe6rdi', 'verbose_name_plural': 'konfigurationsv\xe6rdier'},
        ),
        migrations.AlterModelOptions(
            name='contactperson',
            options={'verbose_name': 'kontaktperson', 'verbose_name_plural': 'kontaktpersoner'},
        ),
        migrations.AlterModelOptions(
            name='errornotification',
            options={'verbose_name': 'registreret fejlbesked', 'verbose_name_plural': 'registrede fejlbeskeder'},
        ),
        migrations.AlterModelOptions(
            name='testmeasure',
            options={'verbose_name': 'm\xe5lt v\xe6rdi', 'verbose_name_plural': 'm\xe5lte v\xe6rdier'},
        ),
        migrations.AlterModelOptions(
            name='testrun',
            options={'verbose_name': 'testafvikling', 'verbose_name_plural': 'testafviklinger'},
        ),
        migrations.AlterModelOptions(
            name='testsuite',
            options={'verbose_name': 'testsuite', 'verbose_name_plural': 'testsuiter'},
        ),
        migrations.AddField(
            model_name='testmeasure',
            name='spent_time',
            field=models.FloatField(default=None, null=True, editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='errornotification',
            name='failed_measure',
            field=models.ForeignKey(blank=True, to='appmonitor.TestMeasure', null=True),
        ),
        migrations.AlterField(
            model_name='testmeasure',
            name='ended',
            field=models.DateTimeField(db_index=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='testmeasure',
            name='started',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='testrun',
            name='ended',
            field=models.DateTimeField(db_index=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='testrun',
            name='started',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='testrun',
            name='status',
            field=models.IntegerField(default=0, choices=[(0, b'CREATED'), (1, b'RUNNING'), (2, b'FAILED'), (3, b'COMPLETED'), (3, b'COMPLETED with alerts')]),
        ),
        migrations.AddField(
            model_name='testmeasureconfig',
            name='alarm_triggered_by',
            field=models.ForeignKey(default=None, blank=True, editable=False, to='appmonitor.TestMeasure', null=True),
        ),
        migrations.AddField(
            model_name='testmeasureconfig',
            name='test_suite',
            field=models.ForeignKey(to='appmonitor.TestSuite'),
        ),
        migrations.AddField(
            model_name='screenshot',
            name='test_run',
            field=models.ForeignKey(to='appmonitor.TestRun'),
        ),
        migrations.AddField(
            model_name='testmeasure',
            name='config',
            field=models.ForeignKey(blank=True, to='appmonitor.TestMeasureConfig', null=True),
        ),
    ]
