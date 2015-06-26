# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re, os, sys

from appmonitor.models import TestSuite

class SeleniumTest(unittest.TestCase):
    def setUp(self):
        self.test_suite = TestSuite.locate_by_path(__file__)
        self.test_run = self.test_suite.start_run()
        self.driver = webdriver.Ie();
        self.driver.implicitly_wait(30)
        self.base_url = "https://redmine.magenta-aps.dk"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_selenium(self):
        driver = self.driver
        measure = self.test_run.create_measure("Naviger til start")
        driver.get(self.base_url + "/")
        accountElem = driver.find_element_by_id("account")
        measure.succeed()
        # TODO: measure.fail()
        measure = self.test_run.create_measure("Naviger til login")
        accountElem.find_element_by_css_selector("a.login").click()
        unameElem = driver.find_element_by_id("username")
        measure.succeed()
    
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
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)
        self.test_run.finish()

if __name__ == "__main__":
    unittest.main()
