
#@+leo-ver=5-thin
#@+node:leohag.20081204085551.1: * @file scrolledmessage.py
#@@first

#@+<< docstring >>
#@+node:leohag.20081203143921.2: ** << docstring >>
""" Provides a Scrolled Message Dialog service for Qt.

The plugin can display messages supplied as plain text or formatted as html. In
addition the plugin can accept messages in rst format and convert them to be
displayed as html.

There are two possible user interfaces, controlled by::
    
    @bool scrolledmessage_use_viewrendered = True
    
1. When True (the default) the plugin will use the rendering pane
   created by the viewrendered plugin.
   
2. Otherwise, the plugin will use a separate pane as described below:

The displayed format can be controlled by the user via check boxes, so rst
messages may be viewed either as text or as html. Html messages can also be
viewed as raw text, which will be a good debug feature when creating complex
dynamically generated html messages.

The user interface is provided by a ScrolledMessage.ui file which is dynamically
loaded each time a new dialog is loaded.

The dialog is not modal and many dialogs can exist at one time. Dialogs can be
named and output directed to a dialog with a specific name.

The plugin is invoked like this::

    g.doHook('scrolledMessage', c=c, msg='message', title='title',  ...etc    )

or::

    g.app.gui.runScrolledMessageDialog(c=c, ...etc)

All parameters are optional except c.

**Parameters**

msg:
    The text to be displayed (html, rst, plain).

    If the text starts with 'rst:' it is assumed to be rst text and
    is converted to html for display after the rst: prefix has been removed.
    If the text starts with '<' it is assumed to be html.
    These auto detection features can be overridden by 'flags'.

label:
    The text to appear in a label above the display. If it is '', the label is hidden.

title:
    The title to appear on the window or dock.

flags:
    Says what kind of message, for example: 'rst', 'text', 'html'. This overrides auto-detection.

    Flags can be combined, for example: 'rst html' causes the message to be interpreted as rst and
    displayed as html.

**To Do**

- Add parameters to control position, size, closing, hiding etc.

- Save or print files from the dialog.

- Add an option to put the dialog in leo's log notebook.

- Add \@settings to control default behavior

- Provide a menu of plugins that allows their docstring to be displayed.

- Provide a menu of @rst nodes in the current outline, automatically track changes
  if it is set to display any of these nodes.

"""
#@-<< docstring >>

#@@language python
#@@tabwidth -4
#@@pagewidth 80

controllers = {}
globalPrinter = None

#@+<< imports >>
#@+node:leohag.20081203143921.3: ** << imports >>
import leo.core.leoGlobals as g
# import leo.plugins.leo_to_html as leo_to_html

import inspect 

try:
    from PyQt4 import QtCore, QtGui, uic
    Qt = QtCore.Qt
except ImportError:
    Qt = None
    
try:
    # from docutils import core as docutils_core
    import docutils
except ImportError:
    docutils = None
    g.es('scrolledMessage.py: Can not import docutils', color='blue')

#@+others
#@-others
#@-<< imports >>

#@+others
#@+node:leohag.20081203143921.4: ** init
def init():

    ok = g.app.gui.guiName().startswith("qt")
    if ok:
        g.registerHandler(('open2','new'), onCreate)
        g.registerHandler('scrolledMessage', scrolledMessageHandler)
        g.registerHandler('scrolledMessage', selectHandler)

        g.plugin_signon(__name__)

    return ok
#@+node:leohag.20081203143921.5: ** onCreate
def onCreate (tag,key):

    c = key.get('c')
    if c and c.exists and c not in controllers:
        controllers[c] = ScrolledMessageController(c) 

#@+node:leohag.20081206052547.20: ** globalGetPrinter
def getGlobalPrinter():
    global globalPrinter

    if not globalPrinter:
        globalPrinter = QtGui.QPrinter()
    return globalPrinter
#@+node:leohag.20081203143921.6: ** scrolledMessageHandler
def scrolledMessageHandler(tag, keywords):

    c = keywords.get('c')
    if  c in controllers:
        return controllers[c].scrolledMessageHandler(tag, keywords)
