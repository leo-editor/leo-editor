# -*- coding: utf-8 -*-
# Copyright (C) 2016, the Pyzo development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.


""" Module shellStack

Implements the stack of shells. Also implements the nifty debug button
and a dialog to edit the shell configurations.

"""

import time
import webbrowser
from pyzo.util.qt import QtCore, QtGui, QtWidgets  # noqa

import pyzo
from pyzo import translate
from pyzo.core.shell import PythonShell
from pyzo.core.pyzoLogging import print  # noqa
from pyzo.core.menu import ShellTabContextMenu, ShellButtonMenu
from pyzo.core.icons import ShellIconMaker


def shellTitle(shell, moreinfo=False):
    """ Given a shell instance, build the text title to represent it.
    """
    
    # Get name
    nameText = shell._info.name
    
    # Build version text
    if shell._version:
        versionText = 'v{}'.format(shell._version)
    else:
        versionText = 'v?'
    
    # Build gui text
    guiText = shell._startup_info.get('gui')
    guiText = guiText or ''
    if guiText.lower() in ['none', '']:
        guiText = 'without gui'
    else:
        guiText = 'with ' + guiText + ' gui'
    
    # Build state text
    stateText = shell._state or ''
    
    # Build text for elapsed time
    elapsed = time.time() - shell._start_time
    hh = elapsed//3600
    mm = (elapsed - hh*3600)//60
    ss = elapsed - hh*3600 - mm*60
    runtimeText = 'runtime: %i:%02i:%02i' % (hh, mm, ss)
    
    # Build text
    if not moreinfo:
        text = nameText
    else:
        text = "'%s' (%s %s) - %s, %s" % (nameText, versionText, guiText, stateText, runtimeText)
    
    # Done
    return text


