#@+leo-ver=5-thin
#@+node:tom.20230424140347.1: * @file ../plugins/rpcalc.py
#@@language python
"""An RPN calculator plugin in a log tab panel.

Adapted from rpcalc.
"""

#@+<< rpcalc: imports >>
#@+node:tom.20230425232153.1: ** << rpcalc: imports >>
from __future__ import annotations
import sys
import os.path
import webbrowser
import math
from pathlib import PurePath
from typing import Any

from leo.core.leoQt import QtCore, MouseButton
from leo.core.leoQt import QtGui, FocusPolicy
from leo.core.leoQt import QtWidgets, QAction
from leo.core.leoQt import Shape, Shadow, KeyboardModifier
from leo.core.leoQt import Qt as Qt1

from leo.core.leoQt import WindowType, DialogCode

import leo.core.leoGlobals as g
from leo.plugins.mod_scripting import scriptingController

#@-<< rpcalc: imports >>
#@+<< rpcalc: Qt Name Assignments >>
#@+node:tom.20230428182001.1: ** << rpcalc: Qt Name Assignments >>
Qt = QtCore.Qt

QApplication = QtWidgets.QApplication
QButtonGroup  = QtWidgets.QButtonGroup
QCheckBox = QtWidgets.QCheckBox
QClipboard = QtGui.QClipboard
QColor = QtGui.QColor
QDialog = QtWidgets.QDialog

QDoubleValidator = QtGui.QDoubleValidator
QFrame = QtWidgets.QFrame
QGridLayout = QtWidgets.QGridLayout
QHBoxLayout = QtWidgets.QHBoxLayout
QGroupBox = QtWidgets.QGroupBox

QIcon = QtGui.QIcon
QLabel = QtWidgets.QLabel
QLineEdit = QtWidgets.QLineEdit
QListView = QtWidgets.QListView
QMenu = QtWidgets.QMenu
QLCDNumber = QtWidgets.QLCDNumber
QMainWindow = QtWidgets.QMainWindow
QMessageBox = QtWidgets.QMessageBox

QPalette = QtGui.QPalette
QPixmap = QtGui.QPixmap
QPoint = QtCore.QPoint
QPushButton = QtWidgets.QPushButton
QRadioButton = QtWidgets.QRadioButton
QSizePolicy = QtWidgets.QSizePolicy
QSpinBox = QtWidgets.QSpinBox

QSize = QtCore.QSize
QStatusBar = QtWidgets.QStatusBar
QTabWidget = QtWidgets.QTabWidget
QTextBrowser = QtWidgets.QTextBrowser
QTextDocument = QtGui.QTextDocument
QTimer = QtCore.QTimer
QTreeWidget = QtWidgets.QTreeWidget

QTreeWidgetItem = QtWidgets.QTreeWidgetItem
QUrl = QtCore.QUrl
QVBoxLayout = QtWidgets.QVBoxLayout
QValidator = QtGui.QValidator
QWidget = QtWidgets.QWidget

try:
    SegmentStyle = QLCDNumber.SegmentStyle
except AttributeError:
    SegmentStyle = Qt1

pyqtSignal = QtCore.pyqtSignal

g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.
#@-<< rpcalc: Qt Name Assignments >>

__version__ = 0.91
__author__ = 'Douglas W. Bell, Thomas B. Passin'

TABNAME = 'RPCalc'
module_path = PurePath(__file__).parent
iconPath = module_path / 'rpcalc' / 'icons'

#@+<< rpcalc: LICENCE >>
#@+node:ekr.20230617002028.1: ** << rpcalc: LICENCE >>
LICENSE = """\
This program is a modified version of the rpcalc program, a
Reverse Polish Notation (RPN) calculator.  It has been minimally modified
by Thomas B. Passin to run in a log frame tab in the Leo editor.  The license
remains the same as the original, which is reproduced here:

#****************************************************************************
# rpCalc, an RPN calculator
# Copyright (C) 2017, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY.  See the included LICENSE file for details.
#*****************************************************************************

The license for the modified code is:

#****************************************************************************
# rpCalc, an RPN calculator
# Copyright (C) 2017, Douglas W. Bell
# Modified for the Leo Editor by Thomas B. Passin
# Leo editor modifications Copyright (C) 2023, Thomas B. Passin.
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License (GPL), either Version 2 or any
# later version.  This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY.  See the included GPL 2 LICENSE file
# at rpcalc/docs.
#****************************************************************************
"""
#@-<< rpcalc: LICENCE >>

#@+others
#@+node:tom.20230424130102.154: **  optiondefaults
defaultList = [\
    "# Options for the rpCalc program",
    "#",
    "# Colors for extra views:",
    "UseDefaultColors    yes",
    "# If UseDefaultColors is no, use:",
    "BackgroundR         255",
    "BackgroundG         255",
    "BackgroundB         255",
    "ForegroundR         0",
    "ForegroundG         0",
    "ForegroundB         0",
    "#",
    "# The following options are set from within the program,",
    "# editing here is not recommended",
    "NumDecimalPlaces    4",
    "ThousandsSeparator  no",
    "ForceSciNotation    no",
    "UseEngNotation      no",
    "TrimExponents       no",
    "HideLcdHighlight    no",
    "AngleUnit           deg",
    "SaveStacks          yes",
    "ExtraViewStartup    no",
    "AltBaseStartup      no",
    "MaxHistLength       100",
    "ViewRegisters       no",
    "AltBaseBits         32",
    "UseTwosComplement   no",
    "#",
    "# Storage for persistant data",
    "Stack0              0.0",
    "Stack1              0.0",
    "Stack2              0.0",
    "Stack3              0.0",
    "Mem0                0.0",
    "Mem1                0.0",
    "Mem2                0.0",
    "Mem3                0.0",
    "Mem4                0.0",
    "Mem5                0.0",
    "Mem6                0.0",
    "Mem7                0.0",
    "Mem8                0.0",
    "Mem9                0.0",
    "#",
    "MainDlgXSize        0",
    "MainDlgYSize        0",
    "MainDlgXPos         0",
    "MainDlgYPos         0",
    "ExtraViewXSize      0",
    "ExtraViewYSize      0",
    "ExtraViewXPos       0",
    "ExtraViewYPos       0",
    "AltBaseXPos         0",
    "AltBaseYPos         0"]
#@@language python
#@@tabwidth -4
#@+node:tom.20230428180838.1: ** init
def init() -> bool:
    """Return True if the plugin has loaded successfully."""
    # 2031: Allow this plugin to run without Qt.
    g.registerHandler('after-create-leo-frame', onCreate)
    g.plugin_signon(__name__)
    return True
#@+node:tom.20230428190428.1: ** g.command rpcalc-toggle
@g.command('rpcalc-toggle')
def toggle_tab(event) -> None:
    c = event.c
    log = c.frame.log

    toggle_app_tab(log, TABNAME, widget = CalcDlg)
#@+node:tom.20230501083631.1: ** copyToClip
def copyToClip(text):
    """Copy text to the clipboard.
    """
    clip = QApplication.clipboard()
    if clip.supportsSelection():
        clip.setText(text, QClipboard.Selection)
    clip.setText(text)

#@+node:tom.20230428180647.1: ** onCreate
def onCreate(tag: str, keys: Any) -> None:
    global CMDR
    c = keys.get('c')
    if c:
        sc = scriptingController(c)
        sc.createIconButton(
            args = None,
            text = 'RPCalc',
            command = lambda: c.doCommandByName('rpcalc-toggle'),
            statusLine=None)
#@+node:tom.20230424130102.2: **  altbasedialog
#@+others
#@+node:tom.20230424130102.3: *3* class AltBaseDialog
class AltBaseDialog(QWidget): # type: ignore
    """Displays edit boxes for other number bases.
    """
    baseCode = {'X':16, 'O':8, 'B':2, 'D':10}
    #@+others
    #@+node:tom.20230424130102.4: *4* __init__
    def __init__(self, dlgRef, parent=None):
        QWidget.__init__(self, parent)
        self.dlgRef = dlgRef
        self.prevBase = None   # revert to prevBase after temp base change
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, False)
        self.setWindowTitle('rpCalc Alternate Bases')
        topLay = QVBoxLayout(self)
        self.setLayout(topLay)
        mainLay = QGridLayout()
        topLay.addLayout(mainLay)
        self.buttons = QButtonGroup(self)
        self.baseBoxes = {}
        hexButton = QPushButton('He&x')
        self.buttons.addButton(hexButton, 16)
        mainLay.addWidget(hexButton, 0, 0, Qt.AlignmentFlag.AlignRight)
        self.baseBoxes[16] = AltBaseBox(16, self.dlgRef.calc)
        mainLay.addWidget(self.baseBoxes[16], 0, 1)
        octalButton = QPushButton('&Octal')
        self.buttons.addButton(octalButton, 8)
        mainLay.addWidget(octalButton, 1, 0, Qt.AlignmentFlag.AlignRight)
        self.baseBoxes[8] = AltBaseBox(8, self.dlgRef.calc)
        mainLay.addWidget(self.baseBoxes[8], 1, 1)
        binaryButton = QPushButton('&Binary')
        self.buttons.addButton(binaryButton, 2)
        mainLay.addWidget(binaryButton, 2, 0, Qt.AlignmentFlag.AlignRight)
        self.baseBoxes[2] = AltBaseBox(2, self.dlgRef.calc)
        mainLay.addWidget(self.baseBoxes[2], 2, 1)
        decimalButton = QPushButton('&Decimal')
        self.buttons.addButton(decimalButton, 10)
        mainLay.addWidget(decimalButton, 3, 0, Qt.AlignmentFlag.AlignRight)
        self.baseBoxes[10] = AltBaseBox(10, self.dlgRef.calc)
        mainLay.addWidget(self.baseBoxes[10], 3, 1)
        for button in self.buttons.buttons():
            button.setCheckable(True)
        self.buttons.buttonClicked.connect(self.changeBase)
        self.bitsLabel = QLabel()
        self.bitsLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.bitsLabel.setFrameStyle(Shape.Box | Shadow.Plain)
        topLay.addSpacing(3)
        topLay.addWidget(self.bitsLabel)
        topLay.addSpacing(3)
        buttonLay = QHBoxLayout()
        topLay.addLayout(buttonLay)
        copyButton = QPushButton('Copy &Value')
        buttonLay.addWidget(copyButton)
        copyButton.clicked.connect(self.copyValue)
        closeButton = QPushButton('&Close')
        buttonLay.addWidget(closeButton)
        closeButton.clicked.connect(self.close)
        self.changeBase(self.dlgRef.calc.base, False)
        self.updateOptions()
        option = self.dlgRef.calc.option
        self.move(option.intData('AltBaseXPos', 0, 10000),
                  option.intData('AltBaseYPos', 0, 10000))

    #@+node:tom.20230424130102.5: *4* updateData
    def updateData(self):
        """Update edit box contents for current registers.
        """
        if self.prevBase and self.dlgRef.calc.flag != Mode.entryMode:
            self.changeBase(self.prevBase, False)
            self.prevBase = None
        for box in self.baseBoxes.values():
            box.setValue(self.dlgRef.calc.stack[0])

    #@+node:tom.20230424130102.6: *4* changeBase
    def changeBase(self, base, endEntryMode=True):
        """Change core's base, button depression and label highlighting.
        """
        self.baseBoxes[self.dlgRef.calc.base].setHighlight(False)
        self.baseBoxes[base].setHighlight(True)
        self.buttons.button(base).setChecked(True)
        if endEntryMode and self.dlgRef.calc.base != base and \
                self.dlgRef.calc.flag == Mode.entryMode:
            self.dlgRef.calc.flag = Mode.saveMode
        self.dlgRef.calc.base = base

    #@+node:tom.20230424130102.7: *4* setCodedBase
    def setCodedBase(self, baseCode, temp=True):
        """Set new base from letter code, temporarily if temp is true.
        """
        if temp:
            self.prevBase = self.dlgRef.calc.base
        else:
            self.prevBase = None
        try:
            self.changeBase(AltBaseDialog.baseCode[baseCode], not temp)
        except KeyError:
            pass

    #@+node:tom.20230424130102.8: *4* updateOptions
    def updateOptions(self):
        """Update bit limit and two's complement use.
        """
        self.dlgRef.calc.setAltBaseOptions()
        if self.dlgRef.calc.useTwosComplement:
            text = '{0} bit, two\'s complement'.format(self.dlgRef.calc.
                                                       numBits)
        else:
            text = '{0} bit, no two\'s complement'.format(self.dlgRef.calc.
                                                          numBits)
        self.bitsLabel.setText(text)

    #@+node:tom.20230424130102.9: *4* copyValue
    def copyValue(self):
        """Copy the value in the current base to the clipboard.
        """
        text = str(self.baseBoxes[self.dlgRef.calc.base].text())
        clip = QApplication.clipboard()
        if clip.supportsSelection():
            clip.setText(text, QClipboard.Selection)
        clip.setText(text)

    #@+node:tom.20230424130102.10: *4* keyPressEvent
    def keyPressEvent(self, keyEvent):
        """Pass all keypresses to main dialog.
        """
        self.dlgRef.keyPressEvent(keyEvent)

    #@+node:tom.20230424130102.11: *4* keyReleaseEvent
    def keyReleaseEvent(self, keyEvent):
        """Pass all key releases to main dialog.
        """
        self.dlgRef.keyReleaseEvent(keyEvent)

    #@+node:tom.20230424130102.12: *4* closeEvent
    def closeEvent(self, closeEvent):
        """Change back to base 10 before closing.
        """
        self.changeBase(10)
        QWidget.closeEvent(self, closeEvent)


    #@-others
