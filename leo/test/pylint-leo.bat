echo off
rem ekr pylint-leo.bat

rem *** Most warnings are disabled in the .rc file.

rem E0602 Undefined variable
rem E1101 Instance of <class> has no x member

REM passed...
REM *** leoEditCommands.py: Dangerous: E1101
REM *** leoGlobals.py: Dangerous: E0602,E1101.
REM *** leoTkinterFrame.py: Harmless: W0221: mismatch between Tk.Text methods and overridden methods.
rem call pylint.bat c:\prog\tigris-cvs\leo\src\leoAtFile.py        --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
rem call pylint.bat c:\prog\tigris-cvs\leo\src\leoChapters.py      --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
rem call pylint.bat c:\prog\tigris-cvs\leo\src\leoCommands.py      --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
rem call pylint.bat c:\prog\tigris-cvs\leo\src\leoEditCommands.py  --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
rem call pylint.bat c:\prog\tigris-cvs\leo\src\leoFileCommands.py  --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
rem call pylint.bat c:\prog\tigris-cvs\leo\src\leoFind.py          --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
rem call pylint.bat c:\prog\tigris-cvs\leo\src\leoFrame.py         --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
rem call pylint.bat c:\prog\tigris-cvs\leo\src\leoGlobals.py       --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
rem call pylint.bat c:\prog\tigris-cvs\leo\src\leoGui.py           --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
rem call pylint.bat c:\prog\tigris-cvs\leo\src\leoImport.py        --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
rem call pylint.bat c:\prog\tigris-cvs\leo\src\leoMenu.py          --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
rem call pylint.bat c:\prog\tigris-cvs\leo\src\leoNodes.py         --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
rem call pylint.bat c:\prog\tigris-cvs\leo\src\leoPlugins.py       --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
rem call pylint.bat c:\prog\tigris-cvs\leo\src\leoTangle.py        --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
rem call pylint.bat c:\prog\tigris-cvs\leo\src\leoUndo.py          --disable-msg=W0102 --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
rem call pylint.bat c:\prog\tigris-cvs\leo\src\leoTkinterDialog.py --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
rem call pylint.bat c:\prog\tigris-cvs\leo\src\leoTkinterFind.py   --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
rem call pylint.bat c:\prog\tigris-cvs\leo\src\leoTkinterGui.py    --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
rem call pylint.bat c:\prog\tigris-cvs\leo\src\leoTkinterFrame.py  --disable-msg=W0221 --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
rem call pylint.bat c:\prog\tigris-cvs\leo\src\leoTkinterKeys.py   --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
rem call pylint.bat c:\prog\tigris-cvs\leo\src\leoTkinterMenu.py   --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
rem call pylint.bat c:\prog\tigris-cvs\leo\src\leoTkinterTree.py   --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt

REM echo on

echo leoAtFile.py
call pylint.bat c:\prog\tigris-cvs\leo\src\leoAtFile.py        --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
echo leoChapters.py
call pylint.bat c:\prog\tigris-cvs\leo\src\leoChapters.py      --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
echo leoCommands.py
call pylint.bat c:\prog\tigris-cvs\leo\src\leoCommands.py      --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
echo leoEditCommands.py
call pylint.bat c:\prog\tigris-cvs\leo\src\leoEditCommands.py  --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
echo leoFileCommands.py
call pylint.bat c:\prog\tigris-cvs\leo\src\leoFileCommands.py  --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
echo leoFind.py
call pylint.bat c:\prog\tigris-cvs\leo\src\leoFind.py          --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
echo leoFrame.py
call pylint.bat c:\prog\tigris-cvs\leo\src\leoFrame.py         --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
echo leoGlobals.py
call pylint.bat c:\prog\tigris-cvs\leo\src\leoGlobals.py       --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
echo leoGui.py
call pylint.bat c:\prog\tigris-cvs\leo\src\leoGui.py           --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
echo leoImport.py
call pylint.bat c:\prog\tigris-cvs\leo\src\leoImport.py        --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
echo leoMenu.py
call pylint.bat c:\prog\tigris-cvs\leo\src\leoMenu.py          --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
echo leoNodes.py
call pylint.bat c:\prog\tigris-cvs\leo\src\leoNodes.py         --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
echo leoPlugins.py
call pylint.bat c:\prog\tigris-cvs\leo\src\leoPlugins.py       --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
echo leoTangle.py
call pylint.bat c:\prog\tigris-cvs\leo\src\leoTangle.py        --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
echo leoUndo.py
call pylint.bat c:\prog\tigris-cvs\leo\src\leoUndo.py          --disable-msg=W0102 --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
echo leoTkinterDialog.py
call pylint.bat c:\prog\tigris-cvs\leo\src\leoTkinterDialog.py --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
echo leoTkinterFind.py
call pylint.bat c:\prog\tigris-cvs\leo\src\leoTkinterFind.py   --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
echo leoTkinterGui.py
call pylint.bat c:\prog\tigris-cvs\leo\src\leoTkinterGui.py    --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
echo leoTkinterFrame.py
call pylint.bat c:\prog\tigris-cvs\leo\src\leoTkinterFrame.py  --disable-msg=W0221 --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
echo leoTkinterKeys.py
call pylint.bat c:\prog\tigris-cvs\leo\src\leoTkinterKeys.py   --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
echo leoTkinterMenu.py
call pylint.bat c:\prog\tigris-cvs\leo\src\leoTkinterMenu.py   --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt
echo leoTkinterTree.py
call pylint.bat c:\prog\tigris-cvs\leo\src\leoTkinterTree.py   --rcfile=c:\prog\tigris-cvs\leo\test\pylint-leo-rc.txt

echo "*****done*****"

pause