#@+node:leohag.20081207032616.20: ** selectHandler
def selectHandler(tag, keywords):

    c = keywords.get('c')
    if  c in controllers:
        return controllers[c].selectHandler(tag, keywords)
#@+node:leohag.20081207032616.18: ** safe
def safe(msg):
    return msg.replace('&','&amp;').replace('<', '&lt;').replace('>', '&gt;')
#@+node:leohag.20081203143921.19: ** class ScrolledMessageController
class ScrolledMessageController(object):


    kwDefaults = {'msg':'', 'flags':'', 'name':'', 'title':'Leo Message', 'label':''}

    #@+others
    #@+node:leohag.20081206052547.1: *3* __init__
    def __init__(self, c):

        self.dialogs = {}
        self.usedNames = set()

        self.c = c
    #@+node:leohag.20081203143921.20: *3* updateDialog
    def updateDialog(self, kw):

        # print(self.c, self.dialogs)

        if  not kw['name']:
            # name = self.getUniqueName()
            name = 'leo_system'
            kw['name'] = name

        if kw['name'] not in self.dialogs:
            self.createDialog(kw)
        else:
            self.dialogs[kw['name']].updateDialog(kw)

    #@+node:leohag.20081203143921.21: *3* createDialog
    def createDialog(self, kw):

        self.dialogs[kw['name']] = ScrolledMessageDialog(self, kw)

        self.usedNames.add(kw['name'])
    #@+node:leohag.20081203143921.25: *3* getUniqueName
    def getUniqueName(self):

        count = 0
        while True:
            count += 1
            name = 'ScrolledMessage_%s'%count
            if name not in self.usedNames:
                return name


    #@+node:leohag.20081203143921.26: *3* scrolledMessageHandler
    def scrolledMessageHandler(self, tag, keywords):   

        for k, v in self.kwDefaults.items():
            if k not in keywords:
                keywords[k] = v 

        # g.trace(keywords)
        self.updateDialog(keywords)

        return keywords

    #@+node:leohag.20081207032616.21: *3* afterRedrawHandler
    def afterRedrawHandler(self, tag, keywords):   

        for name, dialog in dialogs:
            self.afterRedrawHandler()
    #@+node:leohag.20081203210510.3: *3* onDialogClosing
    def onDialogClosing(self, dialog):

        del self.dialogs[dialog.name]
    #@-others

