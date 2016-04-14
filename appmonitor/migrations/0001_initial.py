# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ConfigurationValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('value', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ContactPerson',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=255)),
                ('middle_names', models.CharField(max_length=255, blank=True)),
                ('last_name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='ErrorNotification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('when', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='TestMeasure',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('started', models.DateTimeField()),
                ('ended', models.DateTimeField(null=True, blank=True)),
                ('success', models.IntegerField(null=True, blank=True)),
                ('failure_reason', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='TestRun',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('started', models.DateTimeField()),
                ('ended', models.DateTimeField(null=True, blank=True)),
                ('exitstatus', models.IntegerField(null=True, blank=True)),
                ('pid', models.IntegerField(null=True, blank=True)),
                ('status', models.IntegerField(default=0, choices=[(0, b'CREATED'), (1, b'RUNNING'), (2, b'FAILED'), (3, b'COMPLETED')])),
            ],
        ),
        migrations.CreateModel(
            name='TestSuite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('directory', models.CharField(max_length=255)),
                ('executeable', models.CharField(max_length=255)),
                ('email_message', models.TextField(null=True, verbose_name='Emailbesked ved fejl', blank=True)),
                ('contactpersons', models.ManyToManyField(related_name='testsuites', to='appmonitor.ContactPerson', blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='testrun',
            name='test_suite',
            field=models.ForeignKey(to='appmonitor.TestSuite'),
        ),
        migrations.AddField(
            model_name='testmeasure',
            name='test_run',
            field=models.ForeignKey(to='appmonitor.TestRun'),
        ),
        migrations.AddField(
            model_name='errornotification',
            name='failed_measure',
            field=models.ForeignKey(to='appmonitor.TestMeasure', blank=True),
        ),
        migrations.AddField(
            model_name='errornotification',
            name='test_suite',
            field=models.ForeignKey(to='appmonitor.TestSuite'),
        ),
    ]
