# -*- coding: utf-8 -*-
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
from django.db import models
from django.db.models import Q
from django.conf import settings
from django.utils import timezone
from appmonitor.utils import get_smtp_server, make_email_header
from appmonitor.utils import mimeencode_header
from django.template.loader import get_template
from email.mime.text import MIMEText
from email.utils import parseaddr

import os, io, xlwt, csv, platform

# Create your models here.

class ContactPerson(models.Model):

    class Meta:
        verbose_name = u"kontaktperson"
        verbose_name_plural = u"kontaktpersoner"

    first_name = models.CharField(max_length=255)
    middle_names = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()

    def __unicode__(self):
        return self.verbose_name()

    def verbose_name(self):
        return self.full_name() + " <" + self.email + ">"

    def full_name(self):
        names = [self.first_name]
        if self.middle_names:
            names.append(self.middle_names)
        names.append(self.last_name)
        return " ".join(names)

    def email_as_header(self):
        return make_email_header(self.email, self.full_name())

class TestSuite(models.Model):

    class Meta:
        verbose_name = u"testsuite"
        verbose_name_plural = u"testsuiter"

    name = models.CharField(max_length=255)
    directory = models.CharField(max_length=255)
    executeable = models.CharField(max_length=255)

    contactpersons = models.ManyToManyField(
        ContactPerson, blank=True, related_name='testsuites'
    )

    email_message = models.TextField(
        blank=True, null=True,
        verbose_name=u'Emailbesked ved fejl'
    )
    def __unicode__(self):
        return self.name

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
        run.status = TestRun.STATUS_RUNNING
        run.pid = os.getpid()
        run.save()
        return run

        self.testrun_set.count()

    def tests(self):
        return self.testrun_set

    def failed_tests(self):
        return self.testrun_set.filter(
            ~Q(exitstatus=0) | Q(exitstatus=None)
        )

    def failed_pct(self):
        total = self.tests().count()
        if 0 == total:
            return 0
        failures = self.failed_tests().count()
        return float(failures) / total * 100

    def contactperson_count(self):
        return self.contactpersons.count()

    # Calculates the probable order in which measurements should appear in
    # output by using the order from the latest run and inserting previously
    # removed measurements after the previous measurement in the run in which
    # they are first encountered.
    def ordered_names(self):
        indexes = {}
        names = []
        for run in self.testrun_set.order_by('-started', '-ended'):
            current_idx = 0
            for m in run.testmeasure_set.order_by('started', 'ended'):
                if m.name not in indexes:
                    # insert at current index
                    names.insert(current_idx, m.name)
                    indexes[m.name] = current_idx

                    # Bump the index of the following names
                    for n in names[current_idx + 1:]:
                        indexes[n] += 1

                # Next index is one higher than the index of the current
                # element, unless that index is less than the current one
                if indexes[m.name] >= current_idx:
                    current_idx = indexes[m.name] + 1
        return names

    def test_data(self):
        data = {}
        for m in TestMeasure.objects.filter(test_run__test_suite=self):
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

    def as_xls(self):
        ordered_names = self.ordered_names()

        headers = [
            'Afviklings-Id',
            'Afvikling startet',
            'Afvikling afsluttet'
        ]

        for n in ordered_names:
            headers.append(n + ":startet")
            headers.append(n+ ":afsluttet")
            headers.append(n + ":tid brugt")
            headers.append(n + ":success")

        book = xlwt.Workbook(encoding="utf-8")
        sheet = book.add_sheet("Data")

        boldstyle = xlwt.Style.easyxf("font: bold on")
        datestyle = xlwt.XFStyle()
        datestyle.num_format_str = 'YYYY-MM-DD hh:mm:ss'

        rownr = 0
        colnr = 0

        # 20 characters wide
        ts_width = 256 * 20

        for h in headers:
            sheet.col(colnr).width = ts_width
            sheet.write(rownr, colnr, h, boldstyle)
            colnr += 1

        rownr += 1
        colnr = 0
        for run in self.testrun_set.all():
            sheet.write(rownr, colnr, run.pk)
            colnr += 1

            sheet.write(
                rownr, colnr, timezone.make_naive(run.started), datestyle
            )
            colnr += 1

            if run.ended:
                sheet.write(
                    rownr, colnr, timezone.make_naive(run.ended), datestyle
                )
            else :
                sheet.write(rownr, colnr, "")
            colnr += 1

            lookup = {}
            for m in run.testmeasure_set.all():
                lookup[m.name] = m

            for n in ordered_names:
                if n in lookup:
                    m = lookup[n]

                    started = timezone.make_naive(m.started)
                    sheet.write(rownr, colnr, started, datestyle)
                    colnr += 1

                    if m.ended:
                        ended = timezone.make_naive(m.ended)
                        sheet.write(rownr, colnr, ended, datestyle)
                        colnr += 1

                        delta_time = (ended - started).total_seconds()
                        sheet.write(rownr, colnr, delta_time)
                        colnr += 1
                    else:
                        for x in range(2):
                            sheet.write(rownr, colnr, "")
                            colnr += 1

                    success = "ja" if m.success else "nej"
                    sheet.write(rownr, colnr, success)
                    colnr += 1
                else:
                    for x in range(4):
                        sheet.write(rownr, colnr, "")
                        colnr += 1

            rownr += 1
            colnr = 0

        output = io.BytesIO()
        book.save(output)
        return output.getvalue()

