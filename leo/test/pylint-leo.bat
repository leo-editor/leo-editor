echo off
rem ekr pylint-leo.bat

rem *** Most warnings are disabled in the .rc file.

rem E0602 Undefined variable
rem E1101 Instance of <class> has no x member

echo cd c:\leo.repo\leo-editor\trunk\leo
cd c:\leo.repo\leo-editor\trunk\leo

REM tests that fail with dangerous settings enabled...

REM goto passed

echo leoEditCommands.py  Dangerous: E0602,E1101
call pylint.bat src\leoEditCommands.py  --disable-msg=W0221 --rcfile=test\pylint-leo-rc.txt

echo leoGlobals.py Dangerous: E0602,E1101
call pylint.bat src\leoGlobals.py       --disable-msg=W0104 --rcfile=test\pylint-leo-rc.txt

echo leoTkinterFind.py Dangerous: E1101,E1103
call pylint.bat src\leoTkinterFind.py   --disable-msg= --rcfile=test\pylint-leo-rc.txt

echo leoTkinterGui.py Dangerous: E1101
call pylint.bat src\leoTkinterGui.py    --disable-msg= --rcfile=test\pylint-leo-rc.txt

echo leoTkinterFrame.py Harmless: W0221: mismatch between Tk.Text methods and overridden methods.
echo leoTkinterFrame.py Dangerous: E1101
call pylint.bat src\leoTkinterFrame.py  --disable-msg=W0221 --rcfile=test\pylint-leo-rc.txt

echo leoTkinterKeys.py Dangerous: E1101
call pylint.bat src\leoTkinterKeys.py   --disable-msg= --rcfile=test\pylint-leo-rc.txt

echo leoTkinterMenu.py Dangerous: E1101
call pylint.bat src\leoTkinterMenu.py   --disable-msg= --rcfile=test\pylint-leo-rc.txt

goto done

rem passed...
:passed

echo leo.py
call pylint.bat src\leo.py              --rcfile=test\pylint-leo-rc.txt
echo leoApp.py
call pylint.bat src\leoApp.py           --rcfile=test\pylint-leo-rc.txt
echo leoAtFile.py
call pylint.bat src\leoAtFile.py        --rcfile=test\pylint-leo-rc.txt
echo leoChapters.py
call pylint.bat src\leoChapters.py      --rcfile=test\pylint-leo-rc.txt
echo leoCommands.py
call pylint.bat src\leoCommands.py      --rcfile=test\pylint-leo-rc.txt
echo leoEditCommands.py  Dangerous: E0602,E1101
call pylint.bat src\leoEditCommands.py  --disable-msg=W0221,E0602,E1101 --rcfile=test\pylint-leo-rc.txt
echo leoFileCommands.py
call pylint.bat src\leoFileCommands.py  --rcfile=test\pylint-leo-rc.txt
echo leoFind.py
call pylint.bat src\leoFind.py          --rcfile=test\pylint-leo-rc.txt
echo leoFrame.py
call pylint.bat src\leoFrame.py         --rcfile=test\pylint-leo-rc.txt
echo leoGlobals.py Dangerous: E0602,E1101
call pylint.bat src\leoGlobals.py       --disable-msg=W0104,E0602,E1101 --rcfile=test\pylint-leo-rc.txt
echo leoGui.py
call pylint.bat src\leoGui.py           --rcfile=test\pylint-leo-rc.txt
echo leoImport.py
call pylint.bat src\leoImport.py        --rcfile=test\pylint-leo-rc.txt
echo leoMenu.py
call pylint.bat src\leoMenu.py          --rcfile=test\pylint-leo-rc.txt
echo leoNodes.py
call pylint.bat src\leoNodes.py         --rcfile=test\pylint-leo-rc.txt
echo leoPlugins.py
call pylint.bat src\leoPlugins.py       --rcfile=test\pylint-leo-rc.txt
echo leoTangle.py
call pylint.bat src\leoTangle.py        --rcfile=test\pylint-leo-rc.txt
echo leoUndo.py
call pylint.bat src\leoUndo.py          --disable-msg=W0102 --rcfile=test\pylint-leo-rc.txt
echo leoTkinterDialog.py
call pylint.bat src\leoTkinterDialog.py --rcfile=test\pylint-leo-rc.txt
echo leoTkinterFind.py Dangerous: E1101,E1103
call pylint.bat src\leoTkinterFind.py   --disable-msg=E1101,E1103 --rcfile=test\pylint-leo-rc.txt
echo leoTkinterGui.py Dangerous: E1101
call pylint.bat src\leoTkinterGui.py    --disable-msg=E1101 --rcfile=test\pylint-leo-rc.txt
echo leoTkinterFrame.py Harmless: W0221: mismatch between Tk.Text methods and overridden methods.
echo leoTkinterFrame.py Dangerous: E1101
call pylint.bat src\leoTkinterFrame.py  --disable-msg=W0221,E1101 --rcfile=test\pylint-leo-rc.txt
echo leoTkinterKeys.py Dangerous: E1101
call pylint.bat src\leoTkinterKeys.py   --disable-msg=E1101 --rcfile=test\pylint-leo-rc.txt
echo leoTkinterMenu.py Dangerous: E1101
call pylint.bat src\leoTkinterMenu.py   --disable-msg=E1101 --rcfile=test\pylint-leo-rc.txt
echo leoTkinterTree.py
call pylint.bat src\leoTkinterTree.py   --rcfile=test\pylint-leo-rc.txt

:done
echo "*****done*****"

pause