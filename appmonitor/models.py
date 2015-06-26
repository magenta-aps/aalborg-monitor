from django.db import models
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

    contactpersons = models.ManyToManyField(ContactPerson, blank=True)

    def __unicode__(self):
        return "TestSuite: " + self.name

    @classmethod
    def locate_by_path(cls, path):
        path = os.path.abspath(path)
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

    def create_measure(self, name):
        measure = TestMeasure()
        measure.test_run = self
        measure.name = name
        measure.started = timezone.now()
        measure.save()
        return measure

class TestMeasure(models.Model):
    test_run = models.ForeignKey(TestRun)

    name = models.CharField(max_length=255)

    started = models.DateTimeField()
    ended = models.DateTimeField(null=True, blank=True)
    success = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return ("TestMeasure: " + self.name + " for " +
                self.test_run.verbose_name())
    
    def succeed(self):
        self.ended = datetime.now()
        self.success = 1
        self.save()

    def fail(self):
        self.success = 0
        self.save()
    