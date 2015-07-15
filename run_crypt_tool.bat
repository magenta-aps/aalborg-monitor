@echo off
call %~dp0%configure_environment.bat
start Autoit3.exe %~dp0%lib\autoit\crypt_tool.au3
