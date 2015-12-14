# Afvikling af test-scripts via Windows Planlagte Opgaver

Det er muligt at afvikle test-scripts via windows planlagte opgaver ved at
oprette en opgave der kører `.bat`-filen der starter testen. Man skal dog være
opmærksom på følgende:

* Tests der sættes op til at afvikles uden at brugeren er logget ind vil
  ikke have adgang til for eksempel digital signatur for brugeren.
* AutoIT-baserede tests der sættes op til at afvikles uden at brugeren er
  logget ind vil ikke kunne bruge Windows-kontroller som for eksempel knapper
  på java-applets, da disse ikke eksisterer i Internet Explorer sessioner der
  kører i baggrunden.

På grund af ovenstående vil man oftest have behov for at køre en test for en
bruger der allerede er logget ind. For samtidig at sikre adgangen til maskinen
vil det derfor være nødvendigt at logge brugeren ind og efterfølgende låse
maskinen. Dette giver igen nogen problemer, da operativsystemets fokus altid
vil være på login-skærmbilledet på en låst Windows-maskine.

Dette gør at følgende ikke er muligt:

* Man kan ikke bruge AutoIT kommandoer der forventer et aktivt vindue såsom
  `Send` og `MouseClick`. I stedet skal man lokalisere en kontrol og bruge de
  tilsvarende `Control...` kommandoer. Se
  https://www.autoitscript.com/wiki/FAQ#Why_doesn.27t_my_script_work_on_a_locked_workstation.3F
  for mere information.
* Det er i visse tilfælde ikke muligt at afsende en formular via tryk på enter.
  Man bør i stedet bruge en submit-knap, hvis denne findes, og eller bruge
  javascript til at simulere en submit-event.

## Anbefalet opsætning for gentaget afvikling af en test

Det anbefales at en planlagt opgave sættes op som følger:

* Generelt
    * "Kør kun, når brugeren er logget på" valgt
    * "Kør med højeste rettigheder" valgt
    * "Skjult" ikke valgt
* Udløsere - opret en enkelt med følgende indstillinger:
    * "Daglig" valgt
    * Passende førstegangs starttidspunkt
    * Gentag hver 1 dag
    * Gentag opgaven hver X minutter/timer for en varighed på 1 dag
    * Stop en opgaver der kører længere end X minutter
* Handlinger - open enkelt "Start et program"
    * Program/script: `.bat`-filen der starter testen
    * Start i (valgfri): Mappen hvor `.bat`-filen ligger
* Betingelser
    * Sættes op efter behov
* Indstillinger
    * Hvis opgaven allerede kører, anvendes den følgende regel:
      Stop den eksisterende forekomst
    * Resten sættes op efter behov

Ovenstående skulle gerne sikre at opgaven udføres hver X minutter og forsøger
at lukke eksisterende opgaver der ikke er afsluttet ned. Husk at låse
computeren i stedet for at logge af, da testen ellers ikke vil blive afviklet.
