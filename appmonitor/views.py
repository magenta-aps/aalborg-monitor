from django.shortcuts import render
from django.views.generic import ListView
from appmonitor.models import TestSuite

# Create your views here.
class TestSuiteList(ListView):
    template_name = "root.html"
    queryset = TestSuite.objects.exclude(
        name="DEBUG"
    ).order_by('name')