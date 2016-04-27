@echo off
call %~dp0%..\configure_environment.bat

set SQL=
set SQL=%SQL% update appmonitor_testmeasure
set SQL=%SQL% set spent_time=(julianday(ended) - julianday(started))*24*60*60
set SQL=%SQL%  where started is not null and ended is not null;

echo %SQL% | sqlite3.exe %~dp0%..\db.sqlite3
pause
