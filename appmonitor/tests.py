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
from appmonitor.models import TestSuite, TestMeasure
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import ui
from selenium.webdriver.support import expected_conditions as EC

import unittest, django, os, datetime
# Create your tests here.

class AppmonitorTestCase(unittest.TestCase):
    test_run = None
    active_measures = {}
    last_measure = None

    def appmonitorSetUp(self, filename):
        # Setup internet explorer
        #caps = DesiredCapabilities.INTERNETEXPLORER.copy()
        #caps['ignoreProtectedModeSettings'] = True
        #self.driver = webdriver.Ie(capabilities=caps)
        self.driver = webdriver.Ie()
        self.driver.implicitly_wait(30)
        self.verificationErrors = []
        self.accept_next_alert = True

        # Setup testrun
        django.setup()
        self.test_suite = TestSuite.locate_by_path(filename)
        self.test_run = self.test_suite.start_run()

        # Register cleanup handler
        self.addCleanup(self.appmonitorCleanup)

    def getFailureMessage(self):
        res = self._resultForDoCleanups

        # If we have any errors, use the last error
        if len(res.errors) > 0:
            return res.errors[-1][1]

        # If we have any failures, use the last failure
        if len(res.failures) > 0:
            return res.failures[-1][1]

        return None

    def appmonitorCleanup(self):
        success = self._resultForDoCleanups.wasSuccessful()

        # Fail any dangling measure
        if self.last_measure and self.last_measure.success is None:
            self.last_measure.failure_reason = self.getFailureMessage()
            self.last_measure.fail()

        if self.test_run:
            exitstatus = 0 if success else -1
            self.test_run.finish(exitstatus)
            
        if not success:
            aalborg_monitor_root = os.path.dirname( # aalborg-monitor
                os.path.dirname(                    # appmonitor/
                    os.path.realpath(__file__)      # This script
                )
            )
            file_name = '%s.png' % datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
            path = os.path.join(aalborg_monitor_root, 'aalborgmonitor', 'static', 'screenshots', file_name)
            self.driver.get_screenshot_as_file(path)

        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

    def start_measure(self, name, failure_threshold=None):
        measure = self.test_run.create_measure(
            name, failure_threshold=failure_threshold
        )
        self.active_measures[name] = measure
        self.last_measure = measure
        return measure

    def end_measure(self, measure_or_name=None):
        # If no specification is giving, assume we try to finish the last
        # registered measure
        if measure_or_name is None:
            measure_or_name = self.last_measure
            if measure_or_name is None:
                raise Exception(
                    "Trying to finish current measure, but no current " +
                    "measure is registered"
                )

        if isinstance(measure_or_name, TestMeasure):
            name = measure_or_name.name
            measure = measure_or_name
        else:
            name = measure_or_name
            if name in self.active_measures:
                measure = self.active_measures[name]
            else:
                raise Exception(
                    "Measure with name %s not registered" % name
                )

        measure.succeed()
        if name in self.active_measures:
            del self.active_measures[name]

        self.last_measure = None

    def wait_for_visible(self, how, what, timeout=10):
        elem = ui.WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((how, what))
        )
        return elem
        
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException, e: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True

