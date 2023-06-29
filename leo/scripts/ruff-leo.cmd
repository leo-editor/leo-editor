@echo off
cd %~dp0..\..

echo ruff leo/core
call python -m ruff leo/core

echo ruff leo/commands
call python -m ruff leo/commands
