@echo off
call %~dp0%..\..\configure_environment.bat
python -m appmonitor.autoit %~dp0%google_search.au3
