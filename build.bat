@ECHO OFF
SET CURRENT_DIR=%cd%
SET SCRIPT_DIR=%~dp0
RMDIR bin /s /q
CD /D %SCRIPT_DIR%\src
python setup.py build -b ..\bin
CD /D %CURRENT_DIR%
