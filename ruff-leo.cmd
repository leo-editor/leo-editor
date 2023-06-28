@echo off
call %~dp0\set-repo-dir

echo ruff leo/core
call ruff leo/core

echo ruff leo/commands
call ruff leo/commands
