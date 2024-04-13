#@+leo-ver=5-thin
#@+node:peckj.20150428142633.1: * @file ../plugins/python_terminal.py
#@@language python
#@@tabwidth -4

# **Warning**: Use at your own risk.
# Numerous significant problems have been reported, including segfaults.

# This code from http://stackoverflow.com/questions/12431555
# with modifications from Jake Peck and EKR.

#@+<< docstring >>
#@+node:peckj.20150428142633.2: ** << docstring >>
"""Provides an interactive python terminal in the log pane.

**Warning**: Use at your own risk.
Numerous significant problems have been reported, including segfaults.


By Jacob M. Peck

Usage
=====
Enabling this plugin will add a new tab to the Log pane, labeled "Python Console".
This is a fully interactive python command shell, with access to `g`, `c`, and `p` included!

Features:
- Includes support for g, c, and p
- Each outline tab has a separate python console, with a separate namespace (aside from g, of course)
- Extremely primitive tab-completion
- Command history (use !hist to list, and !hist(n) to recall the n'th entry)
- !clear to clear the console

Caveats:

Stdout and stderr are proprely redirected to the interactive console pane while
it has focus, but proprely reset to their previous values when focus is lost. If
code executed inside the interactive console pane needs to output to the
command-line stdout/stderr, please use sys.__stdout__ and sys.__stderr__. - Just
as with scripts, if you do something dangerous, you're on your own

This code is largely lifted from
http://stackoverflow.com/questions/12431555/
enabling-code-completion-in-an-embedded-python-interpreter,
with some modifications made for Leo embedding.
"""
#@-<< docstring >>
#@+<< imports >>
#@+node:peckj.20150428142729.2: ** << imports >>
import re
import sys
import code
from typing import Any
from leo.core import leoGlobals as g
from leo.core.leoQt import QtWidgets
from leo.core.leoQt import Key

# A workaround for #1212: segfaults at startup when importing this file.
# True: enable tab completion, at the risk of segfaults.
use_rlcompleter = False

# Third-party imports.
if use_rlcompleter:
    from rlcompleter import Completer
else:
    Completer = None  # type:ignore

# Fail fast, right after all imports.
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.
#@-<< imports >>

#@+others
#@+node:peckj.20150428142729.3: ** class MyInterpreter
class MyInterpreter(QtWidgets.QWidget):  # type:ignore

    def __init__(self, parent, c):
        super().__init__(parent)
        hBox = QtWidgets.QHBoxLayout()
        self.setLayout(hBox)
        self.textEdit = PyInterp(self, c)
        # this is how you pass in locals to the interpreter
        self.textEdit.initInterpreter(locals())
        hBox.addWidget(self.textEdit)
        hBox.setContentsMargins(0, 0, 0, 0)
        hBox.setSpacing(0)
#@+node:peckj.20150428142729.6: ** class InteractiveInterpreter (code.InteractiveInterpreter)
class InteractiveInterpreter(code.InteractiveInterpreter):
    #@+others
    #@+node:peckj.20150428142729.7: *3* InteractiveInterpreter.__init__
    def __init__(self, locals, c):
        """Ctor for InteractiveInterpreter class."""
        self.c = c
        # inject g, c, p
        loc = locals
        loc['c'] = self.c
        loc['g'] = g
        loc['p'] = self.c.p
        super().__init__(loc)
    #@+node:peckj.20150428142729.8: *3* InteractiveInterpreter.runIt
    def runIt(self, command):

        code.InteractiveInterpreter.runsource(self, command)
    #@-others
