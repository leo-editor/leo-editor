# -*- coding: utf-8 -*-
""" Module editor

Defines the PyzoEditor class which is used to edit documents.
This module/class also implements all the relatively low level
file loading/saving /reloading stuff.
"""
try:
    import leo.core.leoGlobals as leo_g
    # leo_g.pr('pyzo/core/editor.py')
except Exception:
    leo_g = None


import os, sys
import re, codecs

from pyzo.util.qt import QtCore, QtGui, QtWidgets
qt = QtGui

from pyzo.codeeditor import Manager
from pyzo.core.menu import EditorContextMenu
from pyzo.core.baseTextCtrl import BaseTextCtrl, normalizePath
from pyzo.core.pyzoLogging import print  # noqa
assert print
import pyzo

#
# Set default line ending (if not set)
if not pyzo.config.settings.defaultLineEndings:
    line_ending = 'CRLF' if sys.platform.startswith('win') else 'LF'
    pyzo.config.settings.defaultLineEndings = line_ending

def determineEncoding(bb):
    """ Get the encoding used to encode a file.
    Accepts the bytes of the file. Returns the codec name. If the
    codec could not be determined, uses UTF-8.
    """

    # Init
    firstTwoLines = bb.split(b'\n', 2)[:2]
    encoding = 'UTF-8'

    for line in firstTwoLines:

        # Try to make line a string
        try:
            line = line.decode('ASCII').strip()
        except Exception:
            continue

        # Has comment?
        if line and line[0] == '#':

            # Matches regular expression given in PEP 0263?
            expression = "coding[:=]\s*([-\w.]+)"
            result = re.search(expression, line)
            if result:

                # Is it a known encoding? Correct name if it is
                candidate_encoding = result.group(1)
                try:
                    c = codecs.lookup(candidate_encoding)
                    candidate_encoding = c.name
                except Exception:
                    pass
                else:
                    encoding = candidate_encoding

    # Done
    return encoding
def determineLineEnding(text):
    """ Get the line ending style used in the text.
    \n, \r, \r\n,
    The EOLmode is determined by counting the occurrences of each
    line ending...
    """
    # test line ending by counting the occurrence of each
    c_win = text.count("\r\n")
    c_mac = text.count("\r") - c_win
    c_lin = text.count("\n") - c_win
    # set the appropriate style
    if c_win > c_mac and c_win > c_lin:
        mode = '\r\n'
    elif c_mac > c_win and c_mac > c_lin:
        mode = '\r'
    else:
        mode = '\n'

    # return
    return mode
def determineIndentation(text):
    """ Get the indentation used in this document.
    The text is analyzed to find the most used
    indentations.
    The result is -1 if tab indents are most common.
    A positive result means spaces are used; the amount
    signifies the amount of spaces per indentation.
    0 is returned if the indentation could not be determined.
    """

    # create dictionary of indents, -1 means a tab
    indents = {}
    indents[-1] = 0

    lines = text.splitlines()
    lines.insert(0,"") # so the lines start at 1
    for i in range( len(lines) ):
        line = lines[i]

        # remove indentation
        tmp = line.lstrip()
        indent = len(line) - len(tmp)
        line = tmp.rstrip()

        if line.startswith('#'):
            continue
        else:
            # remove everything after the #
            line = line.split("#",1)[0].rstrip()
        if not line:
            # continue of no line left
            continue

        # a colon means there will be an indent
        # check the next line (or the one thereafter)
        # and calculate the indentation difference with THIS line.
        if line.endswith(":"):
            if len(lines) > i+2:
                line2 = lines[i+1]
                tmp = line2.lstrip()
                if not tmp:
                    line2 = lines[i+2]
                    tmp = line2.lstrip()
                if tmp:
                    ind2 = len(line2)-len(tmp)
                    ind3 = ind2 - indent
                    if line2.startswith("\t"):
                        indents[-1] += 1
                    elif ind3>0:
                        if not ind3 in indents:
                            indents[ind3] = 1
                        indents[ind3] += 1

    # find which was the most common tab width.
    indent, maxvotes = 0,0
    for nspaces in indents:
        if indents[nspaces] > maxvotes:
            indent, maxvotes = nspaces, indents[nspaces]
    #print "found tabwidth %i" % indent
    return indent

