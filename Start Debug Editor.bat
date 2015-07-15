@ECHO OFF
call %~dp0%configure_environment.bat
SET APPMONITOR_SQLITE_FILE=%~dp0%db.sqlite3
SET APPMONITOR_RUN_ID=1
START AutoIT\SciTe\SciTe.exe