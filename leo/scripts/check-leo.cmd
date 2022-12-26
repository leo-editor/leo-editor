echo off
cd c:\Repos\leo-editor

echo check-leo
call reindent-leo.cmd
call beautify-leo.cmd
call flake8-leo.cmd
