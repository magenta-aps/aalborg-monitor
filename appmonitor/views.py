from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, Http404
from django.views.generic import ListView, DetailView, TemplateView
from appmonitor.models import TestSuite, TestRun, TestMeasure
from markdown import Markdown
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import io, os, datetime
import glob

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

class MeasureDataPNGView(ListView):
    model = TestMeasure
    allow_empty = False

    def get_queryset(self):
        qs = self.model.objects.filter(
            test_run__test_suite__pk = self.kwargs["pk"],
            name = self.kwargs["mname"],
            success = 1
        ).order_by("started", "ended")
        return qs

    def get(self, request, *args, **kwargs):
        dates = []
        measures = []

        max_measure = 0
        items = self.get_queryset()

        if len(items) == 0:
            raise Http404("No data")

        for item in items:
            dates.append(item.started)
            diff = (item.ended - item.started).total_seconds()
            measures.append(diff)
            if diff > max_measure:
                max_measure = diff
        
        now = datetime.datetime.now()
        
        fig, ax = plt.subplots()
        ax.plot_date(dates, measures, '-')

        ax.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d %H:%M"))
        ax.set_ylim(bottom = 0, top = max_measure + 1)
        ax.set_xlim(
            dates[0] - datetime.timedelta(minutes = 15),
            dates[-1] + datetime.timedelta(minutes = 15)
        )
        ax.grid(True)
        
        fig.autofmt_xdate()
        
        buf = io.BytesIO()
        
        fig.savefig(buf, format='png')
        buf.seek(0)

        response = HttpResponse(
            buf,
            'image/png'
        )
        return response
