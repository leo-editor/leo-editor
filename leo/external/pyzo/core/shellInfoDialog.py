# -*- coding: utf-8 -*-
# Copyright (C) 2016, the Pyzo development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.


""" Module shellInfoDialog

Implements shell configuration dialog.

"""

import os, sys
from pyzo.util.qt import QtCore, QtGui, QtWidgets  # noqa

import pyzo
from pyzo.core.pyzoLogging import print
from pyzo.core.kernelbroker import KernelInfo
from pyzo import translate


## Implement widgets that have a common interface


class ShellInfoLineEdit(QtWidgets.QLineEdit):
    
    def setTheText(self, value):
        self.setText(value)
    
    def getTheText(self):
        return self.text()



class ShellInfo_name(ShellInfoLineEdit):
    
    def __init__(self, *args, **kwargs):
        ShellInfoLineEdit.__init__(self, *args, **kwargs)
        self.editingFinished.connect(self.onValueChanged)
        t = translate('shell', 'name ::: The name of this configuration.')
        self.setPlaceholderText(t.tt)
    
    
    def setTheText(self, value):
        ShellInfoLineEdit.setTheText(self, value)
        self.onValueChanged()
    
    
    def onValueChanged(self):
        self.parent().parent().parent().setTabTitle(self.getTheText())



class ShellInfo_exe(QtWidgets.QComboBox):
    
    def __init__(self, *args):
        QtWidgets.QComboBox.__init__(self, *args)
    
    def _interpreterName(self, p):
        if p.is_conda:
            return '%s  [v%s, conda]' % (p.path, p.version)
        else:
            return '%s  [v%s]' % (p.path, p.version)
    
    def setTheText(self, value):
        
        # Init
        self.clear()
        self.setEditable(True)
        self.setInsertPolicy(self.InsertAtTop)
        
        # Get known interpreters from shellDialog (which are sorted by version)
        shellDialog = self
        while not isinstance(shellDialog, ShellInfoDialog):
            shellDialog = shellDialog.parent()
        interpreters = shellDialog.interpreters
        exes = [p.path for p in interpreters]
        
        # Hande current value
        if value in exes:
            value = self._interpreterName( interpreters[exes.index(value)] )
        else:
            self.addItem(value)
        
        # Add all found interpreters
        for p in interpreters:
            self.addItem(self._interpreterName(p))
        
        # Set current text
        self.setEditText(value)
    
    
    def getTheText(self):
        #return self.currentText().split('(')[0].rstrip()
        value = self.currentText()
        if value.endswith(']') and '[' in value:
            value = value.rsplit('[', 1)[0]
        return value.strip()


class ShellInfo_ipython(QtWidgets.QCheckBox):
    
    def __init__(self, parent):
        QtWidgets.QCheckBox.__init__(self, parent)
        t = translate('shell', 'ipython ::: Use IPython shell if available.')
        self.setText(t.tt)
        self.setChecked(False)
    
    def setTheText(self, value):
        if value.lower() in ['', 'no', 'false']:  # Also for empty string; default is False
            self.setChecked(False)
        else:
            self.setChecked(True)
    
    def getTheText(self):
        if self.isChecked():
            return 'yes'
        else:
            return 'no'


class ShellInfo_gui(QtWidgets.QComboBox):
    
    # For (backward) compatibility
    COMPAT = {'QT4':'PYQT4'}
    
    # GUI names
    GUIS = [    ('None', 'no GUI support'),
                ('Auto', 'Use what is available (recommended)'),
                ('Asyncio', 'Python\'s builtin event loop'),
                ('PyQt5', 'GPL/commercial licensed wrapper to Qt'),
                ('PyQt4', 'GPL/commercial licensed wrapper to Qt'),
                ('PySide', 'LGPL licensed wrapper to Qt'),
                ('PySide2', 'LGPL licensed wrapper to Qt5'),
                ('Tornado', 'Tornado asynchronous networking library'),
                ('Tk', 'Tk widget toolkit'),
                ('WX', 'wxPython'),
                ('FLTK', 'The fast light toolkit'),
                ('GTK', 'GIMP Toolkit'),
            ]
    
    # GUI descriptions
    
    def setTheText(self, value):
        
        # Process value
        value = value.upper()
        value = self.COMPAT.get(value, value)
        
        # Set options
        ii = 0
        self.clear()
        for i in range(len(self.GUIS)):
            gui, des = self.GUIS[i]
            if value == gui.upper():
                ii = i
            self.addItem('%s  -  %s' % (gui, des))
        
        # Set current text
        self.setCurrentIndex(ii)
    
    
    def getTheText(self):
        text = self.currentText().lower()
        return text.partition('-')[0].strip()



