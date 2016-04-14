@echo off
call %~dp0%..\configure_environment.bat

set SQL=
set SQL=%SQL% insert into django_migrations (app, name, applied)
set SQL=%SQL% select 'appmonitor', '0001_initial', DATETIME('now')
set SQL=%SQL% where not exists (
set SQL=%SQL%  select 1 from django_migrations
set SQL=%SQL%  where app='appmonitor' and name='0001_initial'
set SQL=%SQL% );

echo %SQL% | sqlite3.exe %~dp0%..\db.sqlite3
pause
