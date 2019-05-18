# -*- coding: utf-8 -*-
# Copyright (C) 2013, the codeeditor development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

from ..qt import QtCore, QtGui, QtWidgets  # noqa
Qt = QtCore.Qt

class Calltip(object):
    _styleElements = [('Editor.calltip', 'The style of the calltip. ',
                        'fore:#555, back:#ff9, border:1')]
    
    class __CalltipLabel(QtWidgets.QLabel):
        def __init__(self):
            QtWidgets.QLabel.__init__(self)
            
            # Start hidden
            self.hide()
            # Accept rich text
            self.setTextFormat(QtCore.Qt.RichText)
            # Show as tooltip
            self.setIndent(2)
            self.setWindowFlags(QtCore.Qt.ToolTip)
        
        def enterEvent(self, event):
            # Act a bit like a tooltip
            self.hide()
    
    
    def __init__(self, *args, **kwds):
        super(Calltip, self).__init__(*args, **kwds)
        # Create label for call tips
        self.__calltipLabel = self.__CalltipLabel()
        # Be notified of style updates
        self.styleChanged.connect(self.__afterSetStyle)
        
        # Prevents calltips from being shown immediately after pressing
        # the escape key.
        self.__noshow = False
    
    
    def __afterSetStyle(self):
        format = self.getStyleElementFormat('editor.calltip')
        ss = "QLabel { color:%s; background:%s; border:%ipx solid %s; }" % (
                    format['fore'], format['back'],
                    int(format['border']), format['fore'] )
        self.__calltipLabel.setStyleSheet(ss)
    
    
    def calltipShow(self, offset=0, richText='', highlightFunctionName=False):
        """ calltipShow(offset=0, richText='', highlightFunctionName=False)
        
        Shows the given calltip.
        
        Parameters
        ----------
        offset : int
            The character offset to show the tooltip.
        richText : str
            The text to show (may contain basic html for markup).
        highlightFunctionName : bool
            If True the text before the first opening brace is made bold.
            default False.
        
        """
        
        # Do not show the calltip if it was deliberately hidden by the
        # user.
        if self.__noshow:
            return
        
        # Process calltip text?
        if highlightFunctionName:
            i = richText.find('(')
            if i>0:
                richText = '<b>{}</b>{}'.format(richText[:i], richText[i:])
        
        # Get a cursor to establish the position to show the calltip
        startcursor = self.textCursor()
        startcursor.movePosition(startcursor.Left, n=offset)
        
        # Get position in pixel coordinates
        rect = self.cursorRect(startcursor)
        pos = rect.topLeft()
        pos.setY( pos.y() - rect.height() - 1 ) # Move one above line
        pos.setX( pos.x() - 3) # Correct for border and indent
        pos = self.viewport().mapToGlobal(pos)
        
        # Set text and update font
        self.__calltipLabel.setText(richText)
        self.__calltipLabel.setFont(self.font())
        
        # Use a qt tooltip to show the calltip
        if richText:
            self.__calltipLabel.move(pos)
            self.__calltipLabel.show()
        else:
            self.__calltipLabel.hide()
    
    
    def calltipCancel(self):
        """ calltipCancel()
        
        Hides the calltip.
        
        """
        self.__calltipLabel.hide()
    
    
    def calltipActive(self):
        """ calltipActive()
        
        Get whether the calltip is currently active.
        
        """
        return self.__calltipLabel.isVisible()
    
    
    def focusOutEvent(self, event):
        super(Calltip, self).focusOutEvent(event)
        self.__calltipLabel.hide()
    
    
    def keyPressEvent(self,event):
        # If the user presses Escape and the calltip is active, hide it
        if event.key() == Qt.Key_Escape and event.modifiers() == Qt.NoModifier \
                and self.calltipActive():
            self.calltipCancel()
            self.__noshow = True
            return
        
        if event.key() in [Qt.Key_ParenLeft, Qt.Key_ParenRight]:
            self.__noshow = False
        
        # Proceed processing the keystrike
        super(Calltip, self).keyPressEvent(event)
