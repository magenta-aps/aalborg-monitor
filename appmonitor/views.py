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
from aalborgmonitor.forms import TestSuiteDetailForm
from django.shortcuts import render
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.http.request import QueryDict
from django.utils import dateparse, timezone
from django.views.generic import ListView, DetailView, TemplateView, View
from appmonitor.models import TestSuite, TestRun, TestMeasure
from appmonitor.models import TestMeasureConfig
from django.db.models import Count
from markdown import Markdown
import io, os, datetime, sys, glob, subprocess, locale, json

markdown_formatter = Markdown(output_format="html5")

# Create your views here.
class TestSuiteList(ListView):
    template_name = "root.html"
    queryset = TestSuite.objects.exclude(
        name="DEBUG"
    ).order_by('name')


class TestSuiteDetailView(DetailView):
    model = TestSuite
    template_name = 'testsuite.html'
    context_object_name = 'testsuite'
    form = None

    def tz_and_dateify(self, date):
        if not date:
            return None

        return timezone.datetime(
            year=date.year,
            month=date.month,
            day=date.day,
            hour=0,
            minute=0,
            tzinfo=timezone.get_current_timezone()
        )

    def get_context_data(self, **kwargs):
        today = timezone.now().date()
        one_week_ago = today - datetime.timedelta(days=7)

        context = super(TestSuiteDetailView, self).get_context_data(**kwargs)

        context['form'] = self.get_form()
        cdata = context['form'].cleaned_data

        context['result_overview_from'] = cdata.get("result_overview_from")
        context['result_overview_to'] = cdata.get("result_overview_to")
        context['executed_tests_from'] = cdata.get("executed_tests_from")
        context['executed_tests_to'] = cdata.get("executed_tests_to")

        result_overview_from = self.tz_and_dateify(
            context['result_overview_from']
        )
        result_overview_to = self.tz_and_dateify(
            context['result_overview_to']
        )
        executed_tests_from = self.tz_and_dateify(
            context['executed_tests_from']
        )
        executed_tests_to = self.tz_and_dateify(
            context['executed_tests_to']
        )


        if self.object:
            context['test_data'] = self.object.test_data(
                result_overview_from,
                result_overview_to
            )


            qs = self.object.testrun_set
            if executed_tests_from:
                qs = qs.filter(started__gte=executed_tests_from)
            if executed_tests_to:
                qs = qs.filter(
                    started__lt=executed_tests_to + datetime.timedelta(days=1)
                )

            context['runs'] = qs.order_by('-started')

        return context

    def get_form(self):
        if not self.form:
            # Make new form object
            self.form = TestSuiteDetailForm(
                self.request.GET,
            )
            # Process the form
            self.form.is_valid()
        return self.form


class TestSuiteDownloadView(DetailView):
    model = TestSuite

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        response = HttpResponse(
            self.object.as_xls(), 'application/vnd.ms-excel'
        )
        dtstamp =  datetime.datetime.now().isoformat()[:19]
        dtstamp = dtstamp.replace("T", "_").replace(":", "")
        fname = 'excel_export_%d_%s.xls' % (self.object.pk, dtstamp)
        hdr = 'attachment; filename="%s"' % fname
        response['Content-Disposition'] = hdr
        return response


class TestRunDetailView(DetailView):
    model = TestRun
    template_name = 'testrun.html'
    context_object_name = 'testrun'

    def get_context_data(self, **kwargs):
        context = super(TestRunDetailView, self).get_context_data(**kwargs)

        if self.object:
            context['measures'] = self.object.testmeasure_set.order_by(
                'started', 'ended'
            )

        return context


class DocumentationView(TemplateView):
    template_name = 'documentation.html'

    def get_context_data(self, **kwargs):
        context = super(DocumentationView, self).get_context_data(**kwargs)

        doc_dir = os.path.join(settings.BASE_DIR, "doc")
        menuitems = glob.glob(os.path.join(doc_dir, "*.md"))
        context['menuitems'] = [
            os.path.basename(x).decode("latin-1")[:-3] for x in menuitems
        ]

        md_file = os.path.join(settings.BASE_DIR, "README.md")
        if "fname" in kwargs:
            md_file = os.path.join(doc_dir, kwargs["fname"] + ".md")
            context['subentry'] = kwargs["fname"]

        if not os.path.exists(md_file):
            raise Http404("Documentation not found")
        
        f = open(md_file)
        context['markdown_html'] = markdown_formatter.convert(
            f.read().decode('utf8')
        )

        return context