# To give each new file a unique name
newFileCounter = 0
def createEditor(parent, filename=None):
    """ Tries to load the file given by the filename and
    if succesful, creates an editor instance to put it in,
    which is returned.
    If filename is None, an new/unsaved/temp file is created.
    """
    
    # if leo_g: leo_g.pr('editor.py function.createEditor: %r' % filename)

    if filename is None:
        # Increase counter
        global newFileCounter
        newFileCounter  += 1
        # Create editor
        editor = PyzoEditor(parent)
        editor.document().setModified(True)
        # Set name
        editor._name = "<tmp {}>".format(newFileCounter)
    else:
        # check and normalize
        if not os.path.isfile(filename):
            raise IOError("File does not exist '%s'." % filename)
        # load file (as bytes)
        with open(filename, 'rb') as f:
            bb = f.read()
            f.close()
        # convert to text, be gentle with files not encoded with utf-8
        encoding = determineEncoding(bb)
        text = bb.decode(encoding,'replace')

        # process line endings
        lineEndings = determineLineEnding(text)

        # if we got here safely ...

        # create editor and set text
        editor = PyzoEditor(parent) # showlinenumbers=False)
        editor.setPlainText(text)
        editor.lineEndings = lineEndings
        editor.encoding = encoding
        editor.document().setModified(False)

        # store name and filename
        editor._filename = filename
        editor._name = os.path.split(filename)[1]

        # process indentation
        indentWidth = determineIndentation(text)
        if indentWidth == -1: #Tabs
            editor.setIndentWidth(pyzo.config.settings.defaultIndentWidth)
            editor.setIndentUsingSpaces(False)
        elif indentWidth:
            editor.setIndentWidth(indentWidth)
            editor.setIndentUsingSpaces(True)

    if editor._filename:
        editor._modifyTime = os.path.getmtime(editor._filename)

    # Set parser
    if editor._filename:
        ext = os.path.splitext(editor._filename)[1]
        parser = Manager.suggestParser(ext, text)
        editor.setParser(parser)
    else:
        # todo: rename style -> parser
        editor.setParser(pyzo.config.settings.defaultStyle)

    # return
    return editor
