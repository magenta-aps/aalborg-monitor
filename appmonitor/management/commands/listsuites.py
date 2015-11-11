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
from django.core.management.base import BaseCommand, CommandError
from appmonitor.models import TestSuite

class Command(BaseCommand):
    help = 'Lists TestSuites and their ids'

    def handle(self, *args, **options):
        self.stdout.write('Testsuites:')
        suites = TestSuite.objects.order_by("pk")
        for s in suites:
            self.stdout.write('  %d: %s (%s\\%s)' % (
                s.pk,
                s.name,
                s.directory,
                s.executeable
            ))
        if len(suites) == 0:
            self.stdout.write('  No suites found')
