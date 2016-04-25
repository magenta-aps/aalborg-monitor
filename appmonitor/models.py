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

    def email_as_header(self):
        return make_email_header(self.email, self.full_name())

class TestSuite(models.Model):
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

    def test_data(self, from_date=None, to_date=None):
        data = {}
        if from_date and to_date:
            measures = TestMeasure.objects.filter(
                test_run__test_suite=self,
                started__gte=from_date,
                started__lte=to_date
            )
        elif from_date:
            measures = TestMeasure.objects.filter(
                test_run__test_suite=self,
                started__gte=from_date
            )
        elif to_date:
            measures = TestMeasure.objects.filter(
                test_run__test_suite=self,
                started__lte=to_date
            )
        else:
            measures = TestMeasure.objects.filter(
                test_run__test_suite=self
            )
        for m in measures:
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
        if data:
            for name in self.ordered_names():
                entry = data.get(name, {})
                if entry:
                    if entry.get('successes', 0) > 0:
                        entry['avg_time'] = entry.get('spent_time', 0) / entry['successes']
                    else:
                        entry['avg_time'] = 0
                    entry['failures'] = entry.get('total', 0) - entry.get('successes', 0)

                    if entry.get('failures') == 0:
                        entry['class'] = 'success'
                    else:
                        if entry.get('failures') == entry.get('total'):
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
    test_suite = models.ForeignKey(TestSuite)

    started = models.DateTimeField()
    ended = models.DateTimeField(null=True, blank=True)
    exitstatus = models.IntegerField(null=True, blank=True)
    pid = models.IntegerField(null=True, blank=True)

    STATUS_CREATED = 0
    STATUS_RUNNING = 1
    STATUS_FAILED = 2
    STATUS_COMPLETED = 3

    STATUS_CHOICES = (
        (STATUS_CREATED, "CREATED"),
        (STATUS_RUNNING, "RUNNING"),
        (STATUS_FAILED, "FAILED"),
        (STATUS_COMPLETED, "COMPLETED"),
    )

    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=STATUS_CREATED
    )

    def __unicode__(self):
        return "TestRun: " + self.verbose_name()

    def verbose_name(self):
        return self.test_suite.name + "@" + str(self.started)[:19]

    def finish(self, exitstatus=0):
        if exitstatus != 0:
            self.status = TestRun.STATUS_FAILED
        else:
            self.status = TestRun.STATUS_COMPLETED
        self.exitstatus = exitstatus
        self.ended = timezone.now()
        self.save()

        self.notify_contactpersons()

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

    def notify_contactpersons(self):
        # Only notify if something went wrong
        if self.status != TestRun.STATUS_FAILED:
            return

        measure = self.get_failed_measure()

        one_day_ago = timezone.now() - timezone.timedelta(1)

        # Check if a similar notification has been sent withing the last day
        filter = {
            'test_suite': self.test_suite,
            'when__gte': one_day_ago
        }
        if measure is None:
            # Search for a notification failure without an associated
            # measure
            filter['failed_measure'] = None
        else:
            # Search for a notification with the same name and message
            # as the current one
            filter['failed_measure__name'] = measure.name
            filter['failed_measure__failure_reason'] = measure.failure_reason

        notifications = ErrorNotification.objects.filter(**filter)[:1]

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
                'measure': measure,
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
            notification.failed_measure = measure
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
            self.notify_contactpersons()


class TestMeasure(models.Model):
    test_run = models.ForeignKey(TestRun)

    name = models.CharField(max_length=255)

    started = models.DateTimeField()
    ended = models.DateTimeField(null=True, blank=True)
    success = models.IntegerField(null=True, blank=True)
    failure_reason = models.TextField(null=True, blank=True)

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
        self.ended = timezone.now()
        self.success = 0
        self.save()
    
class ConfigurationValue(models.Model):
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    def __unicode__(self):
        return "ConfigurationValue (" + self.name + ")"

class ErrorNotification(models.Model):
    test_suite = models.ForeignKey(TestSuite)
    failed_measure = models.ForeignKey(TestMeasure, blank=True)
    when = models.DateTimeField()

    def __unicode__(self):
        return self.test_suite.name + ": " + str(self.when)[:19]
