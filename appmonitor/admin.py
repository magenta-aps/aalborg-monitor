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
from django.contrib import admin

from appmonitor.models import ContactPerson, TestMeasure, TestRun, TestSuite
from appmonitor.models import TestMeasureConfig
from appmonitor.models import ConfigurationValue, ErrorNotification

# Register your models here.

admin.site.register(ContactPerson)
admin.site.register(TestMeasure)
admin.site.register(TestMeasureConfig)
admin.site.register(TestRun)
admin.site.register(TestSuite)
admin.site.register(ConfigurationValue)
#admin.site.register(ErrorNotification)
