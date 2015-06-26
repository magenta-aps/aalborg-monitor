from django.contrib import admin

from appmonitor.models import ContactPerson, TestMeasure, TestRun, TestSuite

# Register your models here.

admin.site.register(ContactPerson)
admin.site.register(TestMeasure)
admin.site.register(TestRun)
admin.site.register(TestSuite)
