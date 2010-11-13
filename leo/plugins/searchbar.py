#@+leo-ver=5-thin
#@+node:ekr.20101110095202.5852: * @file searchbar.py
""" Emulates the 'Find' panel in an iconBar."""

#@@language python
#@@tabwidth -4

__version__ = "0.1"
__plugin_name__ = 'Search Bar'
__plugin_id__ = 'Searchbar'

controllers = {}

#@+<< version history >>
#@+node:bobjack.20080510064957.115: ** << version history >>
#@+at
# 0.1 bobjack:
#     - initial version
#@-<< version history >>
#@+<< todo >>
#@+node:bobjack.20080510064957.116: ** << todo >>
#@+at
#@-<< todo >>
#@+<< imports >>
#@+node:bobjack.20080510064957.117: ** << imports >>
import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

import re
import sys
import os

Tk  = g.importExtension('Tkinter',pluginName=__name__,verbose=True,required=True)
Pmw = g.importExtension("Pmw",pluginName=__name__,verbose=True,required=True)

try:
    from PIL import Image
    from PIL import ImageTk
except ImportError:
    Image = ImageTk = None

import rClickBasePluginClasses as baseClasses
#@-<< imports >>
#@+<< required ivars >>
#@+node:bobjack.20080510064957.118: ** << required ivars >>
#@+at
# This is a list of ivars that the pluginController must have and the type of objects they are allowed to contain.
# 
#     (ivar, type)
# 
# where type may be a tuple and False indicates any type will do
# 
# The list is used by unit tests.
#@@c

requiredIvars = (

)
#@-<< required ivars >>

allowedButtonConfigItems = (
    'image', 'bg', 'fg', 'justify', 'padx', 'pady', 
    'relief', 'text', 'command', 'state',
)

#@+others
#@+node:bobjack.20080510064957.119: ** Module-level
#@+node:bobjack.20080510064957.120: *3* init
def init ():

    """Initialize and register plugin."""

    ok = Tk and g.app.gui.guiName() == "tkinter" and not g.app.unitTesting

    if ok:
        g.registerHandler('after-create-leo-frame', onCreate)
        g.registerHandler('close-frame', onClose)
        g.plugin_signon(__name__)

    return ok
#@+node:bobjack.20080510064957.121: *3* onPreCreate
def onPreCreate (tag, keys):
    """Handle before-create-leo-frame hook."""

    c = keys.get('c')
    if not (c and c.exists):
        return

    pass
#@+node:bobjack.20080510064957.105: *3* onCreate
def onCreate (tag, keys):
    """Handle after-create-leo-frame hook.

    Make sure the pluginController is created only once.
    """

    c = keys.get('c')
    if not (c and c.exists):
        return

    controller = controllers.get(c)
    if not controller:
        controllers[c] = controller = pluginController(c)
        controller.onCreate()

        c.theSearchbarController = controller



#@+node:bobjack.20080510064957.122: *3* onClose
def onClose (tag, keys):

    """Tell controller to clean up then destroy it."""

    c = keys.get('c')
    if not (c and c.exists):
        return

    controller = controllers.get(c)

    try: 
        del controllers[c]
    except KeyError:
        pass

    if not controller:
        return

    try:
        controller.onClose()
    finally:
        controller = None
#@+node:bobjack.20080516105903.12: ** class searchbarCommandClass
class searchbarCommandClass(baseClasses.pluginCommandClass):

    """Base class for all commands defined in the searchbar.py plugin."""

    pass
#@+node:bobjack.20080617071658.8: ** class SearchbarEntryWidget
class SearchbarEntryWidget(Tk.Frame, object):

    """A subclass of Tk.Frame that is parented on c.frame.top.



    """

    #@+others
    #@+node:bobjack.20080617071658.9: *3* __init__
    def __init__(self, c):

        self.c = c

        Tk.Frame.__init__(self, c.frame.top)

        self.deleteOnRightClick = False

        self.handler = c.searchCommands.findTabHandler

        self.textVar = Tk.StringVar()

        self.entry = g.app.gui.plainTextWidget(self, bg=self.bg,
            relief="flat", height=1, width=20, name='find-text')

        self.textVar.trace_variable('w', self.onTextChanged)

        self.button = c.frame.getIconButton(
            text=self.labelText,
            fg='blue',
            command=self.command, 
        )

        self.entry.pack(side='left')
        self.button.pack(in_=self,side='left')

        self.createBindings()

        self.leoDragHandle = self.button
    #@+node:bobjack.20080618081827.5: *4* createBindings
    def createBindings (self):

        c = self.c ; k = c.k

        def resetWrapCallback(event,self=self,k=k):
            self.handler.resetWrap(event)
            return k.masterKeyHandler(event)

        def rightClickCallback(event=None):
            val = k.masterClick3Handler(event, self.onRightClick)
            c.outerUpdate()
            return val

        def keyreleaseCallback(event=None):
            val = k.masterClickHandler(event, self.onTextChanged)
            c.outerUpdate()
            return val


        table = [
            ('<Button-1>',  k.masterClickHandler),
            ('<Double-1>',  k.masterClickHandler),
            ('<Button-3>',  rightClickCallback),
            #('<Double-3>',  k.masterClickHandler),
            ('<Key>',       resetWrapCallback),
            ('<Return>',    self.onReturn),
            #("<Escape>",    self.hideTab),
            ('<KeyRelease>', keyreleaseCallback)
        ]

        # table2 = (
            # ('<Button-2>',  self.frame.OnPaste,  k.masterClickHandler),
        # )

        # if c.config.getBool('allow_middle_button_paste'):
            # table.extend(table2)

        for event, callback in table:
            c.bind(self.entry,event,callback)
    #@+node:bobjack.20080617071658.12: *3* detachWidget
    def detachWidget(self):

        """Remove this widget from its containing iconBar."""

        try:
            bar = self.leoIconBar
        except:
            bar = None

        if bar:
            self.leoIconBar.removeWidget(self)

    removeWidget = detachWidget

    #@+node:bobjack.20080617071658.13: *3* deleteButton
    def deleteButton(self, event=None):

        """Delete the given button.

        This method does not actually delete the widget, override the method
        in a derived class to do that. 

        """

        self.detachWidget()


    #@+node:bobjack.20080617071658.14: *3* onTextChanged
    def onTextChanged(self, *args):

        c = self.c

        slave = getattr(self.handler, self.slave)

        text = self.entry.getAllText()

        slave.setAllText(text)

    #@+node:bobjack.20080617170156.14: *3* onRightClick
    def onRightClick(self, event):

        g.doHook('rclick-popup', c=self.c, event=event, context_menu=self.entry_menu)
    #@+node:bobjack.20080618081827.6: *3* onReturn
    def onReturn(self, event=None):

        c = self.c

        c.executeMinibufferCommand(self.command)

        #c.outerUpdate()
        return 'break'
    #@-others
