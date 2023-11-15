@echo off
cd %~dp0..\..

rem qt_main.py is auto generated.
rem call py -m ruff leo/plugins/qt*.py

echo ruff leo/core, leo/commands, leo/plugins/qt...
call py -m ruff leo/core
call py -m ruff leo/commands
call py -m ruff leo/plugins/qt_gui.py
call py -m ruff leo/plugins/qt_text.py
call py -m ruff leo/plugins/qt_tree.py