#@+node:leohag.20081203143921.9: ** class ScrolledMessageDialog
class ScrolledMessageDialog(object):

    # 'labels' with no sub menu are the names of actions without the 'action' prefix
    # eg ('Save', None) refers to actionSave

    menuList = [
        ('File', [
            ('Save', None),
            ('', None),
            ('PageSetup', None),
            ('PrintPreview', None),
            ('PrintDialog', None),
        ]),
        ('Outline',[
            ('OutlineShow', None),
            ('RST3', None),
            ('', None),
            ('OutlineThisNode', None),
            ('OutlineExpandFollowsTree', None),
            ('OutlineIncludeBody', None),
        ]),
        ('Help', [
            ('About', None),
        ])
    ]

    #@+others
    #@+node:ekr.20110319081254.14462: *3* Birth
    #@+node:leohag.20081203210510.1: *4* __init__
    def __init__(self, parent,kw):

        self.c = c = parent.c
        self.dock = None
        self.parent = parent
        self.leo_ui = None
        # g.trace('(ScrolledMessageDialog)',kw)
        
        pc = hasattr(c,'viewrendered') and c.viewrendered
        self.use_viewrendered = pc and c.config.getBool('scrolledmessage_use_viewrendered',True)

        if self.use_viewrendered:
            s=kw.get('msg')
            title = kw.get('short_title','').strip()
            pc.view('rst',s,title=title)
            return
        
        top = c.frame.top
        self.leo_ui = self.getGui()(self)
        self.createMenuBar()
        self.dock = dock = QtGui.QDockWidget("Scrolled Message Dialog",top)
        dock.setAllowedAreas(Qt.AllDockWidgetAreas)
        dock.setWidget(self.leo_ui)
        dock.resize(400, 500)
        top.addDockWidget(Qt.RightDockWidgetArea,dock)
        dock.setFloating(False)

        self.controls = {}
        self.controlFlags = {}

        self.findChkControls()
        self.chkBtnChanged(silent=True)

        self.updateDialog(kw)
        self.leo_ui.show()
    #@+node:leohag.20081206052547.34: *4* createMenuBar & helper
    def createMenuBar(self):

        self.menubar = mb = QtGui.QMenuBar(self.leo_ui)

        for title, subMenu in self.menuList:
            menu = self.createSubMenu(mb, title, subMenu)
            mb.addMenu(menu)

        self.leo_ui.leo_menubar_frame.layout().insertWidget(0, mb)
        mb.show()

    #@+node:leohag.20081206052547.13: *5* createSubMenu
    def createSubMenu(self, parent, title, menuList):

        #g.trace(title, menuList)

        menu = QtGui.QMenu(title, parent)
        for subTitle, subList in menuList:

            if subList:
                submenu = self.createSubMenu(menu, subTitle, subList)
                menu.addMenu(submenu)
            elif subTitle:
                #< < find and bind action >>

                action = getattr(self.leo_ui, 'action%s'%subTitle, None)
                if action:
                    method = getattr(self, 'doAction%s'%subTitle, None)
                    if method: 
                        action.connect(action, QtCore.SIGNAL('triggered(bool)'), method)
                    menu.addAction(action)
            else:
                menu.addSeparator()

        return menu
    #@+node:leohag.20081203143921.10: *4* findChkControls
    def findChkControls(self):
        
        s = 'leo_chk_'; n = len(s)
        for k, v in self.leo_ui.__dict__.items():
            if k.startswith(s):
                self.controls[k[n:]] = v

    #@+node:leohag.20081203143921.22: *4* getGui & helper
    def getGui(self):

        form_class, base_class = uic.loadUiType(self.getUiPath())
        #@+<< define class Base_UI>>
        #@+node:leohag.20081203143921.23: *5* <<define class Base_UI>>
        class Base_UI(QtGui.QWidget, form_class):
            """Class to wrap QDesigner ui object and provide glue code to make it work."""

            def __init__(self, parent, *args):
                QtGui.QWidget.__init__(self, *args)
                self.leoParent = parent
                #@+<< inject action callbacks >>
                #@+node:leohag.20081206052547.18: *6* << inject action callbacks >>
                #@+at
                # for name, method in inspect.getmembers(self.leoParent):
                #     if name.startswith('doAction'):
                #         def doAction(self, name=name):
                #             getattr(self.leoParent, name)()
                #         setattr(self.__class__, name, doAction)
                # 
                #@-<< inject action callbacks >>
                self.setupUi(self)

            def chkBtnChanged(self):
                self.leoParent.chkBtnChanged()

            def closeEvent(self, event):
                self.leoParent.closeMe(event)
        #@-<< define class Base_UI>>
        return Base_UI
    #@+node:leohag.20081203143921.24: *5* getUiPath
    def getUiPath(self):

        return g.os_path_join(g.app.loadDir,'..','plugins', 'ScrolledMessage.ui')
    #@+node:ekr.20110319081254.14465: *4* updateIvars
    def updateIvars(self,kw):

        for k in list(kw.keys()):

            setattr(self, k, kw[k])

    #@+node:leohag.20081206052547.14: *3* Action Handlers (slots)
    #@+node:leohag.20081206052547.35: *4* File Menu
    #@+node:leohag.20081206052547.19: *5* _print
    def _print(self, printer):

        self.leo_ui.leo_webView.print_(printer)

    #@+node:leohag.20081206052547.21: *5* PageSetup
    def doActionPageSetup(self, checked):

        dialog = QtGui.QPageSetupDialog(getGlobalPrinter(), self.leo_ui)

        c.in_qt_dialog = True
        dialog.exec_()
        c.in_qt_dialog = False
    #@+node:leohag.20081206052547.15: *5* Print
    def doActionPrint(self, checked):

        self._print(getGlobalPrinter())
    #@+node:leohag.20081206052547.24: *5* PrintDialog
    def doActionPrintDialog(self, checked):

        d = QtGui.QPrintDialog(getGlobalPrinter(),self.leo_ui)
        
        c.in_qt_dialog = True
        val = d.exec_()
        c.in_qt_dialog = False

        if val == QtGui.QDialog.Accepted:
            self._print(getGlobalPrinter())
    #@+node:leohag.20081206052547.23: *5* PrintPreview
    def doActionPrintPreview(self, checked):

        d = QtGui.QPrintPreviewDialog(getGlobalPrinter(),self.leo_ui)
        d.connect(dialog, QtCore.SIGNAL('paintRequested(QPrinter*)'), self._print )
        
        c.in_qt_dialog = True
        d.exec_()
        c.in_qt_dialog = False
    #@+node:leohag.20081206052547.16: *5* Save
    def doActionSave(self):

        result = g.app.gui.runSaveFileDialog()

        if result:
            f = open(result, 'wb')
            f.write(self.convertMessage().encode('utf-8'))
            f.close()

    #@+node:leohag.20081206052547.27: *4* Outline Menu
    #@+node:leohag.20081206052547.28: *5* doActionOutlineShow
    def doActionOutlineShow(self, checked):

        #@+<< define msg >>
        #@+node:leohag.20081207032616.16: *6* << define msg >>
        msg = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
        <head>
        <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
        <title>
            %s
        </title>
        </head>
        <body>
        %s
        </body></html>
        """
        #@-<< define msg >>
        node = self.leo_ui.actionOutlineThisNode.isChecked()
        self._includeBody = self.leo_ui.actionOutlineIncludeBody.isChecked()
        self._expandFollowsTree  = self.leo_ui.actionOutlineExpandFollowsTree.isChecked()

        html = []
        html.append('<ol>')

        if node:
            root = self.c.currentPosition()
            self.doNextLevel(root, html)
        else:
            root = self.c.rootPosition()
            for pp in root.following_siblings():
                self.doNextLevel(pp, html)

        html.append('</ol>')
        label = self.c.frame.shortFileName() or 'untitled'
        msg = msg % (label, '\n'.join(html))

        g.doHook('scrolledMessage', c=self.c, name=self.name, msg=msg, label=label, flags='html')
    #@+node:leohag.20081207032616.17: *6* doNextLevel
    def doNextLevel(self, p, html):
        """" Recursivley proccess an outline node into an html list."""

        html.append('<li>')
        html.append(safe(p.headString())) 

        if self._includeBody:
            html.append('<div><pre>%s</pre></div>'%safe(p.bodyString()))

        if p.hasChildren() and (p.isExpanded() or not self._expandFollowsTree):

            html.append('<ol>')
            for item in p.children():
                self.doNextLevel(item, html)
            html.append('</ol>')

        html.append('</li>')


    #@+node:leohag.20081206052547.36: *4* Help Menu
    #@+node:leohag.20081206052547.17: *5* About
    def doActionAbout(self, checked):

        pass
    #@+node:leohag.20081207032616.24: *4* doActionRST3
    def doActionRST3(self,checked):
        
        # This is connected in leo\plugins\ScrolledMessage.ui
        
        if 0: # original code:
            
            pc = g.app.pluginsController
            rst3 = pc.getPluginModule('rst3')

            if not rst3:
                rst3 = pc.loadOnePlugin('rst3',verbose=True)
                if rst3:
                    g.es('rst3 loaded')
                    rst3.onCreate('tag',{'c':self.c})

            if rst3:
                controller = rst3.controllers.get(self.c)
                if controller:
                    g.doHook('scrolledMessage', c=self.c, msg='loading..', flags='text')
                    p,s = controller.writeNodeToString(ext='.html')
                    g.doHook('scrolledMessage', c=self.c, msg=s, flags='html')
        
        if 0: # New code, doesn't work.

            c = self.c
            g.doHook('scrolledMessage',c=c, msg='loading..',flags='text')
            p,s = c.rstCommands.writeNodeToString(ext='.html')
            g.doHook('scrolledMessage',c=c,msg=s,flags='html')
    #@+node:ekr.20110319081254.14463: *3* Callbacks
    #@+node:leohag.20081203205020.1: *4* closeMe
    def closeMe(self, visible):
        
        self.parent.onDialogClosing(self)
        
        if self.dock:
            self.dock.destroy()
    #@+node:leohag.20081203143921.13: *4* chkBtnClhanged & helper
    def  chkBtnChanged(self,silent=False):

        self.setFlagsFromControls()

        if not silent:
            self.showMessage()
    #@+node:leohag.20081203143921.11: *5* setFlagsFromControls
    def setFlagsFromControls(self):
        
        for flag, control in self.controls.items():
            self.controlFlags[flag] = bool(control.isChecked())
    #@+node:leohag.20081203143921.14: *3* showMessage & helpers
    def showMessage(self, show=True):

        s = self.convertMessage()
        self.leo_ui.leo_webView.setHtml(s)

        if show and self.dock:
            self.dock.show()
            toggle = self.dock.toggleViewAction()
            toggle.setChecked(True)
    #@+node:leohag.20081206052547.37: *4* convertMessage & helpers
    def convertMessage(self):
        
        '''Return self.msg converted to html.'''
        
        # g.trace(self.msg,g.callers())

        s = self.msg
        f = self.controlFlags
        if f['html']:
            if f['rst']:
                s = self.rstToHtml(s)
            if f['text']:
                s = self.textToHtml(s)
        else:
            s = self.textToHtml(s)

        return s
    #@+node:leohag.20081203143921.15: *5* rstToHtml
    def rstToHtml(self,s):
        
        if not docutils:
            return self.textToHtml(s)

        overrides = {
            'doctitle_xform': False,
            'initial_header_level': 1
        }

        try:
            parts = docutils.core.publish_parts(
                source=s,
                writer_name='html',
                settings_overrides=overrides
            )
        except Exception:
            g.es_print('scrolledMessage: rst conversion error', color='blue')
            return self.textToHtml(s)

        return parts['whole']
    #@+node:leohag.20081203143921.16: *5* textToHtml
    def textToHtml(self,s):

        return '<pre>%s<pre>' % safe(s)
    #@+node:leohag.20081203143921.17: *3* updateDialog & helper
    def updateDialog(self, kw):
        
        c = self.c
        
        if self.use_viewrendered:
            pc = c.viewrendered
            s=kw.get('msg')
            title = kw.get('short_title','').strip()
            pc.view('rst',s=s,title=title)
            return

        self.updateIvars(kw)

        if not g.isString(self.msg):
            self.msg = '<h2 style="color:red" >Illegal! Message must be string.</h2>'
            self.flags = 'html'

        # auto detect message type
        if not self.flags.strip():
            self.flags = 'text'
            if self.msg.startswith('rst:'):
                self.flags = 'rst html'
                self.msg = self.msg[4:]
            elif self.msg.startswith('<'):
                self.flags = 'html'

        flags = self.flags.split(' ')
        if 'rst' in flags and 'text' not in flags:
            flags.append('html')

        # update the ui check box controls
        ff = self.controlFlags 

        for flag in list(ff.keys()):
            if flag in flags:
                ff[flag] = True
            else:
                ff[flag] = False

        self.setControlsFromFlags()

        # update label
        w = self.leo_ui.leo_topLabel
        if self.label:
            w.setText(self.label)
            w.show()
        else:
            w.hide()

        #update title
        if self.dock:
            self.dock.setWindowTitle(self.title)
        self.showMessage()
    #@+node:leohag.20081203143921.12: *4* setControlsFromFlags
    def setControlsFromFlags(self):
        for flag, value in self.controlFlags.items():
            self.controls[flag].setChecked(bool(value))

    #@-others

#@-others
#@-leo
