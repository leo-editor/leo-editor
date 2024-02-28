@echo off

echo cd leo-editor
cd %~dp0..\..

echo pip freeze > temp_requirements.txt
call pip freeze > temp_requirements.txt

rem A hack: Remove leo.egg-info

echo del leo.egg-info
del leo.egg-info

echo pip uninstall -r temp_requirements.txt -y
call pip uninstall -r temp_requirements.txt -y --verbose

echo del temp_requirements.txt
del temp_requirements.txt

echo pip list
call pip list

echo done!