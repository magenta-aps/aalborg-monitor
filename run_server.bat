@echo off
call %~dp0%configure_environment.bat
start python manage.py runserver