class ShellinfoWithSystemDefault(QtWidgets.QVBoxLayout):
    
    DISABLE_SYSTEM_DEFAULT = sys.platform == 'darwin'
    SYSTEM_VALUE = ''
    
    def __init__(self, parent, widget):
        # Do not pass parent, because is a sublayout
        QtWidgets.QVBoxLayout.__init__(self)
        
        # Layout
        self.setSpacing(1)
        self.addWidget(widget)
        
        # Create checkbox widget
        if not self.DISABLE_SYSTEM_DEFAULT:
            t = translate('shell', 'Use system default')
            self._check = QtWidgets.QCheckBox(t, parent)
            self._check.stateChanged.connect(self.onCheckChanged)
            self.addWidget(self._check)
        
        # The actual value of this shell config attribute
        self._value = ''
        
        # A buffered version, so that clicking the text box does not
        # remove the value at once
        self._bufferedValue = ''
    
    
    def onEditChanged(self):
        if self.DISABLE_SYSTEM_DEFAULT or not self._check.isChecked():
            self._value = self.getWidgetText()
    
    
    def onCheckChanged(self, state):
        if state:
            self._bufferedValue = self._value
            self.setTheText(self.SYSTEM_VALUE)
        else:
            self.setTheText(self._bufferedValue)
    
    
    def setTheText(self, value):
        
        if self.DISABLE_SYSTEM_DEFAULT:
            # Just set the value
            self._edit.setReadOnly(False)
            self.setWidgetText(value)
        
        elif value != self.SYSTEM_VALUE:
            # Value given, enable edit
            self._check.setChecked(False)
            self._edit.setReadOnly(False)
            # Set the text
            self.setWidgetText(value)
        
        else:
            # Use system default, disable edit widget
            self._check.setChecked(True)
            self._edit.setReadOnly(True)
            # Set text using system environment
            self.setWidgetText(None)
        
        # Store value
        self._value = value
    
    
    def getTheText(self):
        return self._value



class ShellInfo_pythonPath(ShellinfoWithSystemDefault):
    
    SYSTEM_VALUE = '$PYTHONPATH'
    
    def __init__(self, parent):
        
        # Create sub-widget
        self._edit = QtWidgets.QTextEdit(parent)
        self._edit.zoomOut(1)
        self._edit.setMaximumHeight(80)
        self._edit.setMinimumWidth(200)
        self._edit.textChanged.connect(self.onEditChanged)
        
        # Instantiate
        ShellinfoWithSystemDefault.__init__(self, parent, self._edit)
    
    
    def getWidgetText(self):
        return self._edit.toPlainText()
    
    
    def setWidgetText(self, value=None):
        if value is None:
            pp = os.environ.get('PYTHONPATH','')
            pp = pp.replace(os.pathsep, '\n').strip()
            value = '$PYTHONPATH:\n%s\n' % pp
        self._edit.setText(value)



# class ShellInfo_startupScript(ShellinfoWithSystemDefault):
#
#     SYSTEM_VALUE = '$PYTHONSTARTUP'
#
#     def __init__(self, parent):
#
#         # Create sub-widget
#         self._edit = QtWidgets.QLineEdit(parent)
#         self._edit.textEdited.connect(self.onEditChanged)
#
#         # Instantiate
#         ShellinfoWithSystemDefault.__init__(self, parent, self._edit)
#
#
#     def getWidgetText(self):
#         return self._edit.text()
#
#
#     def setWidgetText(self, value=None):
#         if value is None:
#             pp = os.environ.get('PYTHONSTARTUP','').strip()
#             if pp:
#                 value = '$PYTHONSTARTUP: "%s"' % pp
#             else:
#                 value = '$PYTHONSTARTUP: None'
#
#         self._edit.setText(value)



