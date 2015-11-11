# Arbejde med gemte konfigurations-værdier

Ved at bruge administrations-interfacet fra
[webserveren](020_Opstart af webserveren.md)
er det muligt at
opsætte konfigurations-værdier som kan tilgås og anvendes i scripts.

Værdier kan oprettes og redigerings ved at klikke på linket
`Konfigurations-værdier` i hovedmenuen for roden af webserveren.

Nedenfor findes eksempler på hvordan sådanne værdier tilgås fra scripts.

## AutoIT

    Local $hDb = AppmonitorConnectDb()
    Local $sMyConfigValue = AppmonitorGetDbConfigValue($hDb, "myConfigName")
    ;~ Do something with $sMyConfigValue

## Selenium

    from appmonitor.models import ConfigurationValue
    confval = ConfigurationValue.objects.get(name="myConfigName").value
    # Do something with confval

## Krypterede værdier for Aalborg test-suiter

Til de to testsuiter udviklet til Aalborg kommune skal der opsættes
følgende konfigurations-værdier:

### DUBU

Der skal oprettes en konfiguratons-værdi med nøglen
`krypteret_digital_signatur_login` indeholdende den krypterede værdi af
password'et der bruges til at logge på med digital signatur.

### Workbase

Der skal oprettes en konfiguratons-værdi med nøglen
`krypteret_workbase_input` indeholdende den krypterede værdi af
CPR-nummeret på den person der ønskes fremsøgt i forbindelse med tests.
