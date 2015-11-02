# -*- coding: utf-8 -*-
import unittest, time, re

from appmonitor.tests import AppmonitorTestCase

class SeleniumExport(AppmonitorTestCase):
    def setUp(self):
        self.appmonitorSetUp(__file__)
        self.base_url = "https://www.google.dk"
    
    def test_google_search(self):
        driver = self.driver

        self.start_measure("Naviger til google.dk")
        driver.get(self.base_url + "/")
        nextElem = driver.find_element_by_id("lst-ib")
        self.end_measure()

        self.start_measure("Input søgestreng")
        nextElem.clear()
        nextElem.send_keys("aalborg kommune")
        nextElem = driver.find_element_by_link_text("Aalborg Kommune: Borger")
        self.end_measure()
        
        self.start_measure("Klik på link")
        nextElem.click()
        driver.find_element_by_id("main-search");
        self.end_measure()
    
if __name__ == "__main__":
    unittest.main()