#@+node:tom.20230424130102.13: *3* class AltBaseBox
class AltBaseBox(QLabel): # type: ignore
    """Displays an edit box at a particular base.
    """
    #@+others
    #@+node:tom.20230424130102.14: *4* __init__
    def __init__(self, base, calcRef, parent=None):
        QLabel.__init__(self, parent)
        self.base = base
        self.calcRef = calcRef
        self.setHighlight(False)
        self.setLineWidth(3)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Minimum)

    #@+node:tom.20230424130102.15: *4* setValue
    def setValue(self, num):
        """Set value to num in proper base.
        """
        self.setText(self.calcRef.numberStr(num, self.base))

    #@+node:tom.20230424130102.16: *4* setHighlight
    def setHighlight(self, turnOn=True):
        """Make border bolder if turnOn is true, restore if false.
        """
        if turnOn:
            style = Shape.Panel | Shadow.Plain
        else:
            style = Shape.Panel | Shadow.Sunken
        self.setFrameStyle(style)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@+node:tom.20230424130102.18: **  calcbutton
#@+others
#@+node:tom.20230424130102.19: *3* class CalcButton
class CalcButton(QPushButton): # type: ignore
    """Calculator button class - size change & emits clicked text signal.
    """
    activated = pyqtSignal(str)
    #@+others
    #@+node:tom.20230424130102.20: *4* __init__
    def __init__(self, text, parent=None):
        QPushButton.__init__(self, text, parent)
        self.setMinimumSize(38, 16)
        self.setSizePolicy(QSizePolicy.Policy.Preferred,
                                             QSizePolicy.Policy.Preferred)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.clicked.connect(self.clickEvent)

    #@+node:tom.20230424130102.21: *4* clickEvent
    def clickEvent(self):
        """Emits signal with button text.
        """
        self.activated.emit(self.text())

    #@+node:tom.20230424130102.22: *4* sizeHint
    def sizeHint(self):
        """Set prefered size.
        """
        size = QPushButton.sizeHint(self)
        size.setWidth(size.width() // 2)
        return size

    #@+node:tom.20230424130102.23: *4* tmpDown
    def tmpDown(self, mSec):
        """Button shows pushed in for mSec milliseconds.
        """
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(self.timerUp)
        timer.start(mSec)
        self.setDown(True)

    #@+node:tom.20230424130102.24: *4* timerUp
    def timerUp(self):
        """Button up at end of timer for tmpDown.
        """
        self.setDown(False)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@+node:tom.20230424130102.26: **  calccore
#@+others
#@+node:tom.20230424130102.27: *3* class Mode
class Mode:
    """Enum for calculator modes.
    """
    entryMode = 100  # in num entry - adds to num string
    saveMode = 101   # after result - previous result becomes Y
    replMode = 102   # after enter key - replaces X
    expMode = 103    # in exponent entry - adds to exp string
    memStoMode = 104 # in memory register entry - needs 0-9 for num to store
    memRclMode = 105 # in memory register entry - needs 0-9 for num to recall
    decPlcMode = 106 # in decimal places entry - needs 0-9 for value
    errorMode = 107  # error notification - any cmd to resume


#@+node:tom.20230424130102.28: *3* class CalcCore
class CalcCore:
    """Reverse Polish calculator functionality.
    """
    minMaxHist = 10
    maxMaxHist = 10000
    minNumBits = 4
    maxNumBits = 128
    #@+others
    #@+node:tom.20230424130102.29: *4* __init__
    def __init__(self):
        self.stack = CalcStack()
        self.option = Option('rpcalc', 20)
        self.option.loadAll(defaultList)
        self.restoreStack()
        self.xStr = ''
        self.updateXStr()
        self.flag = Mode.saveMode
        self.base = 10
        self.numBits = 0
        self.useTwosComplement = False
        self.history = []
        self.histChg = 0
        self.setAltBaseOptions()

    #@+node:tom.20230424130102.30: *4* setAltBaseOptions
    def setAltBaseOptions(self):
        """Update bit limit and two's complement use.
        """
        self.numBits = self.option.intData('AltBaseBits', CalcCore.minNumBits,
                                           CalcCore.maxNumBits)
        if not self.numBits:
            self.numBits = CalcCore.maxNumBits
        self.useTwosComplement = self.option.boolData('UseTwosComplement')

    #@+node:tom.20230424130102.31: *4* restoreStack
    def restoreStack(self):
        """Read stack from option file.
        """
        if self.option.boolData('SaveStacks'):
            self.stack.replaceAll([self.option.numData('Stack' + repr(x)) for
                                   x in range(4)])
            self.mem = [self.option.numData('Mem' + repr(x)) for x in
                        range(10)]
        else:
            self.mem = [0.0] * 10

    #@+node:tom.20230424130102.32: *4* saveStack
    def saveStack(self):
        """Store stack to option file.
        """
        if self.option.boolData('SaveStacks'):
            [self.option.changeData('Stack' + repr(x), repr(self.stack[x]), 1)
             for x in range(4)]
            [self.option.changeData('Mem' + repr(x), repr(self.mem[x]), 1)
             for x in range(10)]
            self.option.writeChanges()

    #@+node:tom.20230424130102.33: *4* updateXStr
    def updateXStr(self):
        """get display string from X register.
        """
        if abs(self.stack[0]) > 1e299:
            self.xStr = 'error 9'
            self.flag = Mode.errorMode
            self.stack[0] = 0.0
            if abs(self.stack[1]) > 1e299:
                self.stack.replaceXY(0.0)
        else:
            self.xStr = self.formatNum(self.stack[0])

    #@+node:tom.20230424130102.34: *4* formatNum
    def formatNum(self, num):
        """Return number formatted per options.
        """
        absNum = abs(num)
        plcs = self.option.intData('NumDecimalPlaces', 0, 9)
        forceSci = self.option.boolData('ForceSciNotation')
        useEng = self.option.boolData('UseEngNotation')
        exp = 0
        if absNum != 0.0 and (absNum < 1e-4 or absNum >= 1e7 or forceSci
                              or useEng):
            exp = int(math.floor(math.log10(absNum)))
            if useEng:
                exp = 3 * (exp // 3)
            num /= 10**exp
            num = round(num, plcs)  # check if rounding bumps exponent
            if useEng and abs(num) >= 1000.0:
                num /= 1000.0
                exp += 3
            elif not useEng and abs(num) >= 10.0:
                num /= 10.0
                exp += 1
        numStr = '{: 0.{pl}f}'.format(num, pl=plcs)
        if self.option.boolData('ThousandsSeparator'):
            numStr = self.addThousandsSep(numStr)
        if exp != 0 or forceSci:
            expDigits = 4
            if self.option.boolData('TrimExponents'):
                expDigits = 1
            numStr = '{0}e{1:+0{pl}d}'.format(numStr, exp, pl=expDigits)
        return numStr

    #@+node:tom.20230424130102.35: *4* addThousandsSep
    def addThousandsSep(self, numStr):
        """Return number string with thousands separators added.
        """
        leadChar = ''
        if numStr[0] < '0' or numStr[0] > '9':
            leadChar = numStr[0]
            numStr = numStr[1:]
        numStr = numStr.replace(' ', '')
        decPos = numStr.find('.')
        if decPos < 0:
            decPos = len(numStr)
        for i in range(decPos - 3, 0, -3):
            numStr = numStr[:i] + ' ' + numStr[i:]
        return leadChar + numStr

    #@+node:tom.20230424130102.36: *4* sciFormatX
    def sciFormatX(self, decPlcs):
        """Return X register str in sci notation.
        """
        return '{: 0.{pl}e}'.format(self.stack[0], pl=decPlcs)

    #@+node:tom.20230424130102.37: *4* newXValue
    def newXValue(self, value):
        """Push X onto stack, replace with value.
        """
        self.stack.enterX()
        self.stack[0] = float(value)
        self.updateXStr()
        self.flag = Mode.saveMode

    #@+node:tom.20230424130102.38: *4* numEntry
    def numEntry(self, entStr):
        """Interpret a digit entered depending on mode.
        """
        if self.flag == Mode.saveMode:
            self.stack.enterX()
        if self.flag in (Mode.entryMode, Mode.expMode):
            if self.base == 10:
                newStr = self.xStr + entStr
            else:
                newStr = self.numberStr(self.stack[0], self.base) + entStr
        else:
            newStr = ' ' + entStr    # space for minus sign
            if newStr == ' .':
                newStr = ' 0.'
        try:
            num = self.convertNum(newStr)
        except ValueError:
            return False
        if self.base != 10:
            newStr = self.formatNum(num)    # decimal num in main display
        self.stack[0] = num
        if self.option.boolData('ThousandsSeparator'):
            newStr = self.addThousandsSep(newStr)
        self.xStr = newStr
        if self.flag != Mode.expMode:
            self.flag = Mode.entryMode
        return True

    #@+node:tom.20230424130102.39: *4* numberStr
    def numberStr(self, number, base):
        """Return string of number in given base (2-16).
        """
        digits = '0123456789abcdef'
        number = int(round(number))
        result = ''
        sign = ''
        if number == 0:
            return '0'
        if self.useTwosComplement:
            if number >= 2**(self.numBits - 1) or \
                    number < -2**(self.numBits - 1):
                return 'overflow'
            if number < 0:
                number = 2**self.numBits + number
        else:
            if number < 0:
                number = abs(number)
                sign = '-'
            if number >= 2**self.numBits:
                return 'overflow'
        while number:
            number, remainder = divmod(number, base)
            result = '{0}{1}'.format(digits[remainder], result)
        return '{0}{1}'.format(sign, result)

    #@+node:tom.20230424130102.40: *4* convertNum
    def convertNum(self, numStr):
        """Convert number string to float using current base.
        """
        numStr = numStr.replace(' ', '')
        if self.base == 10:
            return float(numStr)
        num = float(int(numStr, self.base))
        if num >= 2**self.numBits:
            self.xStr = 'error 9'
            self.flag = Mode.errorMode
            self.stack[0] = num
            raise ValueError
        if self.useTwosComplement and num >= 2**(self.numBits - 1):
            num = num - 2**self.numBits
        return num

    #@+node:tom.20230424130102.41: *4* expCmd
    def expCmd(self):
        """Command to add an exponent.
        """
        if self.flag == Mode.expMode or self.base != 10:
            return False
        if self.flag == Mode.entryMode:
            self.xStr = self.xStr + 'e+0'
        else:
            if self.flag == Mode.saveMode:
                self.stack.enterX()
            self.stack[0]= 1.0
            self.xStr = '1e+0'
        self.flag = Mode.expMode
        return True

    #@+node:tom.20230424130102.42: *4* bspCmd
    def bspCmd(self):
        """Backspace command.
        """
        if self.base != 10 and self.flag == Mode.entryMode:
            self.xStr = self.numberStr(self.stack[0], self.base)
            if self.xStr[0] != '-':
                self.xStr = ' ' + self.xStr
        if self.flag == Mode.entryMode and len(self.xStr) > 2:
            self.xStr = self.xStr[:-1]
        elif self.flag == Mode.expMode:
            numExp = self.xStr.split('e', 1)
            if len(numExp[1]) > 2:
                self.xStr = self.xStr[:-1]
            else:
                self.xStr = numExp[0]
                self.flag = Mode.entryMode
        else:
            self.stack[0] = 0.0
            self.updateXStr()
            self.flag = Mode.replMode
            return True
        self.stack[0] = self.convertNum(self.xStr)
        if self.base != 10:
            self.xStr = self.formatNum(self.stack[0])
        if self.option.boolData('ThousandsSeparator'):
            self.xStr = self.addThousandsSep(self.xStr)
        return True

    #@+node:tom.20230424130102.43: *4* chsCmd
    def chsCmd(self):
        """Change sign command.
        """
        if self.flag == Mode.expMode:
            numExp = self.xStr.split('e', 1)
            if numExp[1][0] == '+':
                self.xStr = numExp[0] + 'e-' + numExp[1][1:]
            else:
                self.xStr = numExp[0] + 'e+' + numExp[1][1:]
        else:
            if self.xStr[0] == ' ':
                self.xStr = '-' + self.xStr[1:]
            else:
                self.xStr = ' ' + self.xStr[1:]
        self.stack[0] = float(self.xStr.replace(' ', ''))
        return True

    #@+node:tom.20230424130102.44: *4* memStoRcl
    def memStoRcl(self, numStr):
        """Handle memMode number entry for mem & dec plcs.
        """
        if len(numStr) == 1 and '0' <= numStr <= '9':
            num = int(numStr)
            if self.flag == Mode.memStoMode:
                self.mem[num] = self.stack[0]
            elif self.flag == Mode.memRclMode:
                self.stack.enterX()
                self.stack[0] = self.mem[num]
            else:        # decimal place mode
                self.option.changeData('NumDecimalPlaces', numStr, 1)
                self.option.writeChanges()
        elif numStr == '<-':         # backspace
            pass
        else:
            return False
        self.updateXStr()
        self.flag = Mode.saveMode
        return True

    #@+node:tom.20230424130102.45: *4* angleConv
    def angleConv(self):
        """Return angular conversion factor from options.
        """
        type = self.option.strData('AngleUnit')
        if type == 'rad':
            return 1.0
        if type == 'grad':
            return math.pi / 200
        return math.pi / 180   # degree

    #@+node:tom.20230424130102.46: *4* cmd
    def cmd(self, cmdStr):
        """Main command interpreter - returns true/false if change made.
        """
        if self.flag in (Mode.memStoMode, Mode.memRclMode, Mode.decPlcMode):
            return self.memStoRcl(cmdStr)
        if self.flag == Mode.errorMode:    # reset display, ignore next command
            self.updateXStr()
            self.flag = Mode.saveMode
            return True
        eqn = ''
        try:
            if len(cmdStr) == 1:
                if '0' <= cmdStr <= '9' or cmdStr == '.':
                    return self.numEntry(cmdStr)
                if self.base == 16 and 'A' <= cmdStr <= 'F':
                    return self.numEntry(cmdStr)
                if cmdStr in '+-*/':
                    eqn = '{0} {1} {2}'.format(self.formatNum(self.stack[1]),
                                               cmdStr,
                                               self.formatNum(self.stack[0]))
                    if cmdStr == '+':
                        self.stack.replaceXY(self.stack[1] + self.stack[0])
                    elif cmdStr == '-':
                        self.stack.replaceXY(self.stack[1] - self.stack[0])
                    elif cmdStr == '*':
                        self.stack.replaceXY(self.stack[1] * self.stack[0])
                    elif cmdStr == '/':
                        self.stack.replaceXY(self.stack[1] / self.stack[0])
                else:
                    return False
            elif cmdStr == 'ENT':          # enter
                self.stack.enterX()
                self.flag = Mode.replMode
                self.updateXStr()
                return True
            elif cmdStr == 'EXP':
                return self.expCmd()
            elif cmdStr == 'X<>Y':         # exchange
                self.stack[0], self.stack[1] = self.stack[1], self.stack[0]
            elif cmdStr == 'CHS':          # change sign
                return self.chsCmd()
            elif cmdStr == 'CLR':          # clear
                self.stack.replaceAll([0.0, 0.0, 0.0, 0.0])
            elif cmdStr == '<-':           # backspace
                return self.bspCmd()
            elif cmdStr == 'STO':          # store to memory
                self.flag = Mode.memStoMode
                self.xStr = '0-9:'
                return True
            elif cmdStr == 'RCL':          # recall from memory
                self.flag = Mode.memRclMode
                self.xStr = '0-9:'
                return True
            elif cmdStr == 'PLCS':         # change dec plc setting
                self.flag = Mode.decPlcMode
                self.xStr = '0-9:'
                return True
            elif cmdStr == 'SCI':          # toggle fix/sci setting
                orig = self.option.boolData('ForceSciNotation')
                new = orig and 'no' or 'yes'
                self.option.changeData('ForceSciNotation', new, 1)
                self.option.writeChanges
            elif cmdStr == 'DEG':           # change deg/rad setting
                orig = self.option.strData('AngleUnit')
                new = orig == 'deg' and 'rad' or 'deg'
                self.option.changeData('AngleUnit', new, 1)
                self.option.writeChanges()
            elif cmdStr == 'R>':           # roll stack back
                self.stack.rollBack()
            elif cmdStr == 'R^':           # roll stack forward
                self.stack.rollUp()
            elif cmdStr == 'PI':           # pi constant
                self.stack.enterX()
                self.stack[0] = math.pi
            elif cmdStr == 'X^2':          # square
                eqn = '{0}^2'.format(self.formatNum(self.stack[0]))
                self.stack[0] = self.stack[0] * self.stack[0]
            elif cmdStr == 'Y^X':          # x power of y
                eqn = '({0})^{1}'.format(self.formatNum(self.stack[1]),
                                         self.formatNum(self.stack[0]))
                self.stack.replaceXY(self.stack[1] ** self.stack[0])
            elif cmdStr == 'XRTY':          # x root of y
                eqn = '({0})^(1/{1})'.format(self.formatNum(self.stack[1]),
                                             self.formatNum(self.stack[0]))
                self.stack.replaceXY(self.stack[1] ** (1/self.stack[0]))
            elif cmdStr == 'RCIP':         # 1/x
                eqn = '1 / ({0})'.format(self.formatNum(self.stack[0]))
                self.stack[0] = 1 / self.stack[0]
            elif cmdStr == 'E^X':          # inverse natural log
                eqn = 'e^({0})'.format(self.formatNum(self.stack[0]))
                self.stack[0] = math.exp(self.stack[0])
            elif cmdStr == 'TN^X':         # inverse base 10 log
                eqn = '10^({0})'.format(self.formatNum(self.stack[0]))
                self.stack[0] = 10.0 ** self.stack[0]
            else:
                eqn = '{0}({1})'.format(cmdStr, self.formatNum(self.stack[0]))
                if cmdStr == 'SQRT':         # square root
                    self.stack[0] = math.sqrt(self.stack[0])
                elif cmdStr == 'SIN':          # sine
                    self.stack[0] = math.sin(self.stack[0] *
                                             self.angleConv())
                elif cmdStr == 'COS':          # cosine
                    self.stack[0] = math.cos(self.stack[0] *
                                             self.angleConv())
                elif cmdStr == 'TAN':          # tangent
                    self.stack[0] = math.tan(self.stack[0] *
                                             self.angleConv())
                elif cmdStr == 'LN':           # natural log
                    self.stack[0] = math.log(self.stack[0])
                elif cmdStr == 'ASIN':         # arcsine
                    self.stack[0] = math.asin(self.stack[0]) \
                                    / self.angleConv()
                elif cmdStr == 'ACOS':         # arccosine
                    self.stack[0] = math.acos(self.stack[0]) \
                                    / self.angleConv()
                elif cmdStr == 'ATAN':         # arctangent
                    self.stack[0] = math.atan(self.stack[0]) \
                                    / self.angleConv()
                elif cmdStr == 'LOG':          # base 10 log
                    self.stack[0] = math.log10(self.stack[0])
                else:
                    return False
            self.flag = Mode.saveMode
            self.updateXStr()
            if eqn:
                self.history.append((eqn, self.stack[0]))
                self.histChg += 1
                maxLen = self.option.intData('MaxHistLength',
                                             CalcCore.minMaxHist,
                                             CalcCore.maxMaxHist)
                while len(self.history) > maxLen:
                    del self.history[0]
            return True
        except (ValueError, ZeroDivisionError):
            self.xStr = 'error 0'
            self.flag = Mode.errorMode
            return True
        except OverflowError:
            self.xStr = 'error 9'
            self.flag = Mode.errorMode
            return True

    #@+node:tom.20230424130102.47: *4* printDebug
    def printDebug(self):
        """Print display string and all registers for debug.
        """
        print('x =', self.xStr)
        print('\n'.join([repr(num) for num in self.stack]))


    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@+node:tom.20230424130102.50: ** class CalcDlg
class CalcDlg(QWidget): # type: ignore
    """Main dialog for calculator program.
    """
    #@+others
    #@+node:tom.20230424130102.51: *3* __init__
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.calc = CalcCore()
        self.setWindowTitle('rpCalc')
        modPath = os.path.abspath(sys.path[0])
        if modPath.endswith('.zip') or modPath.endswith('.exe'):
            modPath = os.path.dirname(modPath)  # for py2exe/cx_freeze

        iconPathList = [iconPath]
        self.icons = IconDict()
        self.icons.addIconPath(filter(None, iconPathList))
        self.icons.addIconPath([path for path in iconPathList if path])

        self.setFocusPolicy(FocusPolicy.StrongFocus)
        self.helpView = None
        self.extraView = None
        self.regView = None
        self.histView = None
        self.memView = None

        self.altBaseView = None
        self.optDlg = None
        #@+<< create popup menu >>
        #@+node:tom.20230428234315.1: *4* << create popup menu >>
        self.popupMenu = QMenu(self)
        self.popupMenu.addAction('Registers on &LCD', self.toggleReg)
        self.popupMenu.addSeparator()
        self.popupMenu.addAction('Show &Register List', self.viewReg)

        self.popupMenu.addAction('Show &History List', self.viewHist)
        self.popupMenu.addAction('Show &Memory List', self.viewMem)
        self.popupMenu.addSeparator()
        self.popupMenu.addAction('Show Other &Bases', self.viewAltBases)
        self.popupMenu.addSeparator()
        self.popupMenu.addAction('Show Help &File', self.help)

        self.popupMenu.addAction('&About rpCalc', self.about)
        self.popupMenu.addAction('&License', self.license)
        # self.popupMenu.addSeparator()
        # self.popupMenu.addAction('&Quit', self.close)
        topLay = QVBoxLayout(self)
        self.setLayout(topLay)
        #@-<< create popup menu >>
        topLay.setSpacing(4)
        topLay.setContentsMargins(6, 6, 6, 6)

        lcdBox = LcdBox()
        topLay.addWidget(lcdBox)
        lcdLay = QGridLayout(lcdBox)
        lcdLay.setColumnStretch(1, 1)
        lcdLay.setRowStretch(3, 1)
        self.extraLabels = [QLabel(' T:',), QLabel(' Z:',),
                            QLabel(' Y:',)]

        #@+<< populate lcd widget >>
        #@+node:tom.20230428234437.1: *4* << populate lcd widget >>
        for i in range(3):
            lcdLay.addWidget(self.extraLabels[i], i, 0, Qt.AlignmentFlag.AlignLeft)
        self.extraLcds = [Lcd(1.5, 13), Lcd(1.5, 13), Lcd(1.5, 13)]
        lcdLay.addWidget(self.extraLcds[2], 0, 1, Qt.AlignmentFlag.AlignRight)
        lcdLay.addWidget(self.extraLcds[1], 1, 1, Qt.AlignmentFlag.AlignRight)
        lcdLay.addWidget(self.extraLcds[0], 2, 1, Qt.AlignmentFlag.AlignRight)
        if not self.calc.option.boolData('ViewRegisters'):
            for w in self.extraLabels + self.extraLcds:
                w.hide()
        self.lcd = Lcd(2.0, 13)
        lcdLay.addWidget(self.lcd, 3, 0, 1, 2, Qt.AlignmentFlag.AlignRight)
        self.setLcdHighlight()
        self.updateLcd()
        self.updateColors()
        #@-<< populate lcd widget >>

        self.cmdLay = QGridLayout()
        topLay.addLayout(self.cmdLay)
        self.cmdDict = {}
        self.addCmdButton('x^2', 0, 0)
        self.addCmdButton('sqRT', 0, 1)
        self.addCmdButton('y^X', 0, 2)
        self.addCmdButton('xRTy', 0, 3)
        self.addCmdButton('RCIP', 0, 4)
        self.addCmdButton('SIN', 1, 0)
        self.addCmdButton('COS', 1, 1)
        self.addCmdButton('TAN', 1, 2)
        self.addCmdButton('LN', 1, 3)
        self.addCmdButton('e^X', 1, 4)
        self.addCmdButton('ASIN', 2, 0)
        self.addCmdButton('ACOS', 2, 1)
        self.addCmdButton('ATAN', 2, 2)
        self.addCmdButton('LOG', 2, 3)
        self.addCmdButton('tn^X', 2, 4)
        self.addCmdButton('STO', 3, 0)
        self.addCmdButton('RCL', 3, 1)
        self.addCmdButton('R^', 3, 2)
        self.addCmdButton('R>', 3, 3)
        self.addCmdButton('x<>y', 3, 4)
        self.addCmdButton('SHOW', 4, 0)
        self.addCmdButton('CLR', 4, 1)
        self.addCmdButton('PLCS', 4, 2)
        self.addCmdButton('SCI', 4, 3)
        self.addCmdButton('DEG', 4, 4)
        self.addCmdButton('>CLIP', 5, 0)
        self.addCmdButton('Pi', 5, 1)
        self.addCmdButton('EXP', 5, 2)
        self.addCmdButton('CHS', 5, 3)
        self.addCmdButton('<-', 5, 4)

        self.mainLay = QGridLayout()
        topLay.addLayout(self.mainLay)
        self.mainDict: dict[int, Any] = {}
        self.addMainButton(0, 'OPT', 0, 0)
        self.addMainButton(Qt.Key.Key_Slash, '/', 0, 1)
        self.addMainButton(Qt.Key.Key_Slash, '/', 0, 1)
        self.addMainButton(Qt.Key.Key_Asterisk, '*', 0, 2)
        self.addMainButton(Qt.Key.Key_Minus, '-', 0, 3)
        self.addMainButton(Qt.Key.Key_7, '7', 1, 0)
        self.addMainButton(Qt.Key.Key_8, '8', 1, 1)
        self.addMainButton(Qt.Key.Key_9, '9', 1, 2)
        self.addMainButton(Qt.Key.Key_Plus, '+', 1, 3, 1, 0)
        self.addMainButton(Qt.Key.Key_4, '4', 2, 0)
        self.addMainButton(Qt.Key.Key_5, '5', 2, 1)
        self.addMainButton(Qt.Key.Key_6, '6', 2, 2)
        self.addMainButton(Qt.Key.Key_1, '1', 3, 0)
        self.addMainButton(Qt.Key.Key_2, '2', 3, 1)
        self.addMainButton(Qt.Key.Key_3, '3', 3, 2)
        self.addMainButton(Qt.Key.Key_Enter, 'ENT', 3, 3, 1, 0)
        self.addMainButton(Qt.Key.Key_0, '0', 4, 0, 0, 1)
        self.addMainButton(Qt.Key.Key_Period, '.', 4, 2)

        self.mainDict[Qt.Key.Key_Return] = \
                     self.mainDict[Qt.Key.Key_Enter]
        # added for european keyboards:
        self.mainDict[Qt.Key.Key_Comma] = \
                     self.mainDict[Qt.Key.Key_Period]
        self.cmdDict['ENT'] = self.mainDict[Qt.Key.Key_Enter]
        self.cmdDict['OPT'] = self.mainDict[0]

        self.entryStr = ''
        self.showMode = False

        statusBox = QFrame()
        statusBox.setFrameStyle(Shape.Panel | Shadow.Sunken)
        statusBox.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        topLay.addWidget(statusBox)
        statusLay = QHBoxLayout(statusBox)
        self.entryLabel = QLabel(statusBox)
        statusLay.addWidget(self.entryLabel)
        statusLay.setContentsMargins(1, 1, 1, 1)
        self.statusLabel = QLabel(statusBox)
        self.statusLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
        statusLay.addWidget(self.statusLabel)

        if self.calc.option.boolData('ExtraViewStartup'):
            self.viewReg()
        if self.calc.option.boolData('AltBaseStartup'):
            self.viewAltBases()

        xSize = self.calc.option.intData('MainDlgXSize', 0, 10000)
        ySize = self.calc.option.intData('MainDlgYSize', 0, 10000)
        if xSize and ySize:
            self.resize(xSize, ySize)
        self.move(self.calc.option.intData('MainDlgXPos', 0, 10000),
                  self.calc.option.intData('MainDlgYPos', 0, 10000))

        self.updateEntryLabel('rpCalc Version {0}'.format(__version__))
        QTimer.singleShot(5000, self.updateEntryLabel)
        self.standalone = False


    #@+node:tom.20230424130102.52: *3* updateEntryLabel
    def updateEntryLabel(self, subsText=''):
        """Set entry & status label text, use entryStr or subsText, options.
        """
        numFormat = self.calc.option.boolData('ForceSciNotation') and 'sci' \
                    or 'fix'
        decPlcs = self.calc.option.intData('NumDecimalPlaces', 0, 9)
        angle = self.calc.option.strData('AngleUnit')
        self.statusLabel.setText('{0} {1}  {2}'.format(numFormat, decPlcs,
                                                       angle))
        self.entryLabel.setText(subsText or '> {0}'.format(self.entryStr))

    #@+node:tom.20230424130102.53: *3* setOptions
    def setOptions(self):
        """Starts option dialog, called by option key.
        """
        oldViewReg = self.calc.option.boolData('ViewRegisters')
        self.optDlg = OptionDlg(self.calc.option, self)
        self.optDlg.startGroupBox('Startup', 8)
        OptionDlgBool(self.optDlg, 'SaveStacks',
                                'Save previous entries')
        OptionDlgBool(self.optDlg, 'ExtraViewStartup',
                                'Auto open extra data view')
        OptionDlgBool(self.optDlg, 'AltBaseStartup',
                                'Auto open alternate base view')
        self.optDlg.startGroupBox('Display', 8)
        OptionDlgInt(self.optDlg, 'NumDecimalPlaces',
                               'Number of decimal places', 0, 9)
        OptionDlgBool(self.optDlg, 'ThousandsSeparator',
                                'Separate thousands with spaces')
        OptionDlgBool(self.optDlg, 'ForceSciNotation',
                                'Always show exponent')
        OptionDlgBool(self.optDlg, 'UseEngNotation',
                                'Use engineering notation')
        OptionDlgBool(self.optDlg, 'TrimExponents',
                                'Hide exponent leading zeros')
        OptionDlgBool(self.optDlg, 'ViewRegisters',
                                'View Registers on LCD')
        OptionDlgBool(self.optDlg, 'HideLcdHighlight',
                                'Hide LCD highlight')
        self.optDlg.startNewColumn()
        OptionDlgRadio(self.optDlg, 'AngleUnit', 'Angular Units',
                                 [('deg', 'Degrees'), ('rad', 'Radians')])
        self.optDlg.startGroupBox('Alternate Bases')
        OptionDlgInt(self.optDlg, 'AltBaseBits', 'Size limit',
                               CalcCore.minNumBits, CalcCore.maxNumBits,
                               True, 4, False, ' bits')
        OptionDlgBool(self.optDlg, 'UseTwosComplement',
                                'Use two\'s complement\nnegative numbers')
        self.optDlg.startGroupBox('Extra Views',)
        OptionDlgPush(self.optDlg, 'View Extra Data', self.viewExtra)
        OptionDlgPush(self.optDlg, 'View Other Bases',
                                self.viewAltBases)
        OptionDlgPush(self.optDlg, 'View Help file', self.help)
        OptionDlgInt(self.optDlg, 'MaxHistLength',
                               'Saved history steps', CalcCore.minMaxHist,
                               CalcCore.maxMaxHist, True, 10)
        if self.optDlg.exec_() == QDialog.DialogCode.Accepted:
            self.calc.option.writeChanges()
            newViewReg = self.calc.option.boolData('ViewRegisters')
            if newViewReg != oldViewReg:
                if newViewReg:
                    for w in self.extraLabels + self.extraLcds:
                        w.show()
                else:
                    for w in self.extraLabels + self.extraLcds:
                        w.hide()
                QApplication.processEvents()
                self.adjustSize()
            if self.altBaseView:
                self.altBaseView.updateOptions()
            self.setLcdHighlight()
            self.calc.updateXStr()
        self.optDlg = None

    #@+node:tom.20230424130102.54: *3* setLcdHighlight
    def setLcdHighlight(self):
        """Set lcd highlight based on option.
        """
        opt = self.calc.option.boolData('HideLcdHighlight') and \
              SegmentStyle.Flat or SegmentStyle.Filled
        self.lcd.setSegmentStyle(opt)
        for lcd in self.extraLcds:
            lcd.setSegmentStyle(opt)

    #@+node:tom.20230424130102.55: *3* updateColors
    def updateColors(self):
        """Adjust the colors to the current option settings.
        """
        if self.calc.option.boolData('UseDefaultColors'):
            return
        pal = QApplication.palette()
        background = QColor(self.calc.option.intData('BackgroundR',
                                                           0, 255),
                                  self.calc.option.intData('BackgroundG',
                                                           0, 255),
                                  self.calc.option.intData('BackgroundB',
                                                           0, 255))
        foreground = QColor(self.calc.option.intData('ForegroundR',
                                                           0, 255),
                                  self.calc.option.intData('ForegroundG',
                                                           0, 255),
                                  self.calc.option.intData('ForegroundB',
                                                           0, 255))
        pal.setColor(QPalette.Base, background)
        pal.setColor(QPalette.Text, foreground)
        QApplication.setPalette(pal)

    #@+node:tom.20230424130102.56: *3* viewExtra
    def viewExtra(self, defaultTab=0):
        """Show extra data view.
        """
        if self.optDlg:
            self.optDlg.reject()   # unfortunately necessary?
        if not self.extraView:
            self.extraView = ExtraDisplay(self)
        self.extraView.tabUpdate(defaultTab)
        self.extraView.tab.setCurrentIndex(defaultTab)
        self.extraView.show()

    #@+node:tom.20230424130102.57: *3* viewReg
    def viewReg(self):
        """Show extra data view with register tab open.
        """
        self.viewExtra(0)

    #@+node:tom.20230424130102.58: *3* viewHist
    def viewHist(self):
        """Show extra data view with history tab open.
        """
        self.viewExtra(1)

    #@+node:tom.20230424130102.59: *3* viewMem
    def viewMem(self):
        """Show extra data view with memory tab open.
        """
        self.viewExtra(2)

    #@+node:tom.20230424130102.60: *3* updateExtra
    def updateExtra(self):
        """Update current extra and alt base views.
        """
        if self.extraView and self.extraView.isVisible():
            self.extraView.updateData()
        if self.altBaseView:
            self.altBaseView.updateData()

    #@+node:tom.20230424130102.61: *3* toggleReg
    def toggleReg(self):
        """Toggle register display on LCD.
        """
        viewReg = not self.calc.option.boolData('ViewRegisters')
        self.calc.option.changeData('ViewRegisters',
                                    viewReg and 'yes' or 'no', 1)
        if viewReg:
            for w in self.extraLabels + self.extraLcds:
                w.show()
        else:
            for w in self.extraLabels + self.extraLcds:
                w.hide()
        self.adjustSize()
        self.calc.updateXStr()

    #@+node:tom.20230424130102.62: *3* viewAltBases
    def viewAltBases(self):
        """Show alternate base view.
        """
        if self.optDlg:
            self.optDlg.reject()   # unfortunately necessary?

        if not self.altBaseView:
            self.altBaseView = AltBaseDialog(self)
        self.altBaseView.updateData()
        self.altBaseView.show()

    #@+node:tom.20230424130102.64: *3* help
    def help(self):
        """View the ReadMe file.
        """
        if self.optDlg:
            self.optDlg.reject()   # unfortunately necessary?

        self.helpView = HelpView('', 'rpCalc README File', self.icons, self)
        self.helpView.show()

    #@+node:tom.20230424130102.65: *3* about
    def about(self):
        """About this program.
        """
        QMessageBox.about(self, 'rpCalc',
                                'rpCalc for the Leo Editor, Version {0}\n by {1}'.
                                format(__version__, __author__))

    #@+node:tom.20230429090628.1: *3* license
    def license(self):
        """he license for this program.
        """
        QMessageBox.about(self, 'rpCalc License', LICENSE)
    #@+node:tom.20230424130102.66: *3* addCmdButton
    def addCmdButton(self, text, row, col):
        """Adds a CalcButton for command functions.
        """
        button = CalcButton(text)
        self.cmdDict[text.upper()] = button
        self.cmdLay.addWidget(button, row, col)
        button.activated.connect(self.issueCmd)

    #@+node:tom.20230424130102.67: *3* addMainButton
    def addMainButton(self, key, text, row, col, extraRow=0, extraCol=0):
        """Adds a CalcButton for number and 4-function keys.
        """
        button = CalcButton(text)
        self.mainDict[key] = button
        self.mainLay.addWidget(button, row, col, 1+extraRow, 1+extraCol)
        button.activated.connect(self.issueCmd)

    #@+node:tom.20230424130102.68: *3* updateLcd
    def updateLcd(self):
        """Sets display back to CalcCore string.
        """
        numDigits = int(self.calc.option.numData('NumDecimalPlaces', 0, 9)) + 9
        if self.calc.option.boolData('ThousandsSeparator') or \
                self.calc.option.boolData('UseEngNotation'):
            numDigits += 2
        self.lcd.setDisplay(self.calc.xStr, numDigits)
        if self.calc.option.boolData('ViewRegisters'):
            nums = [self.calc.formatNum(num) for num in self.calc.stack[1:]]
            for num, lcd in zip(nums, self.extraLcds):
                lcd.setDisplay(num, numDigits)
        self.updateExtra()

    #@+node:tom.20230424130102.69: *3* issueCmd
    def issueCmd(self, text):
        """Sends command text to CalcCore - connected to button signals.
        """
        mode = self.calc.flag
        text = str(text).upper()
        if text == 'OPT':
            self.setOptions()
        elif text == 'SHOW':
            if not self.showMode:
                valueStr = self.calc.sciFormatX(11).replace('e', ' E', 1)
                self.lcd.setNumDigits(19)
                self.lcd.display(valueStr)
                self.showMode = True
                return
        elif text == '>CLIP':
            copyToClip(self.calc.sciFormatX(11).replace('e', ' E', 1))
            return
        else:
            self.calc.cmd(text)
        if text in ('SCI', 'DEG', 'OPT') or mode == Mode.decPlcMode:
            self.updateEntryLabel()
        self.showMode = False
        self.updateLcd()

    #@+node:tom.20230424130102.70: *3* textEntry
    def textEntry(self, ch):
        """Searches for button match from text entry.
        """
        if not ch:
            return False
        if ord(ch) == 8:   # backspace key
            self.entryStr = self.entryStr[:-1]
        elif ord(ch) == 27:  # escape key
            self.entryStr = ''
        elif ch == '\t':     # tab key
            cmds = [key for key in self.cmdDict.keys() if
                    key.startswith(self.entryStr.upper())]
            if len(cmds) == 1:
                button = self.cmdDict[cmds[0]]
                button.clickEvent()
                button.tmpDown(300)
                self.entryStr = ''
            else:
                QApplication.beep()
        elif ch == ':' and not self.entryStr:
            self.entryStr = ':'   # optional command prefix
        else:
            newStr = (self.entryStr + ch).upper()
            if newStr == ':Q':    # vim-like shortcut
                newStr = '>CLIP'
            button = self.cmdDict.get(newStr.lstrip(':'))
            if button:
                button.clickEvent()
                button.tmpDown(300)
                self.entryStr = ''
            else:
                if [key for key in self.cmdDict.keys() if
                    key.startswith(newStr.lstrip(':'))]:
                    self.entryStr += ch
                else:
                    QApplication.beep()
                    return False
        self.updateEntryLabel()
        return True

    #@+node:tom.20230424130102.71: *3* keyPressEvent
    def keyPressEvent(self, keyEvent):
        """Event handler for keys - checks for numbers and typed commands.
        """
        button = self.mainDict.get(keyEvent.key())
        if not self.entryStr and button:
            button.clickEvent()
            button.setDown(True)
            return
        letter = str(keyEvent.text()).upper()
        if keyEvent.modifiers() == KeyboardModifier.AltModifier:
            if self.altBaseView and self.altBaseView.isVisible():
                if letter in ('X', 'O', 'B', 'D'):
                    self.altBaseView.setCodedBase(letter, False)
                elif letter == 'V':
                    self.altBaseView.copyValue()
                elif letter == 'C':
                    self.altBaseView.close()
        elif not self.entryStr and self.calc.base == 16 and \
                 'A' <= letter <= 'F':
            self.issueCmd(keyEvent.text())
        elif self.altBaseView and self.altBaseView.isVisible() and \
                (self.calc.xStr == ' 0' or \
                 (self.calc.stack[0] == 0.0 and self.calc.base != 10)) and \
                self.calc.flag == Mode.entryMode and \
                letter in ('X', 'O', 'B', 'D'):
            self.altBaseView.setCodedBase(letter, True)
        elif not self.entryStr and keyEvent.key() == Qt.Key.Key_Backspace:
            button = self.cmdDict['<-']
            button.clickEvent()
            button.tmpDown(300)
        elif not self.entryStr and keyEvent.key() == Qt.Key.Key_Escape:
            self.popupMenu.popup(self.mapToGlobal(QPoint(0, 0)))
        elif not self.textEntry(str(keyEvent.text())):
            QWidget.keyPressEvent(self, keyEvent)

    #@+node:tom.20230424130102.72: *3* keyReleaseEvent
    def keyReleaseEvent(self, keyEvent):
        """Event handler for keys - sets button back to raised position.
        """
        # A hack: our widget is not getting keyPressEvent events
        # when running in a tab (as opposed to running stand-alone).
        # So when a key is released, we first send the even to
        # the key press handler.
        # self.standalone is initialized to False and set to True
        # by the tab toggle command.
        # The standalone test is required to avoid processing
        # the same keypressed event twice.

        if not self.standalone:
            self.keyPressEvent(keyEvent)
        button = self.mainDict.get(keyEvent.key())
        if not self.entryStr and button:
            button.setDown(False)

    #@+node:tom.20230424130102.73: *3* closeEvent
    def closeEvent(self, event):
        """Saves the stack prior to closing.
        """
        self.calc.saveStack()
        self.calc.option.changeData('MainDlgXSize', self.width(), True)
        self.calc.option.changeData('MainDlgYSize', self.height(), True)
        self.calc.option.changeData('MainDlgXPos', self.x(), True)
        self.calc.option.changeData('MainDlgYPos', self.y(), True)
        if self.extraView:
            self.calc.option.changeData('ExtraViewXSize',
                                        self.extraView.width(), True)
            self.calc.option.changeData('ExtraViewYSize',
                                        self.extraView.height(), True)
            self.calc.option.changeData('ExtraViewXPos',
                                        self.extraView.x(), True)
            self.calc.option.changeData('ExtraViewYPos',
                                        self.extraView.y(), True)
        if self.altBaseView:
            self.calc.option.changeData('AltBaseXPos',
                                        self.altBaseView.x(), True)
            self.calc.option.changeData('AltBaseYPos',
                                        self.altBaseView.y(), True)
        self.calc.option.writeChanges()
        QWidget.closeEvent(self, event)
    #@-others
#@+node:tom.20230424130102.75: **  calclcd

#@+others
#@+node:tom.20230424130102.76: *3* class Lcd
class Lcd(QLCDNumber): # type: ignore
    """Main LCD Display.
    """
    #@+others
    #@+node:tom.20230424130102.77: *4* __init__
    def __init__(self, sizeFactor=1, numDigits=8, parent=None):
        QLCDNumber.__init__(self, numDigits, parent)
        self.sizeFactor = sizeFactor
        self.setSegmentStyle(QLCDNumber.SegmentStyle.Filled)
        self.setMinimumSize(10, 23)
        self.setFrameStyle(Shape.NoFrame)

    #@+node:tom.20230424130102.78: *4* setDisplay
    def setDisplay(self, text, numDigits):
        """Update display value.
        """
        text = text.replace('e', ' E', 1)  # add space before exp
        if len(text) > numDigits:  # mark if digits hidden
            text = 'c{0}'.format(text[1-numDigits:])
        self.setNumDigits(numDigits)
        self.display(text)

    #@+node:tom.20230424130102.79: *4* sizeHint
    def sizeHint(self):
        """Set prefered size.
        """
        # default in Qt is 23 height & about 10 * numDigits
        size = QLCDNumber.sizeHint(self)
        return QSize(int(size.width() * self.sizeFactor),
                            int(size.height() * self.sizeFactor))


    #@-others
#@+node:tom.20230424130102.80: *3* class LcdBox
class LcdBox(QFrame): # type: ignore
    """Frame for LCD display.
    """
    #@+others
    #@+node:tom.20230424130102.81: *4* __init__
    def __init__(self, parent=None):
        QFrame.__init__(self, parent)
        self.setFrameStyle(Shape.Panel | Shadow.Sunken)
        self.setLineWidth(3)

    #@+node:tom.20230424130102.82: *4* mouseReleaseEvent
    def mouseReleaseEvent(self, event):
        """Mouse release event for popup menus.
        """
        if event.button() == MouseButton.RightButton:
            popup = self.parentWidget().popupMenu
            popup.exec_(self.mapToGlobal(event.pos()))
            popup.clearFocus()
        QFrame.mouseReleaseEvent(self, event)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@+node:tom.20230424130102.85: ** class CalcStack
class CalcStack(list):
    """Stores and rotates stack of 4 numbers.
    """
    #@+others
    #@+node:tom.20230424130102.86: *3* __init__
    def __init__(self, initList=None):
        if initList:
            list.__init__(self, initList)
        else:
            list.__init__(self, [0.0, 0.0, 0.0, 0.0])

    #@+node:tom.20230424130102.87: *3* replaceAll
    def replaceAll(self, numList):
        """Replace stack with numList.
        """
        self[:] = numList

    #@+node:tom.20230424130102.88: *3* replaceXY
    def replaceXY(self, num):
        """Replace X & Y registers with num, pulls stack.
        """
        del self[0]
        self[0] = num
        self.append(self[2])

    #@+node:tom.20230424130102.89: *3* enterX
    def enterX(self):
        """Push X onto stack into Y register.
        """
        self.insert(0, self[0])
        del self[4]

    #@+node:tom.20230424130102.90: *3* rollBack
    def rollBack(self):
        """Roll stack so x = old y, etc..
        """
        num = self[0]
        del self[0]
        self.append(num)

    #@+node:tom.20230424130102.91: *3* rollUp
    def rollUp(self):
        """Roll stack so x = old stack bottom.
        """
        num = self[3]
        del self[3]
        self.insert(0, num)
    #@-others
#@+node:tom.20230424130102.93: **  extradisplay

#@+others
#@+node:tom.20230424130102.94: *3* class ExtraViewWidget
class ExtraViewWidget(QTreeWidget): # type: ignore
    """Base class of list views for ExtraDisplay.
    """
    #@+others
    #@+node:tom.20230424130102.95: *4* __init__
    def __init__(self, calcRef, parent=None):
        QListView.__init__(self, parent)
        self.calcRef = calcRef
        self.setRootIsDecorated(False)

    #@+node:tom.20230424130102.96: *4* setHeadings
    def setHeadings(self, headerLabels):
        """Add headings to columns.
        """
        self.setColumnCount(len(headerLabels))
        self.setHeaderLabels(headerLabels)


    #@-others
#@+node:tom.20230424130102.97: *3* class RegViewWidget
class RegViewWidget(ExtraViewWidget):
    """Register list view for ExtraDisplay.
    """
    #@+others
    #@+node:tom.20230424130102.98: *4* __init__
    def __init__(self, calcRef, parent=None):
        ExtraViewWidget.__init__(self, calcRef, parent)
        self.setHeadings(['Name', 'Value'])
        for text in ['T', 'Y', 'Z', 'X']:
            item = QTreeWidgetItem(self)
            item.setText(0, text)
            item.setTextAlignment(0, Qt.AlignmentFlag.AlignCenter)
        self.resizeColumnToContents(0)
        self.setCurrentItem(item)
        self.updateData()

    #@+node:tom.20230424130102.99: *4* updateData
    def updateData(self):
        """Update with current data.
        """
        for i in range(4):
            self.topLevelItem(i).setText(1, '{:.15g}'.
                                         format(self.calcRef.stack[3 - i]))

    #@+node:tom.20230424130102.100: *4* selectedValue
    def selectedValue(self):
        """Return number for selected line.
        """
        if self.selectedItems():
            pos = self.indexOfTopLevelItem(self.selectedItems()[0])
            return self.calcRef.stack[3 - pos]
        return 0.0


    #@-others
#@+node:tom.20230424130102.101: *3* class HistViewWidget
class HistViewWidget(ExtraViewWidget):
    """History list view for ExtraDisplay.
    """
    #@+others
    #@+node:tom.20230424130102.102: *4* __init__
    def __init__(self, calcRef, parent=None):
        ExtraViewWidget.__init__(self, calcRef, parent)
        self.setHeadings(['Equation', 'Value'])
        self.updateData()

    #@+node:tom.20230424130102.103: *4* updateData
    def updateData(self):
        """Update with current data.
        """
        if not self.calcRef.histChg:
            return
        maxLen = self.calcRef.option.intData('MaxHistLength',
                                             self.calcRef.minMaxHist,
                                             self.calcRef.maxMaxHist)
        for eqn, value in self.calcRef.history[-self.calcRef.histChg:]:
            item = QTreeWidgetItem(self,
                                         [eqn, self.calcRef.formatNum(value)])
            if self.topLevelItemCount() > maxLen:
                self.takeTopLevelItem(0)
        self.resizeColumnToContents(0)
        self.clearSelection()
        self.setCurrentItem(item)
        self.scrollToItem(item)
        self.calcRef.histChg = 0

    #@+node:tom.20230424130102.104: *4* selectedValue
    def selectedValue(self):
        """Return number for selected line.
        """
        if self.selectedItems():
            pos = self.indexOfTopLevelItem(self.selectedItems()[0])
            return self.calcRef.history[pos][1]
        return 0.0


    #@-others
#@+node:tom.20230424130102.105: *3* class MemViewWidget
class MemViewWidget(ExtraViewWidget):
    """Memory list view for ExtraDisplay.
    """
    #@+others
    #@+node:tom.20230424130102.106: *4* __init__
    def __init__(self, calcRef, parent=None):
        ExtraViewWidget.__init__(self, calcRef, parent)
        self.setHeadings(['Num', 'Value'])
        for num in range(10):
            item = QTreeWidgetItem(self)
            item.setText(0, repr(num))
            item.setTextAlignment(0, Qt.AlignmentFlag.AlignCenter)
        self.resizeColumnToContents(0)
        self.setCurrentItem(self.topLevelItem(0))
        self.updateData()

    #@+node:tom.20230424130102.107: *4* updateData
    def updateData(self):
        """Update with current data.
        """
        for i in range(10):
            self.topLevelItem(i).setText(1, self.calcRef.
                                            formatNum(self.calcRef.mem[i]))

    #@+node:tom.20230424130102.108: *4* selectedValue
    def selectedValue(self):
        """Return number for selected line.
        """
        if self.selectedItems():
            pos = self.indexOfTopLevelItem(self.selectedItems()[0])
            return self.calcRef.mem[pos]
        return 0.0


    #@-others
#@+node:tom.20230424130102.109: *3* class ExtraDisplay
class ExtraDisplay(QWidget): # type: ignore
    """Displays registers, history or memory values, allows copies.
    """
    #@+others
    #@+node:tom.20230424130102.110: *4* __init__
    def __init__(self, dlgRef, parent=None):
        QWidget.__init__(self, parent)
        self.dlgRef = dlgRef
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, False)
        self.setWindowTitle('rpCalc Extra Data')
        topLay = QVBoxLayout(self)
        self.setLayout(topLay)

        self.tab = QTabWidget()
        self.regView = RegViewWidget(dlgRef.calc)
        self.tab.addTab(self.regView, '&Registers')
        self.histView = HistViewWidget(dlgRef.calc)
        self.tab.addTab(self.histView, '&History')
        self.memView = MemViewWidget(dlgRef.calc)

        self.tab.addTab(self.memView, '&Memory')
        self.tab.setFocus()
        topLay.addWidget(self.tab)
        self.tab.currentChanged.connect(self.tabUpdate)
        buttonLay = QHBoxLayout()
        topLay.addLayout(buttonLay)

        setButton = QPushButton('&Set\nCalc X')
        buttonLay.addWidget(setButton)
        setButton.clicked.connect(self.setXValue)
        allCopyButton = QPushButton('Copy\n&Precise')
        buttonLay.addWidget(allCopyButton)
        allCopyButton.clicked.connect(self.copyAllValue)

        fixedCopyButton = QPushButton('Copy\n&Fixed')
        buttonLay.addWidget(fixedCopyButton)
        fixedCopyButton.clicked.connect(self.copyFixedValue)
        self.buttonList = [setButton, allCopyButton, fixedCopyButton]
        closeButton = QPushButton('&Close')
        topLay.addWidget(closeButton)

        closeButton.clicked.connect(self.close)
        self.enableControls()
        option = self.dlgRef.calc.option
        xSize = option.intData('ExtraViewXSize', 0, 10000)
        ySize = option.intData('ExtraViewYSize', 0, 10000)
        if xSize and ySize:
            self.resize(xSize, ySize)
        self.move(option.intData('ExtraViewXPos', 0, 10000),
                  option.intData('ExtraViewYPos', 0, 10000))

    #@+node:tom.20230424130102.111: *4* tabUpdate
    def tabUpdate(self, index):
        """Update given tab widget.
        """
        self.tab.widget(index).updateData()
        self.enableControls()

    #@+node:tom.20230424130102.112: *4* updateData
    def updateData(self):
        """Update data in current tab.
        """
        self.tab.currentWidget().updateData()
        self.enableControls()

    #@+node:tom.20230424130102.113: *4* enableControls
    def enableControls(self):
        """Enable or disable buttons depending on content available.
        """
        for button in self.buttonList:
            button.setEnabled(len(self.tab.currentWidget().selectedItems()) >
                                  0)

    #@+node:tom.20230424130102.114: *4* setXValue
    def setXValue(self):
        """Copy selected value to calculator X register.
        """
        self.dlgRef.calc.newXValue(self.tab.currentWidget().selectedValue())
        self.dlgRef.updateLcd()

    #@+node:tom.20230424130102.115: *4* copyAllValue
    def copyAllValue(self):
        """Copy selected value to clipboard.
        """
        self.copyToClip('{:.15g}'.format(self.tab.currentWidget().
                                         selectedValue()))

    #@+node:tom.20230424130102.116: *4* copyFixedValue
    def copyFixedValue(self):
        """Copy selected value to clipboard after formatting.
        """
        self.copyToClip(self.dlgRef.calc.formatNum(self.tab.currentWidget().
                                                   selectedValue()))

    #@+node:tom.20230424130102.117: *4* copyToClip
    def copyToClip(self, text):
        """Copy text to the clipboard.
        """
        clip = QApplication.clipboard()
        if clip.supportsSelection():
            clip.setText(text, QClipboard.Selection)
        clip.setText(text)

    #@+node:tom.20230424130102.118: *4* keyPressEvent
    def keyPressEvent(self, keyEvent):
        """Pass most keypresses to main dialog.
        """
        if keyEvent.modifiers == Qt.AltModifier:
            QWidget.keyPressEvent(self, keyEvent)
        else:
            self.dlgRef.keyPressEvent(keyEvent)

    #@+node:tom.20230424130102.119: *4* keyReleaseEvent
    def keyReleaseEvent(self, keyEvent):
        """Pass most key releases to main dialog.
        """
        if keyEvent.modifiers == Qt.AltModifier:
            QWidget.keyReleaseEvent(self, keyEvent)
        else:
            self.dlgRef.keyReleaseEvent(keyEvent)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@+node:tom.20230424130102.121: **  helpview
#@+others
#@+node:tom.20230424130102.122: *3* class HelpView
class HelpView(QMainWindow): # type: ignore
    """Main window for viewing an html help file.
    """
    #@+others
    #@+node:tom.20230424130102.123: *4* __init__
    def __init__(self, path, caption, icons, parent=None):
        """Helpview initialize with text.
        """
        QMainWindow.__init__(self, parent)
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, False)
        self.setWindowFlags(Qt.WindowType.Window)
        self.setStatusBar(QStatusBar())
        self.textView = HelpViewer(self)
        self.setCentralWidget(self.textView)

        self.textView.setHtml(HELPDOC)
        self.resize(520, 500)
        self.setWindowTitle(caption)
        tools = self.addToolBar('Tools')
        self.menu = QMenu(self.textView)
        # self.textView.highlighted[str].connect(self.showLink) ????
        self.textView.highlighted.connect(self.showLink)

        backAct = QAction('&Back', self)
        backAct.setIcon(icons['helpback'])
        tools.addAction(backAct)
        self.menu.addAction(backAct)
        backAct.triggered.connect(self.textView.backward)
        backAct.setEnabled(False)
        self.textView.backwardAvailable.connect(backAct.setEnabled)

        forwardAct = QAction('&Forward', self)
        forwardAct.setIcon(icons['helpforward'])
        tools.addAction(forwardAct)
        self.menu.addAction(forwardAct)
        forwardAct.triggered.connect(self.textView.forward)
        forwardAct.setEnabled(False)
        self.textView.forwardAvailable.connect(forwardAct.setEnabled)

        homeAct = QAction('&Home', self)
        homeAct.setIcon(icons['helphome'])
        tools.addAction(homeAct)
        self.menu.addAction(homeAct)
        homeAct.triggered.connect(self.textView.home)

        tools.addSeparator()
        tools.addSeparator()
        findLabel = QLabel(' Find: ', self)
        tools.addWidget(findLabel)
        self.findEdit = QLineEdit(self)
        tools.addWidget(self.findEdit)
        self.findEdit.textEdited.connect(self.findTextChanged)
        self.findEdit.returnPressed.connect(self.findNext)

        self.findPreviousAct = QAction('Find &Previous', self)
        self.findPreviousAct.setIcon(icons['helpprevious'])
        tools.addAction(self.findPreviousAct)
        self.menu.addAction(self.findPreviousAct)
        self.findPreviousAct.triggered.connect(self.findPrevious)
        self.findPreviousAct.setEnabled(False)

        self.findNextAct = QAction('Find &Next', self)
        self.findNextAct.setIcon(icons['helpnext'])
        tools.addAction(self.findNextAct)
        self.menu.addAction(self.findNextAct)
        self.findNextAct.triggered.connect(self.findNext)
        self.findNextAct.setEnabled(False)

    #@+node:tom.20230424130102.124: *4* showLink
    def showLink(self, text):
        """Send link text to the statusbar.
        """
        self.statusBar().showMessage(f'{text}')

    #@+node:tom.20230424130102.125: *4* findTextChanged
    def findTextChanged(self, text):
        """Update find controls based on text in text edit.
        """
        self.findPreviousAct.setEnabled(len(text) > 0)
        self.findNextAct.setEnabled(len(text) > 0)

    #@+node:tom.20230424130102.126: *4* findPrevious
    def findPrevious(self):
        """Command to find the previous string.
        """
        if self.textView.find(self.findEdit.text(),
                              QTextDocument.FindFlag.FindBackward):
            self.statusBar().clearMessage()
        else:
            self.statusBar().showMessage('Text string not found')

    #@+node:tom.20230424130102.127: *4* findNext
    def findNext(self):
        """Command to find the next string.
        """
        if self.textView.find(self.findEdit.text()):
            self.statusBar().clearMessage()
        else:
            self.statusBar().showMessage('Text string not found')


    #@-others
