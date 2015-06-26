@echo off
call %~dp0%..\..\configure_environment.bat
set APPMONITOR_SQLITE_FILE=..\..\db.sqlite3
set APPMONITOR_RUN_ID=6
AutoIt3.exe appmonitor.au3
pause