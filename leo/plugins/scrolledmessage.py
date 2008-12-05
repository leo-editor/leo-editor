
#@+leo-ver=4-thin
#@+node:leohag.20081204085551.1:@thin scrolledmessage.py
#@@first

#@<< docstring >>
#@+node:leohag.20081203143921.2:<< docstring >>
"""
Scrolled Message Dialog
=======================

Provides a Scrolled Message Dialog service for Qt based guis/plugins.

The plugin can display messages supplied as plain text or formated as html. In addition the plugin can accept messages in rst format and convert them to be displayed as html.

The displayed format can be controlled by the user via check boxes, so rst messages may be viewed either as text or as html. Html messages can also be viwed as raw text, which will be a good debug feature when creating complex dynamically generated html messages.

The user interface is provided by a ScrolledMessage.ui file which is dynamically loaded each time a new dialog is loaded.

The dialog is not modal and many dialogs can exist at one time. Dialogs can be named and output directed to a dialog with a specific name.  

The plugin is invoked like this:

    g.doHook('scrolledMessage', c=c, msg='message', title='title',  ...etc    )

or
    g.app.gui.runScrolledMessageDialog(c=c, ...etc)

all parameters are optional except c.

Parameters
----------
    msg:
        The text to be displayed (html, rst, plain).

        If the text starts with 'rst:' it is assumed to be rst text and
        is converted to html for display, (after the rst: prefix has been removed.

        If the text starts with '<' it is assumed to be html.

        These auto detection features can be overridden by 'flags'.

    label:
        The text to appear in a label above the display. If it is '', the label is hidden.

    title:
        The title to appear on the window or dock.

    flags:
        Says what kind of message eg: 'rst', 'text', 'html'. This overrides auto-detection.

        Flags can be combined, eg 'rst html' causes the message to be interpreted as rst and
        displayed as html.

To Do
-----
    - Add parameters to control position, size, closing, hiding etc.

    - Save or print files from the dialog.

    - Add an option to put the dialog in leo's log notebook.

    - Add \@settings to control default behaviour

    - Provide a menu of plugins that allows their docstring to be displayed.

    - Provide a menu of @rst nodes in the current outline, automatically track changes
      if it is set to display any of these nodes.

"""
#@-node:leohag.20081203143921.2:<< docstring >>
#@nl

#@@language python
#@@tabwidth -4
#@@pagewidth 80

controllers = {}

#@<< imports >>
#@+node:leohag.20081203143921.3:<< imports >>
import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

try:
    from PyQt4 import QtCore, QtGui, uic
    Qt = QtCore.Qt
except ImportError:
    Qt = None

#@+others
#@-others
#@-node:leohag.20081203143921.3:<< imports >>
#@nl

#@+others
#@+node:leohag.20081203143921.4:init
def init():

    ok = g.app.gui.guiName().startswith("qt")
    if ok:
        leoPlugins.registerHandler(('open2','new'), onCreate)
        g.plugin_signon(__name__)

    return ok
#@-node:leohag.20081203143921.4:init
#@+node:leohag.20081203143921.5:onCreate
def onCreate (tag,key):

    c = key.get('c')
    if c in controllers:
        return

    controllers[c] = cc = ScrolledMessageController(c) 
    leoPlugins.registerHandler('scrolledMessage', cc.scrolledMessageHandler)

#@-node:leohag.20081203143921.5:onCreate
#@+node:leohag.20081203143921.6:scrolledMessageHandler
def scrolledMessageHandler(tag, keywords):

    c = keywords.get('c')
    if  c in controllers:
        controllers[c].scrolledMessageHandler(tag, keywords)
