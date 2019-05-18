# -*- coding: utf-8 -*-
# Copyright (C) 2016, the Pyzo development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.


import sys, re

from pyzo.util.qt import QtCore, QtGui, QtWidgets  # noqa
import pyzo

tool_name = pyzo.translate("pyzoInteractiveHelp","Interactive help")
tool_summary = "Shows help on an object when using up/down in autocomplete."

#
htmlWrap = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN"
"http://www.w3.org/TR/REC-html40/strict.dtd">
<html>
<head>
<style type="text/css">
</style>
</head>
<body style=" font-family:'Sans Serif'; font-size:{}pt; font-weight:400; font-style:normal;">
{}
</body>
</html>
"""

# Define title text (font-size percentage does not seem to work sadly.)
def get_title_text(objectName, h_class='', h_repr=''):
    title_text = "<p style='background-color:#def;'>"
    title_text += "<b>Object:</b> {}".format(objectName)
    if h_class:
        title_text += ", <b>class:</b> {}".format(h_class)
    if h_repr:
        if len(h_repr) > 40:
            h_repr = h_repr[:37] + '...'
        title_text += ", <b>repr:</b> {}".format(h_repr)
        
    # Finish
    title_text += '</p>\n'
    return title_text

initText =  """
Help information is queried from the current shell
when moving up/down in the autocompletion list
and when double clicking on a name.
"""


class PyzoInteractiveHelp(QtWidgets.QWidget):
    
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        
        
        # Create text field, checkbox, and button
        self._text = QtWidgets.QLineEdit(self)
        self._printBut = QtWidgets.QPushButton("Print", self)
        
        # Create options button
        self._options = QtWidgets.QToolButton(self)
        self._options.setIcon(pyzo.icons.wrench)
        self._options.setIconSize(QtCore.QSize(16,16))
        self._options.setPopupMode(self._options.InstantPopup)
        self._options.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        
        # Create options menu
        self._options._menu = QtWidgets.QMenu()
        self._options.setMenu(self._options._menu)
        
        # Create browser
        self._browser = QtWidgets.QTextBrowser(self)
        self._browser_text = initText
        
        # Create two sizers
        self._sizer1 = QtWidgets.QVBoxLayout(self)
        self._sizer2 = QtWidgets.QHBoxLayout()
        
        # Put the elements together
        self._sizer2.addWidget(self._text, 4)
        self._sizer2.addWidget(self._printBut, 0)
        self._sizer2.addWidget(self._options, 2)
        #
        self._sizer1.addLayout(self._sizer2, 0)
        self._sizer1.addWidget(self._browser, 1)
        #
        self._sizer1.setSpacing(2)
        self._sizer1.setContentsMargins(4,4,4,4)
        self.setLayout(self._sizer1)
        
        # Set config
        toolId =  self.__class__.__name__.lower()
        self._config = config = pyzo.config.tools[toolId]
        #
        if not hasattr(config, 'smartNewlines'):
            config.smartNewlines = True
        if not hasattr(config, 'fontSize'):
            if sys.platform == 'darwin':
                config.fontSize = 12
            else:
                config.fontSize = 10
        
        # Create callbacks
        self._text.returnPressed.connect(self.queryDoc)
        self._printBut.clicked.connect(self.printDoc)
        #
        self._options.pressed.connect(self.onOptionsPress)
        self._options._menu.triggered.connect(self.onOptionMenuTiggered)
        
        # Start
        self.setText()  # Set default text
        self.onOptionsPress() # Fill menu
    
    
    def onOptionsPress(self):
        """ Create the menu for the button, Do each time to make sure
        the checks are right. """
        
        # Get menu
        menu = self._options._menu
        menu.clear()
        
        # Add smart format option
        action = menu.addAction('Smart format')
        action.setCheckable(True)
        action.setChecked(bool(self._config.smartNewlines))
        
        # Add delimiter
        menu.addSeparator()
        
        # Add font size options
        currentSize = self._config.fontSize
        for i in range(8,15):
            action = menu.addAction('font-size: %ipx' % i)
            action.setCheckable(True)
            action.setChecked(i==currentSize)
    
    
    def onOptionMenuTiggered(self, action):
        """  The user decides what to show in the structure. """
        
        # Get text
        text = action.text().lower()
        
        if 'smart' in text:
            # Swap value
            current = bool(self._config.smartNewlines)
            self._config.smartNewlines = not current
            # Update
            self.queryDoc()
        
        elif 'size' in text:
            # Get font size
            size = int( text.split(':',1)[1][:-2] )
            # Update
            self._config.fontSize = size
            # Update
            self.setText()
    
    
    def setText(self, text=None):
        
        # (Re)store text
        if text is None:
            text = self._browser_text
        else:
            self._browser_text = text
        
        # Set text with html header
        size = self._config.fontSize
        self._browser.setHtml(htmlWrap.format(size,text))
    
    
    def setObjectName(self, name):
        """ Set the object name programatically
        and query documentation for it. """
        self._text.setText(name)
        self.queryDoc()
    
    
    def printDoc(self):
        """ Print the doc for the text in the line edit. """
        # Get name
        name = self._text.text()
        # Tell shell to print doc
        shell = pyzo.shells.getCurrentShell()
        if shell and name:
            shell.processLine('print({}.__doc__)'.format(name))
    
    
    def queryDoc(self):
        """ Query the doc for the text in the line edit. """
        # Get name
        name = self._text.text()
        # Get shell and ask for the documentation
        shell = pyzo.shells.getCurrentShell()
        if shell and name:
            future = shell._request.doc(name)
            future.add_done_callback(self.queryDoc_response)
        elif not name:
            self.setText(initText)
    
    
    def queryDoc_response(self, future):
        """ Process the response from the shell. """
        
        # Process future
        if future.cancelled():
            #print('Introspect cancelled') # No living kernel
            return
        elif future.exception():
            print('Introspect-queryDoc-exception: ', future.exception())
            return
        else:
            response = future.result()
            if not response:
                return
        
        try:
            # Get parts
            parts = response.split('\n')
            objectName, h_class, h_fun, h_repr = tuple(parts[:4])
            h_text = '\n'.join(parts[4:])
            
            # Obtain newlines that we hid for repr
            h_repr.replace('/r', '/n')
            
            # Make all newlines \n in h_text and strip
            h_text = h_text.replace('\r\n', '\n').replace('\r', '\n')
            h_text = h_text.lstrip()
            
            # Init text
            text = ''
            
            # These signs will fool the html
            h_repr = h_repr.replace("<","&lt;")
            h_repr = h_repr.replace(">","&gt;")
            h_text = h_text.replace("<","&lt;")
            h_text = h_text.replace(">","&gt;")
            
            if self._config.smartNewlines:
                
                # Make sure the signature is separated from the rest using at
                # least two newlines
                header = ''
                if True:
                    # Get short version of objectName
                    name = objectName.split('.')[-1]
                    # Is the signature in the docstring?
                    docs = h_text.replace('\n','|')
                    tmp = re.search('[a-zA-z_\.]*?'+name+'\(.*?\)', docs)
                    if tmp and tmp.span(0)[0]<5:
                        header = tmp.group(0)
                        h_text = h_text[len(header):].lstrip(':').lstrip()
                        header = header.replace('|','')
                        #h_text = header + '\n\n' + h_text
                    elif h_text.startswith(objectName) or h_text.startswith(name):
                        header, sep, docs = h_text.partition('\n')
                        #h_text = header + '\n\n' + docs
                        h_text = docs
                
                # Parse the text as rest/numpy like docstring
                h_text = self.smartFormat(h_text)
                if header:
                    h_text = "<p style='color:#005;'><b>%s</b></p>\n%s" % (
                                                            header, h_text)
                    #h_text = "<b>%s</b><br /><br />\n%s" % (header, h_text)
            else:
                # Make newlines html
                h_text = h_text.replace("\n","<br />")
            
            # Compile rich text
            text += get_title_text(objectName, h_class, h_repr)
            text += '{}<br />'.format(h_text)
        
        except Exception as why:
            try:
                text += get_title_text(objectName, h_class, h_repr)
                text += h_text
            except Exception:
                text = response
        
        # Done
        # size = self._config.fontSize
        self.setText(text)
    
    
    def smartFormat(self, text):
        
        # Get lines
        lines = text.splitlines()
        
        # Test minimal indentation
        minIndent = 9999
        for line in lines[1:]:
            line_ = line.lstrip()
            indent = len(line) - len(line_)
            if line_:
                minIndent = min(minIndent, indent)
        
        # Remove minimal indentation
        lines2 = [lines[0]]
        for line in lines[1:]:
            lines2.append( line[minIndent:] )
        
        # Prepare
        prevLine_ = ''
        prevIndent = 0
        prevWasHeader = False
        inExample = False
        forceNewline = False
        
        # Format line by line
        lines3 = []
        for line in lines2:
            
            
            # Get indentation
            line_ = line.lstrip()
            indent = len(line) - len(line_)
            #indentPart = line[:indent-minIndent]
            indentPart = line[:indent]
            
            if not line_:
                lines3.append("<br />")
                forceNewline = True
                continue
            
            # Indent in html
            line = "&nbsp;" * len(indentPart) + line
            
            # Determine if we should introduce a newline
            isHeader = False
            if ("---" in line or "===" in line) and indent == prevIndent:
                # Header
                lines3[-1] = '<b>' + lines3[-1] + '</b>'
                line = ''#'<br /> ' + line
                isHeader = True
                inExample = False
                # Special case, examples
                if prevLine_.lower().startswith('example'):
                    inExample = True
                else:
                    inExample = False
            elif ' : ' in line:
                tmp = line.split(' : ',1)
                line = '<br /><u>' + tmp[0] + '</u> : ' + tmp[1]
            elif line_.startswith('* '):
                line = '<br />&nbsp;&nbsp;&nbsp;&#8226;' + line_[2:]
            elif prevWasHeader or inExample or forceNewline:
                line = '<br />' + line
            else:
                if prevLine_:
                    line = " " + line_
                else:
                    line = line_
            
            # Force next line to be on a new line if using a colon
            if ' : ' in line:
                forceNewline = True
            else:
                forceNewline = False
            
            # Prepare for next line
            prevLine_ = line_
            prevIndent = indent
            prevWasHeader = isHeader
            
            # Done with line
            lines3.append(line)
        
        # Done formatting
        return ''.join(lines3)
    
