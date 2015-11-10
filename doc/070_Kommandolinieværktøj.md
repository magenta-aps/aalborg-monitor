# Kommandolinie-værktøj

Kommandolinie-værktøjet for løsningen er lavet som en udvidelse til
[django-admin eller manage.py](https://docs.djangoproject.com/en/1.8/ref/django-admin/).

Den nemmeste måde at tilgå funktionerne på er ved at klikke på genvejen
`Command Line DjangoEnv.bat` i roder af projektet. Dette åbner en kommando-prompt
hvor man har adgang til `django-admin` kommandoen.

For at få en liste over de forskellige kommandoer afvikles kommandoen
`django-admin help`.

Appmonitor-specifikke kommandoer vil blive listet i toppen
af output'et fra denne kommando.

For at få yderligere information om de enkelte
kommandoer køres `django-admin help <kommandonavn>`.

## Listning af test-suiter

For at få en liste over test-suiter køres kommandoen

`django-admin listsuites`

Dette viser en liste over de forskellige test-suiter og deres id'er.

## Generering af Excel-udtræk

For at lave et Excel-udtræk køres følgende kommando:

`django-admin exportexcel <id> <filnavn.xls>`

hvor `<id>` er et id på en testsuite fundet via `django-admin listsuites`
kommandoen og `<filnavn.xls>` er det filnavn man ønsker rapporten skrevet til.

## Afvikling fra batch-scripts

Django-admin kommandoer vil kunne udføres fra `.bat`-scripts hvis disse kalder
scriptet `configure_environment.bat` fra roden af projektet inden
django-admin kommandoerne udføres.