class TestRun(models.Model):

    class Meta:
        verbose_name = u"testafvikling"
        verbose_name_plural = u"testafviklinger"

    test_suite = models.ForeignKey(TestSuite)

    started = models.DateTimeField()
    ended = models.DateTimeField(null=True, blank=True)
    exitstatus = models.IntegerField(null=True, blank=True)
    pid = models.IntegerField(null=True, blank=True)

    STATUS_CREATED = 0
    STATUS_RUNNING = 1
    STATUS_FAILED = 2
    STATUS_COMPLETED = 3
    STATUS_COMPLETED_WITH_ALERTS = 4

    STATUS_CHOICES = (
        (STATUS_CREATED, "CREATED"),
        (STATUS_RUNNING, "RUNNING"),
        (STATUS_FAILED, "FAILED"),
        (STATUS_COMPLETED, "COMPLETED"),
        (STATUS_COMPLETED, "COMPLETED with alerts"),
    )

    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=STATUS_CREATED
    )

    def __unicode__(self):
        return self.verbose_name()

    def verbose_name(self):
        return self.test_suite.name + " @ " + str(self.started)[:19]

    def finish(self, exitstatus=0):
        if exitstatus != 0:
            self.status = TestRun.STATUS_FAILED
        else:
            self.status = TestRun.STATUS_COMPLETED

        self.exitstatus = exitstatus
        self.ended = timezone.now()

        self.save()

        self.check_alerts()

    def succeeded(self):
        return (
            self.exitstatus is not None and self.exitstatus == 0 and
            not self.has_alerts()
        )

    def has_alerts(self):
        return self.status == TestRun.STATUS_COMPLETED_WITH_ALERTS

    def create_measure(self, name, failure_threshold=None):
        measure = TestMeasure()
        measure.test_run = self
        measure.name = name
        measure.started = timezone.now()
        measure.save()

        if failure_threshold is not None:
            measure.set_initial_failure_threshold(failure_threshold)

        return measure

    def export_environment(self):
        os.environ.set(
            "APPMONITOR_SQLITE_FILE",
            str(settings.DATABASES['default']['NAME'])
        )
        os.environ.set('APPMONITOR_RUN_ID', self.pk)

    def calculate_success(self):
        if self.exitstatus is None:
            failed_measure = self.get_failed_measure()

            # Having failed measures is considered a failure
            if failed_measure is not None:
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

    def get_failed_measure(self):
        failed_measures = self.testmeasure_set.filter(
            Q(success=0) | Q(success=None)
        )[:1]
        if len(failed_measures) > 0:
            return failed_measures[0]
        else:
            return None

    def check_alerts(self):
        alarms = []

        for x in self.testmeasure_set.all():
            print "Checking %s" % x.name
            if x.update_alert_status():
                alarms.append(x)

        if len(alarms) > 0:
            if self.status == TestRun.STATUS_COMPLETED:
                self.status = TestRun.STATUS_COMPLETED_WITH_ALERTS
                self.save()
            self.notify_contactpersons(alarms)


    def notify_contactpersons(self, failed_measures=[]):
        # Only notify if something went wrong
        if self.status not in [
            TestRun.STATUS_FAILED, TestRun.STATUS_COMPLETED_WITH_ALERTS
        ]:
            return

        # If we have no specifically failed measures the whole run must have
        # failed before running any measures. In this case check if a previous
        # message has been sent out within the last 24 hours and skip sending
        # if that is the case.
        if len(failed_measures) == 0:
            one_day_ago = timezone.now() - timezone.timedelta(1)

            notifications = ErrorNotification.objects.filter(
                test_suite=self.test_suite,
                when__gte=one_day_ago,
                failed_measure=None
            )[:1]

            if len(notifications) > 0:
                return

        try:
            # Find out who we need to contact
            contactpersons = self.test_suite.contactpersons.all()
            if len(contactpersons) == 0:
                return

            # Check if we have a configured SMTP server and connect
            smtp = get_smtp_server()

            # render email template
            template = get_template("testrun_failure.email.txt")
            context = {
                'testrun': self,
                'testsuite': self.test_suite,
                'contactpersons': contactpersons,
                'failed_measures': failed_measures,
                'systemname': platform.node()
            }
            content = template.render(context)
            content = content.replace("\\\r\n", "").replace("\\\n", "")

            # generate mime message
            msg = MIMEText(content, "plain", "UTF-8")
            msg['From'] = make_email_header(settings.MAIL_FROM_EMAIL)
            msg['Subject'] = mimeencode_header(settings.MAIL_SUBJECT)
            for p in contactpersons:
                msg.add_header("To", p.email_as_header())

            # Send the mail
            smtp.sendmail(
                parseaddr(settings.MAIL_FROM_EMAIL)[1],
                [p.email for p in contactpersons],
                msg.as_string()
            )

            # Register the error notification
            notification = ErrorNotification()
            notification.when = timezone.now()
            notification.test_suite = self.test_suite
            notification.failed_measure = None
            notification.save()

        except Exception as e:
            print "Failed to send notification. Error: %s" % str(e)

    @classmethod
    def fix_failed_processes(cls):
        for r in cls.objects.filter(status=cls.STATUS_RUNNING):
            # Skip still-running processes
            if psutil.pid_exists(r.pid):
                continue

            r.status = cls.STATUS_FAILED
            r.exitstatus = -1
            if r.testmeasure_set.count() > 0:
                r.fix_ended_time()