#@+node:tom.20230424130102.128: *3* class HelpViewer
class HelpViewer(QTextBrowser):  # type: ignore
    """Shows an html help file.
    """
    #@+others
    #@+node:tom.20230424130102.129: *4* __init__
    def __init__(self, parent=None):
        QTextBrowser.__init__(self, parent)
        self.setOpenLinks(False)
        self.anchorClicked.connect(self.setSource)

    #@+node:tom.20230424130102.130: *4* setSource
    def setSource(self, url):
        """Called when user clicks on a URL.
        """
        name = url.toString()
        if name.startswith('http'):
            webbrowser.open(name, True)
        else:
            QTextBrowser.setSource(self, url)

    #@+node:tom.20230424130102.131: *4* contextMenuEvent
    def contextMenuEvent(self, event):
        """Init popup menu on right click"".
        """
        self.parentWidget().menu.exec_(event.globalPos())
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@+node:tom.20230424130102.134: ** class IconDict
class IconDict(dict):
    """Stores icons by name, loads on demand.
    """
    iconExt = ['.png', '.bmp']
    #@+others
    #@+node:tom.20230424130102.135: *3* __init__
    def __init__(self):
        dict.__init__(self, {})
        self.pathList = [iconPath]

    #@+node:tom.20230424130102.136: *3* addIconPath
    def addIconPath(self, potentialPaths = []):
        pass
    #@+node:tom.20230424130102.137: *3* __getitem__
    def __getitem__(self, name):
        """Return icon, loading if necessary.
        """
        try:
            return dict.__getitem__(self, name)
        except KeyError:
            icon = self.loadIcon(name)
            if not icon:
                raise
            return icon

    #@+node:tom.20230424130102.138: *3* loadAllIcons
    def loadAllIcons(self):
        """Load all icons available in self.pathList.
        """
        self.clear()
        for path in self.pathList:
            try:
                for name in os.listdir(path):
                    pixmap = QPixmap(os.path.join(path, name))
                    if not pixmap.isNull():
                        name = os.path.splitext(name)[0]
                        try:
                            icon = self[name]
                        except KeyError:
                            icon = QIcon()
                            self[name] = icon
                        icon.addPixmap(pixmap)
            except OSError:
                pass
        print(self.items())
    #@+node:tom.20230424130102.139: *3* loadIcon
    def loadIcon(self, iconName):
        """Load icon from iconPath, add to dictionary and return the icon.
        """
        icon = QIcon()
        for path in self.pathList:
            for ext in IconDict.iconExt:
                fileName = iconName + ext
                pixmap = QPixmap(os.path.join(path, fileName))
                if not pixmap.isNull():
                    icon.addPixmap(pixmap)
                if not icon.isNull():
                    self[iconName] = icon
                    return icon
        return None
    #@-others
