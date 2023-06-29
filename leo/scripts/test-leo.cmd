@echo off
cd %~dp0..\..

call reindent-leo.cmd

echo test-leo
py -m unittest %*
