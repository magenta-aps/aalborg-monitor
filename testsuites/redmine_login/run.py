# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re, os, sys

from appmonitor.models import TestSuite
from appmonitor.tests import AppmonitorTestCase

class SeleniumTest(AppmonitorTestCase):
    def setUp(self):
        self.appmonitorSetUp(__file__)
        self.base_url = "https://redmine.magenta-aps.dk"
    
    def test_selenium(self):
        driver = self.driver
        self.start_measure("Naviger til start")
        driver.get(self.base_url + "/")
        accountElem = driver.find_element_by_id("account")
        self.end_measure()

        self.start_measure("Naviger til login")
        accountElem.find_element_by_css_selector("a.login").click()
        self.driver.implicitly_wait(2)
        unameElem = driver.find_element_by_id("usernameasdf")
        self.end_measure()
    
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

if __name__ == "__main__":
    unittest.main()