class ShellInfo_startupScript(QtWidgets.QVBoxLayout):
    
    DISABLE_SYSTEM_DEFAULT = sys.platform == 'darwin'
    SYSTEM_VALUE = '$PYTHONSTARTUP'
    RUN_AFTER_GUI_TEXT = '# AFTER_GUI - code below runs after integrating the GUI\n'
    
    def __init__(self, parent):
        # Do not pass parent, because is a sublayout
        QtWidgets.QVBoxLayout.__init__(self)
        
        # Create sub-widget
        self._edit1 = QtWidgets.QLineEdit(parent)
        self._edit1.textEdited.connect(self.onEditChanged)
        if sys.platform.startswith('win'):
            self._edit1.setPlaceholderText('C:\\path\\to\\script.py')
        else:
            self._edit1.setPlaceholderText('/path/to/script.py')
        #
        self._edit2 = QtWidgets.QTextEdit(parent)
        self._edit2.zoomOut(1)
        self._edit2.setMaximumHeight(80)
        self._edit2.setMinimumWidth(200)
        self._edit2.textChanged.connect(self.onEditChanged)
        
        # Layout
        self.setSpacing(1)
        self.addWidget(self._edit1)
        self.addWidget(self._edit2)
        
        # Create radio widget for system default
        t = translate('shell', 'Use system default')
        self._radio_system = QtWidgets.QRadioButton(t, parent)
        self._radio_system.toggled.connect(self.onCheckChanged)
        self.addWidget(self._radio_system)
        if self.DISABLE_SYSTEM_DEFAULT:
            self._radio_system.hide()
        
        # Create radio widget for file
        t = translate('shell', 'File to run at startup')
        self._radio_file = QtWidgets.QRadioButton(t, parent)
        self._radio_file.toggled.connect(self.onCheckChanged)
        self.addWidget(self._radio_file)
        
        # Create radio widget for code
        t = translate('shell', 'Code to run at startup')
        self._radio_code = QtWidgets.QRadioButton(t, parent)
        self._radio_code.toggled.connect(self.onCheckChanged)
        self.addWidget(self._radio_code)
        
        # The actual value of this shell config attribute
        self._value = ''
        
        # A buffered version, so that clicking the text box does not
        # remove the value at once
        self._valueFile = ''
        self._valueCode = '\n'
    
    
    def onEditChanged(self):
        if self._radio_file.isChecked():
            self._value = self._valueFile = self._edit1.text().strip()
        elif self._radio_code.isChecked():
            # ensure newline!
            self._value = self._valueCode = self._edit2.toPlainText().strip() + '\n'
    
    
    def onCheckChanged(self, state):
        if self._radio_system.isChecked():
            self.setWidgetText(self.SYSTEM_VALUE)
        elif self._radio_file.isChecked():
            self.setWidgetText(self._valueFile)
        elif self._radio_code.isChecked():
            self.setWidgetText(self._valueCode)
    
    
    def setTheText(self, value):
        self.setWidgetText(value, True)
        self._value = value
        
    
    def setWidgetText(self, value, init=False):
        self._value = value
        
        if value == self.SYSTEM_VALUE and not self.DISABLE_SYSTEM_DEFAULT:
            # System default
            if init:
                self._radio_system.setChecked(True)
            pp = os.environ.get('PYTHONSTARTUP','').strip()
            if pp:
                value = '$PYTHONSTARTUP: "%s"' % pp
            else:
                value = '$PYTHONSTARTUP: None'
            #
            self._edit1.setReadOnly(True)
            self._edit1.show()
            self._edit2.hide()
            self._edit1.setText(value)
        
        elif not '\n' in value:
            # File
            if init:
                self._radio_file.setChecked(True)
            self._edit1.setReadOnly(False)
            self._edit1.show()
            self._edit2.hide()
            self._edit1.setText(value)
            
        
        else:
            # Code
            if init:
                self._radio_code.setChecked(True)
            self._edit1.hide()
            self._edit2.show()
            if not value.strip():
                value = self.RUN_AFTER_GUI_TEXT
            self._edit2.setText(value)
    
    
    def getTheText(self):
        return self._value