#@+node:bobjack.20080617071658.25: ** class FindEntry
class FindEntry(SearchbarEntryWidget):

    labelText = 'Find'
    slave = 'find_ctrl'
    bg = 'honeydew1'

    command = 'find-next'

    context_menu='searchbar-find-button-menu'
    entry_menu = 'searchbar-find-entry-menu'

#@+node:bobjack.20080617071658.26: ** class ChangeEntry
class ChangeEntry(SearchbarEntryWidget):

    labelText = 'Change'
    slave = 'change_ctrl'
    bg = 'LavenderBlush1'

    command='change'

    context_menu = 'searchbar-change-button-menu'
    entry_menu = 'searchbar-change-entry-menu'
#@+node:bobjack.20080510064957.123: ** class pluginController
class pluginController(baseClasses.basePluginController):

    """A per commander controller."""

    commandPrefix = 'searchbar'

    #@+<< command list >>
    #@+node:bobjack.20080617163822.2: *3* << command list >>
    commandList = (
        'toggle-searchbar',
    )
    #@-<< command list >>
    #@+<< deault context menus >>
    #@+node:bobjack.20080617163822.3: *3* << deault context menus >>
    defaultContextMenus = {

        'searchbar-find-button-menu': [
            ('&', 'rclick-find-controls'),
        ],

        'searchbar-change-button-menu': [
            ('&', 'rclick-find-controls'),
        ],

        'searchbar-change-then-find-button-menu': [
            ('&', 'rclick-find-controls'),
        ],

        'searchbar-find-entry-menu': [
            ('&', 'edit-menu'),
        ],

        'searchbar-change-entry-menu': [
            ('&', 'edit-menu'),
        ]
    }
    #@-<< deault context menus >>

    #@+others
    #@+node:bobjack.20080510064957.125: *3* postCreate
    def postCreate(self):

        self.createBarWidgets()
    #@+node:bobjack.20080517142334.2: *3* createBarWidgets
    def createBarWidgets(self):

        c = self.c 

        try:
            bar = c.frame.iconBars['iconbar']
        except AttributeError:
            return

        self.toggleButton = btn = bar.getButton(
            text='SEARCHBAR',
            command='toggle-searchbar',
            icon='Tango/16x16/actions/kfind.png',
            balloonText='Toggle Visibility of the Searchbar',
            menu='searachbar-toggle-button-menu',
        )
        bar.addWidget(btn, index=1)

        self.bar = bar = c.frame.createIconBar(barName='searchbar')
        self.bar.hide()

        self.findeEntry = w = FindEntry(c)
        bar.addWidget(w)

        self.changeEntry = w = ChangeEntry(c)
        bar.addWidget(w)


        self.changeThenFindButton = btn = self.bar.getButton(
            text='Change Then Find',
            command='change-then-find',
            menu='searchbar-change-then-find-button-menu',
        )
        self.bar.addWidget(btn)

    #@+node:bobjack.20080510064957.130: *3* Generator Commands
    #@+node:bobjack.20080616185440.10: *4* toggle-searchbar
    class toggleSearchbarCommandClass(searchbarCommandClass):

        """Minibuffer command to toggle the visibility of the searchbar."""

        #@+others
        #@-others

        def doCommand(self, keywords):

            c = self.c

            phase = self.phase or 'minibuffer'

            bar = self.getNamedBar('searchbar')
            if not bar:
                g.trace('no searchbar')
                return

            if phase == 'generate':
                label = bar.visible and self.hideLabel or self.showLabel
                self.menu_table[:0] =  [(label % 'searchbar', 'toggle-searchbar')]

            elif phase in ['invoke', 'minibuffer']:
                bar.visible = not bar.visible
            else:
                g.trace('illegal phase')
                pass

    #@+node:bobjack.20080510064957.133: *3* Invocation Commands
    #@-others
#@-others
#@-leo