class ShellStackWidget(QtWidgets.QWidget):
    """ The shell stack widget provides a stack of shells.
    
    It wrapps a QStackedWidget that contains the shell objects. This
    stack is used as a reference to synchronize the shell selection with.
    We keep track of what is the current selected shell and apply updates
    if necessary. Therefore, changing the current shell in the stack
    should be enough to invoke a full update.
    
    """
    
    # When the current shell changes.
    currentShellChanged = QtCore.Signal()
    
    # When the current shells state (or debug state) changes,
    # or when a new prompt is received.
    # Also fired when the current shell changes.
    currentShellStateChanged = QtCore.Signal()
    
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        
        # create toolbar
        self._toolbar = QtWidgets.QToolBar(self)
        self._toolbar.setMaximumHeight(26)
        self._toolbar.setIconSize(QtCore.QSize(16,16))
        
        # create stack
        self._stack = QtWidgets.QStackedWidget(self)
        
        # Populate toolbar
        self._shellButton = ShellControl(self._toolbar, self._stack)
        self._debugmode = 0
        self._dbs = DebugStack(self._toolbar)
        #
        self._toolbar.addWidget(self._shellButton)
        self._toolbar.addSeparator()
        # self._toolbar.addWidget(self._dbc) -> delayed, see addContextMenu()
        
        self._interpreterhelp = InterpreterHelper(self)
        
        # widget layout
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._toolbar)
        layout.addWidget(self._stack, 0)
        layout.addWidget(self._interpreterhelp, 0)
        self.setLayout(layout)
        
        # make callbacks
        self._stack.currentChanged.connect(self.onCurrentChanged)

        self.showInterpreterHelper()
    
    def __iter__(self):
        i = 0
        while i < self._stack.count():
            w = self._stack.widget(i)
            i += 1
            yield w
    
    def showInterpreterHelper(self, show=True):
        self._interpreterhelp.setVisible(show)
        self._toolbar.setVisible(not show)
        self._stack.setVisible(not show)
        if show:
            self._interpreterhelp.detect()
    
    def addShell(self, shellInfo=None):
        """ addShell()
        Add a shell to the widget. """
        
        # Create shell and add to stack
        shell = PythonShell(self, shellInfo)
        self._stack.addWidget(shell)
        # Bind to signals
        shell.stateChanged.connect(self.onShellStateChange)
        shell.debugStateChanged.connect(self.onShellDebugStateChange)
        # Select it and focus on it (invokes onCurrentChanged)
        self._stack.setCurrentWidget(shell)
        shell.setFocus()
        return shell
    
    
    def removeShell(self, shell):
        """ removeShell()
        Remove an existing shell from the widget
        """
        self._stack.removeWidget(shell)
    
    
    def onCurrentChanged(self, index):
        """ When another shell is selected, update some things.
        """
        
        # Get current
        shell = self.getCurrentShell()
        # Call functions
        self.onShellStateChange(shell)
        self.onShellDebugStateChange(shell)
        # Emit Signal
        self.currentShellChanged.emit()
    
    
    def onShellStateChange(self, shell):
        """ Called when the shell state changes, and is called
        by onCurrentChanged. Sets the mainwindow's icon if busy.
        """
        
        # Keep shell button and its menu up-to-date
        self._shellButton.updateShellMenu(shell)
       
        if shell is self.getCurrentShell(): # can be None
            # Update application icon
            if shell and shell._state in ['Busy']:
                pyzo.main.setWindowIcon(pyzo.iconRunning)
            else:
                pyzo.main.setWindowIcon(pyzo.icon)
            # Send signal
            self.currentShellStateChanged.emit()
    
    
    def onShellDebugStateChange(self, shell):
        """ Called when the shell debug state changes, and is called
        by onCurrentChanged. Sets the debug button.
        """
        
        if shell is self.getCurrentShell():
            
            # Update debug info
            if shell and shell._debugState:
                info = shell._debugState
                self._debugmode = info['debugmode']
                for action in self._debugActions:
                    action.setEnabled(self._debugmode==2)
                self._debugActions[-1].setEnabled(self._debugmode>0)  # Stop
                self._dbs.setTrace(shell._debugState)
            else:
                for action in self._debugActions:
                    action.setEnabled(False)
                self._debugmode = 0
                self._dbs.setTrace(None)
            # Send signal
            self.currentShellStateChanged.emit()
    
    
    def getCurrentShell(self):
        """ getCurrentShell()
        Get the currently active shell.
        """
        
        w = None
        if self._stack.count():
            w = self._stack.currentWidget()
        if not w:
            return None
        else:
            return w
    
    
    def getShells(self):
        """ Get all shell in stack as list """
        
        shells = []
        for i in range(self._stack.count()):
            shell = self.getShellAt(i)
            if shell is not None:
                shells.append(shell)
        
        return shells
    
    
    def getShellAt(self, i):
        return
        """ Get shell at current tab index """
        
        return self._stack.widget(i)

    
    def addContextMenu(self):
        # A bit awkward... but the ShellMenu needs the ShellStack, so it
        # can only be initialized *after* the shellstack is created ...
        
        # Give shell tool button a menu
        self._shellButton.setMenu(ShellButtonMenu(self, 'Shell button menu'))
        self._shellButton.menu().aboutToShow.connect(self._shellButton._elapsedTimesTimer.start)
        
        # Also give it a context menu
        self._shellButton.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._shellButton.customContextMenuRequested.connect(self.contextMenuTriggered)
        
        # Add actions
        for action in pyzo.main.menuBar()._menumap['shell']._shellActions:
            action = self._toolbar.addAction(action)
        
        self._toolbar.addSeparator()
        
        # Add debug actions
        self._debugActions = []
        for action in pyzo.main.menuBar()._menumap['shell']._shellDebugActions:
            self._debugActions.append(action)
            action = self._toolbar.addAction(action)
        
        # Delayed-add debug control buttons
        self._toolbar.addWidget(self._dbs)
    
    def contextMenuTriggered(self, p):
        """ Called when context menu is clicked """
        
        # Get index of shell belonging to the tab
        shell = self.getCurrentShell()
        
        if shell:
            p = self._shellButton.mapToGlobal(self._shellButton.rect().bottomLeft())
            ShellTabContextMenu(shell=shell, parent=self).popup(p)
    
    
    def onShellAction(self, action):
        shell = self.getCurrentShell()
        if shell:
            getattr(shell, action)()