#@nonl
#@-node:leohag.20081203143921.6:scrolledMessageHandler
#@+node:leohag.20081203143921.9:class ScrolledMessageDialog
class ScrolledMessageDialog(object):

    #@    @+others
    #@+node:leohag.20081203210510.1:__init__
    def __init__(self, parent, kw ):

        self.parent = parent
        self.c = parent.c
        self.ui = self.getGui()(self)

        #self.menubar = mb = QtGui.QMenuBar(self.ui)
        #mb.show()
        #mb.addAction('hello')
        #self.ui.layout().insertWidget(0, self.menubar)

        top = self.c.frame.top
        self.dock = dock = QtGui.QDockWidget("Scrolled Message Dialog", top)
        dock.setAllowedAreas(Qt.AllDockWidgetAreas)
        dock.setWidget(self.ui)
        dock.resize(400, 600)

        top.addDockWidget(Qt.RightDockWidgetArea, dock)

        dock.setFloating(True)

        self.controls = {}
        self.controlFlags = {}

        self.findChkControls()
        self.chkBtnChanged(silent=True)

        self.updateDialog(kw)
        self.ui.show()
    #@-node:leohag.20081203210510.1:__init__
    #@+node:leohag.20081203143921.24:getUiPath
    def getUiPath(self):

        return g.os_path_join(g.app.loadDir,'..','plugins', 'ScrolledMessage.ui')
    #@nonl
    #@-node:leohag.20081203143921.24:getUiPath
    #@+node:leohag.20081203143921.22:getGui

    def getGui(self):

        form_class, base_class = uic.loadUiType(self.getUiPath())
        #@    << define class Base_UI>>
        #@+node:leohag.20081203143921.23:<<define class Base_UI>>
        class Base_UI(QtGui.QWidget, form_class):
            """Class to wrap QDesigner ui object and provide glue code to make it work."""

            def __init__(self, parent, *args):
                QtGui.QWidget.__init__(self, *args)
                self.setupUi(self)
                self.leoParent = parent

            def chkBtnChanged(self):
                self.leoParent.chkBtnChanged()

            def closeEvent(self, event):
                self.leoParent.closeMe(event)
        #@-node:leohag.20081203143921.23:<<define class Base_UI>>
        #@nl
        return Base_UI
    #@-node:leohag.20081203143921.22:getGui
    #@+node:leohag.20081203205020.1:closeMe
    def closeMe(self, visible):
            self.parent.onDialogClosing(self)
            self.dock.destroy()

            print self.dock
            print self.ui

    #@-node:leohag.20081203205020.1:closeMe
    #@+node:leohag.20081203143921.10:findChkControls
    def findChkControls(self):
        s = 'leo_chk_'; ls = len(s)
        for k, v in self.ui.__dict__.iteritems():
            if k.startswith(s):
                self.controls[k[ls:]] = v

    #@-node:leohag.20081203143921.10:findChkControls
    #@+node:leohag.20081203143921.11:setFlagsFromControls
    def setFlagsFromControls(self):
        for flag, control in self.controls.iteritems():
            self.controlFlags[flag] = bool(control.isChecked())

    #@-node:leohag.20081203143921.11:setFlagsFromControls
    #@+node:leohag.20081203143921.12:setControlsFromFlags
    def setControlsFromFlags(self):
        for flag, value in self.controlFlags.iteritems():
            self.controls[flag].setChecked(bool(value))

    #@-node:leohag.20081203143921.12:setControlsFromFlags
    #@+node:leohag.20081203143921.13:chkBtnClhanged
    def  chkBtnChanged(self,silent=False):
        self.setFlagsFromControls()
        if not silent:
            self.showMessage()

    #@-node:leohag.20081203143921.13:chkBtnClhanged
    #@+node:leohag.20081203143921.14:showMessage
    def showMessage(self):
        msg = self.msg
        f = self.controlFlags
        #g.trace(self.controlFlags)
        if f['html']:
            if f['rst']:
                msg = self.rstToHtml(msg)
            if f['text']:
                    msg = self.textToHtml(msg)
        else:
            msg = self.textToHtml(msg)

        self.ui.leo_webView.setHtml(msg)
        self.dock.show()
        toggle = self.dock.toggleViewAction()
        toggle.setChecked(True)

    #@-node:leohag.20081203143921.14:showMessage
    #@+node:leohag.20081203143921.15:rstToHtml
    def rstToHtml( self, rst):

        try:
            from docutils import core
        except ImportError:
            g.es('scrolledMessage: Can not import docutils', color='blue')
            return self.textToHtml(rst)

        overrides = {
            'doctitle_xform': False,
            'initial_header_level': 1
        }

        try:
            parts = core.publish_parts(
                source= rst,
                writer_name='html',
                settings_overrides=overrides
            )
        except Exception:
            g.es('scrolledMessage: rst conversion error', color='blue')
            return self.textToHtml(rst)

        return parts['whole']

    #@-node:leohag.20081203143921.15:rstToHtml
    #@+node:leohag.20081203143921.16:textToHtml
    def textToHtml(self, msg):

        msg = msg.replace('&','&amp;').replace('<', '&lt;').replace('>', '&gt;')
        #msg = msg.replace(' ','&nbsp;').replace('\n','<br>');
        return '<pre>%s<pre>'%msg



    #@-node:leohag.20081203143921.16:textToHtml
    #@+node:leohag.20081203143921.17:updateDialog
    def updateDialog(self, kw):

        # update ivars
        for k in kw.keys():
            setattr(self, k, kw[k])

        # auto detect message type
        if not self.flags.strip():
            self.flags = 'text'
            if self.msg.startswith('rst:'):
                self.flags = 'rst html'
                self.msg = self.msg[4:]
            elif self.msg.startswith('<'):
                self.flags = 'html'

        flags = self.flags.split(' ')

        # update the ui check box controls
        ff = self.controlFlags
        for flag in ff.keys():
            if flag in flags:
                ff[flag] = True
            else:
                ff[flag] == False

        if 'rst' in flags and 'text' not in flags:
            ff['html']=True

        self.setControlsFromFlags()

        # update label
        w = self.ui.leo_topLabel
        if self.label:
            w.setText(self.label)
            w.show()
        else:
            w.hide()

        #update title
        self.dock.setWindowTitle(self.title)

        self.showMessage()
    #@-node:leohag.20081203143921.17:updateDialog
    #@+node:leohag.20081203143921.18:show
    def show(self):
        self.ui.show()
    #@nonl
    #@-node:leohag.20081203143921.18:show
    #@-others