class ShellInfo_startDir(ShellInfoLineEdit):
    def __init__(self, parent):
        ShellInfoLineEdit.__init__(self, parent)
        if sys.platform.startswith('win'):
            self.setPlaceholderText('C:\\path\\to\\your\\python\\modules')
        else:
            self.setPlaceholderText('/path/to/your/python/modules')



class ShellInfo_argv(ShellInfoLineEdit):
    def __init__(self, parent):
        ShellInfoLineEdit.__init__(self, parent)
        self.setPlaceholderText('arg1 arg2 "arg with spaces"')



class ShellInfo_environ(QtWidgets.QTextEdit):
    EXAMPLE = 'EXAMPLE_VAR1=value1\nPYZO_PROCESS_EVENTS_WHILE_DEBUGGING=1'
    
    def __init__(self, parent):
        QtWidgets.QTextEdit.__init__(self, parent)
        self.zoomOut(1)
        self.setText(self.EXAMPLE)
    
    def _cleanText(self, txt):
        return '\n'.join([line.strip() for line in txt.splitlines()])
    
    def setTheText(self, value):
        value = self._cleanText(value)
        if value:
            self.setText(value)
        else:
            self.setText(self.EXAMPLE)
    
    def getTheText(self):
        value = self.toPlainText()
        value = self._cleanText(value)
        if value == self.EXAMPLE:
            return ''
        else:
            return value



## The dialog class and container with tabs


class ShellInfoTab(QtWidgets.QScrollArea):
    
    INFO_KEYS = [   translate('shell', 'name ::: The name of this configuration.'),
                    translate('shell', 'exe ::: The Python executable.'),
                    translate('shell', 'ipython ::: Use IPython shell if available.'),
                    translate('shell', 'gui ::: The GUI toolkit to integrate (for interactive plotting, etc.).'),
                    translate('shell', 'pythonPath ::: A list of directories to search for modules and packages. Write each path on a new line, or separate with the default seperator for this OS.'),  # noqa
                    translate('shell', 'startupScript ::: The script to run at startup (not in script mode).'),
                    translate('shell', 'startDir ::: The start directory (not in script mode).'),
                    translate('shell', 'argv ::: The command line arguments (sys.argv).'),
                    translate('shell', 'environ ::: Extra environment variables (os.environ).'),
                ]
    
    def __init__(self, parent):
        QtWidgets.QScrollArea.__init__(self, parent)
        
        # Init the scroll area
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setWidgetResizable(True)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        
        # Create widget and a layout
        self._content = QtWidgets.QWidget(parent)
        self._formLayout = QtWidgets.QFormLayout(self._content)
        
        # Collect classes of widgets to instantiate
        classes = []
        for t in self.INFO_KEYS:
            className = 'ShellInfo_' + t.key
            cls = globals()[className]
            classes.append((t, cls))
        
        # Instantiate all classes
        self._shellInfoWidgets = {}
        for t, cls in classes:
            # Instantiate and store
            instance = cls(self._content)
            self._shellInfoWidgets[t.key] = instance
            # Create label
            label = QtWidgets.QLabel(t, self._content)
            label.setToolTip(t.tt)
            # Add to layout
            self._formLayout.addRow(label, instance)
        
        # Add delete button
        
        t = translate('shell', 'Delete ::: Delete this shell configuration')
        label = QtWidgets.QLabel('', self._content)
        instance = QtWidgets.QPushButton(pyzo.icons.cancel, t, self._content)
        instance.setToolTip(t.tt)
        instance.setAutoDefault(False)
        instance.clicked.connect(self.parent().parent().onTabClose)
        deleteLayout = QtWidgets.QHBoxLayout()
        deleteLayout.addWidget(instance, 0)
        deleteLayout.addStretch(1)
        # Add to layout
        self._formLayout.addRow(label, deleteLayout)
        
        # Apply layout
        self._formLayout.setSpacing(15)
        self._content.setLayout(self._formLayout)
        self.setWidget(self._content)
    
    
    def setTabTitle(self, name):
        tabWidget = self.parent().parent()
        tabWidget.setTabText(tabWidget.indexOf(self), name)
    
    
    def setInfo(self, info=None):
        """  Set the shell info struct, and use it to update the widgets.
        Not via init, because this function also sets the tab name.
        """
        
        # If info not given, use default as specified by the KernelInfo struct
        if info is None:
            info = KernelInfo()
            # Name
            n = self.parent().parent().count()
            if n > 1:
                info.name = "Shell config %i" % n
        
        # Store info
        self._info = info
        
        # Set widget values according to info
        try:
            for key in info:
                widget = self._shellInfoWidgets.get(key, None)
                if widget is not None:
                    widget.setTheText(info[key])
        
        except Exception as why:
            print("Error setting info in shell config:", why)
            print(info)

    
    def getInfo(self):
        
        info = self._info
        
        # Set struct values according to widgets
        try:
            for key, widget in self._shellInfoWidgets.items():
                info[key] = widget.getTheText()
        
        except Exception as why:
            print("Error getting info in shell config:", why)
            print(info)
        
        # Return the original (but modified) ssdf Dict object
        return info



