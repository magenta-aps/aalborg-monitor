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
