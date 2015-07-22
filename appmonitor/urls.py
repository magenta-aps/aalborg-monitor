from django.conf.urls import url
from appmonitor.views import TestSuiteList, TestSuiteDetailView
from appmonitor.views import TestSuiteDownloadView
from appmonitor.views import TestRunDetailView, ReadmeView

urlpatterns = [
    url(r'^$',
        TestSuiteList.as_view(),
        name="index"),
    url(r'^testsuite/(?P<pk>[0-9]+)/download/?',
        TestSuiteDownloadView.as_view(),
        name="testsuite_download"),
    url(r'^testsuite/(?P<pk>[0-9]+)/?',
        TestSuiteDetailView.as_view(),
        name="testsuite"),
    url(r'^testrun/(?P<pk>[0-9]+)/?',
        TestRunDetailView.as_view(),
        name="testrun"),
    url(r'^readme/?',
        ReadmeView.as_view(),
        name="readme")
]
