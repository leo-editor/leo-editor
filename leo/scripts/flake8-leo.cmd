echo off
cd c:\Repos\leo-editor
rem: See leo-editor/setup.cfg for defaults.
python -m flake8 %*
