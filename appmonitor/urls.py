from django.conf.urls import url
from appmonitor.views import TestSuiteList, TestSuiteDetailView
from appmonitor.views import TestRunDetailView, ReadmeView

urlpatterns = [
    url(r'^$', TestSuiteList.as_view()),
    url(r'^testsuite/(?P<pk>[0-9]+)/?', TestSuiteDetailView.as_view()),
    url(r'^testrun/(?P<pk>[0-9]+)/?', TestRunDetailView.as_view()),
    url(r'^readme/?', ReadmeView.as_view())
]