#@+node:tom.20230424130102.142: ** class Option
class Option:
    """Stores and retrieves string options.
    """
    #@+others
    #@+node:tom.20230424130102.143: *3* __init__
    def __init__(self, baseFileName, keySpaces=20):
        self.path = ''
        if baseFileName:
            if sys.platform.startswith('win'):
                fileName = '{0}.ini'.format(baseFileName)
                userPath = os.environ.get('APPDATA', '')
                if userPath:
                    userPath = os.path.join(userPath, 'bellz', baseFileName)
            else:
                fileName = '.{0}'.format(baseFileName)
                userPath = os.environ.get('HOME', '')
            self.path = os.path.join(userPath, fileName)
            if not os.path.exists(self.path):
                modPath = os.path.abspath(sys.path[0])
                if modPath.endswith('.zip') or modPath.endswith('.exe'):
                    modPath = os.path.dirname(modPath)  # for py2exe/cx_freeze
                self.path = os.path.join(modPath, fileName)
                if not os.access(self.path, os.W_OK):
                    self.path = os.path.join(userPath, fileName)
                    if not os.path.exists(userPath):
                        try:
                            os.makedirs(userPath)
                        except OSError:
                            print('Error - could not write to config dir')
                            self.path = ''
        self.keySpaces = keySpaces
        self.dfltDict = {} # type: ignore
        self.userDict = {} # type: ignore
        self.dictList = (self.userDict, self.dfltDict)
        self.chgList = []

    #@+node:tom.20230424130102.144: *3* loadAll
    def loadAll(self, defaultList):
        """Reads defaultList & file, writes file if required
           return true if file read.
        """
        self.loadSet(defaultList, self.dfltDict)
        if self.path:
            try:
                with open(self.path, 'r', encoding='utf-8') as f:
                    self.loadSet(f.readlines(), self.userDict)
                    return True
            except IOError:
                try:
                    with open(self.path, 'w', encoding='utf-8') as f:
                        f.writelines([line + '\n' for line in defaultList])
                except IOError:
                    print('Error - could not write to config file', self.path)
                    self.path = ''
                return False
        return False

    #@+node:tom.20230424130102.145: *3* loadSet
    def loadSet(self, list, data):
        """Reads settings from list into dict.
        """
        for line in list:
            line = line.split('#', 1)[0].strip()
            if line:
                item = line.split(None, 1) + ['']   # add value if blank
                data[item[0]] = item[1].strip()

    #@+node:tom.20230424130102.146: *3* addData
    def addData(self, key, strData, storeChange=0):
        """Add new entry, add to write list if storeChange.
        """
        self.userDict[key] = strData
        if storeChange:
            self.chgList.append(key)

    #@+node:tom.20230424130102.147: *3* boolData
    def boolData(self, key):
        """Returns true or false from yes or no in option data.
        """
        for data in self.dictList:
            val = data.get(key)
            if val and val[0] in ('y', 'Y'):
                return True
            if val and val[0] in ('n', 'N'):
                return False
        print('Option error - bool key', key, 'is not valid')
        return False

    #@+node:tom.20230424130102.148: *3* numData
    def numData(self, key, min=None, max=None):
        """Return float from option data.
        """
        for data in self.dictList:
            val = data.get(key)
            if val:
                try:
                    num = float(val)
                    if (min == None or num >= min) and \
                       (max == None or num <= max):
                        return num
                except ValueError:
                    pass
        print('Option error - float key', key, 'is not valid')
        return 0

    #@+node:tom.20230424130102.149: *3* intData
    def intData(self, key, min=None, max=None):
        """Return int from option data.
        """
        for data in self.dictList:
            val = data.get(key)
            if val:
                try:
                    num = int(val)
                    if (min == None or num >= min) and \
                       (max == None or num <= max):
                        return num
                except ValueError:
                    pass
        print('Option error - int key', key, 'is not valid')
        return 0

    #@+node:tom.20230424130102.150: *3* strData
    def strData(self, key, emptyOk=0):
        """Return string from option data.
        """
        for data in self.dictList:
            val = data.get(key)
            if val != None:
                if val or emptyOk:
                    return val
        print('Option error - string key', key, 'is not valid')
        return ''

    #@+node:tom.20230424130102.151: *3* changeData
    def changeData(self, key, strData, storeChange):
        """Change entry, add to write list if storeChange
           Return true if changed.
        """
        for data in self.dictList:
            val = data.get(key)
            if val != None:
                if strData == val:  # no change reqd
                    return False
                self.userDict[key] = strData
                if storeChange:
                    self.chgList.append(key)
                return True
        print('Option error - key', key, 'is not valid')
        return False

    #@+node:tom.20230424130102.152: *3* writeChanges
    def writeChanges(self):
        """Write any stored changes to the option file - rtn true on success.
        """
        if self.path and self.chgList:
            try:
                with open(self.path, 'r', encoding='utf-8') as f:
                    fileList = f.readlines()
                for key in self.chgList[:]:
                    hitList = [line for line in fileList if
                               line.strip().split(None, 1)[:1] == [key]]
                    if not hitList:
                        hitList = [line for line in fileList if
                                   line.replace('#', ' ', 1).strip().
                                   split(None, 1)[:1] == [key]]
                    if hitList:
                        fileList[fileList.index(hitList[-1])] = '{0}{1}\n'.\
                                format(key.ljust(self.keySpaces),
                                       self.userDict[key])
                        self.chgList.remove(key)
                for key in self.chgList:
                    fileList.append('{0}{1}\n'.format(key.ljust(self.keySpaces),
                                                      self.userDict[key]))
                with open(self.path, 'w', encoding='utf-8') as f:
                    f.writelines([line for line in fileList])
                return True
            except IOError:
                print('Error - could not write to config file', self.path)
        return False
    #@-others