class TestMeasure(models.Model):

    class Meta:
        verbose_name = u"målt værdi"
        verbose_name_plural = u"målte værdier"

    test_run = models.ForeignKey(TestRun)

    name = models.CharField(max_length=255)

    started = models.DateTimeField()
    ended = models.DateTimeField(null=True, blank=True)
    success = models.IntegerField(null=True, blank=True)
    failure_reason = models.TextField(null=True, blank=True)

    config = models.ForeignKey('TestMeasureConfig', blank=True, null=True)

    def __unicode__(self):
        return u"%s: %s" % (self.test_run.verbose_name(), self.name)

    def measure_time(self):
        if self.ended is None or self.started is None:
            return None

        return (self.ended - self.started).total_seconds()

    def succeed(self):
        self.ended = timezone.now()
        self.success = 1
        self.save()

    def fail(self):
        self.ended = timezone.now()
        self.success = 0
        self.save()

    def get_or_create_config(self):
        if not self.config:
            self.config = TestMeasureConfig.get_or_create(
                self.test_run.test_suite,
                self.name
            )
            self.save()

        return self.config

    def set_initial_failure_threshold(self, value):
        cnf = self.get_or_create_config()

        if cnf.failure_threshold is None:
            cnf.failure_threshold = value;
            cnf.save()

    def get_previous_run(self):
        return TestRun.objects.filter(
            test_suite=self.test_suite,
            pk__lt=self.pk
        ).order_by('-pk').first()

    # Sets alarm if this measure and the previous one exceeds the configured
    # threshold. Returns a boolean specifying whether a new alert was
    # triggered,
    def update_alert_status(self):
        cnf = self.get_or_create_config()
        
        print "Existing status: %s" % cnf.get_alarm_status_display()

        # Don't check if we're already in alert status
        if cnf.alarm_status == TestMeasureConfig.ALARM_STATUS_ALARM:
            return False

        if self.failed_or_exceeds_threshold:
            if cnf.alarm_status == TestMeasureConfig.ALARM_STATUS_FAILED_ONCE:
                cnf.alarm_status = TestMeasureConfig.ALARM_STATUS_ALARM
            else:
                cnf.alarm_status = TestMeasureConfig.ALARM_STATUS_FAILED_ONCE
            cnf.save()
        else:
            if cnf.alarm_status != TestMeasureConfig.ALARM_STATUS_NORMAL:
                cnf.alarm_status = TestMeasureConfig.ALARM_STATUS_NORMAL
                cnf.save()

        return cnf.alarm_status == TestMeasureConfig.ALARM_STATUS_ALARM

    @property
    def failed_or_exceeds_threshold(self):
        if self.success == 0:
            return True

        time = self.measure_time()

        if time is None:
            return False
        
        cnf = self.get_or_create_config()
        threshold = cnf.failure_threshold

        print "%s vs %s" % (time, threshold)

        if threshold is None:
            return False

        return time >= threshold

