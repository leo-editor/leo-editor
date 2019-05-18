#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" This script runs a test for the code editor component.
"""

import os, sys
from qt import QtGui, QtCore, QtWidgets
Qt = QtCore.Qt

## Go up one directory and then import the codeeditor package

os.chdir('..')
sys.path.insert(0,'.')
from codeeditor import CodeEditor


    

if __name__=='__main__':
    
    app = QtWidgets.QApplication([])
  
            
    # Create editor instance
    e = CodeEditor(highlightCurrentLine = True, longLineIndicatorPosition = 20,
        showIndentationGuides = True, showWhitespace = True,
        showLineEndings = True, wrap = True, showLineNumbers = True)

    QtWidgets.QShortcut(QtGui.QKeySequence("F1"), e).activated.connect(e.autocompleteShow)
    QtWidgets.QShortcut(QtGui.QKeySequence("F2"), e).activated.connect(e.autocompleteCancel)
    QtWidgets.QShortcut(QtGui.QKeySequence("F3"), e).activated.connect(lambda: e.calltipShow(0, 'test(foo, bar)'))
    QtWidgets.QShortcut(QtGui.QKeySequence("Shift+Tab"), e).activated.connect(e.dedentSelection) # Shift + Tab
   
    #TODO: somehow these shortcuts don't work in this test-app, but they do in
    # pyzo. May have something to do with overriding slots of Qt-native objects?
    QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+C"), e).activated.connect(e.copy)
    QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+X"), e).activated.connect(e.cut)
    QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+V"), e).activated.connect(e.paste)
    QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Shift+V"), e).activated.connect(e.pasteAndSelect)
    QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Z"), e).activated.connect(e.undo)
    QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Y"), e).activated.connect(e.redo)
    
    e.setPlainText("foo(bar)\nfor bar in range(5):\n  print bar\n" +
                    "\nclass aap:\n  def monkey(self):\n    pass\n\n")

    
    # Run application
    e.show()
    s=QtWidgets.QSplitter()
    s.addWidget(e)
    s.addWidget(QtWidgets.QLabel('test'))
    s.show()
    app.exec_()
