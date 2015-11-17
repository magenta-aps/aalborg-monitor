@echo off
call %~dp0%..\..\configure_environment.bat
python %~dp0%google_search_ie8.py