class TestMeasureConfig(models.Model):

    class Meta:
        verbose_name = u"indstillinger for måling"
        verbose_name_plural = u"indstillinger for målinger"

    test_suite = models.ForeignKey(TestSuite)
    name = models.CharField(max_length=255)

    failure_threshold = models.FloatField(
        blank=True,
        null=True,
        default=None,
        verbose_name=u"Alarmtærskel"
    )

    ALARM_STATUS_NORMAL = 0
    ALARM_STATUS_ALARM = 1
    ALARM_STATUS_FAILED_ONCE = 2

    alarm_status_choices = (
        (ALARM_STATUS_NORMAL, u"Normal"),
        (ALARM_STATUS_FAILED_ONCE, u"Fejlet én gang"),
        (ALARM_STATUS_ALARM, u"Alarm"),
    )

    alarm_status = models.IntegerField(
        choices=alarm_status_choices,
        default=ALARM_STATUS_NORMAL
    )

    alarm_triggered_by = models.ForeignKey(
        TestMeasure,
        null=True,
        blank=True,
        default=None,
        editable=False
    )

    @classmethod
    def get_or_create(cls, test_suite, name):
        try:
            return cls.objects.get(
                test_suite=test_suite,
                name=name
            )
        except TestMeasureConfig.DoesNotExist:
            new_obj = TestMeasureConfig(
                test_suite=test_suite,
                name=name
            )
            new_obj.save()
            return new_obj

    def __unicode__(self):
        return u"Indstillinger for %s: %s" % (self.test_suite.name, self.name)

class ConfigurationValue(models.Model):

    class Meta:
        verbose_name = u"konfigurationsværdi"
        verbose_name_plural = u"konfigurationsværdier"
        
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    @classmethod
    def get_or_create_default(cls, name, default):
        try:
            obj = cls.objects.get(name=name)
        except cls.DoesNotExist:
            obj = cls(
                name=name,
                value=default
            )
            obj.save()

        return obj

    def __unicode__(self):
        return self.name

class ErrorNotification(models.Model):

    class Meta:
        verbose_name = u"registreret fejlbesked"
        verbose_name_plural = u"registrede fejlbeskeder"
        
    test_suite = models.ForeignKey(TestSuite)
    failed_measure = models.ForeignKey(
        TestMeasure,
        blank=True,
        null=True
    )
    when = models.DateTimeField()

    def __unicode__(self):
        return self.test_suite.name + ": " + str(self.when)[:19]
