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
