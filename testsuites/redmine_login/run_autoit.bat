@echo off
call %~dp0%..\..\configure_environment.bat
call wrap_autoit %~dp0%appmonitor.au3
pause