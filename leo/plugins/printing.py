#@+leo-ver=5-thin
#@+node:peckj.20130514093558.4062: * @file printing.py
#@@language python
#@@tabwidth -4

#@+<< docstring >>
#@+node:peckj.20130513115943.16252: ** << docstring >>
'''Supports printing for the Qt GUI.

By Jacob M. Peck.

Commands
========

This plugin supports the following commands:
    
print-selected-node
-------------------

Opens up the print dialog to print the selected headline and node.

print-preview-selected-node
---------------------------

Opens up the print preview dialog to preview the selected headline 
and node.

print-selected-node-body
------------------------

Opens up the print dialog to print the selected node body.

print-preview-selected-node-body
--------------------------------

Opens up the print preview dialog to preview the selected node body.

print-expanded-node
-------------------

Opens up the print dialog to print the expanded contents of the 
selected node, with top-level headline.

print-preview-expanded-node
---------------------------

Opens up the print preview dialog to preview the expanded contents 
of theselected node, with top-level headline.

print-expanded-node-body
------------------------

Opens up the print dialog to print the expanded node body.

print-preview-expanded-node-body
--------------------------------

Opens up the print preview dialog to preview the expanded node 
body.

print-marked-nodes
------------------

Opens up the print dialog to print all marked nodes in the current
outline, with headlines.

print-preview-marked-nodes
--------------------------

Opens up the print preview dialog to preview all marked nodes in \
the current outline, with headlines.

print-marked-node-bodies
------------------------

Opens up the print dialog to print the bodies of all marked nodes
in the current outline.

print-preview-marked-node-bodies
--------------------------------

Opens up the print preview dialog to preview the bodies of all 
marked nodes in the current outline.

print-selected-node-body-html
-----------------------------

Opens up the print dialog to print the body of the selected node
as a rendered HTML (i.e., rich text) document.

print-preview-selected-node-body-html
-------------------------------------

Opens up the print preview dialog to preview the body of the selected
node as a rendered HTML (i.e., rich text) document.

Settings
========

- ``@string printing-font-family = DejaVu Sans Mono``
  The font family for printing.  A monospaced font is recommended.

- ``@string printing-font-size = 12``
  The font size for printing bodies, in px.  Due to limitations
  of PyQt, the size of headlines cannot be changed.

Custom Printing
===============

Most custom jobs can be accomplished with the richtext.py plugin and the 
print-preview-selected-node-body-html command.

There is a blog post at http://leo-editor.github.io/custom_printing.html that explains 
how to print custom documents with the printing.py plugin in a programmatic
fashion, using scripts to define your document.

'''
#@-<< docstring >>
#@+<< version history >>
#@+node:peckj.20130513115943.16254: ** << version history >>
#@+at
# 
# version 0.1 (2013-05-14) - initial release
# version 0.2 (2013-08-14) - added print-html-node (rich text) commands
# 
#@@c
#@-<< version history >>
#@+<< imports >>
#@+node:peckj.20130513115943.16253: ** << imports >>
import leo.core.leoGlobals as g
import leo.plugins.qtGui as qtGui
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
        ## expanded node
        c.k.registerCommand('print-expanded-node-body',shortcut=None,func=self.print_expanded_node_body)
        c.k.registerCommand('print-preview-expanded-node-body',
                            shortcut=None,func=self.print_preview_expanded_node_body)
        c.k.registerCommand('print-expanded-node',shortcut=None,func=self.print_expanded_node)
        c.k.registerCommand('print-preview-expanded-node',
                            shortcut=None,func=self.print_preview_expanded_node)
        ## marked nodes
        c.k.registerCommand('print-marked-node-bodies',shortcut=None,func=self.print_marked_node_bodies)
        c.k.registerCommand('print-preview-marked-node-bodies',
                            shortcut=None,func=self.print_preview_marked_node_bodies)
        c.k.registerCommand('print-marked-nodes',shortcut=None,func=self.print_marked_nodes)
        c.k.registerCommand('print-preview-marked-nodes',
                            shortcut=None,func=self.print_preview_marked_nodes)
        ## selected node html
        c.k.registerCommand('print-selected-node-body-html',shortcut=None,func=self.print_selected_node_body_html)
        c.k.registerCommand('print-preview-selected-node-body-html',
                            shortcut=None,func=self.print_preview_selected_node_body_html)
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
        text = self.sanitize_html(text)
        if head:
            head = self.sanitize_html(head)
            contents = "<h1>%s</h1>\n<pre>%s</pre>" % (head, text)
        else:
            contents = "<pre>%s<pre>" % text
        doc.setHtml(contents)
        return doc
    #@+node:peckj.20130814150446.4883: *4* construct html document
    def construct_html_document(self, text):
        doc = QtGui.QTextDocument()
        doc.setDefaultStyleSheet(self.stylesheet)
        doc.setHtml(text)
        return doc
    #@+node:peckj.20130514082859.5603: *4* construct complex document
    def construct_complex_document(self, nodes, heads=False):
        doc = QtGui.QTextDocument()
        doc.setDefaultStyleSheet(self.stylesheet)
        contents = ''
        for n in nodes:
            if heads:
                contents += '<h1>%s</h1>\n' % (self.sanitize_html(n.h))
            contents += '<pre>%s</pre>\n' % (self.sanitize_html(n.b))
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
    #@+node:peckj.20130514082859.5604: *4* sanitize html
    def sanitize_html(self, html):
        ''' quick and dirty way to make sure html is escaped properly for printing '''
        return html.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    #@+node:peckj.20130514082859.5610: *4* untangle
    def untangle(self,p):
        return g.getScript(self.c,p,
            useSelectedText=False,
            useSentinels=False)
    #@+node:peckj.20130513115943.22666: *3* selected node
    #@+node:peckj.20130814150446.4884: *4* html
    #@+node:peckj.20130814145125.4886: *5* print_selected_node_body_html
    def print_selected_node_body_html (self,event=None):
        ''' prints the selected node body as html (rich text)'''
        
        doc = self.construct_html_document(self.c.p.b)
        self.print_doc(doc)
    #@+node:peckj.20130814145125.4884: *5* print_preview_selected_node_body_html
    def print_preview_selected_node_body_html (self,event=None):
        ''' print previews the selected node body as html (rich text)'''
        
        doc = self.construct_html_document(self.c.p.b)
        self.print_preview_doc(doc)
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
    #@+node:peckj.20130514082859.5616: *3* expanded selected node
    #@+node:peckj.20130514082859.5617: *4* print_expanded_node_body
    def print_expanded_node_body (self,event=None):
        ''' prints the expanded selected node body '''
         
        doc = self.construct_document(self.untangle(self.c.p))
        self.print_doc(doc)
    #@+node:peckj.20130514082859.5618: *4* print_preview_expanded_node_body
    def print_preview_expanded_node_body (self,event=None):
        ''' print previews the expanded selected node body'''
        
        doc = self.construct_document(self.untangle(self.c.p))
        self.print_preview_doc(doc)
    #@+node:peckj.20130514082859.5619: *4* print_expanded_node
    def print_expanded_node (self,event=None):
        ''' prints the expanded selected node '''
        
        p = self.c.p
        doc = self.construct_document(self.untangle(p), head=p.h)
        self.print_doc(doc)
    #@+node:peckj.20130514082859.5620: *4* print_preview_expanded_node
    def print_preview_expanded_node (self,event=None):
        ''' prints the expanded selected node '''
        
        p = self.c.p
        doc = self.construct_document(self.untangle(p), head=p.h)
        self.print_preview_doc(doc)
    #@+node:peckj.20130514082859.5605: *3* marked nodes
    #@+node:peckj.20130514082859.5606: *4* print_marked_node_bodies
    def print_marked_node_bodies (self,event=None):
        ''' prints the marked node bodies'''
        nodes = []
        for n in self.c.all_positions():
            if n.isMarked():
                nodes.append(n.v)
        doc = self.construct_complex_document(nodes)
        self.print_doc(doc)
    #@+node:peckj.20130514082859.5607: *4* print_preview_marked_node_bodies
    def print_preview_marked_node_bodies (self,event=None):
        ''' print previews the marked node bodies'''
        nodes = []
        for n in self.c.all_positions():
            if n.isMarked():
                nodes.append(n.v)
        doc = self.construct_complex_document(nodes)
        self.print_preview_doc(doc)
    #@+node:peckj.20130514082859.5608: *4* print_marked_nodes
    def print_marked_nodes (self,event=None):
        ''' prints the marked nodes'''
        nodes = []
        for n in self.c.all_positions():
            if n.isMarked():
                nodes.append(n.v)
        doc = self.construct_complex_document(nodes, heads=True)
        self.print_doc(doc)
    #@+node:peckj.20130514082859.5609: *4* print_preview_marked_nodes
    def print_preview_marked_nodes (self,event=None):
        ''' print previews the marked nodes'''
        nodes = []
        for n in self.c.all_positions():
            if n.isMarked():
                nodes.append(n.v)
        doc = self.construct_complex_document(nodes, heads=True)
        self.print_preview_doc(doc)
    #@-others
#@-others
#@-leo
