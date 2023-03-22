echo off
call %~dp0\set-repo-dir

echo reindent leo/core
call reindent leo/core

echo reindent leo/commands
call reindent leo/commands
