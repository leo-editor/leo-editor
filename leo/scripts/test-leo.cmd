@echo off
call %~dp0\set-repo-dir

echo test-leo
py -m unittest %*
