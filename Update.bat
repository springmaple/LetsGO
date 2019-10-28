@ECHO OFF
SET CURRENT_DIR=%cd%
SET SCRIPT_DIR=%~dp0
CD /D %SCRIPT_DIR%
git checkout master && git pull
FOR /F %a in ('git describe --tags') do git checkout %a
pip install -r requirements.txt
CD /D %CURRENT_DIR%
ECHO OK...
PAUSE