#@+node:tom.20230424130102.156: **  optiondlg
#@+others
#@+node:tom.20230424130102.157: *3* class OptionDlg
class OptionDlg(QDialog): # type: ignore
    """Works with Option class to provide a dialog for pref/options.
    """
    #@+others
    #@+node:tom.20230424130102.158: *4* __init__
    def __init__(self, option, parent=None):
        QDialog.__init__(self, parent)
        self.setWindowFlags(DialogCode.Accepted
                            | WindowType.WindowTitleHint
                            | WindowType.WindowSystemMenuHint)
        self.option = option

        topLayout = QVBoxLayout(self)
        self.setLayout(topLayout)
        self.columnLayout = QHBoxLayout()
        topLayout.addLayout(self.columnLayout)
        self.gridLayout = QGridLayout()
        self.columnLayout.addLayout(self.gridLayout)
        self.oldLayout = self.gridLayout

        ctrlLayout = QHBoxLayout()
        topLayout.addLayout(ctrlLayout)
        ctrlLayout.addStretch(0)
        okButton = QPushButton('&OK', self)
        ctrlLayout.addWidget(okButton)
        okButton.clicked.connect(self.accept)
        cancelButton = QPushButton('&Cancel', self)
        ctrlLayout.addWidget(cancelButton)
        cancelButton.clicked.connect(self.reject)
        self.setWindowTitle('Preferences')
        self.itemList = []
        self.curGroup = None

    #@+node:tom.20230424130102.159: *4* addItem
    def addItem(self, dlgItem, widget, label=None):
        """Add a control with optional label, called by OptionDlgItem.
        """
        row = self.gridLayout.rowCount()
        if label:
            self.gridLayout.addWidget(label, row, 0)
            self.gridLayout.addWidget(widget, row, 1)
        else:
            self.gridLayout.addWidget(widget, row, 0, 1, 2)
        self.itemList.append(dlgItem)

    #@+node:tom.20230424130102.160: *4* startGroupBox
    def startGroupBox(self, title, intSpace=5):
        """Use a group box for next added items.
        """
        self.curGroup = QGroupBox(title, self)
        row = self.oldLayout.rowCount()
        self.oldLayout.addWidget(self.curGroup, row, 0, 1, 2)
        self.gridLayout = QGridLayout(self.curGroup)
        self.gridLayout.setVerticalSpacing(intSpace)

    #@+node:tom.20230424130102.161: *4* endGroupBox
    def endGroupBox(self):
        """Cancel group box for next added items.
        """
        self.gridLayout = self.oldLayout
        self.curGroup = None

    #@+node:tom.20230424130102.162: *4* startNewColumn
    def startNewColumn(self):
        """Cancel any group box and start a second column.
        """
        self.curGroup = None
        # row = self.oldLayout.rowCount()
        self.gridLayout = QGridLayout()
        self.columnLayout.addLayout(self.gridLayout)
        self.oldLayout = self.gridLayout

    #@+node:tom.20230424130102.163: *4* parentGroup
    def parentGroup(self):
        """Return parent for new widgets.
        """
        if self.curGroup:
            return self.curGroup
        return self

    #@+node:tom.20230424130102.164: *4* accept
    def accept(self):
        """Called by dialog when OK button pressed.
        """
        for item in self.itemList:
            item.updateData()
        QDialog.accept(self)


    #@-others
