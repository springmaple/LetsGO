@ECHO OFF
SET CURRENT_DIR=%cd%
SET SCRIPT_DIR=%~dp0
CD /D %SCRIPT_DIR%
git pull
pip install -r requirements.txt
CD /D %CURRENT_DIR%
ECHO OK...
PAUSE