class PyzoEditor(BaseTextCtrl):

    # called when dirty changed or filename changed, etc
    somethingChanged = QtCore.Signal()

    def __init__(self, parent, **kwds):
        super().__init__(parent, showLineNumbers = True, **kwds)

        # Init filename and name
        self._filename = ''
        self._name = '<TMP>'

        # View settings
        self.setShowWhitespace(pyzo.config.view.showWhitespace)
        #TODO: self.setViewWrapSymbols(view.showWrapSymbols)
        self.setShowLineEndings(pyzo.config.view.showLineEndings)
        self.setShowIndentationGuides(pyzo.config.view.showIndentationGuides)
        #
        self.setWrap(bool(pyzo.config.view.wrap))
        self.setHighlightCurrentLine(pyzo.config.view.highlightCurrentLine)
        self.setLongLineIndicatorPosition(pyzo.config.view.edgeColumn)
        self.setHighlightMatchingBracket(pyzo.config.view.highlightMatchingBracket)
        #TODO: self.setFolding( int(view.codeFolding)*5 )
        # bracematch is set in baseTextCtrl, since it also applies to shells
        # dito for zoom and tabWidth

        # Set line endings to default
        self.lineEndings = pyzo.config.settings.defaultLineEndings

        # Set encoding to default
        self.encoding = 'UTF-8'

        # Modification time to test file change
        self._modifyTime = 0

        self.modificationChanged.connect(self._onModificationChanged)

        # To see whether the doc has changed to update the parser.
        self.textChanged.connect(self._onModified)

        # This timer is used to hide the marker that shows which code is executed
        self._showRunCursorTimer = QtCore.QTimer()

        # Add context menu (the offset is to prevent accidental auto-clicking)
        self._menu = EditorContextMenu(self)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(lambda p: self._menu.popup(self.mapToGlobal(p)+QtCore.QPoint(0,3)))

    ## Properties
    @property
    def name(self):
        return self._name
    @property
    def filename(self):
        return self._filename
    @property
    def lineEndings(self):
        """
        Line-endings style of this file. Setter accepts machine-readable (e.g. '\r') and human-readable (e.g. 'CR') input
        """
        return self._lineEndings
    @lineEndings.setter
    def lineEndings(self,value):
        if value in ('\r','\n','\r\n'):
            self._lineEndings = value
            return
        try:
            self._lineEndings = {'CR': '\r', 'LF': '\n', 'CRLF': '\r\n'}[value]
        except KeyError:
            raise ValueError('Invalid line endings style %r' % value)
    @property
    def lineEndingsHumanReadable(self):
        """
        Current line-endings style, human readable (e.g. 'CR')
        """
        return {'\r': 'CR', '\n': 'LF', '\r\n': 'CRLF'}[self.lineEndings]
    @property
    def encoding(self):
        """ Encoding used to convert the text of this file to bytes.
        """
        return self._encoding

    @encoding.setter
    def encoding(self, value):
        # Test given value, correct name if it exists
        try:
            c = codecs.lookup(value)
            value = c.name
        except Exception:
            value = codecs.lookup('UTF-8').name
        # Store
        self._encoding = value

    ##
    def justifyText(self):
        """ Overloaded version of justifyText to make it use our
        configurable justificationwidth.
        """
        super().justifyText(pyzo.config.settings.justificationWidth)
    def showRunCursor(self, cursor):
        """
        Momentarily highlight a piece of code to show that this is being executed
        """

        extraSelection = QtWidgets.QTextEdit.ExtraSelection()
        extraSelection.cursor = cursor
        extraSelection.format.setBackground(QtCore.Qt.gray)
        self.setExtraSelections([extraSelection])

        self._showRunCursorTimer.singleShot(200, lambda: self.setExtraSelections([]))
    def id(self):
        """ Get an id of this editor. This is the filename,
        or for tmp files, the name. """
        if self._filename:
            return self._filename
        else:
            return self._name
    def focusInEvent(self, event):
        """ Test whether the file has been changed 'behind our back'
        """
        # Act normally to the focus event
        BaseTextCtrl.focusInEvent(self, event)
        # Test file change
        self.testWhetherFileWasChanged()
    def testWhetherFileWasChanged(self):
        """ testWhetherFileWasChanged()
        Test to see whether the file was changed outside our backs,
        and let the user decide what to do.
        Returns True if it was changed.
        """

        # get the path
        path = self._filename
        if not os.path.isfile(path):
            # file is deleted from the outside
            return

        # test the modification time...
        mtime = os.path.getmtime(path)
        if mtime != self._modifyTime:

            # ask user
            dlg = QtWidgets.QMessageBox(self)
            dlg.setWindowTitle('File was changed')
            dlg.setText("File has been modified outside of the editor:\n"+
                        self._filename)
            dlg.setInformativeText("Do you want to reload?")
            t=dlg.addButton("Reload", QtWidgets.QMessageBox.AcceptRole) #0
            dlg.addButton("Keep this version", QtWidgets.QMessageBox.RejectRole) #1
            dlg.setDefaultButton(t)

            # whatever the result, we will reset the modified time
            self._modifyTime = os.path.getmtime(path)

            # get result and act
            result = dlg.exec_()
            if result == QtWidgets.QMessageBox.AcceptRole:
                self.reload()
            else:
                pass # when cancelled or explicitly said, do nothing

            # Return that indeed the file was changes
            return True
    def _onModificationChanged(self,changed):
        """Handler for the modificationChanged signal. Emit somethingChanged
        for the editorStack to update the modification notice."""
        self.somethingChanged.emit()
    def _onModified(self):
        pyzo.parser.parseThis(self)
    def dragMoveEvent(self, event):
        """ Otherwise cursor can get stuck.
        https://bitbucket.org/iep-project/iep/issue/252
        https://qt-project.org/forums/viewthread/3180
        """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            BaseTextCtrl.dropEvent(self, event)
    def dropEvent(self, event):
        """ Drop files in the list. """
        if event.mimeData().hasUrls():
            # file: let the editorstack do the work.
            pyzo.editors.dropEvent(event)
        else:
            # text: act normal
            BaseTextCtrl.dropEvent(self, event)
    def showEvent(self, event=None):
        """ Capture show event to change title. """
        # Act normally
        if event:
            BaseTextCtrl.showEvent(self, event)

        # Make parser update
        pyzo.parser.parseThis(self)
    def setTitleInMainWindow(self):
        """ set the title  text in the main window to show filename. """

        # compose title
        name, path = self._name, self._filename
        if path:
            pyzo.main.setMainTitle(path)
        else:
            pyzo.main.setMainTitle(name)
    def save(self, filename=None):
        """ Save the file. No checking is done. """

        # get filename
        if filename is None:
            filename = self._filename
        if not filename:
            raise ValueError("No filename specified, and no filename known.")

        # Test whether it was changed without us knowing. If so, dont save now.
        if self.testWhetherFileWasChanged():
            return

        # Get text and remember where we are
        text = self.toPlainText()
        cursor = self.textCursor()
        linenr = cursor.blockNumber() + 1
        index = cursor.positionInBlock()
        scroll = self.verticalScrollBar().value()

        # Convert line endings (optionally remove trailing whitespace
        if pyzo.config.settings.removeTrailingWhitespaceWhenSaving:
            lines = [line.rstrip() for line in text.split('\n')]
            if lines[-1]:
                lines.append('')  # Ensure the file ends in an empty line
            text = self.lineEndings.join(lines)
            self.setPlainText(text)
            # Go back to where we were
            cursor = self.textCursor()
            cursor.movePosition(cursor.Start) # move to begin of the document
            cursor.movePosition(cursor.NextBlock,n=linenr-1) # n blocks down
            index = min(index, cursor.block().length()-1)
            cursor.movePosition(cursor.Right,n=index) # n chars right
            self.setTextCursor(cursor)
            self.verticalScrollBar().setValue(scroll)
        else:
            text = text.replace('\n', self.lineEndings)

        # Make bytes
        bb = text.encode(self.encoding)

        # Store
        f = open(filename, 'wb')
        try:
            f.write(bb)
        finally:
            f.close()

        # Update stats
        self._filename = normalizePath( filename )
        self._name = os.path.split(self._filename)[1]
        self.document().setModified(False)
        self._modifyTime = os.path.getmtime(self._filename)

        # update title (in case of a rename)
        self.setTitleInMainWindow()

        # allow item to update its texts (no need: onModifiedChanged does this)
        #self.somethingChanged.emit()
    def reload(self):
        """ Reload text using the self._filename.
        We do not have a load method; we first try to load the file
        and only when we succeed create an editor to show it in...
        This method is only for reloading in case the file was changed
        outside of the editor. """

        # We can only load if the filename is known
        if not self._filename:
            return
        filename = self._filename

        # Remember where we are
        cursor = self.textCursor()
        linenr = cursor.blockNumber() + 1

        # Load file (as bytes)
        with open(filename, 'rb') as f:
            bb = f.read()

        # Convert to text
        text = bb.decode('UTF-8')

        # Process line endings (before setting the text)
        self.lineEndings= determineLineEnding(text)

        # Set text
        self.setPlainText(text)
        self.document().setModified(False)

        # Go where we were (approximately)
        self.gotoLine(linenr)
    def deleteLines(self):
        cursor = self.textCursor()
        # Find start and end of selection
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        # Expand selection: from start of first block to start of next block
        cursor.setPosition(start)
        cursor.movePosition(cursor.StartOfBlock)
        cursor.setPosition(end, cursor.KeepAnchor)
        cursor.movePosition(cursor.NextBlock, cursor.KeepAnchor)

        cursor.removeSelectedText()
    def duplicateLines(self):
        cursor = self.textCursor()
        # Find start and end of selection
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        # Expand selection: from start of first block to start of next block
        cursor.setPosition(start)
        cursor.movePosition(cursor.StartOfBlock)
        cursor.setPosition(end, cursor.KeepAnchor)
        cursor.movePosition(cursor.NextBlock, cursor.KeepAnchor)

        text = cursor.selectedText()
        cursor.setPosition(start)
        cursor.movePosition(cursor.StartOfBlock)
        cursor.insertText(text)
    def commentCode(self):
        """
        Comment the lines that are currently selected
        """
        indents = []

        def getIndent(cursor):
            text = cursor.block().text().rstrip()
            if text:
                indents.append(len(text) - len(text.lstrip()))

        def commentBlock(cursor):
            cursor.setPosition(cursor.block().position() + minindent)
            cursor.insertText('# ')

        self.doForSelectedBlocks(getIndent)
        minindent = min(indents) if indents else 0
        self.doForSelectedBlocks(commentBlock)
    def uncommentCode(self):
        """
        Uncomment the lines that are currently selected
        """
        #TODO: this should not be applied to lines that are part of a multi-line string

        #Define the uncomment function to be applied to all blocks
        def uncommentBlock(cursor):
            """
            Find the first # on the line; if there is just whitespace before it,
            remove the # and if it is followed by a space remove the space, too
            """
            text = cursor.block().text()
            commentStart = text.find('#')
            if commentStart == -1:
                return #No comment on this line
            if text[:commentStart].strip() != '':
                return #Text before the #
            #Move the cursor to the beginning of the comment
            cursor.setPosition(cursor.block().position() + commentStart)
            cursor.deleteChar()
            if text[commentStart:].startswith('# '):
                cursor.deleteChar()

        #Apply this function to all blocks
        self.doForSelectedBlocks(uncommentBlock)
    def gotoDef(self):
        """
        Goto the definition for the word under the cursor
        """

        # Get name of object to go to
        cursor = self.textCursor()
        if not cursor.hasSelection():
            cursor.select(cursor.WordUnderCursor)
        word = cursor.selection().toPlainText()

        # Send the open command to the shell
        s = pyzo.shells.getCurrentShell()
        if s is not None:
            if word and word.isidentifier():
                s.executeCommand('open %s\n'%word)
            else:
                s.write('Invalid identifier %r\n' % word)

    ## Introspection processing methods
    def processCallTip(self, cto):
        """ Processes a calltip request using a CallTipObject instance.
        """
        # Try using buffer first
        if cto.tryUsingBuffer():
            return

        # Try obtaining calltip from the source
        sig = pyzo.parser.getFictiveSignature(cto.name, self, True)
        if sig:
            # Done
            cto.finish(sig)
        else:
            # Try the shell
            shell = pyzo.shells.getCurrentShell()
            if shell:
                shell.processCallTip(cto)
    def processAutoComp(self, aco):
        """ Processes an autocomp request using an AutoCompObject instance.
        """

        # Try using buffer first
        if aco.tryUsingBuffer():
            return

        # Init name to poll by remote process (can be changed!)
        nameForShell = aco.name

        # Get normal fictive namespace
        fictiveNS = pyzo.parser.getFictiveNameSpace(self)
        fictiveNS = set(fictiveNS)

        # Add names
        if not aco.name:
            # "root" names
            aco.addNames(fictiveNS)
            # imports
            importNames, importLines = pyzo.parser.getFictiveImports(self)
            aco.addNames(importNames)
        else:
            # Prepare list of class names to check out
            classNames = [aco.name]
            handleSelf = True
            # Unroll supers
            while classNames:
                className = classNames.pop(0)
                if not className:
                    continue
                if handleSelf or (className in fictiveNS):
                    # Only the self list (only first iter)
                    fictiveClass = pyzo.parser.getFictiveClass(
                        className, self, handleSelf)
                    handleSelf = False
                    if fictiveClass:
                        aco.addNames( fictiveClass.members )
                        classNames.extend(fictiveClass.supers)
                else:
                    nameForShell = className
                    break

        # If there's a shell, let it finish the autocompletion
        shell = pyzo.shells.getCurrentShell()
        if shell:
            aco.name = nameForShell # might be the same or a base class
            shell.processAutoComp(aco)
        else:
            # Otherwise we finish it ourselves
            aco.finish()

### Don't allow this.
    # if __name__=="__main__":
        # # Do some stubbing to run this module as a unit separate from pyzo
        # # TODO: untangle pyzo from this module where possible
        # class DummyParser:
            # def parseThis(self, x):
                # pass
        # pyzo.parser = DummyParser()
        # EditorContextMenu = QtWidgets.QMenu  # noqa
        # app = QtWidgets.QApplication([])
        # win = PyzoEditor(None)
        # QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+C"), win).activated.connect(win.copy)
        # QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+X"), win).activated.connect(win.cut)
        # QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+V"), win).activated.connect(win.paste)
        # QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Shift+V"), win).activated.connect(win.pasteAndSelect)
        # QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Z"), win).activated.connect(win.undo)
        # QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Y"), win).activated.connect(win.redo)
    
        # tmp = "foo(bar)\nfor bar in range(5):\n  print bar\n"
        # tmp += "\nclass aap:\n  def monkey(self):\n    pass\n\n"
        # win.setPlainText(tmp)
        # win.show()
        # app.exec_()
