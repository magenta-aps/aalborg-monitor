# Udvikling af tests med AutoIT

## Oprettelse af ny test

For at lave AutoIT-baserede tests skal man lave et AutoIT script og inkludere
filen `lib\autoit\appmonitor.au3` i toppen af scriptet. Dette vil give adgang
til metoder der gør det muligt at arbejde med Appmonitor-databasen.

Se `testsuites\google_search\google_search.au3` for et eksempel.

Nye scripts bør placeres i en undermappe til `testsuites` mappen nævnt ovenfor.

Under udvikling kan det være en fordel at starte en editor med scriptet
`Run Debug Editor.bat` der findes i roden af projektet. Denne editor vil
have det nødvendige environment der skal til for at man kan afvikle scripts
og stadig lave databaseoperationer. Dette gør det muligt at bruge editorens
debug-muligheder.

Målinger foretaget fra scripts afviklet under debug-editoren vil blive gemt
under en skjult `DEBUG` testsuite og vil ikke være mulige at se med mindre
man slår op direkte i datasen via admin-interfacet.

## Afvikling af AutoIT-baserede scripts

For at afvikle AutoIT scripts køres følgende:

`python -m appmonitor.autoit <name-of-script>.au3`

Kommandoen skal afvikles inden i et korrekt konfigureret environement for at
det virker. Se scriptet `testsuites\google_search\run_autoit.bat` for hvordan
man gør dette.

## Registrering af målinger i AutoIT scripts

Første gang et script køres vil det automatisk oprette en testsuite ud fra
scriptets navn og den mappe scriptet er placeret i. Hver gang scriptet afvikles
vil der blive registereret en script-afvikling under testsuiten og målinger
angivet i scriptet vil blive registeret under denne afvikling efterhånden som
de udføres.

For at starte en måling kaldes metoden
`AppmonitorCreateMeasure("Navn på måling")` med et enkelt
argument, navnet på den måling der skal udføres. Når målingen er overstået
kaldes metoden `AppmonitorCompleteMeasure()` og tiden mellem de to kald vil
automatisk blive registreret. Mens målingen står på kan man kalde metoden
`AppmonitorCheckCurrentMeasure(@error, "Eventuel besked")` for at afbryde
målingen hvis `@error` er forskellig fra værdien 0. Hvis man angiver en besked
som andet argument vil denne besked blive gemt som fejl-årsag i tilfælde af
fejl.

Et eksempel på en komplet måling, der gør brug af ovenstående:

    AppmonitorCreateMeasure("Klik på Aalborg Kommune link")
    _IELinkClickByText($oIE, "Aalborg Kommune: Borger");
    AppmonitorCheckError(@error, "Kunne klikke på link")
    AppmonitorWaitForId($oIE, "main-search")
    AppmonitorCheckError(@error, "Kunne ikke finde main-search element på aalborg.dk")

[](_ comment to disable wrong highligting in Komodo Edit)
