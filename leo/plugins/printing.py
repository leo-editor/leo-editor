#@+leo-ver=5-thin
#@+node:peckj.20130513193024.6320: * @file printing.py
#@@language python
#@@tabwidth -4

#@+<< docstring >>
#@+node:peckj.20130513115943.16252: ** << docstring >>
'''This plugin allows printing nodes and outlines while using the
PyQt GUI.'''
#@-<< docstring >>
#@+<< version history >>
#@+node:peckj.20130513115943.16254: ** << version history >>
#@+at
# 
#@-<< version history >>
#@+<< imports >>
#@+node:peckj.20130513115943.16253: ** << imports >>
import leo.core.leoGlobals as g
from PyQt4 import QtGui
from PyQt4 import QtCore
#@-<< imports >>

__version__ = '0.1'

#@+others
#@+node:peckj.20130513115943.16247: ** init
def init ():

    if g.app.gui is None:
        g.app.createQtGui(__file__)

    ok = g.app.gui.guiName().startswith('qt')

    if ok:
        g.registerHandler(('new','open2'),onCreate)
        g.plugin_signon(__name__)

    return ok
#@+node:peckj.20130513115943.16248: ** onCreate
def onCreate (tag, keys):
    
    '''Handle the onCreate event in the printing plugin.'''

    c = keys.get('c')
    
    if c:
       pc = printingController(c)
       c.thePrintingController = pc 
       
#@+node:peckj.20130513115943.16249: ** class printingController
class printingController:

    #@+others
    #@+node:peckj.20130513115943.16250: *3* __init__
    def __init__ (self,c):
        self.c = c
        
        # gather settings
        self.font_size = c.config.getString('printing-font-size') or '12'
        self.font_family = c.config.getString('printing-font-family') or 'DejaVu Sans Mono'
        
        # initialize
        self.stylesheet = self.construct_stylesheet()
        
        # register commands
        ## selected node
        c.k.registerCommand('print-selected-node-body',shortcut=None,func=self.print_selected_node_body)
        c.k.registerCommand('print-preview-selected-node-body',
                            shortcut=None,func=self.print_preview_selected_node_body)
        c.k.registerCommand('print-selected-node',shortcut=None,func=self.print_selected_node)
        c.k.registerCommand('print-preview-selected-node',
                            shortcut=None,func=self.print_preview_selected_node)
    #@+node:peckj.20130513115943.22457: *3* helpers
    #@+node:peckj.20130513115943.22458: *4* construct stylesheet
    def construct_stylesheet(self):
        s = 'h1 {font-family: %s}\n' % self.font_family
        s += 'pre {font-family: %s; font-size: %spx}' % (self.font_family, self.font_size)
        return s
    #@+node:peckj.20130513115943.22459: *4* construct document
    def construct_document(self, text, head=None):
        doc = QtGui.QTextDocument()
        doc.setDefaultStyleSheet(self.stylesheet)
        text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        if head:
            head = head.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            contents = "<h1>%s</h1>\n<pre>%s</pre>" % (head, text)
        else:
            contents = "<pre>%s<pre>" % text
        doc.setHtml(contents)
        return doc
    #@+node:peckj.20130513115943.22661: *4* print dialog
    def print_doc(self, doc):
        dialog = QtGui.QPrintDialog()
        if dialog.exec_() == QtGui.QDialog.Accepted:
            doc.print_(dialog.printer())
    #@+node:peckj.20130513115943.22662: *4* print preview dialog
    def print_preview_doc(self, doc):
        dialog = QtGui.QPrintPreviewDialog()
        dialog.paintRequested.connect(doc.print_)
        dialog.exec_()
    #@+node:peckj.20130513115943.22666: *3* selected node
    #@+node:peckj.20130513193024.6336: *4* print_selected_node_body
    def print_selected_node_body (self,event=None):
        ''' prints the selected node body'''
        
        doc = self.construct_document(self.c.p.b)
        self.print_doc(doc)
    #@+node:peckj.20130513193024.6337: *4* print_preview_selected_node_body
    def print_preview_selected_node_body (self,event=None):
        ''' print previews the selected node body'''
        
        doc = self.construct_document(self.c.p.b)
        self.print_preview_doc(doc)
    #@+node:peckj.20130513115943.16251: *4* print_selected_node
    def print_selected_node (self,event=None):
        ''' prints the selected node '''
        
        doc = self.construct_document(self.c.p.b, head=self.c.p.h)
        self.print_doc(doc)
    #@+node:peckj.20130513115943.22456: *4* print_preview_selected_node
    def print_preview_selected_node (self,event=None):
        ''' prints the selected node '''
        
        doc = self.construct_document(self.c.p.b, head=self.c.p.h)
        self.print_preview_doc(doc)
    #@-others
#@-others
#@-leo