#@+node:peckj.20150428142729.5: ** class PyInterp (QTextEdit)
if QtWidgets:

    class PyInterp(QtWidgets.QTextEdit):  # type:ignore
        #@+others
        #@+node:peckj.20150428142729.9: *3* PyInterp.__init__
        def __init__(self, parent, c):
            super().__init__(parent)
            #
            # this widget swallows stdout + stderr while focused,
            # but resets them upon losing focus
            if not g.user_dict.get('old_stdout', None):
                g.user_dict['old_stdout'] = sys.stdout
            if not g.user_dict.get('old_stderr', None):
                g.user_dict['old_stderr'] = sys.stderr
            #
            # init ivars.
            self.indent = 0
            self.refreshMarker = False  # to change back to >>> from ...
            # self.multiLine = False # code spans more than one line
            # self.command        = ''    # command to be ran
            self.printBanner()  # print sys info
            self.insert_marker()  # make the >>> or ... marker
            self.history = []  # list of commands entered
            self.historyIndex = -1
            self.interpreterLocals = {}
            self.c = c
            #
            # initilize interpreter with self locals
            self.initInterpreter(locals())
            #
            # update p when new node selected
            g.registerHandler('select2', self.select2_hook)
        #@+node:peckj.20150428142729.10: *3* PyInterp.select2_hook
        def select2_hook(self, tag, keywords):
            self.interpreter.runIt('p = c.p')
        #@+node:peckj.20150428142729.11: *3* PyInterp.printBanner
        def printBanner(self):
            banner = [
                'Type !hist for a history view and !hist(n) history index recall\n',
                'Type !clear to clear this pane\n'
            ]
            for msg in banner:
                self.write(msg)
        #@+node:peckj.20150428142729.12: *3* PyInterp.insert_marker
        def insert_marker(self):

            # line = '... ' if self.multiLine else '>>> '
            line = '... ' if self.indent > 0 else '>>> '
            self.insertPlainText(line + ' ' * self.indent)
        #@+node:peckj.20150428142729.13: *3* PyInterp.initInterpreter
        def initInterpreter(self, interpreterLocals=None):

            if interpreterLocals:
                # when we pass in locals, we don't want it to be named "self"
                # so we rename it with the name of the class that did the passing
                # and reinsert the locals back into the interpreter dictionary
                selfName = interpreterLocals['self'].__class__.__name__
                interpreterLocalVars = interpreterLocals.pop('self')
                self.interpreterLocals[selfName] = interpreterLocalVars
            else:
                self.interpreterLocals = interpreterLocals

            self.interpreter = InteractiveInterpreter(self.interpreterLocals, self.c)
        #@+node:peckj.20150428142729.14: *3* PyInterp.updateInterpreterLocals
        def updateInterpreterLocals(self, newLocals):
            className = newLocals.__class__.__name__
            self.interpreterLocals[className] = newLocals
        #@+node:peckj.20150428142729.15: *3* PyInterp.write
        def write(self, line):
            self.insertPlainText(line)
            self.ensureCursorVisible()
        #@+node:peckj.20150428142729.16: *3* PyInterp.clearCurrentBlock
        def clearCurrentBlock(self):
            # block being current row
            length = len(self.document().lastBlock().text()[4:])
            if length == 0:
                return None
            #
            # should have a better way of doing this but I can't find it.
            # [self.textCursor().deletePreviousChar() for x in xrange(length)]
            for x in range(length):
                self.textCursor().deletePreviousChar()
            return True
        #@+node:peckj.20150428142729.17: *3* PyInterp.recallHistory
        def recallHistory(self):
            # used when using the arrow keys to scroll through history
            self.clearCurrentBlock()
            if self.historyIndex != -1:
                self.insertPlainText(self.history[self.historyIndex])
            return True
        #@+node:peckj.20150428142729.18: *3* PyInterp.customCommands
        def customCommands(self, command):

            if command == '!hist':  # display history
                self.append('')  # move down one line
                # vars that are in the command are prefixed with ____CC and deleted
                # once the command is done so they don't show up in dir()
                backup = self.interpreterLocals.copy()
                history = self.history[:]
                history.reverse()
                for i, x in enumerate(history):
                    iSize = len(str(i))
                    delta = len(str(len(history))) - iSize
                    line = line = ' ' * delta + '%i: %s' % (i, x) + '\n'
                    self.write(line)
                self.updateInterpreterLocals(backup)
                self.insert_marker()
                return True

            if re.match(r'!hist\(\d+\)', command):  # recall command from history
                backup = self.interpreterLocals.copy()
                history = self.history[:]
                history.reverse()
                index = int(command[6:-1])
                self.clearCurrentBlock()
                command = history[index]
                if command[-1] == ':':
                    # self.multiLine = True
                    self.indent += 4
                self.write(command)
                self.updateInterpreterLocals(backup)
                return True

            if re.match(r'(quit|exit)\(\)', command):  # prevent quitting!
                self.append('')
                self.write('Cannot quit() from an embedded console.\n')
                self.insert_marker()
                return True

            if re.match(r'!clear', command):  # clear the screen
                self.clear()
                self.insert_marker()
                return True

            return False
        #@+node:peckj.20150428142729.19: *3* PyInterp.keyPressEvent & helper
        def keyPressEvent(self, event):

            completer: Any
            try:
                # #1212: Disable this by default.
                if use_rlcompleter and event.key() == Key.Key_Tab:
                    line = str(self.document().lastBlock().text())[4:]
                    completer = Completer(self.interpreter.locals)  # type:ignore
                    suggestion = completer.complete(line, 0)
                    if suggestion is not None:
                        self.insertPlainText(suggestion[len(line) :])
                    return
                if event.key() == Key.Key_Down:
                    if self.historyIndex == len(self.history):
                        self.historyIndex -= 1
                    try:
                        if self.historyIndex > -1:
                            self.historyIndex -= 1
                            self.recallHistory()
                        else:
                            self.clearCurrentBlock()
                    except Exception:
                        pass
                    return
                if event.key() == Key.Key_Up:
                    try:
                        if len(self.history) - 1 > self.historyIndex:
                            self.historyIndex += 1
                            self.recallHistory()
                        else:
                            self.historyIndex = len(self.history)
                    except Exception:
                        pass
                    return
                if event.key() == Key.Key_Home:
                    # set cursor to position 4 in current block. 4 because that's where
                    # the marker stops
                    blockLength = len(self.document().lastBlock().text()[4:])
                    lineLength = len(self.document().toPlainText())
                    position = lineLength - blockLength
                    textCursor = self.textCursor()
                    textCursor.setPosition(position)
                    self.setTextCursor(textCursor)
                    return
                if event.key() in [Key.Key_Left, Key.Key_Backspace]:
                    # don't allow deletion of marker
                    if self.textCursor().positionInBlock() == 4:
                        return
                if event.key() in [Key.Key_Return, Key.Key_Enter]:
                    self.doEnter(event)
                    return
                # allow all other key events
                super().keyPressEvent(event)
            except Exception:
                g.es_exception()
        #@+node:ekr.20180307132016.1: *4* PyInterp.doEnter & helpers
        def doEnter(self, event):
            """Handle the <return> key."""
            #
            # Binding for functions.
            interp = self.interpreter

            #@+others # Helper function
            #@+node:ekr.20190619185252.1: *5* function: compute_indent
            def compute_indent(line):
                """Return the indentation of a line."""
                indent = len(line) - len(line.lstrip())
                if line.endswith(':'):
                    indent += 4
                return indent
            #@+node:ekr.20190619183908.1: *5* function: compile_lines
            def compile_lines(lines):
                """Compile one or more lines, returning the compiled code."""
                source = ''.join(lines)
                try:
                    return code.compile_command(source)
                except SyntaxError:
                    interp.showsyntaxerror()
                except Exception:
                    interp.showtraceback()
                return None
            #@+node:ekr.20190619190805.1: *5* function: compile_and_run_lines
            def compile_and_run_lines(lines):
                """Compile and run code lines.  Return 1 if there are errors."""
                assert lines
                the_code = compile_lines(lines)
                if the_code:
                    return run_code(the_code)
                return None
            #@+node:ekr.20180525110907.1: *5* fucntion: run_code
            def run_code(the_code):
                """Execute the compiled code. Return True if all went well."""
                try:
                    interp.runcode(the_code)
                    return True
                except SyntaxError:
                    interp.showsyntaxerror()
                except Exception:
                    interp.showtraceback()
                return False
            #@-others
            #
            # Set cursor to end of line to avoid line splitting
            textCursor = self.textCursor()
            position = len(self.document().toPlainText())
            textCursor.setPosition(position)
            self.setTextCursor(textCursor)
            lines: list[str] = []
            block = self.document().lastBlock()
            #
            # Scan backward, looking for lines.
            while block:
                line = g.toUnicode(block.text())
                line = line.replace('\t', ' ' * 4)
                block = block.previous()
                if line.startswith('>>> '):
                    lines.insert(0, line[4:])
                    break
                elif line.startswith('... '):
                    lines.insert(0, line[4:])
                else:
                    lines.insert(0, line)
            #
            # Always end the log line.
            self.append('')
            #
            # Clean the lines and compute the last line.
            last_line = lines[-1].rstrip() if lines else ''
            lines = [z.rstrip() + '\n' for z in lines if z.strip()]
            if self.customCommands(last_line):
                return
            #
            # Handle the history and set self.indent for insert_marker.
            if last_line.strip():
                self.history.insert(0, last_line)
                self.indent = compute_indent(last_line)
            #
            # Check for a continued line.
            if self.indent > 0 and last_line:
                self.insert_marker()
                return
            #
            # Execute lines in groups, delimited by indentation.
            indent: int = 0
            ok: bool = True
            exec_lines: list = []
            for line in lines:
                indent = compute_indent(line) if exec_lines else 0
                if indent > 0 or not exec_lines:
                    exec_lines.append(line)
                    continue
                # End of a group.
                ok = compile_and_run_lines(exec_lines)
                exec_lines = [line]
                if not ok:
                    break
            # Tail group.
            if ok and exec_lines:
                compile_and_run_lines(exec_lines)
            self.indent = 0
            self.insert_marker()
        #@+node:peckj.20150428142729.20: *3* PyInterp.focusInEvent
        def focusInEvent(self, event=None):
            # set stdout+stderr properly
            QtWidgets.QTextEdit.focusInEvent(self, event)
            sys.stdout = self  # type:ignore
            sys.stderr = self  # type:ignore
            self.ensureCursorVisible()
        #@+node:peckj.20150428142729.21: *3* PyInterp.focusOutEvent
        def focusOutEvent(self, event):
            # set stdout+stderr properly
            QtWidgets.QTextEdit.focusOutEvent(self, event)
            sys.stdout = g.user_dict['old_stdout']
            sys.stderr = g.user_dict['old_stderr']
        #@-others

#@+node:peckj.20150428142633.4: ** init
def init():
    """Return True if the plugin has loaded successfully."""
    if g.app.gui is None:
        g.app.createQtGui(__file__)
    ok = g.app.gui.guiName().startswith('qt')
    if ok:
        # g.registerHandler(('new','open2'),onCreate)
        # Fail: g.app.log does not exist.
        g.registerHandler('after-create-leo-frame', onCreate)
        g.plugin_signon(__name__)
    else:
        g.es('Plugin %s not loaded.' % __name__, color='red')
    return ok
#@+node:peckj.20150428142633.5: ** onCreate
def onCreate(tag, keys):
    """python_terminal.py onCreate handler."""
    c = keys.get('c')
    if c:
        win = MyInterpreter(None, c)
        c.frame.log.createTab('Python Console', widget=win)
#@-others


#@-leo
