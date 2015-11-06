# Working with encrypted configurable variables

Systemet tillader brug af to-vejs kryptering så det er muligt at gemme
følsomme data som konfigurations-værdier i databasen.

For at gemme en krypteret værdi skal du starte krypteringsværktøjet via
scriptet `run_crypt_tool.bat` i roden af projektet. Brug værktøjet til at
generere en krypteret værdi og gem denne værdi på normal vis som en
konfigurations-værdi i databasen.

Når den krypterede værdi er gemt kan man bruge koden nedenfor til at tilgå
den dekrypterede værdi fra scripts.

## AutoIT

    Local $hDb = AppmonitorConnectDb()
    Local $sEncrypted = AppmonitorGetDbConfigValue($hDb, "myCryptVal")
    Local $sDecrypted = AppmonitorDecrypt($sEncrypted)
    ;~ Do something with $sDecrypted

## Selenium

    from appmonitor.models import ConfigurationValue
    from appmonitor.utils import decrypt_from_hex
    encrypted = ConfigurationValue.objects.get(name="myCryptVal").value
    decrypted = decrypt_from_hex(encrypted)
    # Do something with decrypted
