from django.conf.urls import url
from appmonitor.views import TestSuiteList, TestSuiteDetailView
from appmonitor.views import TestSuiteDownloadView, MeasureDataPNGView
from appmonitor.views import TestRunDetailView, DocumentationView

urlpatterns = [
    url(r'^$',
        TestSuiteList.as_view(),
        name="index"),
    url(r'^testsuite/(?P<pk>[0-9]+)/(?P<mname>[^/]+)/?',
        MeasureDataPNGView.as_view(),
        name="png"),
    url(r'^testsuite/(?P<pk>[0-9]+)/download/?',
        TestSuiteDownloadView.as_view(),
        name="testsuite_download"),
    url(r'^testsuite/(?P<pk>[0-9]+)/?',
        TestSuiteDetailView.as_view(),
        name="testsuite"),
    url(r'^testrun/(?P<pk>[0-9]+)/?',
        TestRunDetailView.as_view(),
        name="testrun"),
    url(r'^documentation/(?P<fname>[^/]+)/?',
        DocumentationView.as_view(),
        name="documentation"),
    url(r'^documentation/?',
        DocumentationView.as_view(),
        name="documentation")
]
