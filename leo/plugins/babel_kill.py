#!/usr/bin/python
#coding=utf-8
#@+leo-ver=5-thin
#@+node:ekr.20180504191650.17: * @file babel_kill.py
#@@first
#@@first
#@@language python
#@@tabwidth -4

from PyQt5 import QtWidgets     # Can't fail, because Leo-Babel won't run without it.
import signal                   # Can't fail, because Leo-Babel won't run without it.

app = QtWidgets.QApplication([__file__])

try:
    import os
    import sys

except ImportError as err:
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    errMsg = ('Python Package required by Leo-Babel is missing.\n'
        'Importing Python module {0} failed.'.format(err.name))
    QtWidgets.QMessageBox.critical(None, 'Missing Python Package', errMsg)
    exit(1)

pidTarg = int(sys.argv[1])
msg = 'Kill Leo-Babel process {0}?'.format(pidTarg)
reply = QtWidgets.QMessageBox.question(None, msg, msg,
         QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
if reply == QtWidgets.QMessageBox.Yes:
    os.kill(pidTarg, signal.SIGHUP) # This kills most Bash scripts and most Python scripts
#@-leo
