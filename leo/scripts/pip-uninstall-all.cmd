@echo off

echo cd leo-editor
cd %~dp0..\..

echo pip freeze > temp_requirements.txt
call pip freeze > temp_requirements.txt

rem A hack: Remove leo.egg-info if it exists from a legacy installation.
echo del leo.egg-info
del leo.egg-info

rem Uninstall all requirements, prompting for each in turn.
rem In other words, the -y option is suitable only for testing.
echo pip uninstall -r temp_requirements.txt
call pip uninstall -r temp_requirements.txt

echo del temp_requirements.txt
del temp_requirements.txt

echo pip list
call pip list

echo done!