class ShellControl(QtWidgets.QToolButton):
    """ A button that can be used to select a shell and start a new shell.
    """
    
    def __init__(self, parent, shellStack):
        QtWidgets.QToolButton.__init__(self, parent)
        
        # Store reference of shell stack
        self._shellStack = shellStack
        
        # Keep reference of actions corresponding to shells
        self._shellActions = []
        
        # Set text and tooltip
        self.setText('Warming up ...')
        self.setToolTip(translate("shells", "Click to select shell."))
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.setPopupMode(self.InstantPopup)
        
        # Set icon
        self._iconMaker = ShellIconMaker(self)
        self._iconMaker.updateIcon('busy') # Busy initializing
        
        # Create timer
        self._elapsedTimesTimer = QtCore.QTimer(self)
        self._elapsedTimesTimer.setInterval(200)
        self._elapsedTimesTimer.setSingleShot(False)
        self._elapsedTimesTimer.timeout.connect(self.onElapsedTimesTimer)
    
    
    def updateShellMenu(self, shellToUpdate=None):
        """ Update the shell menu. Ensure that there is a menu item
        for each shell. If shellToUpdate is given, updates the corresponding
        menu item.
        """
        menu = self.menu()
        
        # Get shells now active
        currentShell = self._shellStack.currentWidget()
        shells = [self._shellStack.widget(i) for i in range(self._shellStack.count())]
        
        # Synchronize actions. Remove invalid actions
        for action in self._shellActions:
            # Check match with shells
            if action._shell in shells:
                shells.remove(action._shell)
            else:
                menu.removeAction(action)
            # Update checked state
            if action._shell is currentShell and currentShell:
                action.setChecked(True)
            else:
                action.setChecked(False)
            # Update text if necessary
            if action._shell is shellToUpdate:
                action.setText(shellTitle(shellToUpdate, True))
        
        # Any items left in shells need a menu item
        # Dont give them an icon, or the icon is used as checkbox thingy
        for shell in shells:
            text = shellTitle(shell)
            action = menu.addItem(text, None, self._shellStack.setCurrentWidget, shell)
            action._shell = shell
            action.setCheckable(True)
            self._shellActions.append(action)
        
        # Is the shell being updated the current?
        if currentShell is shellToUpdate and currentShell is not None:
            self._iconMaker.updateIcon(currentShell._state)
            self.setText(shellTitle(currentShell))
        elif currentShell is None:
            self._iconMaker.updateIcon('')
            self.setText('No shell selected')
    
    
    def onElapsedTimesTimer(self):
        # Automatically turn timer off is menu is hidden
        if not self.menu().isVisible():
            self._elapsedTimesTimer.stop()
            return
        
        # Update text for each shell action
        for action in self._shellActions:
            action.setText(shellTitle(action._shell, True))



# todo: remove this?
# class DebugControl(QtWidgets.QToolButton):
#     """ A button to control debugging.
#     """
#
#     def __init__(self, parent):
#         QtWidgets.QToolButton.__init__(self, parent)
#
#         # Flag
#         self._debugmode = False
#
#         # Set text
#         self.setText(translate('debug', 'Debug'))
#         self.setIcon(pyzo.icons.bug)
#         self.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
#         #self.setPopupMode(self.InstantPopup)
#
#         # Bind to triggers
#         self.triggered.connect(self.onTriggered)
#         self.pressed.connect(self.onPressed)
#         self.buildMenu()
#
#
#     def buildMenu(self):
#
#         # Count breakpoints
#         bpcount = 0
#         for e in pyzo.editors:
#             bpcount += len(e.breakPoints())
#
#         # Prepare a text
#         clearallbps = translate('debug', 'Clear all {} breakpoints')
#         clearallbps = clearallbps.format(bpcount)
#
#         # Set menu
#         menu = QtWidgets.QMenu(self)
#         self.setMenu(menu)
#
#         for cmd, enabled, icon, text in [
#                 ('CLEAR', self._debugmode==0, pyzo.icons.bug_delete, clearallbps),
#                 ('PM', self._debugmode==0, pyzo.icons.bug_error,
#                     translate('debug', 'Postmortem: debug from last traceback')),
#                 ('STOP', self._debugmode>0, pyzo.icons.debug_quit,
#                     translate('debug', 'Stop debugging')),
# #                 ('NEXT', self._debugmode==2, pyzo.icons.debug_next,
# #                     translate('debug', 'Next: proceed until next line')),
# #                 ('STEP', self._debugmode==2, pyzo.icons.debug_step,
# #                     translate('debug', 'Step: proceed one step')),
# #                 ('RETURN', self._debugmode==2, pyzo.icons.debug_return,
# #                     translate('debug', 'Return: proceed until returns')),
# #                 ('CONTINUE', self._debugmode==2, pyzo.icons.debug_continue,
# #                     translate('debug', 'Continue: proceed to next breakpoint')),
#                 ]:
#             if cmd is None:
#                 menu.addSeparator()
#             else:
#                 if icon is not None:
#                     a = menu.addAction(icon, text)
#                 else:
#                     a = menu.addAction(text)
#                 if hasattr(text, 'tt'):
#                     a.setToolTip(text.tt)
#                 a.cmd = cmd
#                 a.setEnabled(enabled)
#
#
#     def onPressed(self, show=True):
#         self.buildMenu()
#         self.showMenu()
#
#
#     def onTriggered(self, action):
#         if action.cmd == 'PM':
#             # Initiate postmortem debugging
#             shell = pyzo.shells.getCurrentShell()
#             if shell:
#                 shell.executeCommand('DB START\n')
#
#         elif action.cmd == 'CLEAR':
#             # Clear all breakpoints
#             for e in pyzo.editors:
#                 e.clearBreakPoints()
#
#         else:
#             command = action.cmd.upper()
#             shell = pyzo.shells.getCurrentShell()
#             if shell:
#                 shell.executeCommand('DB %s\n' % command)
#
#
#     def setTrace(self, info):
#         """ Determine whether we are in debug mode.
#         """
#         if info is None:
#             self._debugmode = 0
#         else:
#             self._debugmode = info['debugmode']



