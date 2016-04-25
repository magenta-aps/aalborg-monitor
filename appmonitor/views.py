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
from django.http import HttpResponse, Http404
from django.utils import dateparse, timezone
from django.views.generic import ListView, DetailView, TemplateView, View
from appmonitor.models import TestSuite, TestRun, TestMeasure
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

    def get_context_data(self, **kwargs):
        today = timezone.now().date()
        one_week_ago = today - datetime.timedelta(days=7)

        context = super(TestSuiteDetailView, self).get_context_data(**kwargs)
        # context['form'] = TestSuiteDetailForm(kwargs)
        context['form'] = self.get_form()
        context['result_overview_from'] = self.request.GET.get("result_overview_from")
        context['result_overview_to'] = self.request.GET.get("result_overview_to")
        context['executed_tests_from'] = self.request.GET.get("executed_tests_from")
        context['executed_tests_to'] = self.request.GET.get("executed_tests_to")

        if context['result_overview_from'] is None or context['result_overview_from'] == '':
            result_overview_from = one_week_ago
        else:
            result_overview_from = datetime.datetime.strptime(context['result_overview_from'], '%d-%m-%Y')

        if context['result_overview_to'] is None or context['result_overview_to'] == '':
            result_overview_to = None
        else:
            result_overview_to = datetime.datetime.strptime(context['result_overview_to'], '%d-%m-%Y')

        if context['executed_tests_from'] is None or context['executed_tests_from'] == '':
            executed_tests_from = one_week_ago
        else:
            executed_tests_from = datetime.datetime.strptime(context['executed_tests_from'], '%d-%m-%Y')

        if context['executed_tests_to'] is None or context['executed_tests_to'] == '':
            executed_tests_to = None
        else:
            executed_tests_to = datetime.datetime.strptime(context['executed_tests_to'], '%d-%m-%Y')

        if self.object:
            context['test_data'] = self.object.test_data(
                result_overview_from,
                result_overview_to
            )
            if executed_tests_from and executed_tests_to:
                context['runs'] = self.object.testrun_set.filter(
                    started__gte=executed_tests_from,
                    started__lte=executed_tests_to
                ).order_by('-started')
            elif executed_tests_from:
                context['runs'] = self.object.testrun_set.filter(
                    started__gte=executed_tests_from,
                ).order_by('-started')
            elif executed_tests_to:
                context['runs'] = self.object.testrun_set.filter(
                    started__gte=executed_tests_to,
                ).order_by('-started')
            else:
                context['runs'] = self.object.testrun_set.order_by('-started')

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
        print dtstamp
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

    def get_context_data(self, **kwargs):
        context = super(MeasureView, self).get_context_data(**kwargs)

        context['testsuite'] = TestSuite.objects.get(pk=kwargs['pk'])
        context['mname'] = kwargs['mname']
        context['t'] = self.request.GET.get("t", "")
        context['cmp'] = self.request.GET.get("cmp", "")
        context['cmp_ts'] = self.request.GET.get("cmp_ts", "")
        context['from'] = self.request.GET.get("from", "")
        context['to'] = self.request.GET.get("to", "")
        days = self.request.GET.get("days", "")
        if days == '':
            context['days'] = '7'
        else:
            context['days'] = days

        cmp_data = []
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
        context["cmp_data"] = cmp_data
        context["cmp_data_json"] = json.dumps(cmp_data)

        return context


class MeasurePNGView(View):
    def get(self, request, *args, **kwargs):
        os_encoding = locale.getpreferredencoding()
        cmd = [
            settings.PYTHON_EXE,
            os.path.join(settings.BASE_DIR, "bin", "plot_png.py"),
            kwargs["pk"],
            kwargs["mname"],
            request.GET.get("t", ""),
        ]
        cmp_str = request.GET.get("cmp", None)
        if cmp_str:
            for x in cmp_str.split("/", 1):
                cmd.append(x)
        else:
            cmd.append("")
            cmd.append("")
        # 'days=' in query string calculates and overrules 'from='
        if request.GET.get("days", None):
            days = request.GET.get("days")
            t_from = ''
            now = datetime.datetime.now()
            if days == '1':
                t_from = now - datetime.timedelta(1)
            elif days == '3':
                t_from = now - datetime.timedelta(3)
            elif days == '7' or days == '':
                t_from = now - datetime.timedelta(7)
            elif days == '30':
                t_from = now - datetime.timedelta(30)
            # this is ruled by 'days=' here
            cmd.append(str(t_from))
        else:
            t_from = request.GET.get("from", None)
            try:
                t_from = dateparse.parse_datetime(t_from)
                if not t_from:
                    t_from = ""
            except:
                t_from = ""
            cmd.append(str(t_from))

            t_to = request.GET.get("to", None)
            try:
                t_to = dateparse.parse_datetime(t_to)
                if not t_to:
                    t_to = ""
            except:
                t_to = ""
            cmd.append(str(t_to))

        cmd = [unicode(x).encode(os_encoding) for x in cmd]
        fname = subprocess.check_output(cmd, env=os.environ.copy()).strip()
        if fname and fname != "":
            f = open(fname.decode(os_encoding), 'rb')
            response = HttpResponse(f.read(), 'image/png')
            f.close()
            return response
        else:
            f = open('appmonitor/static/appmonitor/nodata.png'.decode(os_encoding), 'rb')
            response = HttpResponse(f.read(), 'image/png')
            f.close()
            return response

            #raise Http404("Image not found")


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

