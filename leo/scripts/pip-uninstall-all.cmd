@echo off

echo cd leo-editor
cd %~dp0..\..

echo pip freeze > temp_requirements.txt
call pip freeze > temp_requirements.txt

rem A hack: Remove leo.egg-info if it exists from a legacy installation.
echo del leo.egg-info
del leo.egg-info

echo pip uninstall -r temp_requirements.txt -y
call pip uninstall -r temp_requirements.txt -y

echo del temp_requirements.txt
del temp_requirements.txt

echo pip list
call pip list

echo done!