class DebugStack(QtWidgets.QToolButton):
    """ A button that shows the stack trace.
    """
    
    def __init__(self, parent):
        QtWidgets.QToolButton.__init__(self, parent)
        
        # Set text and tooltip
        self._baseText = translate('debug', 'Stack')
        self.setText('%s:' % self._baseText)
        self.setIcon(pyzo.icons.text_align_justify)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.setPopupMode(self.InstantPopup)
        
        # Bind to triggers
        self.triggered.connect(self.onTriggered)
    
    
    def onTriggered(self, action):
        
        # Get shell
        shell = pyzo.shells.getCurrentShell()
        if not shell:
            return
        
        # Change stack index
        if not action._isCurrent:
            shell.executeCommand('DB FRAME {}\n'.format(action._index))
        # Open file and select line
        if True:
            line = action.text().split(': ',1)[1]
            self.debugFocus(line)
    
    
    def setTrace(self, info):
        """ Set the stack trace. This method is called from
        the shell that receives the trace via its status channel
        directly from the interpreter.
        If trace is None, removes the trace
        """
        
        # Get info
        if info:
            index, frames, debugmode = info['index'], info['frames'], info['debugmode']
        else:
            index, frames = -1, []
        
        if (not frames) or (debugmode==0):
            
            # Remove trace
            self.setMenu(None)
            self.setText('')  #(self._baseText)
            self.setEnabled(False)
            pyzo.editors.setDebugLineIndicators(None)
        
        else:
            # Get the current frame
            theAction = None
            
            # Create menu and add __main__
            menu = QtWidgets.QMenu(self)
            self.setMenu(menu)
            
            # Fill trace
            for i in range(len(frames)):
                thisIndex = i + 1
                # Set text for action
                text = '{}: File "{}", line {}, in {}'
                text = text.format(thisIndex, *frames[i])
                action = menu.addAction(text)
                action._index = thisIndex
                action._isCurrent = False
                if thisIndex == index:
                    action._isCurrent = True
                    theAction = action
                    self.debugFocus(text.split(': ',1)[1])  # Load editor
            
            # Get debug indicators
            debugIndicators = []
            for i in range(len(frames)):
                thisIndex = i + 1
                filename, linenr, func = frames[i]
                debugIndicators.append((filename, linenr))
                if thisIndex == index:
                    break
            # Set debug indicators
            pyzo.editors.setDebugLineIndicators(*debugIndicators)
            
            # Highlight current item and set the button text
            if theAction:
                menu.setDefaultAction(theAction)
                #self.setText(theAction.text().ljust(20))
                i = theAction._index
                text = "{} ({}/{}):  ".format(self._baseText, i, len(frames))
                self.setText(text)
            
            self.setEnabled(True)
    
    
    def debugFocus(self, lineFromDebugState):
        """ debugFocus(lineFromDebugState)
        Open the file and show the linenr of the given lineFromDebugState.
        """
        # Get filenr and item
        try:
            tmp = lineFromDebugState.split(', in ')[0].split(', line ')
            filename = tmp[0][len('File '):].strip('"')
            linenr = int(tmp[1].strip())
        except Exception:
            return 'Could not focus!'
        # Cannot open <console>
        if filename == '<console>':
            return 'Stack frame is <console>.'
        elif filename.startswith('<ipython-input-'):
            return 'Stack frame is IPython input.'
        elif filename.startswith('<'):
            return 'Stack frame is special name'
        # Go there!
        result = pyzo.editors.loadFile(filename)
        if not result:
            return 'Could not open file where the error occured.'
        else:
            editor = result._editor
            # Goto line and select it
            editor.gotoLine(linenr)
            cursor = editor.textCursor()
            cursor.movePosition(cursor.StartOfBlock)
            cursor.movePosition(cursor.EndOfBlock, cursor.KeepAnchor)
            editor.setTextCursor(cursor)