class ShellInfoDialog(QtWidgets.QDialog):
    """ Dialog to edit the shell configurations. """
    
    def __init__(self, *args):
        QtWidgets.QDialog.__init__(self, *args)
        self.setModal(True)
        
        # Set title
        self.setWindowTitle(pyzo.translate('shell', 'Shell configurations'))
        # Create tab widget
        self._tabs = QtWidgets.QTabWidget(self)
        #self._tabs = CompactTabWidget(self, padding=(4,4,5,5))
        #self._tabs.setDocumentMode(False)
        self._tabs.setMovable(True)
        
        # Get known interpreters (sorted them by version)
        # Do this here so we only need to do it once ...
        from pyzo.util.interpreters import get_interpreters
        self.interpreters = list(reversed(get_interpreters('2.4')))
        
        # Introduce an entry if there's none
        if not pyzo.config.shellConfigs2:
            w = ShellInfoTab(self._tabs)
            self._tabs.addTab(w, '---')
            w.setInfo()
        
        # Fill tabs
        for item in pyzo.config.shellConfigs2:
            w = ShellInfoTab(self._tabs)
            self._tabs.addTab(w, '---')
            w.setInfo(item)
        
        # Enable making new tabs and closing tabs
        self._add = QtWidgets.QToolButton(self)
        self._tabs.setCornerWidget(self._add)
        self._add.clicked.connect(self.onAdd)
        self._add.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self._add.setIcon(pyzo.icons.add)
        self._add.setText(translate('shell', 'Add config'))
        #
        #self._tabs.setTabsClosable(True)
        self._tabs.tabCloseRequested.connect(self.onTabClose)
        
        # Create buttons
        cancelBut = QtWidgets.QPushButton("Cancel", self)
        okBut = QtWidgets.QPushButton("Done", self)
        cancelBut.clicked.connect(self.close)
        okBut.clicked.connect(self.applyAndClose)
        # Layout for buttons
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(cancelBut)
        buttonLayout.addSpacing(10)
        buttonLayout.addWidget(okBut)
        
        # Layout the widgets
        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.addSpacing(8)
        mainLayout.addWidget(self._tabs,0)
        mainLayout.addLayout(buttonLayout,0)
        self.setLayout(mainLayout)
        
        # Prevent resizing
        self.show()
        self.setMinimumSize(500, 400)
        self.resize(640, 500)
        #self.setMaximumHeight(500)
        
    
    
    def onAdd(self):
        # Create widget and add to tabs
        w = ShellInfoTab(self._tabs)
        self._tabs.addTab(w, '---')
        w.setInfo()
        # Select
        self._tabs.setCurrentWidget(w)
        w.setFocus()
    
    
    def onTabClose(self):
        index = self._tabs.currentIndex()
        self._tabs.removeTab( index )
    
    
    def applyAndClose(self, event=None):
        self.apply()
        self.close()
    
    
    def apply(self):
        """ Apply changes for all tabs. """
        
        # Clear
        pyzo.config.shellConfigs2 = []
        
        # Set new versions. Note that although we recreate the list,
        # the list is filled with the orignal structs, so having a
        # reference to such a struct (as the shell has) will enable
        # you to keep track of any made changes.
        for i in range(self._tabs.count()):
            w = self._tabs.widget(i)
            pyzo.config.shellConfigs2.append( w.getInfo() )
