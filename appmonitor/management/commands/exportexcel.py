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
    help = 'Exports TestSuite data in excel format'

    def add_arguments(self, parser):
        parser.add_argument(
            'suite_id',
            type=int,
            help=(
                "The id of the suite you want to export data from. " +
                "You can find the id by using the listsuites command."
            )
        )
        parser.add_argument(
            'output_filename',
            type=str,
            help="The name of the file you want to save the data in"
        )

    def handle(self, *args, **options):
        suite_id = options['suite_id']
        filename = options['output_filename']

        try:
            suite = TestSuite.objects.get(pk=suite_id)
        except TestSuite.DoesNotExist:
            raise CommandError('TestSuite "%s" does not exist' % suite_id)

        try:
            f = open(filename, "wb")
            f.write(suite.as_xls())
            f.close()
        except Exception as e:
            raise CommandError('Error write to file "%s"' % filename)

        self.stdout.write(
            'Wrote XLS data for TestSuite "%s" to %s' % (str(suite), filename)
        )
