echo off
cd c:\Repos\leo-editor

call reindent-leo.cmd
call beautify-leo.cmd
call flake8-leo.cmd
