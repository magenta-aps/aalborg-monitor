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
from appmonitor.models import TestMeasure
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from django.utils import timezone, dateparse
import io, os, datetime, sys, django, locale

def plot_png(
        pk, mname, targetvalue = None, cmp_pk = None, cmp_mname = None,
        t_from = None, t_to = None
    ):
    timezone.activate(timezone.get_current_timezone())
    if not (pk and mname):
        raise Exception("You must specify at least two command line args")
    django.setup()
    try:
        targetvalue = float(targetvalue)
    except:
        targetvalue = None

    dates = []
    measures = []

    extra_filters = {}
    try:
        t_from = dateparse.parse_datetime(t_from)
        if t_from:
            extra_filters['started__gte'] = t_from
    except:
        pass
    
    try:
        t_to = dateparse.parse_datetime(t_to)
        if t_to:
            extra_filters['ended__lte'] = t_to
    except:
        pass

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
        label=u"Måling",
        marker="x",
        linestyle="-"
    )

    if cmp_pk and cmp_mname:
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
                label=u"Referancemåling",
                marker="x",
                linestyle="-",
                color='g'
            )
                

    if targetvalue:
        plt.axhline(
            targetvalue, 0, 1, None,
            color="r",
            label=u"Målsætning"
        )
        if targetvalue > max_measure:
            max_measure = targetvalue

    # Plot the legends
    ax.legend(numpoints = 1, loc='upper left')

    # Configure axes and grid
    ax.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d %H:%M"))
    ax.set_ylim(bottom = 0, top = max_measure + 1)
    ax.set_xlim(
        min_date - datetime.timedelta(minutes = 15),
        max_date + datetime.timedelta(minutes = 15)
    )
    ax.grid(True)
    
    fig.autofmt_xdate()

    fname = u"_".join([
        unicode(x).replace("/", "_") for x in [
            pk, mname, cmp_pk, cmp_mname, targetvalue
        ] if x
    ]) + ".png"

    full_path_fname = os.path.join(settings.STATIC_ROOT, "plots", fname)
    fig.savefig(full_path_fname, format='png')
    return full_path_fname

if __name__ == '__main__':
    os_encoding = locale.getpreferredencoding()
    args = [x.decode(os_encoding) for x in sys.argv[1:]]
    fname = plot_png(*args)
    print fname.encode(os_encoding)
