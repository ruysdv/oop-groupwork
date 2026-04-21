@echo off
chcp 65001 >nul
title Server Client

set "SERVER_HOME=%~dp0"
set "PYTHON_EXE=%SERVER_HOME%python\python.exe"
set "PYTHONPATH=%SERVER_HOME%Lib"

cd /d "%SERVER_HOME%server"
echo Don't close this window!
echo http://127.0.0.1:2333
echo Ctrl+C to stop
echo 666666666666666666666666666666666666666666

"%PYTHON_EXE%" main.py

pause