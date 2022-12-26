echo off
cd c:\Repos\leo-editor
rem: See leo-editor/setup.cfg for defaults.

echo flake8-leo
python -m flake8 %*