class InterpreterHelper(QtWidgets.QWidget):
    """ This sits in place of a shell to help the user download miniconda.
    """
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self._label = QtWidgets.QLabel('hello world')
        self._label.setTextFormat(QtCore.Qt.RichText)
        self._label.setWordWrap(True)
        # self._label.setOpenExternalLinks(True)
        self._label.linkActivated.connect(self.handle_link)
        font = self._label.font()
        font.setPointSize(font.pointSize()+2)
        self._label.setFont(font)
        
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self._label, 1)
    
    def refresh(self):
        self._label.setText('Detecting interpreters ...')
        QtWidgets.qApp.flush()
        QtWidgets.qApp.processEvents()
        self.detect()
        
    def detect(self):
        
        python_link = '<a href="https://www.python.org/">Python</a>'
        conda_link = '<a href="https://miniconda.pyzo.org">Miniconda</a>'
        self._the_exe = None
        configs = pyzo.config.shellConfigs2
        
        # Hide now?
        if configs and configs[0].exe:
            self._label.setText('Happy coding!')
            QtCore.QTimer.singleShot(1200, self.hide_this)
            return
        
        # Try to find an interpreter
        from pyzo.util.interpreters import get_interpreters
        interpreters = list(reversed(get_interpreters('2.4')))
        conda_interpreters = [i for i in interpreters if i.is_conda]
        conda_interpreters.sort(key=lambda x:len(x.path.replace('pyzo', 'pyzo'*10)))
        
        # Always sleep for a bit, so show that we've refreshed
        time.sleep(0.05)
        
        if conda_interpreters and conda_interpreters[0].version > '3':
            self._the_exe = conda_interpreters[0].path
            text = """Pyzo detected a conda environment in:
                      <br />%s<br /><br />
                      You can <a href='usefound'>use&nbsp;this&nbsp;environment</a>
                      (recommended), or manually specify an interpreter
                      by setting the exe in the <a href='config'>shell&nbsp;config</a>.
                      <br /><br />Click one of the links above, or <a href='refresh'>refresh</a>.
                   """ % (self._the_exe, )
        elif interpreters and interpreters[0].version > '3':
            self._the_exe = interpreters[0].path
            text = """Pyzo detected a Python interpreter in:
                      <br />%s<br /><br />
                      You can <a href='usefound'>use&nbsp;this&nbsp;environment</a>
                      (recommended), or manually specify an interpreter
                      by setting the exe in the <a href='config'>shell&nbsp;config</a>.
                      <br /><br />Click one of the links above, or <a href='refresh'>refresh</a>.
                   """ % (self._the_exe, )
        elif interpreters:
            text = """Pyzo detected a Python interpreter,
                      but it is Python 2. We strongly recommend using Python 3 instead.
                      <br /><br />
                      If you installed %s or %s in a non-default location,
                      or if you want to manually specify an interpreter,
                      set the exe in the <a href='config'>shell&nbsp;config</a>.
                      <br /><br />Click one of the links above, or <a href='refresh'>refresh</a>.
                   """ % (python_link, conda_link)
        else:
            text = """Pyzo did not detect any Python interpreters.
                      We recomment installing %s or %s
                      (and click <a href='refresh'>refresh</a> when done).
                      <br /><br />
                      If you installed Python or Miniconda in a non-default location,
                      or if you want to manually specify the interpreter,
                      set the exe in the <a href='config'>shell&nbsp;config</a>.
                   """ % (python_link, conda_link)
        
        link_style = 'font-weight: bold; color:#369; text-decoration:underline;'
        self._label.setText(text.replace('<a ', '<a style="%s" ' % link_style))
    
    def handle_link(self, url):
        if url == 'refresh':
            self.refresh()
        elif url == 'config':
            self.editShellConfig()
        elif url == 'usefound':
            self.useFound()
        elif url.startswith(('http://', 'https://')):
            webbrowser.open(url)
        else:
            raise ValueError('Unknown link in conda helper: %s' % url)
    
    def editShellConfig(self):
        from pyzo.core.shellInfoDialog import ShellInfoDialog
        d = ShellInfoDialog()
        d.exec_()
        self.refresh()
        self.restart_shell()
    
    def useFound(self):
        # Set newfound interpreter
        if self._the_exe:
            configs = pyzo.config.shellConfigs2
            if not configs:
                from pyzo.core.kernelbroker import KernelInfo
                pyzo.config.shellConfigs2.append( KernelInfo() )
            configs[0].exe = self._the_exe
            self.restart_shell()
        self.refresh()
    
    def hide_this(self):
        shells = self.parent()
        shells.showInterpreterHelper(False)
    
    def restart_shell(self):
        shells = self.parent()
        shell = shells.getCurrentShell()
        if shell is not None:
            shell.closeShell()
        shells.addShell(pyzo.config.shellConfigs2[0])
