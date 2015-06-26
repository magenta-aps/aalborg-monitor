@echo off

REM set root dir
set APPMONITOR_ROOT_DIR=%~dp0%

REM load virtual env
call %APPMONITOR_ROOT_DIR%env\Scripts\activate

REM add AutoIT to the path
set PATH=%PATH%;%APPMONITOR_ROOT_DIR%bin;%APPMONITOR_ROOT_DIR%AutoIT

REM Configure python include path
IF "x%PYTHONPATH%" == "x" GOTO empty_path

REM if path is set append to it
set PYTHONPATH=%PYTHONPATH%;%~dp0%
GOTO finish

:empty_path
REM when path is not set, just set it
SET PYTHONPATH=%~dp0%
GOTO finish

:finish
REM tell django which file to use for settings
SET DJANGO_SETTINGS_MODULE=aalborgmonitor.settings
