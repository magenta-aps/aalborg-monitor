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
