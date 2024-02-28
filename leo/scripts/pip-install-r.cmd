@echo off

rem Install all of Leo's requirements. This does *not* install leo itself.

echo cd leo-editor
cd %~dp0..\..

echo pip install -r requirements.txt --no-warn-script-location
pip install -r requirements.txt --no-warn-script-location
