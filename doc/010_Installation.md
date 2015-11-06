# Installation

For at installere løsningen gøres følgende:

* Hent og installer den seneste version af python 2.7 .MSI fra
  [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)
* Hent den seneste version af softwaren fra github:
  [https://github.com/magenta-aps/aalborg-monitor](https://github.com/magenta-aps/aalborg-monitor)
* Pak filerne ud hvis du hentede softwaren som et zip-arkiv
* Åbn mappen med filerne fra projektet
* Kør `initial_setup.bat` scriptet i roden af projektet

Hvis Python ikke er blevet installeret på standard-lokationen og `python.exe`
ikke er til stede i `PATH` kan det være nødvendigt at åbne en kommandoprompt,
sætte `PATHON_PATH` environment variablen op til at pege på roden af
python installationen, og derefter afvikle `initial_setup.bat`.

Hvis du skal bruge Selenium-baserede tests vil det være nødvendigt at sætte
internet explorer op til at have samme sikkerhedsniveau for alle
sikkerhedszoner.
