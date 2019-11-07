@ECHO OFF
SET CURRENT_DIR=%cd%
SET SCRIPT_DIR=%~dp0\src
CD /D %SCRIPT_DIR%
python index.py
