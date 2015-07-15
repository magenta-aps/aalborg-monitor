@echo off

call %~dp0%..\..\configure_environment.bat

python -m appmonitor.autoit %~dp0%run.au3

pause