from django.db import models
from django.db.models import Q
from django.conf import settings
from django.utils import timezone
import os



# Create your models here.

class ContactPerson(models.Model):
    first_name = models.CharField(max_length=255)
    middle_names = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()

    def __unicode__(self):
        return "ContactPerson: " + self.verbose_name()

    def verbose_name(self):
        return self.full_name() + " <" + self.email + ">"

    def full_name(self):
        names = [self.first_name]
        if self.middle_names:
            names.append(self.middle_names)
        names.append(self.last_name)
        return " ".join(names)

class TestSuite(models.Model):
    name = models.CharField(max_length=255)
    directory = models.CharField(max_length=255)
    executeable = models.CharField(max_length=255)

    contactpersons = models.ManyToManyField(
        ContactPerson, blank=True, related_name='testsuites'
    )

    def __unicode__(self):
        return "TestSuite: " + self.name

    @classmethod
    def locate_by_path(cls, path):
        path = os.path.normcase(os.path.abspath(path))
        if not path.startswith(settings.TESTSUITES_DIR):
            raise Exception("Path outside testsuites dir")
        dirname = os.path.basename(os.path.dirname(path))
        execname = os.path.basename(path)
        items = cls.objects.filter(directory=dirname, executeable=execname)[:1]
        if len(items) == 1:
            return items[0]
        else:
            item = cls()
            item.directory = dirname
            item.executeable = execname
            item.name = os.path.join(dirname, execname)
            item.save()
            return item

    def start_run(self):
        run = TestRun()
        run.test_suite = self
        run.started = timezone.now()
        run.save()
        return run

        self.testrun_set.count()

    def tests(self):
        return self.testrun_set

    def failed_tests(self):
        return self.testrun_set.filter(
            Q(exitstatus=0) | Q(exitstatus=None)
        )

    def failed_pct(self):
        total = self.tests().count()
        if 0 == total:
            return 0
        failures = self.failed_tests().count()
        return float(failures) / total * 100

    def contactperson_count(self):
        return self.contactpersons.count()

    def test_data(self):
        data = {}
        for run in self.testrun_set.all():
            for m in run.testmeasure_set.all():
                if m.name not in data:
                    data[m.name] = {
                        'name': m.name,
                        'total': 0,
                        'successes': 0,
                        'spent_time': 0
                    }
                # Register new data
                entry = data[m.name]
                entry['total'] += 1
                if(m.success):
                    entry['successes'] += 1
                    entry['spent_time'] += m.measure_time()

        result = []
        for name in self.ordered_names():
            entry = data[name]
            if entry['successes'] > 0:
                entry['avg_time'] = entry['spent_time'] / entry['successes']
            else:
                entry['avg_time'] = 0
            entry['failures'] = entry['total'] - entry['successes']

            if entry['failures'] == 0:
                entry['class'] = 'success'
            else:
                if entry['failures'] == entry['total']:
                    entry['class'] = 'danger'
                else:
                    entry['class'] = 'warning'
            result.append(entry)
        return result


    def ordered_names(self):
        indexes = {}
        names = []
        for run in self.testrun_set.order_by('started', 'ended'):
            current_idx = 0
            for m in run.testmeasure_set.order_by('started', 'ended'):
                if m.name not in indexes:
                    # insert at current index
                    names.insert(current_idx, m.name)
                    indexes[m.name] = current_idx

                    # Bump the index of the following names
                    for n in names[current_idx + 1:]:
                        indexes[n] += 1

                # Next index is one higher that the index of the current
                # element, unless that index is less than the current one
                if indexes[m.name] >= current_idx:
                    current_idx = indexes[m.name] + 1
        return names

class TestRun(models.Model):
    test_suite = models.ForeignKey(TestSuite)

    started = models.DateTimeField()
    ended = models.DateTimeField(null=True, blank=True)
    exitstatus = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return "TestRun: " + self.verbose_name()

    def verbose_name(self):
        return self.test_suite.name + "@" + str(self.started)

    def finish(self):
        self.ended = timezone.now()
        self.save()

    def succeeded(self):
        return self.exitstatus is not None and self.exitstatus == 0

    def create_measure(self, name):
        measure = TestMeasure()
        measure.test_run = self
        measure.name = name
        measure.started = timezone.now()
        measure.save()
        return measure

    def export_environment(self):
        os.environ.set(
            "APPMONITOR_SQLITE_FILE",
            str(settings.DATABASES['default']['NAME'])
        )
        os.environ.set('APPMONITOR_RUN_ID', self.pk)

    def calculate_success(self):
        if self.exitstatus is None:
            failed_measures = self.testmeasure_set.filter(success=0)
            # Having failed measures is considered a failure
            if failed_measures.count() > 0:
                self.exitstatus = -1
            else:
                # Having run no tests is also considered a fail
                if self.testmeasure_set.count() == 0:
                    self.exitstatus = -1
                else:
                    self.exitstatus = 0
            self.save()

    def fix_ended_time(self):
        if self.ended is None and self.exitstatus == 0:
            last_measure = self.testmeasure_set.order_by('-ended')[0]
            self.ended = last_measure.ended
            self.save()


class TestMeasure(models.Model):
    test_run = models.ForeignKey(TestRun)

    name = models.CharField(max_length=255)

    started = models.DateTimeField()
    ended = models.DateTimeField(null=True, blank=True)
    success = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return ("TestMeasure: " + self.name + " for " +
                self.test_run.verbose_name())

    def measure_time(self):
        if self.ended is None or self.started is None:
            return None

        return (self.ended - self.started).total_seconds()
    
    def succeed(self):
        self.ended = timezone.now()
        self.success = 1
        self.save()

    def fail(self):
        self.success = 0
        self.save()
    
class ConfigurationValue(models.Model):
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    def __unicode__(self):
        return "ConfigurationValue (" + self.name + ")"
    