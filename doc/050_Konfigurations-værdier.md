# Arbejde med gemte konfigurations-værdier

Ved at bruge administrations-interfacet fra webserveren er det muligt at
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
