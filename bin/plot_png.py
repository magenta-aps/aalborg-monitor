# -*- coding: utf-8 -*-
# The contents of this file are subject to the Mozilla Public License
# Version 2.0 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
#    http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# Copyright 2015 Magenta Aps
#
from django.conf import settings
from django.http.request import QueryDict
from appmonitor.models import ConfigurationValue
from appmonitor.models import TestSuite, TestMeasure, TestMeasureConfig
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from datetime import timedelta
from django.utils import timezone, dateparse
import io, os, datetime, sys, django, locale, platform

DPI = 100

def parse_date_arg(arg):
    if not arg:
        return None

    try:
        parts = [int(x) for x in str(arg).split("-")]
    except:
        parts = []

    if len(parts) < 3:
        return None

    return timezone.datetime(
        day=parts[0],
        month=parts[1],
        year=parts[2],
        tzinfo=timezone.get_default_timezone()
    )

def plot_png(argsdict):
    django.setup()
    timezone.activate(timezone.get_current_timezone())

    pk = qdict.get("test_suite_pk")
    mname = qdict.get("measure_name")

    test_suite = TestSuite.objects.get(pk=pk)
    fullscreen = qdict.get("fs", False)

    cmp_args = qdict.get("cmp")
    if cmp_args:
        cmp_args = cmp_args.split("/")
    else:
        cmp_args = [None, None]

    cmp_pk = cmp_args[0]
    cmp_mname = cmp_args[1]
    t_from = parse_date_arg(qdict.get("from"))
    t_to = parse_date_arg(qdict.get("to"))

    if t_from is None:
        t_from = timezone.now() - timedelta(days=7)

    if not (pk and mname):
        raise Exception(
            "You must specify at least test_suite_pk and measure_name"
        )

    config = TestMeasureConfig.get_or_create(pk, mname)
    targetvalue = config.failure_threshold

    try:
        targetvalue = float(targetvalue)
    except:
        targetvalue = None

    dates = []
    measures = []

    extra_filters = {}
    if t_from:
        extra_filters['started__gte'] = t_from

    if t_to:
        extra_filters['ended__lte'] = t_to

    max_measure = 0
    items = TestMeasure.objects.filter(
        test_run__test_suite__pk = pk,
        name = mname,
        success = 1,
        **extra_filters
    ).order_by("started", "ended")

    if len(items) == 0:
        return ""

    fig, ax = plt.subplots()

    alarmstate=0
    if config.alarm_status == TestMeasureConfig.ALARM_STATUS_ALARM:
        ax.set_axis_bgcolor((1, 0.5, 0.5))
        alarmstate=1

    try:
        xsize = int(argsdict.get('xsize', 800))
    except ValueError:
        xsize = 800
    if xsize < 800:
        xsize = 800

    try:
        ysize = int(argsdict.get('ysize', 600))
    except ValueError:
        ysize = 600
    if ysize < 600:
        ysize = 600

    fig.set_size_inches(xsize/DPI, ysize/DPI)


    for item in items:
        dates.append(timezone.make_naive(item.started))
        diff = (item.ended - item.started).total_seconds()
        measures.append(diff)
        if diff > max_measure:
            max_measure = diff

    min_date = dates[0]
    max_date = dates[-1]

    ax.plot_date(
        dates, measures,
        label=u'%s: %s' % (test_suite.name, config.name),
        marker="x",
        linestyle="-"
    )

    if cmp_pk and cmp_mname:
        cmp_testsuite = TestSuite.objects.get(pk=cmp_pk)
        cmp_items = TestMeasure.objects.filter(
            test_run__test_suite__pk = cmp_pk,
            name = cmp_mname,
            success = 1,
            **extra_filters
        ).order_by("started", "ended")
        if len(cmp_items) > 0:
            dates2 = []
            measures2 = []
            for item in cmp_items:
                dates2.append(timezone.make_naive(item.started))
                diff = (item.ended - item.started).total_seconds()
                measures2.append(diff)
                if diff > max_measure:
                    max_measure = diff
            ax.plot_date(
                dates2, measures2,
                label=u'%s: %s' % (cmp_testsuite.name, cmp_mname),
                marker="x",
                linestyle="-",
                color='g'
            )


    if targetvalue:
        plt.axhline(
            targetvalue, 0, 1, None,
            color="r",
            label=u"Alarmtærskel"
        )
        if targetvalue > max_measure:
            max_measure = targetvalue

    # Plot the legends
    ax.legend(numpoints=1, loc='upper left', fontsize='x-small')

    # Configure axes and grid
    ax.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d %H:%M"))

    yaxis_scale = 1.1 if fullscreen else 1.2

    ax.set_ylim(bottom = 0, top = max_measure * yaxis_scale)
    ax.set_xlim(
        min_date - datetime.timedelta(minutes = 15),
        max_date + datetime.timedelta(minutes = 15)
    )
    ax.grid(True)

    fig.autofmt_xdate()

    fname = u"_".join([
        unicode(x).replace("/", "_") for x in [
            pk, mname, cmp_pk, cmp_mname, targetvalue, xsize, ysize
        ] if x
    ]) + ".png"

    full_path_fname = os.path.join(settings.STATIC_ROOT, "plots", fname)

    fig.tight_layout()

    if fullscreen:
        location_cnf = ConfigurationValue.get_or_create_default(
            u"lokation", u"Ukendt lokation"
        )
        ax.set_title(
            u"%s(%s) - %s: %s\n" % (
                platform.node(), location_cnf.value, test_suite.name, mname
            ) +
            u"Kontaktperson(er): %s" % ", ".join(
                [x.full_name() for x in test_suite.contactpersons.all()]
            ),
            fontsize='x-small'
        )
        fig.subplots_adjust(top=0.90)

    fig.savefig(full_path_fname, format='png', dpi=DPI)

    result = QueryDict('', mutable=True, encoding='utf8')
    result.update({
        'fname': full_path_fname,
        'alarm': alarmstate
    })

    return result.urlencode(safe='/%')

if __name__ == '__main__':
    qstring = sys.argv[1]
    qdict = QueryDict(qstring, mutable=True, encoding='utf8')
    print plot_png(qdict)

    
    
