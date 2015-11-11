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
from django.conf.urls import url
from appmonitor.views import TestSuiteList, TestSuiteDetailView
from appmonitor.views import TestSuiteDownloadView, MeasureView, MeasurePNGView
from appmonitor.views import TestRunDetailView, DocumentationView

urlpatterns = [
    url(r'^$',
        TestSuiteList.as_view(),
        name="index"),
    url(r'^testsuite/(?P<pk>[0-9]+)/(?P<mname>[^/]+).png/?',
        MeasurePNGView.as_view(),
        name="png"),
    url(r'^testsuite/(?P<pk>[0-9]+)/(?P<mname>[^/]+)/?',
        MeasureView.as_view(),
        name="measure"),
    url(r'^testsuite-download/(?P<pk>[0-9]+)/?',
        TestSuiteDownloadView.as_view(),
        name="testsuite_download"),
    url(r'^testsuite/(?P<pk>[0-9]+)/?',
        TestSuiteDetailView.as_view(),
        name="testsuite"),
    url(r'^testrun/(?P<pk>[0-9]+)/?',
        TestRunDetailView.as_view(),
        name="testrun"),
    url(r'^documentation/(?P<fname>[^/]+?)(\.md)?/?$',
        DocumentationView.as_view(),
        name="documentation"),
    url(r'^documentation/?',
        DocumentationView.as_view(),
        name="documentation")
]