#@+node:tom.20230424130102.165: *3* class OptionDlgItem
class OptionDlgItem:
    """Base class for items to add to dialog.
    """
    #@+others
    #@+node:tom.20230424130102.166: *4* __init__
    def __init__(self, dlg, key, writeChg):
        self.dlg = dlg
        self.key = key
        self.writeChg = writeChg
        self.control = None

    #@+node:tom.20230424130102.167: *4* updateData
    def updateData(self):
        """Dummy update function.
        """
        pass

    #@-others
#@+node:tom.20230424130102.168: *3* class OptionDlgBool
class OptionDlgBool(OptionDlgItem):
    """Holds widget for bool checkbox.
    """
    #@+others
    #@+node:tom.20230424130102.169: *4* __init__
    def __init__(self, dlg, key, menuText, writeChg=True):
        OptionDlgItem.__init__(self, dlg, key, writeChg)
        self.control = QCheckBox(menuText, dlg.parentGroup())
        self.control.setChecked(dlg.option.boolData(key))
        dlg.addItem(self, self.control)

    #@+node:tom.20230424130102.170: *4* updateData
    def updateData(self):
        """Update Option class based on checkbox status.
        """
        if self.control.isChecked() != self.dlg.option.boolData(self.key):
            if self.control.isChecked():
                self.dlg.option.changeData(self.key, 'yes', self.writeChg)
            else:
                self.dlg.option.changeData(self.key, 'no', self.writeChg)

    #@-others
