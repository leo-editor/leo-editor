echo off
::cd c:\Repos\leo-editor
call set-repo-dir

rem: See leo-editor/setup.cfg for defaults.

echo flake8-leo
py -m flake8 %*
