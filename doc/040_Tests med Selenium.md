# Udvikling af tests med Selenium

## Oprettelse af tests
Selenium-baserede tests udvikles som python unittiests der arver fra klassen
`appmonitor.tests.AppmonitorTestCase`.

Se `testsuites\google_search\google_search.py` for et eksempel.

Nye tests bør placeres i en undermappe til `testsuites` mappen nævnt ovenfor.

En god måde at komme i gang med Selenium-baserede tests er ved at bruge
Selenium IDE plugin'en til Firefox til at optage en serie af handlinger og
eksportere testcasen som en python unittest.

Koden fra en sådan unittest vil for en stor del kunne genbruges direkte i
`def test_<navn>` metoden for en appmonitor-test.

## Afvikling af tests

Selenium-baserede tests afvikles ved at køre scriptet for den pågældende
unittest inden i et environment der er konfigureret til appmonitor.

Se `testsuites\google_search\run_selenium.bat` for hvordan dette kan gøres.

## Registreringer af målinger i Selenium-baserede tests

Første gang et script køres vil det automatisk oprette en testsuite ud fra
scriptets navn og den mappe scriptet er placeret i. Hver gang scriptet afvikles
vil der blive registereret en script-afvikling under testsuiten og målinger
angivet i scriptet vil blive registeret under denne afvikling efterhånden som
de udføres.

En måling under en Selenium-test oprettes ved at kalde
`self.start_measure("Navn på måling")`. Målingen afsluttes ved at kalde
`self.end_measure()`. Man kan fejle den igangværende måling ved at kaste en
python exception.

Et eksempel på en Selenium-måling:

    self.start_measure("Klik på link")
    try:
        elem = driver.find_element_by_link_text("Aalborg Kommune: Borger")
    except:
        raise Exception("Kunne ikke finde link")
    try:
        elem.click()
    except:
        raise Exception("Kunne ikke klikke på fundet link")
    try:
        driver.find_element_by_id("main-search")
    except:
        raise Exception("Kunne ikke finde main-search element på aalborg.dk")
    self.end_measure()

Det er muligt at angive en standard alarmtærskel for en måling som andet
argument til `start_measure`, for eksemepel:

    self.start_measure("Min måling", 5.5)

for en måling med en tærkskelværdi på 5,5 sekunder. Denne værdi vil kun blive
registreret første gang målingen afvikles. Efterfølgende ændringer til
tærskelværdien for målingen vil skulle laves via administrationsinterfacet.