#@+node:tom.20230424130102.171: *3* class OptionDlgInt
class OptionDlgInt(OptionDlgItem):
    """Holds widget for int spinbox.
    """
    #@+others
    #@+node:tom.20230424130102.172: *4* __init__
    def __init__(self, dlg, key, menuText, min, max, writeChg=True, step=1,
                 wrap=False, suffix=''):
        OptionDlgItem.__init__(self, dlg, key, writeChg)
        label = QLabel(menuText, dlg.parentGroup())
        self.control = QSpinBox(dlg.parentGroup())
        self.control.setMinimum(min)
        self.control.setMaximum(max)
        self.control.setSingleStep(step)
        self.control.setWrapping(wrap)
        self.control.setSuffix(suffix)
        self.control.setValue(dlg.option.intData(key, min, max))
        dlg.addItem(self, self.control, label)

    #@+node:tom.20230424130102.173: *4* updateData
    def updateData(self):
        """Update Option class based on spinbox status.
        """
        if self.control.value() != int(self.dlg.option.numData(self.key)):
            self.dlg.option.changeData(self.key, repr(self.control.value()),
                                       self.writeChg)

    #@-others
#@+node:tom.20230424130102.174: *3* class OptionDlgDbl
class OptionDlgDbl(OptionDlgItem):
    """Holds widget for double line edit.
    """
    #@+others
    #@+node:tom.20230424130102.175: *4* __init__
    def __init__(self, dlg, key, menuText, min, max, writeChg=True):
        OptionDlgItem.__init__(self, dlg, key, writeChg)
        label = QLabel(menuText, dlg.parentGroup())
        self.control = QLineEdit(repr(dlg.option.numData(key, min, max)),
                                       dlg.parentGroup())
        valid = QDoubleValidator(min, max, 6, self.control)
        self.control.setValidator(valid)
        dlg.addItem(self, self.control, label)

    #@+node:tom.20230424130102.176: *4* updateData
    def updateData(self):
        """Update Option class based on edit status.
        """
        text = self.control.text()
        unusedPos = 0
        if self.control.validator().validate(text, unusedPos)[0] != \
                QValidator.Acceptable:
            return
        num = float(text)
        if num != self.dlg.option.numData(self.key):
            self.dlg.option.changeData(self.key, repr(num), self.writeChg)

    #@-others
#@+node:tom.20230424130102.177: *3* class OptionDlgStr
class OptionDlgStr(OptionDlgItem):
    """Holds widget for string line edit.
    """
    #@+others
    #@+node:tom.20230424130102.178: *4* __init__
    def __init__(self, dlg, key, menuText, writeChg=True):
        OptionDlgItem.__init__(self, dlg, key, writeChg)
        label = QLabel(menuText, dlg.parentGroup())
        self.control = QLineEdit(dlg.option.strData(key, True),
                                       dlg.parentGroup())
        dlg.addItem(self, self.control, label)

    #@+node:tom.20230424130102.179: *4* updateData
    def updateData(self):
        """Update Option class based on edit status.
        """
        newStr = self.control.text()
        if newStr != self.dlg.option.strData(self.key, True):
            self.dlg.option.changeData(self.key, newStr, self.writeChg)

    #@-others
#@+node:tom.20230424130102.180: *3* class OptionDlgRadio
class OptionDlgRadio(OptionDlgItem):
    """Holds widget for exclusive radio button group.
    """
    #@+others
    #@+node:tom.20230424130102.181: *4* __init__
    def __init__(self, dlg, key, headText, textList, writeChg=True):
        # textList is list of tuples: optionText, labelText
        OptionDlgItem.__init__(self, dlg, key, writeChg)
        self.optionList = [x[0] for x in textList]
        buttonBox = QGroupBox(headText, dlg.parentGroup())
        self.control = QButtonGroup(buttonBox)
        layout = QVBoxLayout(buttonBox)
        buttonBox.setLayout(layout)
        optionSetting = dlg.option.strData(key)
        id = 0
        for optionText, labelText in textList:
            button = QRadioButton(labelText, buttonBox)
            layout.addWidget(button)
            self.control.addButton(button, id)
            id += 1
            if optionText == optionSetting:
                button.setChecked(True)
        dlg.addItem(self, buttonBox)

    #@+node:tom.20230424130102.182: *4* updateData
    def updateData(self):
        """Update Option class based on button status.
        """
        data = self.optionList[self.control.checkedId()]
        if data != self.dlg.option.strData(self.key):
            self.dlg.option.changeData(self.key, data, self.writeChg)

    #@-others
#@+node:tom.20230424130102.183: *3* class OptionDlgPush
class OptionDlgPush(OptionDlgItem):
    """Holds widget for extra misc. push button.
    """
    def __init__(self, dlg, text, cmd):
        OptionDlgItem.__init__(self, dlg, '', 0)
        self.control = QPushButton(text, dlg.parentGroup())
        self.control.clicked.connect(cmd)
        dlg.addItem(self, self.control)