class MeasureView(TemplateView):
    template_name = 'measure.html'

    BY_DAYS_ALL = -1
    BY_DAYS_MANUAL = -2

    by_days_choices = (
        (1, u"Seneste døgn"),
        (3, u"Seneste tre dage"),
        (7, u"Seneste uge"),
        (30, u"Seneste 30 dage"),
        (BY_DAYS_ALL, u"Alle målinger"),
        (BY_DAYS_MANUAL, u"Manuelt angivet"),
    )

    def get_context_data(self, **kwargs):
        context = super(MeasureView, self).get_context_data(**kwargs)

        img_args = self.request.GET.copy()

        context['testsuite'] = TestSuite.objects.get(pk=kwargs['pk'])
        context['mname'] = kwargs['mname']
        days = self.request.GET.get("days", "7")
        try:
            days = int(days)
        except:
            days = 7
        if days not in [x[0] for x in MeasureView.by_days_choices]:
            days = 7

        context["days"] = days
        context["days_choices"] = [
            {'text': x[1], 'value': x[0], 'selected': x[0] == days}
            for x in MeasureView.by_days_choices
        ]

        img_remove_args = ["days", "cmp_ts"]

        if days != MeasureView.BY_DAYS_MANUAL:
            img_remove_args.append("from")
            img_remove_args.append("to")

        for x in img_remove_args:
            if x in img_args:
                img_args.pop(x)

        if days > 0:
            dt = timezone.now() - datetime.timedelta(days=days)
            img_args['from'] = dt.strftime('%d-%m-%Y')

        autoupdate = self.request.GET.get("autoupdate", "10")
        if autoupdate not in ["1", "10", "30", "60", ""]:
            autoupdate = "10"

        context["autoupdate"] = autoupdate


        cmp_data = []
        own_measures = []
        other_measures = []
        qs = TestMeasure.objects.exclude(
            test_run__test_suite__name="DEBUG"
        ).values(
            "test_run__test_suite__pk",
            "test_run__test_suite__name",
            "name"
        ).order_by(
            "test_run__test_suite__name",
            "name"
        ).distinct()

        ts_pk = int(kwargs['pk'])

        for m in qs:
            if (len(cmp_data) == 0 or
                cmp_data[-1]["pk"] != m["test_run__test_suite__pk"]):
                cmp_data.append({
                    "pk": m["test_run__test_suite__pk"],
                    "name": m["test_run__test_suite__name"],
                    "items": []
                })
            cmp_data[-1]["items"].append(
                '%s/%s' % (m["test_run__test_suite__pk"], m["name"])
            )
            if m['test_run__test_suite__pk'] == ts_pk:
                if m["name"] != kwargs["mname"]:
                    own_measures.append(m)
            else:
                other_measures.append(m)

        context["cmp_data"] = cmp_data
        context["cmp_data_json"] = json.dumps(cmp_data)
        context["own_measures"] = own_measures
        context["other_measures"] = other_measures

        context['measureconfig'] = TestMeasureConfig.get_or_create(
            context['testsuite'], kwargs['mname']
        )

        context['img_args'] = img_args.urlencode(safe='%/')

        context['cancel_alarm_url'] = reverse(
            'appmonitor:cancelalarm', args=[kwargs["pk"], kwargs["mname"]]
        )

        return context


class MeasurePNGView(View):
    def get(self, request, *args, **kwargs):
        args_dict = request.GET.copy()
        args_dict.update({
            "test_suite_pk": kwargs["pk"],
            "measure_name": kwargs["mname"]
        })

        cmd = [
            settings.PYTHON_EXE,
            os.path.join(settings.BASE_DIR, "bin", "plot_png.py"),
            args_dict.urlencode(safe='/%')
        ]

        print "Plot png: %s" % cmd[-1]

        result = subprocess.check_output(cmd, env=os.environ.copy()).strip()

        qdict = QueryDict(result)
        fname = qdict.get("fname")
        alarm = qdict.get("alarm")

        if fname and fname != "":
            f = open(fname, 'rb')
            response = HttpResponse(f.read(), 'image/png')
            f.close()
            m_path = reverse(
                'appmonitor:measure', args=[kwargs["pk"], kwargs["mname"]]
            )
            response.set_cookie("alarm_state", alarm, path=m_path)
            return response
        else:
            f = open('appmonitor/static/appmonitor/nodata.png', 'rb')
            response = HttpResponse(f.read(), 'image/png')
            f.close()
            return response

class CancelAlarmView(View):
    def get(self, request, *args, **kwargs):
        cnf = TestMeasureConfig.get_or_create(
            kwargs["pk"], kwargs["mname"]
        )
        cnf.reset_alarm_status()
        return HttpResponse("OK", 'text/plin')


class ErrorReportView(ListView):
    template_name = "error_report.html"
    
    queryset = TestMeasure.objects.filter(
        failure_reason__isnull=False
    ).values(
        "test_run__test_suite__name",
        "name",
        "failure_reason"
    ).annotate(
        fcount=Count("pk")
    ).order_by("-fcount")