#@-node:leohag.20081203143921.9:class ScrolledMessageDialog
#@+node:leohag.20081203143921.19:class ScrolledMessageController
class ScrolledMessageController(object):

    dialogs = {}
    usedNames = set()

    kwDefaults = {'msg':'', 'flags':'', 'name':'', 'title':'Leo Message', 'label':''}

    #@    @+others
    #@+node:leohag.20081203143921.20:updateDialog
    def updateDialog(self, kw):

        if  not kw['name']:
            name = self.getUniqueName()
            kw['name'] = name

        if kw['name'] not in self.dialogs:
            self.createDialog(kw)
        else:
            self.dialogs[kw['name']].updateDialog(kw)

    #@-node:leohag.20081203143921.20:updateDialog
    #@+node:leohag.20081203143921.21:createDialog
    def createDialog(self, kw):

        self.dialogs[kw['name']] = ScrolledMessageDialog(self, kw)
        self.usedNames.add(kw['name'])

    #@-node:leohag.20081203143921.21:createDialog
    #@+node:leohag.20081203143921.25:getUniqueDialogName
    def getUniqueName(self):

        count = 0
        while True:
            count += 1
            name = 'ScrolledMessage_%s'%count
            if name not in self.usedNames:
                return name


    #@-node:leohag.20081203143921.25:getUniqueDialogName
    #@+node:leohag.20081203143921.26:scrolledMessageHandler
    def scrolledMessageHandler(self, tag, keywords):   

        for k, v in self.kwDefaults.iteritems():
            if k not in keywords:
                keywords[k] = v 

        #g.trace(keywords)
        self.updateDialog(keywords)

        return keywords

    #@-node:leohag.20081203143921.26:scrolledMessageHandler
    #@+node:leohag.20081203210510.3:onDialogClosing
    def onDialogClosing(self, dialog):

        del self.dialogs[dialog.name]

    #@-node:leohag.20081203210510.3:onDialogClosing
    #@-others

    def __init__(self, c):

        self.c = c
#@-node:leohag.20081203143921.19:class ScrolledMessageController
#@-others
#@-node:leohag.20081204085551.1:@thin scrolledmessage.py
#@-leo
