@echo off

echo cd leo-editor
cd %~dp0..\..

echo pip install -r requirements.txt --no-warn-script-location
pip install -r requirements.txt --no-warn-script-location