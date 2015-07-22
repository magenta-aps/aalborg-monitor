from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from django.views.generic import ListView, DetailView, TemplateView
from appmonitor.models import TestSuite, TestRun
from markdown import Markdown
import os, datetime

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

    def get_context_data(self, **kwargs):
        context = super(TestSuiteDetailView, self).get_context_data(**kwargs)

        if self.object:
            context['runs'] = self.object.testrun_set.order_by('-started')

        return context

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


class ReadmeView(TemplateView):
    template_name = 'readme.html'

    def get_context_data(self, **kwargs):
        context = super(ReadmeView, self).get_context_data(**kwargs)

        f = open(os.path.join(settings.BASE_DIR, "README.md"))
        context['markdown_html'] = markdown_formatter.convert(
            f.read()
        )

        return context

