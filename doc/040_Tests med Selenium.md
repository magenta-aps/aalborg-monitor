# Udvikling af tests med Selenium

Selenium-baserede tests udvikles som python unittiests der arver fra klassen
`appmonitor.tests.AppmonitorTestCase`.

Se `testsuites\google_search\google_search.py` for et eksempel.

En god måde at komme i gang med Selenium-baserede tests er ved at bruge
Selenium IDE plugin'en til Firefox til at optage en serie af handlinger og
eksportere testcasen som en python unittest.

Koden fra en sådan unittest vil for en stor del kunne genbruges direkte i
`def test_<navn>` metoden for en appmonitor-test.

Selenium-baserede tests afvikles ved at køre scriptet for den pågældende
unittest inden i et environment der er konfigureret til appmonitor.

Se `testsuites\google_search\run_selenium.bat` for hvordan dette kan gøres.
