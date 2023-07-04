@echo off
cd %~dp0..\..

echo ruff leo/core
call py -m ruff leo/core

echo ruff leo/commands
call py -m ruff leo/commands

rem qt_main.py is auto generated.
rem call py -m ruff leo/plugins/qt*.py

echo ruff leo/plugins/qt...
call py -m ruff leo/plugins/qt_gui.py
call py -m ruff leo/plugins/qt_text.py
call py -m ruff leo/plugins/qt_tree.py
