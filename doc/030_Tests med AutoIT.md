# Udvikling af tests med AutoIT

For at lave AutoIT-baserede tests skal man lave et AutoIT script og inkludere
filen `lib\autoit\appmonitor.au3` i toppen af scriptet. Dette vil give adgang
til metoder der gør det muligt at arbejde med Appmonitor-databasen.

Se `testsuites\google_search\google_search.au3` for et eksempel.

Under udvikling kan det være en fordel at starte en editor med scriptet
`Run Debug Editor.bat` der findes i roden af projektet. Denne editor vil
have det nødvendige environment der skal til for at man kan afvikle scripts
og stadig lave databaseoperationer. Dette gør det muligt at bruge editorens
debug-muligheder.

Målinger foretaget fra scripts afviklet under debug-editoren vil blive gemt
under en skjult `DEBUG` testsuite og vil ikke være mulige at se med mindre
man slår op direkte i datasen via admin-interfacet.

For at afvikle AutoIT scripts køres følgende:

`python -m appmonitor.autoit <name-of-script>.au3`

Kommandoen skal afvikles inden i et korrekt konfigureret environement for at
det virker. Se scriptet `testsuites\google_search\run_autoit.bat` for hvordan
man gør dette.
