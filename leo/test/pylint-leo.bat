echo off
rem ekr pylint-leo.bat

rem *** Most warnings are disabled in the .rc file.

rem E0602 Undefined variable
rem E1101 Instance of <class> has no x member

echo cd c:\leo.repo\trunk\leo
cd c:\leo.repo\trunk\leo

REM tests that fail...
goto all

echo tests that fail with dangerous settings enabled...

echo .
echo leoTkinterFind.py Dangerous: E1101,E1103: many Erroneous errors given.
call pylint.bat core\leoTkinterFind.py   --rcfile=test\pylint-leo-rc.txt

echo .
echo leoTkinterFrame.py Harmless: W0221: mismatch between Tk.Text methods and overridden methods.
echo leoTkinterFrame.py Dangerous: E1101 : many ERRONEOUS errors given
call pylint.bat core\leoTkinterFrame.py  --disable-msg=W0221 --rcfile=test\pylint-leo-rc.txt

echo .
echo leoTkinterMenu.py Dangerous: E1101: many ERRONEOUS errors given.
call pylint.bat core\leoTkinterMenu.py   --rcfile=test\pylint-leo-rc.txt

goto done

:all
echo all tests, suppressing known errors...

echo .
echo runLeo.py Harmless: W0611 (import pychecker)
call pylint.bat core\runLeo.py            --disable-msg=W0611 --rcfile=test\pylint-leo-rc.txt
echo .
echo leoApp.py
call pylint.bat core\leoApp.py           --rcfile=test\pylint-leo-rc.txt
echo .
echo leoAtFile.py
call pylint.bat core\leoAtFile.py        --rcfile=test\pylint-leo-rc.txt
echo .
echo leoChapters.py
call pylint.bat core\leoChapters.py      --rcfile=test\pylint-leo-rc.txt
echo .
echo leoCommands.py
call pylint.bat core\leoCommands.py      --rcfile=test\pylint-leo-rc.txt
echo .
echo leoEditCommands.py
call pylint.bat core\leoEditCommands.py  --rcfile=test\pylint-leo-rc.txt
echo .
echo leoFileCommands.py
call pylint.bat core\leoFileCommands.py  --rcfile=test\pylint-leo-rc.txt
echo .
echo leoFind.py
call pylint.bat core\leoFind.py          --rcfile=test\pylint-leo-rc.txt
echo .
echo leoFrame.py
call pylint.bat core\leoFrame.py         --rcfile=test\pylint-leo-rc.txt
echo .
echo leoGlobals.py
call pylint.bat core\leoGlobals.py       --rcfile=test\pylint-leo-rc.txt
echo .
echo leoGui.py
call pylint.bat core\leoGui.py           --rcfile=test\pylint-leo-rc.txt
echo .
echo leoImport.py
call pylint.bat core\leoImport.py        --rcfile=test\pylint-leo-rc.txt
echo .
echo leoMenu.py
call pylint.bat core\leoMenu.py          --rcfile=test\pylint-leo-rc.txt
echo .
echo leoNodes.py
call pylint.bat core\leoNodes.py         --rcfile=test\pylint-leo-rc.txt
echo .
echo leoPlugins.py
call pylint.bat core\leoPlugins.py       --rcfile=test\pylint-leo-rc.txt
echo .
echo leoTangle.py
call pylint.bat core\leoTangle.py        --rcfile=test\pylint-leo-rc.txt
echo .
echo leoUndo.py harmless: W0102: dangerous default argument: []
call pylint.bat core\leoUndo.py          --disable-msg=W0102 --rcfile=test\pylint-leo-rc.txt
echo .
echo leoTkinterDialog.py
call pylint.bat core\leoTkinterDialog.py --rcfile=test\pylint-leo-rc.txt
echo .
echo leoTkinterFind.py Dangerous: E1101,E1103: many ERRONEOUS errors
call pylint.bat core\leoTkinterFind.py   --disable-msg=E1101,E1103 --rcfile=test\pylint-leo-rc.txt
echo .
echo leoTkinterGui.py
call pylint.bat core\leoTkinterGui.py    --rcfile=test\pylint-leo-rc.txt
echo .
echo leoTkinterFrame.py Harmless: W0221: mismatch between Tk.Text methods and overridden methods.
echo leoTkinterFrame.py Dangerous: E1101: many ERRONEOUS errors
call pylint.bat core\leoTkinterFrame.py  --disable-msg=W0221,E1101 --rcfile=test\pylint-leo-rc.txt
echo .
echo leoTkinterKeys.py
call pylint.bat core\leoTkinterKeys.py   --rcfile=test\pylint-leo-rc.txt
echo .
echo leoTkinterMenu.py Dangerous: E1101: many ERRONEOUS errors
call pylint.bat core\leoTkinterMenu.py   --disable-msg=E1101 --rcfile=test\pylint-leo-rc.txt
echo .
echo leoTkinterTree.py Dangerous: E1101: many ERRONEOUS errors
call pylint.bat core\leoTkinterTree.py   --disable-msg=E1101 --rcfile=test\pylint-leo-rc.txt

:done
echo "*****done*****"
cd c:\leo.repo\trunk\leo\test

pause