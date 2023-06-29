@echo off
cd %~dp0..\..

echo ruff leo/core
call py -m ruff leo/core

echo ruff leo/commands
call py -m ruff leo/commands