#@-others
#@@language python
#@@tabwidth -4
#@+node:tom.20230426112545.1: ** helpfile
HELPDOC = """
#@+<< help text >>
#@+node:tom.20230502081206.1: *3* << help text >>
<html>
<head>
<title>rpCalc ReadMe</title>
<style type='text/css'>
    a {color: darkorchid;}
</style>
</head>
<body>
<center>
<h1>ReadMe file for rpCalc</h1>
<h2>a reverse polish notation calculator</h2>

<p>Written by Doug Bell<br>
Version 0.8.2<br>
April 8, 2018</p>
<p>Version 0.9<br>
Modified For The Leo Editor by T. B. Passin April 26, 2023
</center>

<h2>Contents</h2>

<ul>
<li><a href="#background">Background</a></li>
<li><a href="#features">Features</a></li>
<li><a href="#legal">Legal Issues</a></li>
<li><a href="#install">Installation</a>
<li><a href="#using">Using rpCalc</a>
  <ul><li><a href="#basics">Basics</a></li>
  <li><a href="#info-win">Information Windows</a></li>
  <li><a href="#alt-base">Alternate Bases</a></li>
  <li><a href="#option">Options</a></li></ul></li>
<li><a href="#revs">Revision History</a></li>
<li><a href="#contact">Questions, Comments, Criticisms?</a></li>
</ul>

<h2><a name="background"></a>Background</h2>

<p>rpCalc started out as a small program written to try out various
Python GUI toolkits.  But I ended up using it all the time (it's much
quicker to pull it up than to pull an actual HP calculator out of the
desk), and I made several improvements.  So I decided to make it
available to others who also like RPN calculators.</p>

<p>Since I'm not in the software business, I'm making this program
free for anyone to use, distribute and modify, as long as it is not
incorporated into any proprietary programs.  If you like the software,
feel free to let others know about it.  And let me know what you think
- my e-mail address is doug101 AT bellz DOT org.<br><br>

<strong>Do not use the above address for matters related to the Leo
plugin.</strong>. See the <a href="#contact">contact links</a> at the end.</p>

<p>The same GPL2 license applies to the modifications to work as
a Leo plugin.</p>

<h2><a name="features"></a>Features</h2>

<ul>

  <li>Uses reverse polish notation, similar to most Hewlett-Packard
  calculators.</li>

  <li>The number, operator or command text on any key can be typed, or
  the mouse can be used to hit the key.</li>

  <li>If desired, the four RPN registers can be shown in the main
  display.</li>

  <li>A separate window can display the four RPN registers, a history of
  recent calculations, or the contents of the ten memory registers.</li>

  <li>A separate window converts to and from other number bases
  (hexadecimal, octal and binary).</li>

  <li>Any values from the extra windows can be copied to the calculator
  display or to the clipboard.</li>

  <li>Options can be set to control the display of numbers and the
  initial window configuration.</li>

  <li>The calculation result (the number on the bottom of the stack,
  also called the "X" position) can be copied to the clipboard.</li>

</ul>

<h2><a name="legal"></a>Legal Issues</h2>

<p>rpCalc is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either Version 2 of the License, or (at your
option) any later version.</p>

<p>This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY.  See the <tt>LICENSE</tt> file provided with
this program for more information.</p>

<h2><a name="install"></a>Installation</h2>
The Leo Plugin requires no installation.  It must be enabled in the
<i>@enabled-plugins</i> node of your <i>myLeoSettings</i> outline.  Add
a line "rpcalc.py" to the node.

<h2><a name="using"></a>Using The RPCalc</h2>

<h3>Toggling The RPCalc Tab On And Off</h3>
After the plugin has been enabled and Leo has been restarted, a new button
will be present in the icon bar.  It is labeled "RPCalc". Clicking it will
add or remove a RPCalc tab in Leo's log frame.<br><br>

In addition, the tab can be toggled using the minibuffer command
<i>rpcalc-toggle</i>, or by using the <i>Plugins/rpcalc</i> menu item.

<h3><a name="basics"></a>Basics</h3>

<p>If you know how to use an RPN calculator (like some Hewlett-Packard
models), you know how to use rpCalc.  It stores previous results in four
registers (usually labeled X, Y, Z and T), and the numbers are entered
before the operators.</p>

<p>The quickest way to enter numbers and the four basic operators is to
use the number pad on the keyboard.  For the other keys, the name on the
key can be typed (not case-sensitive).  What has been typed shows in the
box below the keys.  The tab key may be used to automatically complete a
partially typed command.  Of course, the mouse may also be used to hit
any key.</p>

<p>A few keys have unusual labels to allow them to be typed:  "RCIP"
is 1/X, "tn^X" is 10^X, "R^" rolls the stack forward (or up),
"R&gt;" rolls the stack back (or down), "x&lt;&gt;y" is exchange,
"CLR" clears the registers, and "&lt;-" is backspace.</p>

<p>A few commands ("STO", "RCL" and "PLCS") prompt for a number from
zero through nine.  This number will be the memory register number or
the number of decimal places for the display.</p>

<p>The ">CLIP" key copies the stack bottom (the "X" register) to the system clipboard.</p>

<h3><a name="info-win"></a>Information Windows</h3>

<p>A menu can be displayed by hitting the Esc key or by clicking on the
main number (LCD) display with the right mouse button.  This menu
includes commands to display a list of registers, a calculation history
list, and a memory contents list.  These commands will show a new
window with the requested information.  The extra window is tabbed to
toggle between the three lists.  Buttons on the window can be used to
copy the numbers to the calculator (X-register) or to the clipboard
(with buttons to copy either all decimal places or the formatted fixed
decimal place number).</p>

<p>The register list shows the current contents of each register (X, Y,
Z and T).  The numbers are shown to full precision, with all available
decimal places shown.</p>

<p>The history list shows algebraic equations for every calculation that
was done in the current rpCalc session.  The numbers are shown to the
same precision as the main display.</p>

<p>The memory list shows the current contents of the ten memory
registers (0-9).  The numbers are shown to the same precision as the
main display.</p>

<h3><a name="alt-base"></a>Alternate Bases</h3>

<p>An alternate base window can be shown from the display context menu
(right-click the LCD or hit the Esc key).  This window shows the
hexadecimal, octal and binary equivalents of the number in the
X-register, rounded to the nearest integer.</p>

<p>The Hex, Octal, Binary and Decimal buttons are used to change the
input mode to that base.  There are also keyboard shortcuts (Alt-x,
Alt-o, Alt-b and Alt-d) that do the same thing.  Any typed number is
then interpreted using the current base.  The current mode is kept
until the user changes it.</p>

<p>Prefixes consisting of a zero followed by the base code (x, o, b or
d) can be used to temporarily change the input mode.  For example,
"0x56c" enters the hex number 56c (1388 in decimal).  The input mode
goes back to decimal after hitting enter or using a function.  Note that
the alternate base window must be displayed for these prefixes to
function.</p>

<p>When using non-decimal input modes, the decimal equivalent of the
entry is still displayed on the main LCD.  Also, when in hex input mode,
commands beginning with letters A-F can only be typed if a colon (":")
is used as a command prefix.</p>

<p>There is also a Copy Value button that copies the value of the
current input mode base to the clipboard for use in other
applications.</p>

<p>The option dialog has a setting for a limit on the number of bits.
Numbers larger than the limit will display "overflow" in the alternate
base window.  There is also a setting to show negative numbers as a
two's complement number.</p>

<h3><a name="option"></a>Options</h3>

<p>The OPT key will show an options dialog box.  This includes settings
for startup conditions, display parameters, angle units, alternate bases
and extra views.</p>

<p>The startup options include whether to save the register entries
between sessions and whether to open the extra data or alternate base
windows when starting rpCalc.</p>

<p>The display options include several number formatting settings.  The
number of decimal places, use of space as a thousands separator and
various exponent and engineering notation (exponents divisible by three)
options can be set.  There are also settings for viewing all four RPN
registers on the main display and for hiding the LCD highlight (clearer
for some resolution and window size settings).</p>

<p>The extra views section includes buttons for showing the extra data
window, the alternate base window, and this readme file.  The number of
saved equations in the history list can also be set.</p>

<h2><a name="revs"></a>Revision History</h2>

<h3>May 1, 2023 - Release 0.9 of the Leo plugin version</h3>

<h3>April 8, 2018 - Release 0.8.2</h3>

<ul><b>Updates:</b>

  <li>Added a desktop file to the Linux version to provide menu entries.</li>

  <li>Built the Windows version with an updated version of the GUI
    library.</li>

</ul>

<h3>February 4, 2017 - Release 0.8.1 (Linux only)</h3>

<ul><b>Bug Fixes:</b>

  <li>Replaced outdated dependency checks in the Linux installer - it now
    runs checks for Qt5 libraries.</li>

  <li>Fixed a timing issue in the Linux installer so that byte-compiled files
    do not have old timestamps.</li>

</ul>

<h3>January 15, 2017 - Release 0.8.0</h3>

<ul><b>New Features:</b>

  <li>rpCalc has been ported from the Qt4 to the Qt5 library.</li>

</ul>

<h3>December 6, 2015 - Release 0.7.1</h3>

<ul><b>Updates:</b>

  <li>Clarified some dependency checker error messages in the Linux
  installer.</li>

  <li>Added some MSVC runtime DLL files to the Windows installers to
  avoid problems on PCs that do not already have them.</li>

</ul>

<ul><b>Bug Fixes:</b>

  <li>Fixed problems responding to some keyboard presses when the shift
  key is used on Windows.</li>

</ul>

<h3>January 26, 2014 - Release 0.7.0</h3>

<ul><b>Updates:</b>

  <li>rpCalc has been ported from Python 2 to Python 3.  This porting
  includes some code cleanup.</li>

  <li>The Windows binaries are built using more recent Python, Qt and
  PyQt libraries.</li>

  <li>There is an additional Windows installer for users without
  administrator rights and for portable installations.</li>

  <li>Added an installer option to add a config file to the program's
  directory for portable installations.  If that file is present, no
  config files will be written to users' directories.</li>

</ul>

<h3>October 14, 2008 - Release 0.6.0</h3>

<ul><b>New Features:</b>

  <li>A new base conversion dialog was added.  It shows values in
  hexadecimal, octal and binary bases.  Push buttons or keyboard
  prefixes can be used to allow entry of a value in one of these
  bases.</li>

  <li>A colon (":") can optionally be used as a prefix when typing
  commands.  This is useful in hexadecimal entry mode for commands
  starting with letters "A" through "F".</li>

  <li>New options have been added for alternate base conversions.  The
  number of bits and whether to use two's complement for negative
  numbers can be set.</li>

  <li>A display option was added to separate thousands with spaces in
  the main "LCD".</li>

  <li>An engineering notation display option was added that only shows
  exponents that are divisible by three.</li>

</ul>

<ul><b>Updates:</b>

  <li>Keyboard number and function entry continue to work when the Extra
  Data window has focus.</li>

  <li>The ReadMe file has been updated.</li>

</ul>

<h3>October 3, 2006 - Release 0.5.0</h3>

<ul><b>New Features:</b>

  <li>rpCalc was ported to the Qt4 library. This involved a significant
  rewrite of the code.  The previous versions used Qt3.x on Linux and
  Qt2.3 on Windows.  Benefits include updated widgets and removal of the
  non-commercial license exception in Windows.</li>

</ul>

<ul><b>Updates:</b>

  <li>On Windows, the rpCalc.ini file has been moved from the
  installation directory to a location under the "Documents and
  Settings" folder.  This avoids problems on multi-user systems and for
  users with limited access rights.</li>

</ul>

<h3>March 12, 2004 - Release 0.4.3</h3>

<ul><b>New Features:</b>

  <li>The size and position of the main and extra windows are now saved
  at exit.</li>

  <li>An install program has been added for windows.</li>

</ul>

<ul><b>Bug Fixes:</b>

  <li>Fixed Linux install script problems with certain versions of
  Python.</li>

</ul>

<h3>November 17, 2003 - Release 0.4.2</h3>

<ul><b>New Features:</b>

  <li>Allow the use of commas in addition to periods as decimal points
  to accommodate European keyboards.</li>

</ul>

<ul><b>Updates:</b>

  <li>An install script was added for Linux and Unix systems.</li>

  <li>The windows build now uses Python version 2.3 and PyQt version
  3.8.</li>

</ul>

<h3>July 14, 2003 - Release 0.4.1</h3>

<ul><b>New Features:</b>

  <li>Added option to remove the LCD display highlight.  This is useful
  for smaller displays</li>

</ul>

<ul><b>Bug Fixes:</b>

  <li>Fixed a problem with the option to display the extra data view
  on startup.</li>

</ul>

<h3>April 30, 2003 - Release 0.4.0</h3>

<ul><b>New Features:</b>

  <li>The main display can optionally be expanded to show lines for the
  Y, Z, &amp; T registers.</li>

  <li>The three separate views for extra data (registers, history &amp;
  memory) have been replaced with a single tabbed view.</li>

</ul>

<ul><b>Updates:</b>

  <li>Icon files are now provided with the distributed files.</li>

</ul>

<ul><b>Bug Fixes:</b>

  <li>Crashes caused by some calculation overflows have been fixed.</li>

</ul>

<h3>February 27, 2003 - Release 0.3.0</h3>

<ul><b>New Features:</b>

  <li>The typing of multiple-letter command names has been made easier.
  The return key is no longer needed to finish a command, and hitting
  the tab key auto-completes a partial command.</li>

  <li>Since it is no longer needed for entering commands, the return key
  is now equivalent to the enter key.</li>

  <li>New keys have been added for setting display and angle options.
  "PLCS" prompts for the number of decimal places, "SCI" toggles between
  fixed and scientific display, and "DEG" toggles between degree and
  radian settings.  There is also a new status indicator in the lower
  right corner for these options.</li>

  <li>A new "SHOW" key temporarily toggles to a scientific display
  showing 12 significant figures.  The display goes back to normal after
  the next command or if the "SHOW" command is repeated.</li>

</ul>

<h3>May 28, 2002 - Release 0.2.2a</h3>

<ul><b>Bug Fixes:</b>

  <li>A fix of the Windows binary only.  Fixes major problems by
  upgrading the library version to PyQt 3.2.4.</li>

</ul>

<h3>May 16, 2002 - Release 0.2.2</h3>

<ul><b>Updates:</b>

  <li>rpCalc has been ported to Qt 3.x.  It now works with both Qt
  2.x and 3.x using the same source code.</li>

  <li>The help/readme file has been rewritten and now includes section
  links.</li>

  <li>The binaries for windows have been updated to Python 2.2 and PyQt
  3.2 (but are still using Qt 2.3 Non-commercial).</li>

</ul>

<h3>September 8, 2001 - Release 0.2.1</h3>

<ul><b>Bug Fixes:</b>

  <li>Fixed a problem with extra views not always updating
  properly.</li>

  <li>Fixed copying to the clipboard from the history view.</li>

</ul>

<h3>August 30, 2001 - Release 0.2.0</h3>

<ul><b>New features:</b>

  <li>Extra views listing registers, calculation history and memory
  values were added.</li>

  <li>A popup menu was added to the display.</li>

</ul>

<ul><b>Updates:</b>

  <li>Improved error handling.</li>

</ul>

<h3>August 20, 2001 - Release 0.1.2</h3>

<ul><b>Updates:</b>

  <li>The name was changed to rpCalc to avoid conflicts.</li>

  <li>For MS Windows users, the binary files were upgraded to PyQt
  Version 2.5.</li>

</ul>

<ul><b>Bug Fixes:</b>

  <li>Problems with saving changed options were fixed.</li>

</ul>

<h3>August 10, 2001 - Release 0.1.1</h3>

<ul><b>New features:</b>

  <li>Added a button to the OPT dialog to view the ReadMe file.</li>

</ul>

<ul><b>Updates:</b>

  <li>The rpcalc.ini file on windows was moved to the program
  directory.</li>

</ul>

<h3>July 2, 2001 - Release 0.1.0</h3>

<ul>

  <p>Initial release.</p>

</ul>

<h2><a name="contact"></a>Questions, Comments, Criticisms?</h2>
<div><h3>The original contact notice (not for Leo plugin issues)</h3>
<p>I can be contacted by email at: doug101 AT bellz DOT org<br> I
welcome any feedback, including reports of any bugs you find.  Also, you
can periodically check back to <a
  href="http://www.bellz.org">www.bellz.org</a> for any updates.</p>
<div>

<div><h3>For issues with the Leo plugin</h3>
Questions:
<a href='https://groups.google.com/g/leo-editor'>Leo-Editor Group site</a><br>
Issues:
<a href='https://github.com/leo-editor/leo-editor/issues'>Leo-Editor GitHub site</a>.
</div>
</body>
</html>
#@-<< help text >>
"""
#@+node:tom.20230424140347.3: ** toggle_app_tab
def toggle_app_tab(log, tabname, widget = CalcDlg):
    """Create or remove our app's tab.

    ARGUMENTS
    log -- the log panel object for this outline.
    tabname -- a string to use as the display name of our tab.
    """
    WIDGET_NAME = f'{tabname}-widget'
    VISIBLE = f'{tabname}-visible'
    LOADED = f'{tabname}-loaded'

    # If our tab is visible, remove it
    if log.contentsDict.get(VISIBLE, False):
        log.deleteTab(tabname)
        log.contentsDict[VISIBLE] = False
    else:
        # Show our tab, reusing our widget if already loaded
        if log.contentsDict.get(LOADED, False):
            log.createTab(tabname,
                          widget = log.contentsDict[WIDGET_NAME],
                          createText = False)
            log.contentsDict[VISIBLE] = True
            log.selectTab(tabname)
            w = log.contentsDict[WIDGET_NAME]
        else:
            # Create our widget for the first time
            # w = CalcDlg()
            w = widget()
            log.createTab(tabname, widget = w, createText = False)
            log.selectTab(tabname)
            log.contentsDict[LOADED] = True
            log.contentsDict[VISIBLE] = True
            log.contentsDict[WIDGET_NAME] = w
        w.setFocus(QtCore.Qt.FocusReason.OtherFocusReason)

#@-others

#@-leo
