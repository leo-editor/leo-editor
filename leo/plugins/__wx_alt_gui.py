#@+leo-ver=4-thin
#@+node:bob.20070910154126.2:@thin __wx_alt_gui.py
#@@language python
#@@tabwidth -4

#@<< docstring >>
#@+node:bob.20071231124159:<< docstring >>
"""A plugin to use wxWidgets as Leo's gui.

This version of wxLeo is being developed by

plumloco@hcoop.net


WARNING:
~~~~~~~~
__wx_alt_gui is incomplete and all features are subject to continuous
change. It should NOT be entrusted with anything important.


Priority is being given to getting this plugin right for linux, so it may
or may not work on windows at any particular time.

Requirements:
~~~~~~~~~~~~~

    + Python 2.4 plus
    + wxPython 2.8.7 plus
    + threading_colorizer pugin

Use:
~~~~

__wx_alt_gui.py should appear as the FIRST item in the list
of enabled plugins.

All other plugins, except those named below, should be
dissabled.

These plugins are believed to be compatible with __wx_alt_gui.py:

    + threading_colorizer.py (>=1.4)
    + plugins_menu.py (>=1.15)
    + leo_to_dhtml.py
    + mod_http.py
    + mod_scripting.py
    + mod_tempfname.py
    + datenodes.py
    + open_with.py
    + rst3.py
    + UNL.py
    + vim.py

Other plugins might also be compatible if they use only menus
and standard leo dialogs.

"""
#@-node:bob.20071231124159:<< docstring >>
#@nl

import re

__revision__ = re.sub(r'^\D+([\d\.]+)\D+$', r'\1', "$Revision: 1.13 $")

__version__ = '0.2.%s'% __revision__

__plugin_name__ = " wxPython GUI"

#@<< version history >>
#@+node:bob.20070813163858.2:<< version history >>
#@@nocolor
#@+at
# 
# 0.0 Forked by plumloco from EKR's original __wx_gui prototype.
# 
# 0.1 plumloco: replaced wx.Tree widget with custom tree widget.
# 
# 0.2 plumloco: transferred to leo cvs and started using new version
# numbering.
# 
# 0.2.1.12: plumloco:
# - require python 2.4
# - require wxPython >= 2.8.7
# - added support for threading_colorizer
# - changed to using colors.py for color information.
# - 'fixed' log pane bug (by using a bad hack)
# - added support for nav_butons
# - honors a few more settings
# - added support for headline icons
# - other stuff
# 
#@-at
#@-node:bob.20070813163858.2:<< version history >>
#@nl
#@<< bug list & to-do >>
#@+node:bob.20070813163332.52:<< bug list & to-do >>
#@@nocolor
"""
ToDo:

- Make compatible with plugins, at least don't crash if a
  plugin is loaded which is not compatible.

- Colorize edit pane

- Make widgets honour config fonts and colors.

- Fix so all leo hooks are called.

- Make multiple editors.

- Fix focus (which I totally trashed for some crazy reason).

- Add connecting lines to tee widget.

- Seek threapy ...


Bug list: (oh! to many to list!)

"""






#@-node:bob.20070813163332.52:<< bug list & to-do >>
#@nl

#@<< imports >>
#@+node:bob.20070813163332.62:<< imports >>
import leoGlobals as g
import leoPlugins

import leoColor
import leoCommands
import leoFind
import leoFrame
import leoGui
import leoKeys
import leoMenu
import leoNodes
import leoUndo

import leoChapters

import os
import string
import sys
import traceback

try:
    import wx
    import wx.richtext as richtext
    import wx.stc as stc

except ImportError:
    wx = None
    #g.es_print('wx_alt_gui plugin: can not import wxWidgets')

#@-node:bob.20070813163332.62:<< imports >>
#@nl

#@<< define module level functions >>
#@+node:bob.20070813163332.63:<< define module level functions >>
#@+others
#@+node:bob.20070813163332.64: init
def init():

    if g.app.unitTesting: # Not Ok for unit testing!
        return False

    global colors, getColor, getColorRGB, globalImages



    import colors


    getColor = colors.getColor
    getColorRGB = colors.getColorRGB

    globalImages = {}



    aList = wx.version().split('.')
    v1,v2,v3 = aList[0],aList[1],aList[2]

    if not g.CheckVersion ('%s.%s.%s' % (v1,v2,v3),'2.8.7'):
        g.es_print('\n\n\nwx_gui plugin requires wxPython 2.8.7 or later\n\n\n')
        return False

    ok = wx and not g.app.gui

    if ok:
        g.app.gui = wxGui()
        g.app.root = g.app.gui.createRootWindow()
        g.app.gui.finishCreate()
        g.plugin_signon(__name__)

    elif g.app.gui:
        s = "Can't install wxPython gui: previous gui installed"
        g.es_print(s,color="red")


    if ok:
        #@        <<overrides>>
        #@+node:bob.20070831090830:<< over rides >>

        # import leoAtFile

        # old = leoAtFile.atFile.openFileForReading

        # def wxOpenFileForReading(self,fileName,*args, **kw):
            # #g.trace( fileName)
            # old(self, fileName, *args, **kw)
            # #wx.SafeYield(onlyIfNeeded=True)

        # leoAtFile.atFile.openFileForReading = wxOpenFileForReading
        import leoEditCommands
        g.funcToMethod(getImage, leoEditCommands.editCommandsClass)
        #@-node:bob.20070831090830:<< over rides >>
        #@nl
        pass

    return ok
#@-node:bob.20070813163332.64: init
#@+node:bob.20070813163332.4:name2color
def name2color (name, default='white'):
    """Convert a named color into a wx.Color object.

    'name' must be an instance of string or a
    wx.Colour object, anything else is an error

    if name is already a wx.Colour object it

    """

    #g.trace(name, default)
    if not isinstance(name, basestring):
        assert name is None or isinstance(name, wx.Colour), "`name` must be string or wx.Colour"
        return name

    rgb = getColorRGB(name, default)
    #g.trace('rgb =', rgb)

    #assert rgb is not None, "`name` must be a valid color."
    if rgb is None:
        return None

    #g.trace('wxcolour =', wx.Colour(*rgb))
    return wx.Colour(*rgb)

#@-node:bob.20070813163332.4:name2color
#@+node:bob.20080105141717:getImage
def getImage (self,path):

    c = self.c

    image =  g.app.gui.getImage(c, path)

    if image is None:
        return None, None

    else:
        try:
            return image, image.GetHeight()
        except:
            pass

        return None, None
#@-node:bob.20080105141717:getImage
#@+node:bob.20070901052447:myclass
def myclass(self):
    try:
        return self.__class__.__name__
    except:
        return '< no class name! >'

#@-node:bob.20070901052447:myclass
#@+node:bob.20070902053906:test subs
def _(s):
     ts = type(s)
     return '\n\tText[%s]\n\ttype: %s' % (s[:20].replace('\n', '\\n'),ts)

def _split(i, s):
    return '[%s] [%s]' % (s[:i], s[i:])
#@-node:bob.20070902053906:test subs
#@+node:bob.20070910165627:onGlobalChar
def onGlobalChar(self, event):
    """All key chars come here wherever they originate."""

    c = self.c

    keycode = event.GetKeyCode()

    event.leoWidget = self
    keysym = g.app.gui.eventKeysym(event)

    if keysym:
        # g.trace(
            # '\n\treciever:', myclass(self),
            # '\n\tbase text: keysym:', repr(keysym),
            # '\n\tkeycode:',keycode
        # )
        result = c.k.masterKeyHandler(event,stroke=keysym)
        if not result:
            #g.trace('Skip()')
            event.Skip()
#@-node:bob.20070910165627:onGlobalChar
#@+node:bob.20070910192953:onRogueChar
def onRogueChar(self, event, type):
    g.trace(type, g.callers())

    onGlobalChar(self, event)
#@-node:bob.20070910192953:onRogueChar
#@-others
#@nonl
#@-node:bob.20070813163332.63:<< define module level functions >>
#@nl

if wx:

    #@    << constants >>
    #@+node:bob.20070907223746:<< constants >>
    if wx:
        HORIZONTAL = wx.HORIZONTAL
        VERTICAL = wx.VERTICAL

    #@-node:bob.20070907223746:<< constants >>
    #@nl

    #@    @+others
    #@+node:bob.20071229151620:tkFont.Font
    class tkFont(object):
        """class to emulate tkFont module"""

        class Font(object):
            """class to emulate tkFont.Font object."""

            #@        @+others
            #@+node:bob.20071229151620.1:__init__ (tkFont.Font)
            def __init__(self,*args, **kw):
                #print myclass(self), args, kw

                self.kw = kw




            #@-node:bob.20071229151620.1:__init__ (tkFont.Font)
            #@+node:bob.20071229153618:actual
            def actual(self, key=None):

                if not key:
                    return self.kw

                else:
                    return self.kw.get(key, None)

            #@-node:bob.20071229153618:actual
            #@+node:bob.20071229154443:configure
            def configure(self, **kw):

                self.kw.update(kw)
                #g.trace(self.kw)

            config = configure
            #@-node:bob.20071229154443:configure
            #@-others
    #@-node:bob.20071229151620:tkFont.Font
    #@+node:bob.20071229172621:Tk_Text
    class Tk_Text(object):

        #@    @+others
        #@+node:bob.20071229172621.1:__init__
        def __init__(self):

            pass

        #@-node:bob.20071229172621.1:__init__
        #@+node:bob.20071229174432:tag_add
        def tag_add(self, w, tag, start, stop):
            g.trace( w, tag, start, stop)
        #@nonl
        #@-node:bob.20071229174432:tag_add
        #@+node:bob.20071229174730:tag_ranges
        def tag_ranges(self, w, name):
            g.trace(w, name)
            return tuple()
        #@nonl
        #@-node:bob.20071229174730:tag_ranges
        #@+node:bob.20071229175418:tag_remove
        def tag_remove(self, w, tagName, x_i, x_j):
            g.trace( w, tagName, x_i, x_j)
        #@nonl
        #@-node:bob.20071229175418:tag_remove
        #@+node:bob.20071229172621.2:showcalls
        def showcalls(self, name, *args, **kw):
            g.trace( 'showcalls', name, args, kw)
        #@nonl
        #@-node:bob.20071229172621.2:showcalls
        #@+node:bob.20071229172621.3:__getattr__
        def __getattr__(self, name):

           return lambda *args, **kw : self.showcalls(name, *args, **kw)
        #@-node:bob.20071229172621.3:__getattr__
        #@-others
    #@-node:bob.20071229172621:Tk_Text
    #@+node:bob.20070813163332.136:=== TEXT WIDGETS ===
    #@<< baseTextWidget class >>
    #@+node:bob.20070813163332.137:<< baseTextWidget class >>

    class baseTextWidget (leoFrame.baseTextWidget):

        """The base class for all text wrapper classes."""

        #@    @+others
        #@+node:bob.20070813163332.138:__init__

        def __init__(self,
            leoParent,
            name=None,
            widget=None,
            baseClassName=None,
            bindchar=True,
            **keys
        ):

            self.name = name

            self.leoParent = leoParent
            self.ctrl = widget

            if baseClassName is None:
                baseClassName = self.__class__.__name__

            leoFrame.baseTextWidget.__init__(self,
                 leoParent.c,
                 baseClassName=baseClassName,
                 name=name,
                 widget=widget
            )

            self.virtualInsertPoint = None

            self.widget.leo_wrapper_object = self

            # Binding to lambda's allow default handlers to
            #  be overidden in derived classes.

            bind = self.widget.Bind

            bind(wx.EVT_CHAR,
                lambda event, self=self: onGlobalChar( self, event)
            )

            bind(wx.EVT_SET_FOCUS,
                lambda event: self.onGlobalGainFocus(event)
            )

            bind(wx.EVT_KILL_FOCUS,
                lambda event: self.onGlobalLoseFocus(event)
            )

            self.__repr__ = self.__str__ = lambda : myclass(self) + str(id(self))



        #@-node:bob.20070813163332.138:__init__
        #@+node:bob.20070902072600:setWidget
        #@-node:bob.20070902072600:setWidget
        #@+node:bob.20070823072419:getName

        def getName(self):
            return self.name or self.widget.GetName()

        GetName = getName
        #@-node:bob.20070823072419:getName
        #@+node:bob.20070901042726:== Focus ==
        #@+node:bob.20070826134115:onGlobalGainFocus

        def onGlobalGainFocus(self, event):
            if self.onGainFocus(event):
                return
            self.c.focusManager.gotFocus(self, event)


        #@-node:bob.20070826134115:onGlobalGainFocus
        #@+node:bob.20070901042726.1:onGainFocus

        def onGainFocus(self, event):
            return
        #@nonl
        #@-node:bob.20070901042726.1:onGainFocus
        #@+node:bob.20070901042726.2:onGlobalLoseFocus

        def onGlobalLoseFocus(self, event):
            if self.onLoseFocus(event):
                return
            self.c.focusManager.lostFocus(self, event)
        #@nonl
        #@-node:bob.20070901042726.2:onGlobalLoseFocus
        #@+node:bob.20070901042726.3:onLoseFocus

        def onLoseFocus(self, event):
            return
        #@nonl
        #@-node:bob.20070901042726.3:onLoseFocus
        #@-node:bob.20070901042726:== Focus ==
        #@+node:bob.20070831045021:clear

        def clear(self):
            """Remove all text from the text widget."""

            self._setAllText('')
        #@-node:bob.20070831045021:clear
        #@+node:plumloco.20071211050853:after_idle
        def after_idle(self, *args, **kw):
            wx.CallAfter(*args, **kw)
        #@nonl
        #@-node:plumloco.20071211050853:after_idle
        #@+node:bob.20071229161941:after

        def after(self, *args, **kw):
            wx.CallLater(*args, **kw)
        #@-node:bob.20071229161941:after
        #@+node:bob.20071231142747:setBackgroundColor & SetBackgroundColour
        def setBackgroundColor (self,color):

            return self._setBackgroundColor(name2color(color))


        #@-node:bob.20071231142747:setBackgroundColor & SetBackgroundColour
        #@-others
    #@-node:bob.20070813163332.137:<< baseTextWidget class >>
    #@nl

    #@+others
    #@+node:bob.20070818175928.3:plainTextWidget (baseTextWidget)
    class plainTextWidget (baseTextWidget):

        """The base class for all wxTextCtrl wrappers."""

        #@    @+others
        #@+node:bob.20070818175928.4:__init__
        def __init__ (self, leoParent,
            parent=None,
            multiline=True,
            widget=None,
            name='<unknown plainTextWidget>',
            bindchar=True,
            **keys
        ):

            assert parent or widget, \
            "If a widget is not provided, a parent must be provided so that a widget can be created."


            if 'style' in keys:
                style = keys['style']
            else:
                style = 0

            keys['style'] = style | g.choose(multiline,wx.TE_MULTILINE,0) | wx.WANTS_CHARS

            # Create a gui widget if one is not provided.
            if widget:
                self.widget = widget
            else:
                self.widget = wx.TextCtrl(parent, id=-1, name=name, **keys)


            baseTextWidget.__init__(self, leoParent, name=name, widget=self.widget, bindchar=bindchar)


        #@-node:bob.20070818175928.4:__init__
        #@+node:bob.20070818175928.5:bindings (TextCtrl)

        # Interface non gui text control  methods to physical wx.TextCtrl methods.

        def _appendText(self,s):            return self.widget.AppendText(s)
        def _get(self,i,j):                 return self.widget.GetRange(i,j)
        def _getAllText(self):              return self.widget.GetValue()
        def _getFocus(self):                return self.widget.FindFocus()
        def _getInsertPoint(self):          return self.widget.GetInsertionPoint()
        def _getLastPosition(self):         return self.widget.GetLastPosition()
        def _getSelectedText(self):         return self.widget.GetStringSelection()
        def _getSelectionRange(self):       return self.widget.GetSelection()
        def _hitTest(self,pos):             return self.widget.HitTest(pos)

        def _insertText(self,i,s):
            self.setInsertPoint(i)
            return self.widget.WriteText(s)

        def _scrollLines(self,n):           return self.widget.ScrollLines(n)
        def _see(self,i):                   return self.widget.ShowPosition(i)
        def _setAllText(self,s):
            return self.widget.SetValue(s)
        def _setBackgroundColor(self,color): return self.widget.SetBackgroundColour(color)
        def _setFocus(self):                return self.widget.SetFocus()
        def _setInsertPoint(self,i):        return self.widget.SetInsertionPoint(i)
        def _setSelectionRange(self,i,j):   return self.widget.SetSelection(i,j)

        def _getYScrollPosition(self):      return 0,0 # Could also return None.
        def _setYScrollPosition(self,i):    pass
        #@nonl
        #@-node:bob.20070818175928.5:bindings (TextCtrl)
        #@-others
    #@nonl
    #@-node:bob.20070818175928.3:plainTextWidget (baseTextWidget)
    #@+node:bob.20070813163332.146:stcTextWidget (baseTextWidget)

    class stcTextWidget (stc.StyledTextCtrl, baseTextWidget):

        '''A wrapper for wx.StyledTextCtrl.'''

        # The signatures of tag_add and insert are different from the Tk.Text signatures.
        __pychecker__ = '--no-override' # suppress warning about changed signature.

        #@    @+others
        #@+node:bob.20070813163332.8:__init__

        def __init__ (self, leoParent,
            parent=None,
            widget=None,
            name='body',
            *args, **keys
        ):

            stc.StyledTextCtrl.__init__(self, parent, -1)
            baseTextWidget.__init__(self, leoParent, name, self )


            self.leo_styles = {}
            self.leo_tags = {}

            self.CmdKeyClearAll()
            self.SetUndoCollection(False)
            self.EmptyUndoBuffer()

            self.SetViewWhiteSpace(False)
            self.SetWrapMode(stc.STC_WRAP_NONE)

            self.SetEOLMode(stc.STC_EOL_LF)
            self.SetViewEOL(False)

            self.UsePopUp(False)

            self.SetStyleBits(7)


            self.initStc()



        #@-node:bob.20070813163332.8:__init__
        #@+node:bob.20070911142138:__str__
        def __str__(self):
            return myclass(self) + str(id(self))


        __repr__ = __str__
        #@-node:bob.20070911142138:__str__
        #@+node:bob.20070827204727:initStc
        # Code copied from wxPython demo.

        def initStc (self):

            w = self.widget
            use_fold = False

            # Set left and right margins
            w.SetMargins(10,10)
            w.SetMarginWidth(1,0)
            # Indentation and tab stuff
            w.SetIndentationGuides(False) # Show indent guides

            # Global default style
            if wx.Platform == '__WXMSW__':
                w.StyleSetSpec(stc.STC_STYLE_DEFAULT,
                    'fore:#000000,back:#FFFFFF,face:Courier New,size:11')
            elif wx.Platform == '__WXMAC__':
                # TODO: if this looks fine on Linux too, remove the Mac-specific case
                # and use this whenever OS != MSW.
                w.StyleSetSpec(stc.STC_STYLE_DEFAULT,
                    'fore:#000000,back:#FFFFFF,face:Courier')
            else:
                w.StyleSetSpec(stc.STC_STYLE_DEFAULT,
                    'fore:#000000,back:#FFFFFF,face:Courier,size:13')

            # Set leo default styles
            default = stc.STC_STYLE_DEFAULT


            # Clear styles and revert to default.
            w.StyleClearAll()

            # Following style specs only indicate differences from default.
            # The rest remains unchanged.

            # Line numbers in margin
            w.StyleSetSpec(stc.STC_STYLE_LINENUMBER, 'fore:#000000,back:#99A9C2')

            # Highlighted brace
            w.StyleSetSpec(stc.STC_STYLE_BRACELIGHT,'fore:#00009D,back:#FFFF00')

            # Unmatched brace
            w.StyleSetSpec(stc.STC_STYLE_BRACEBAD,'fore:#00009D,back:#FF0000')

            # Indentation guide
            w.StyleSetSpec(stc.STC_STYLE_INDENTGUIDE, "fore:#CDCDCD")

            # Caret color
            w.SetCaretForeground(name2color("BLUE"))

            # Selection background
            w.SetSelBackground(True,
                wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT))

            # Selection foreground
            w.SetSelForeground(True,
                wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT))

        #@-node:bob.20070827204727:initStc
        #@+node:bob.20070813163332.151:Wrapper methods
        #@+node:bob.20070813163332.152:bindings (stc)
        # Specify the names of widget-specific methods.
        # These particular names are the names of wx.TextCtrl methods.



        def _appendText(self,s):
            #g.trace('stc:', _(s))
            self.widget.AppendText(s)
            #print '\t', _(self.widget.Text)

        def _get(self,i,j):
            #g.trace( 'i: %s j:%s' %(i, j))
            py = self.toStcIndex
            w = self.widget
            s = w.Text
            ii, jj = py(i,s),py(j,s)
            #print '\tii=', ii, ' jj=', jj
            result = self.widget.GetTextRange(ii, jj)
            #print '\n\t', type(result), 'len:', len(result)
            #print _(result)
            return result

        def _getAllText(self):
            text = self.widget.Text
            #g.trace(_(text))
            #print '\t', g.callers()
            return text

        def _getFocus(self):
            #g.trace()
            result = wx.Window.FindFocus()
            #g.trace('stc:',result)
            return result

        def _getInsertPoint(self):
            w = self.widget
            text = w.Text
            # print
            # print '---------------------'
            # g.trace(type(w.Text), type(w.TextUTF8), type(w.TextRaw))
            # g.trace(w.CurrentPos, text)
            result = self.fromStcIndex(w.CurrentPos, text)
            # g.trace(result, '[%s] [%s]' % (text[:result], text[result:]))
            # print '---------------------'
            # print
            return result

        def _getLastPosition(self):
            result = len(self.widget.Text)
            #g.trace('stc:', result)
            return result

        def _getSelectedText(self):
            result = self.widget.SelectedText
            #g.trace('stc:', _(result))
            return result


        def _getSelectionRange(self):

            # g.trace()

            topy = self.fromStcIndex
            w = self.widget
            wt = w.Text
            start, end = w.Selection
            return topy(start, wt), topy(end, wt)


        def _hitTest(self,pos):
            # g.trace()
            assert False, 'oops'
            #return self.widget.PositonFromPoint(wx.Point(pos))

        def _insertText(self,i,s):
            #g.trace()
            assert False, 'oops'

        def _scrollLines(self,n):
             g.trace('stc:', n)
             self.widget.ScrollToLine(n) ##FIXME ??

        def _see(self,i):
            assert False, 'oops'

        def _setAllText(self,s):
            #g.trace('stc:\t', _(s))
            self.widget.SetText(s)
            #print '\t', _(self.widget.Text)

        def _setBackgroundColor(self,color):
            #g.trace('stc:')
            return self.widget.SetBackgroundColour(color)

        def _setFocus(self):
            #g.trace('stc:')
            self.widget.SetFocus()

        def _setInsertPoint(self,i):
            assert False, 'oops'

        def _setSelectionRange(self,i,j):
            assert False, 'oops'

        def _getYScrollPosition(self):
            w = self.widget
            x = w.XOffset
            y = w.FirstVisibleLine
            #g.trace(x, y)
            return (y,99)

        def _setYScrollPosition(self,i):

            w = self.widget
            wantfirst = i

            first = w.FirstVisibleLine

            #print
            #g.trace( '\n\tHave FirstVisible:', first)
            #print '\tWant FirstVisible:', wantfirst

            #print
            w.LineScroll(0, wantfirst - first)
            #print '\tLines to scroll:', wantfirst - first
            #print '\tNew FirstVisible:', w.FirstVisibleLine
            #print
        #@-node:bob.20070813163332.152:bindings (stc)
        #@+node:bob.20070813163332.153:Overrides of baseTextWidget methods
        #@+node:bob.20070901213413:toStcIndex
        def toStcIndex (self, i, s):

            """Convert index into an integer value suitable for use with the stc control."""

            #g.trace('\n\t iput[%s] data-type: %s' %(i, type(s)))


            if i is None:
                return 0


            if isinstance(i, basestring):
                try:
                    row, col = i.split('.')
                    i = g.convertRowColToPythonIndex(s, int(row), int(col))
                    #print('\t  i converted:', i)
                except ValueError:
                    if i == 'end':
                        i = len(s)

            #print '\n\tChar-codes: [', ' | '.join([str(ord(ch)) for ch in s]), ']'

            result =  len(s[:i].encode('utf8'))

            #print '\n\t result', result
            return result

        def fromStcIndex(self, i, s):
            """Translate from stc positions to python positions.

            s must obviously be a unicode string .
            """
            #g.trace('\n\tencoding:', type(s), i)
            try:
                result = s.encode('utf8')[:i]
                #print 'YAY encoded ok: type is ', type(result)
                #print '\n\t len:', len(result),
                #print '\n\t chars:[',  ' | '.join([str(ord(ch)) for ch in result]), ']'
            except:
                print 'encoding error ============================'
                print g.callers()

            try:
                result = result.decode('utf8')
                #print 'YAY DECODING ok: type is ', type(result)
                #print '\n\t len:', len(result),
                #print '\n\t chars:[',  ' | '.join([str(ord(ch)) for ch in result]), ']'
            except:
                print 'decoding error #######################################'

            result = len(result)
            #print '\n\tinput:%s result:%s'%(i, result)
            return result

        #@-node:bob.20070901213413:toStcIndex
        #@+node:bob.20070903082144:appendText
        def appendText (self,s):

            #g.trace('stc:', _(s))
            self.widget.AppendText(s)
            #print '\t', _(self.widget.Text)

        #@-node:bob.20070903082144:appendText
        #@+node:bob.20070903082228:delete
        def delete(self,i,j=None):

            w = self.widget
            py = self.toStcIndex

            s = w.Text

            if j is None:
                j = i+ 1

            w.SetSelection(py(i,s), py(j,s))
            w.DeleteBack()
        #@-node:bob.20070903082228:delete
        #@+node:bob.20070813163332.154:see & seeInsertPoint


        def see(self, i):

            #g.trace( i, g.callers(20))

            w = self.widget

            s = w.Text

            #top = w.FirstVisibleLine
            #line = w.LineFromPosition(w.CurrentPos)

            #g.trace( '\n\ttop:', w.FirstVisibleLine)
            #print '\tcurrent line:', w.LineFromPosition(w.CurrentPos)


            ii = self.toStcIndex(i, s)
            #print '\ttarget line:', w.LineFromPosition(ii)
            w.ScrollToLine(w.LineFromPosition(ii))

        def seeInsertPoint(self):

            #g.trace()
            #w = self.widget
            #w.ScrollToLine(w.LineFromPosition(w.CurrentPos))
            pass

        #@-node:bob.20070813163332.154:see & seeInsertPoint
        #@+node:bob.20070813163332.155:insert
        def insert(self,i, s):

            topy = self.fromStcIndex

            '''Override the baseTextWidget insert method.'''

            #print

            #g.trace('py-index:', i, 'insert[%s]'%s)# g.callers())

            #print '\t\t', g.callers()

            w = self.widget

            wt = w.Text
            ii = self.toStcIndex(i, wt)
            # print '\n\tbefore insert'
            # print '\tstc-index', topy(ii, wt), ii
            # print '\tw.Text ', _split(topy(ii, wt), wt)

            w.InsertText(ii, s)

            #wt = w.Text
            # print '\n\tafter insert'
            # print '\tstc-index', topy(ii, wt), ii
            # print '\tw.Text ', _split(topy(ii, wt), wt)



            #w.SetCurrentPos(i )#+ len(s.encode('utf8')))

            w.GotoPos(ii)
            #wt = w.Text
            # print '\n\twith new caret position'
            # print '\tstc-index', topy(ii, wt), ii
            # print '\tw.Text ', _split(topy(ii, wt), wt)


            #w.ScrollToLine(w.LineFromPosition(ii))

            #w.widget.SetCaretWidth(2)
            #w.widget.SetCaretForeground(wx.RED)
            #g.trace(w.widget.EnsureCaretVisible())
        #@-node:bob.20070813163332.155:insert
        #@+node:bob.20070813163332.156:stc.setInsertPoint
        def setInsertPoint (self,i):

            """Clear selection, set insertion point and ensure it is visible."""

            #g.trace(i)


            w = self.widget
            ii = self.toStcIndex(i, w.Text)

            #print
            #g.trace ('\n\t point:%s, Text[%s]'%(ii, _(w.Text)))


            w.GotoPos(ii)

            #wt = w.Text
            #ii = w.CurrentPos
            #topy = self.fromStcIndex
            # print '\n\tstc-index', topy(ii, wt), ii
            # print '\tw.Text ', _split(topy(ii, wt), wt)
        #@nonl
        #@-node:bob.20070813163332.156:stc.setInsertPoint
        #@+node:bob.20070813163332.157:stc.setSelectionRange

        def setSelectionRange (self,i,j,insert=None):

            __pychecker__ = '--no-argsused' #  insert not used.


            #g.trace(g.callers(20))

            py = self.toStcIndex

            w = self.widget ;

            s = w.Text

            ii, jj, stcInsert = py(i, s), py(j,s), py(insert, s)

            w.virtualInsertPoint = None
            if insert is not None:
                w.virtualInsertPoint = insert

            #print
            #g.trace( '\n\tInput:', i, j, insert)
            #print '\tconverted:', ii, jj, stcInsert

            # Both parts of the selection must be set at once.
            if insert in (None, j):
                w.SetSelection(ii, jj)
                w.SetCurrentPos(jj)
            else:
                w.SetSelection(jj,ii)
                w.SetCurrentPos(ii)

            #print
            #print '\tNew selectio:', w.Selection
            #print '\tNew position:', w.CurrentPos

            # g.trace(self,'stc,new sel',w.widget.GetCurrentPos(),'new range',w.widget.GetSelection())
        #@-node:bob.20070813163332.157:stc.setSelectionRange
        #@+node:bob.20070813163332.159:xyToGui/PythonIndex (to do)
        def xyToPythonIndex (self,x,y):

            w = self

            data = w.widget.PositionFromPoint(wx.Point(x,y))
            #g.trace('data',data)

            return 0 ### ?? Non-zero value may loop.
        #@-node:bob.20070813163332.159:xyToGui/PythonIndex (to do)
        #@+node:bob.20071229180021:tags (to-do)
        #@+node:bob.20071229180021.1:mark_set (to be removed)
        def mark_set(self,markName,i):

            g.trace('stc', markName, i)
            return

            w = self
            i = self.toStcIndex(i)

            ### Tk.Text.mark_set(w,markName,i)
        #@-node:bob.20071229180021.1:mark_set (to be removed)
        #@+node:bob.20071230062331:init_colorizer
        def init_colorizer(self, col):

            #g.trace()

            col.removeOldTags = lambda *args: self.ClearDocumentStyle()

            col.removeAllTags = lambda  : self.ClearDocumentStyle()
        #@-node:bob.20071230062331:init_colorizer
        #@+node:bob.20071230065317:putNewTags
        def putNewTags(self, col, addList, trace, verbose):

            w = col.w

            s = col.s

            for i, j, tagName in addList:

                ii = len(s[:i].encode('utf8'))
                num = len(s[i:j].encode('utf8'))

                if trace and verbose:
                    g.trace('add', tagName, i, j, s[i:j])

                w.StartStyling(ii, 127)
                w.SetStyling(num, w.leo_styles[tagName])

            return True

        #@-node:bob.20071230065317:putNewTags
        #@+node:bob.20071229180021.2:tag_add
        # The signature is slightly different than the Tk.Text.insert method.

        def tag_add(self, tagName,i,j=None,*args):

            g.trace('stc', tagName, i, j, args)

            return

            if j is None:
                j = i + 1

            ii = self.toStcIndex(i)
            jj = self.toStcIndex(j or i +1)


            style = self.leo_styles.get(tagName, None)

            if style is not None:
                g.trace('stc',i,j,tagName)
                #self.textBaseClass.SetStyle(w, ii, jj, style)
        #@-node:bob.20071229180021.2:tag_add
        #@+node:bob.20071229190049:start_tag_configure
        def start_tag_configure(self):
            #g.trace()
            self.leo_tags = {}
            self.leo_styles = {}
        #@nonl
        #@-node:bob.20071229190049:start_tag_configure
        #@+node:bob.20071229180021.3:tag_configure
        def tag_configure (self,tagName,**kw):

            #g.trace('stc', tagName, kw)

            try:
                thistag = self.leo_tags[tagName]
            except KeyError:
                thistag = self.leo_tags[tagName] = {}

            thistag.update(kw)

        tag_config = tag_configure
        #@-node:bob.20071229180021.3:tag_configure
        #@+node:bob.20071229190049.1:end_tag_configure
        def end_tag_configure(self):

            w = self

            # g.trace()

            w.StyleClearAll()

            styleNumber = 0
            for tagName, tagData in self.leo_tags.iteritems():
                styleNumber += 1
                if styleNumber == 32:
                    styleNumber += 8

                w.leo_styles[tagName] = styleNumber

                for item, value in tagData.iteritems():
                    #g.es(item, value, color='darkgreen')

                    if item == ('font'):
                        for fontitem, fontvalue in value.actual().iteritems():

                            if fontitem == 'family':
                                w.StyleSetFaceName(styleNumber, fontvalue)

                            elif fontitem == 'size':
                                w.StyleSetSize(styleNumber, int(fontvalue))

                            elif fontitem == 'underline':
                                w.StyleSetUnderline(styleNumber, fontvalue)
                                #print 'font-underline value: ', fontvalue

                            elif fontitem ==  'weight':
                                w.StyleSetBold(styleNumber, fontvalue == 'bold')

                            elif fontitem == 'slant':
                                w.StyleSetItalic(styleNumber, fontvalue=='italic')

                    elif item == 'foreground':

                        if not value:
                            #print 'no foreground color: ', tagName
                            continue

                        color = getColor(value, None)
                        if value is None:
                            #print 'unknown color [%s]' % color
                            continue
                        w.StyleSetForeground(styleNumber, color)

                    elif item in ('background', 'bg'):
                        item = 'background'
                        if not value:
                            #print 'no background color for: %s' % tagName
                            continue

                        color = getColor(value, None)
                        if value is None:
                            #print g.es('unknown color [%s]' % color)
                            continue
                        w.StyleSetBackground(styleNumber, color)

                    elif item == 'underline':
                        w.StyleSetUnderline(styleNumber, value)

                    else:
                        #print('unknown style, %s, %s' % (item, value))
                        pass

            #print 'no of tags: ', len( self.leo_styles)
        #@-node:bob.20071229190049.1:end_tag_configure
        #@+node:bob.20071229180021.5:tag_delete (NEW)
        def tag_delete (self,tagName,*args,**keys):
            #g.trace('stc', tagName,args,keys)
            pass
        #@nonl
        #@-node:bob.20071229180021.5:tag_delete (NEW)
        #@+node:bob.20071229180021.6:tag_names
        def tag_names (self, *args):
            #g.trace('stc', args)
            return []
        #@-node:bob.20071229180021.6:tag_names
        #@+node:bob.20071229180021.7:tag_ranges
        def tag_ranges(self,tagName):
            #g.trace('stc', tagName)
            return tuple() ###

            w = self
            aList = Tk.Text.tag_ranges(w,tagName)
            aList = [w.toPythonIndex(z) for z in aList]
            return tuple(aList)
        #@-node:bob.20071229180021.7:tag_ranges
        #@+node:bob.20071229180021.8:tag_remove
        def tag_remove(self,tagName,i,j=None,*args):
            #g.trace('stc', tagName, i, j, args)
            return

            w = self

            if j is None:
                j = i + 1

            ii = self.toStcIndex(i)
            jj = self.toStcIndex(j)

            #return ### Not ready yet.

            style = w.leo_styles.get(tagName)

            if style is not None:
                g.trace('stc',i,j,tagName)
                #w.textBaseClass.SetStyle(w,ii,jj,style)
        #@-node:bob.20071229180021.8:tag_remove
        #@-node:bob.20071229180021:tags (to-do)
        #@-node:bob.20070813163332.153:Overrides of baseTextWidget methods
        #@+node:bob.20070903081639:Wrapper methods (widget-independent)
        # These methods are widget-independent because they call the corresponding _xxx methods.

        if 0:
            #@    @+others
            #@+node:bob.20070903081639.1:appendText
            def appendText (self,s):

                w = self
                w._appendText(s)
            #@-node:bob.20070903081639.1:appendText
            #@+node:bob.20070903081639.2:bind
            def bind (self,kind,*args,**keys):

                w = self

                pass # g.trace('wxLeoText',kind,args[0].__name__)
            #@nonl
            #@-node:bob.20070903081639.2:bind
            #@+node:bob.20070903081639.3:clipboard_clear & clipboard_append
            def clipboard_clear (self):

                g.app.gui.replaceClipboardWith('')

            def clipboard_append(self,s):

                s1 = g.app.gui.getTextFromClipboard()

                g.app.gui.replaceClipboardWith(s1 + s)
            #@-node:bob.20070903081639.3:clipboard_clear & clipboard_append
            #@+node:bob.20070903081639.4:delete
            def delete(self,i,j=None):

                w = self
                i = w.toPythonIndex(i)
                if j is None: j = i+ 1
                j = w.toPythonIndex(j)

                # g.trace(i,j,len(s),repr(s[:20]))
                s = w.getAllText()
                w.setAllText(s[:i] + s[j:])
            #@-node:bob.20070903081639.4:delete
            #@+node:bob.20070903081639.5:deleteTextSelection
            def deleteTextSelection (self):

                w = self
                i,j = w._getSelectionRange()
                if i == j: return

                s = w._getAllText()
                s = s[i:] + s[j:]

                # g.trace(len(s),repr(s[:20]))
                w._setAllText(s)
            #@-node:bob.20070903081639.5:deleteTextSelection
            #@+node:bob.20070903081639.6:event_generate (baseTextWidget)
            def event_generate(self,stroke):

                w = self ; c = self.c ; char = stroke

                # Canonicalize the setting.
                stroke = c.k.shortcutFromSetting(stroke)

                # g.trace('baseTextWidget','char',char,'stroke',stroke)

                class eventGenerateEvent:
                    def __init__ (self,c,w,char,keysym):
                        self.c = c
                        self.char = char
                        self.keysym = keysym
                        self.leoWidget = w
                        self.widget = w

                event = eventGenerateEvent(c,w,char,stroke)
                c.k.masterKeyHandler(event,stroke=stroke)
            #@-node:bob.20070903081639.6:event_generate (baseTextWidget)
            #@+node:bob.20070903081639.7:flashCharacter (to do)
            def flashCharacter(self,i,bg='white',fg='red',flashes=3,delay=75): # tkTextWidget.

                w = self

                return ###

                def addFlashCallback(w,count,index):
                    # g.trace(count,index)
                    i,j = w.toPythonIndex(index),w.toPythonIndex(index+1)
                    Tk.Text.tag_add(w,'flash',i,j)
                    Tk.Text.after(w,delay,removeFlashCallback,w,count-1,index)

                def removeFlashCallback(w,count,index):
                    # g.trace(count,index)
                    Tk.Text.tag_remove(w,'flash','1.0','end')
                    if count > 0:
                        Tk.Text.after(w,delay,addFlashCallback,w,count,index)

                try:
                    Tk.Text.tag_configure(w,'flash',foreground=fg,background=bg)
                    addFlashCallback(w,flashes,i)
                except Exception:
                    pass ; g.es_exception()
            #@nonl
            #@-node:bob.20070903081639.7:flashCharacter (to do)
            #@+node:bob.20070903081639.8:getFocus (baseText)
            def getFocus (self):

                w = self
                w2 = w._getFocus()
                # g.trace('w',w,'focus',w2)
                return w2

            findFocus = getFocus
            #@-node:bob.20070903081639.8:getFocus (baseText)
            #@+node:bob.20070903081639.9:get
            def get(self,i,j=None):

                w = self

                i = w.toPythonIndex(i)
                if j is None: j = i+ 1
                j = w.toPythonIndex(j)

                s = w._get(i,j)
                return g.toUnicode(s,g.app.tkEncoding)
            #@-node:bob.20070903081639.9:get
            #@+node:bob.20070903081639.10:getAllText
            def getAllText (self):

                w = self

                s = w._getAllText()
                return g.toUnicode(s,g.app.tkEncoding)
            #@-node:bob.20070903081639.10:getAllText
            #@+node:bob.20070903081639.11:getInsertPoint (baseText)
            def getInsertPoint(self):

                w = self
                i = w._getInsertPoint()

                # g.trace(self,'baseWidget: i:',i,'virtual',w.virtualInsertPoint)

                if i is None:
                    if w.virtualInsertPoint is None:
                        i = 0
                    else:
                        i = w.virtualInsertPoint

                w.virtualInsertPoint = i

                return i
            #@-node:bob.20070903081639.11:getInsertPoint (baseText)
            #@+node:bob.20070903081639.12:getName & GetName
            def GetName(self):
                return self.name

            getName = GetName
            #@nonl
            #@-node:bob.20070903081639.12:getName & GetName
            #@+node:bob.20070903081639.13:getSelectedText
            def getSelectedText (self):

                w = self
                s = w._getSelectedText()
                return g.toUnicode(s,g.app.tkEncoding)
            #@-node:bob.20070903081639.13:getSelectedText
            #@+node:bob.20070903081639.14:getSelectionRange (baseText)
            def getSelectionRange (self,sort=True):

                """Return a tuple representing the selected range of the widget.

                Return a tuple giving the insertion point if no range of text is selected."""

                w = self

                sel = w._getSelectionRange() # wx.richtext.RichTextCtrl returns (-1,-1) on no selection.
                if len(sel) == 2 and sel[0] >= 0 and sel[1] >= 0:
                    #g.trace(self,'baseWidget: sel',repr(sel),g.callers(6))
                    i,j = sel
                    if sort and i > j: i,j = j,i
                    return sel
                else:
                    # Return the insertion point if there is no selected text.
                    i =  w._getInsertPoint()
                    #g.trace(self,'baseWidget: i',i,g.callers(6))
                    return i,i
            #@-node:bob.20070903081639.14:getSelectionRange (baseText)
            #@+node:bob.20070903081639.15:getYScrollPosition
            def getYScrollPosition (self):

                 w = self
                 return w._getYScrollPosition()
            #@-node:bob.20070903081639.15:getYScrollPosition
            #@+node:bob.20070903081639.16:getWidth
            def getWidth (self):

                '''Return the width of the widget.
                This is only called for headline widgets,
                and gui's may choose not to do anything here.'''

                w = self
                return 0
            #@-node:bob.20070903081639.16:getWidth
            #@+node:bob.20070903081639.17:hasSelection
            def hasSelection (self):

                w = self
                i,j = w.getSelectionRange()
                return i != j
            #@-node:bob.20070903081639.17:hasSelection
            #@+node:bob.20070903081639.18:insert
            # The signature is more restrictive than the Tk.Text.insert method.

            def insert(self,i,s):

                w = self
                i = w.toPythonIndex(i)
                # w._setInsertPoint(i)
                w._insertText(i,s)
            #@-node:bob.20070903081639.18:insert
            #@+node:bob.20070903081639.19:indexIsVisible
            def indexIsVisible (self,i):

                return False # Code will loop if this returns True forever.
            #@nonl
            #@-node:bob.20070903081639.19:indexIsVisible
            #@+node:bob.20070903081639.20:replace
            def replace (self,i,j,s):

                w = self
                w.delete(i,j)
                w.insert(i,s)
            #@-node:bob.20070903081639.20:replace
            #@+node:bob.20070903081639.21:scrollLines
            def scrollLines (self,n):

                w = self
                w._scrollLines(n)
            #@nonl
            #@-node:bob.20070903081639.21:scrollLines
            #@+node:bob.20070903081639.22:see & seeInsertPoint
            def see(self,index):

                w = self
                i = self.toPythonIndex(index)
                w._see(i)

            def seeInsertPoint(self):

                w = self
                i = w._getInsertPoint()
                w._see(i)
            #@-node:bob.20070903081639.22:see & seeInsertPoint
            #@+node:bob.20070903081639.23:selectAllText
            def selectAllText (self,insert=None):

                '''Select all text of the widget.'''

                w = self
                w.setSelectionRange(0,'end',insert=insert)
            #@-node:bob.20070903081639.23:selectAllText
            #@+node:bob.20070903081639.24:setAllText
            def setAllText (self,s):

                w = self
                w._setAllText(s)
            #@nonl
            #@-node:bob.20070903081639.24:setAllText
            #@+node:bob.20070903081639.25:setBackgroundColor & SetBackgroundColour
            def setBackgroundColor (self,color):

                w = self

                # Translate tk colors to wx colors.
                d = { 'lightgrey': 'light grey', 'lightblue': 'leo blue',}

                color = d.get(color,color)

                return w._setBackgroundColor(color)

            SetBackgroundColour = setBackgroundColor
            #@nonl
            #@-node:bob.20070903081639.25:setBackgroundColor & SetBackgroundColour
            #@+node:bob.20070903081639.26:setFocus (baseText)
            def setFocus (self):

                w = self
                # g.trace('baseText')
                return w._setFocus()

            SetFocus = setFocus
            #@-node:bob.20070903081639.26:setFocus (baseText)
            #@+node:bob.20070903081639.27:setInsertPoint (baseText)
            def setInsertPoint (self,pos):

                w = self
                w.virtualInsertPoint = i = w.toPythonIndex(pos)
                # g.trace(self,i)
                w._setInsertPoint(i)
            #@-node:bob.20070903081639.27:setInsertPoint (baseText)
            #@+node:bob.20070903081639.28:setSelectionRange (baseText)
            def setSelectionRange (self,i,j,insert=None):

                w = self
                i1, j1, insert1 = i,j,insert
                i,j = w.toPythonIndex(i),w.toPythonIndex(j)

                # g.trace(self,'baseWidget',repr(i1),'=',repr(i),repr(j1),'=',repr(j),repr(insert1),'=',repr(insert),g.callers(4))

                if i == j:
                    w._setInsertPoint(j)
                else:
                    w._setSelectionRange(i,j)

                if insert is not None and insert in (i,j):
                    ins = w.toPythonIndex(insert)
                    if ins in (i,j):
                        self.virtualInsertPoint = ins
            #@-node:bob.20070903081639.28:setSelectionRange (baseText)
            #@+node:bob.20070903081639.29:setWidth
            def setWidth (self,width):

                '''Set the width of the widget.
                This is only called for headline widgets,
                and gui's may choose not to do anything here.'''

                w = self
                pass
            #@-node:bob.20070903081639.29:setWidth
            #@+node:bob.20070903081639.30:setYScrollPosition
            def setYScrollPosition (self,i):

                 w = self
                 w._setYScrollPosition(i)
            #@nonl
            #@-node:bob.20070903081639.30:setYScrollPosition
            #@+node:bob.20070903081639.41:xyToGui/PythonIndex
            def xyToPythonIndex (self,x,y):
                return 0
            #@-node:bob.20070903081639.41:xyToGui/PythonIndex
            #@+node:bob.20070903081639.40:yview
            def yview (self,*args):

                '''w.yview('moveto',y) or w.yview()'''

                return 0,0
            #@nonl
            #@-node:bob.20070903081639.40:yview
            #@-others
        #@nonl
        #@-node:bob.20070903081639:Wrapper methods (widget-independent)
        #@-node:bob.20070813163332.151:Wrapper methods
        #@-others
    #@nonl
    #@-node:bob.20070813163332.146:stcTextWidget (baseTextWidget)
    #@+node:bob.20070821163516:findTextWidget (plainTextWidget)

    class findTextWidget (plainTextWidget):

        """A wrapper for text widgets used in the 'Find' panel."""

        #@    @+others
        #@+node:bob.20070821163516.1:__init__

        def __init__ (self, leoParent,
            parent=None,
            multiline=False,
            widget=None,
            name='<unknown findTextWidget>',
            *args,**keys
        ):

            plainTextWidget.__init__(self, leoParent, parent,
                multiline=multiline, name=name, widget=widget,
                *args, **keys
            )
        #@-node:bob.20070821163516.1:__init__
        #@-others
    #@nonl
    #@-node:bob.20070821163516:findTextWidget (plainTextWidget)
    #@+node:bob.20070831041313:statusTextWidget (plainTextWidget)

    class statusTextWidget (plainTextWidget):

        """A wrapper for text widgets used as status lines."""

        #@    @+others
        #@+node:bob.20070901081127:pass
        pass
        #@nonl
        #@-node:bob.20070901081127:pass
        #@-others
    #@-node:bob.20070831041313:statusTextWidget (plainTextWidget)
    #@+node:bob.20070813163332.140:headlineTextWidget (plainTextWidget)

    class headlineTextWidget (plainTextWidget):

        """A wrapper for  text widgets used to edit headlines."""

        #@    @+others
        #@+node:bob.20070813163332.141:__init__

        def __init__ (self, leoParent,
            parent=None,
            multiline=False,
            widget=None,
            name='headline',
            *args,**keys
        ):

            plainTextWidget.__init__(self, leoParent, parent,
                multiline=multiline, name=name, widget=widget,
                *args, **keys
            )

        #@-node:bob.20070813163332.141:__init__
        #@-others
    #@nonl
    #@-node:bob.20070813163332.140:headlineTextWidget (plainTextWidget)
    #@+node:bob.20070823062818:minibufferTextWidget (plainTextWidget)

    class minibufferTextWidget (plainTextWidget):

        '''A wrapper for the minibuffer text widgets.'''

        #@    @+others
        #@+node:bob.20070823062818.1:__init__

        def __init__ (self, leoParent,
            parent,
            multiline=False,
            widget=None,
            name='minibuffer',
            *args,**keys
        ):

            plainTextWidget.__init__(self, leoParent, parent,
                multiline=multiline, name=name, widget=widget,
                *args, **keys
            )


        #@-node:bob.20070823062818.1:__init__
        #@-others
    #@nonl
    #@-node:bob.20070823062818:minibufferTextWidget (plainTextWidget)
    #@+node:bob.20070813163332.143:richTextWidget (baseTextWidget)

    class richTextWidget (baseTextWidget):

        '''A class wrapping wx.richtext.RichTextCtrl widgets.'''

        #@    @+others
        #@+node:bob.20070813163332.144:__init__

        def __init__ (self, leoParent,
            parent=None,
            multiline=True,
            widget=None,
            name='text <unknown richTextWidget>',
            **kw
        ):

            if not widget:
                widget = richtext.RichTextCtrl(parent, style=wx.WANTS_CHARS, **kw)

            baseTextWidget.__init__(self, leoParent,
                name=name, widget=widget,
            )

            widget.Bind(wx.EVT_SIZE, self.onSize)



        #@-node:bob.20070813163332.144:__init__
        #@+node:bob.20071230181436:onSize
        def onSize(self, event):
            """Handle EVT_SIZE for RichTextCtrl."""

            w = self.widget

            #g.trace(myclass(self), w.GetClientSize())
            w.ShowPosition(w.GetInsertionPoint())

            event.Skip()
        #@-node:bob.20071230181436:onSize
        #@+node:bob.20070826135428:bindings (TextCtrl)

        # Interface non gui text control methods
        #  to physical wx.TextCtrl methods.

        def _appendText(self,s):
            #g.trace('richtext',s)
            return self.widget.AppendText(s)

        def _get(self,i,j):
            #g.trace('richtext',i, j)
            return self.widget.GetRange(i,j)

        def _getAllText(self):
            #g.trace('richtext')
            return self.widget.GetValue()

        def _getFocus(self):
            #g.trace('richtext')
            return self.widget.FindFocus()

        def _getInsertPoint(self):
            #g.trace('richtext')
            return self.widget.GetInsertionPoint()

        def _getLastPosition(self ):
            #g.trace('richtext')
            return self.widget.GetLastPosition()

        def _getSelectedText(self):
            #g.trace('richtext')
            return self.widget.GetStringSelection()

        def _getSelectionRange(self):
            #g.trace('richtext')
            return self.widget.GetSelection()

        def _hitTest(self,pos):
            #g.trace('richtext',pos)
            return self.widget.HitTest(pos)

        def _insertText(self,i,s):
            self.setInsertPoint(i,s)
            return self.widget.WriteText(s)

        def _scrollLines(self,n):
            #g.trace('richtext', n)
            return self.widget.ScrollLines(n)

        def _see(self,i):
            #g.trace('richtext',i)
            return self.widget.ShowPosition(i)

        def _setAllText(self,s):
            #g.trace('richtext',s)
            return self.widget.SetValue(s)

        def _setBackgroundColor(self,color):
            #g.trace('richtext',color)
            return self.widget.SetBackgroundColour(color)

        def _setFocus(self):
            #g.trace('richtext')
            return self.widget.SetFocus()

        def _setInsertPoint(self,i):
            #g.trace('richtext',i)

            self.widget.SetSelection(i, i)

        def _setSelectionRange(self,i,j):
            #g.trace('richtext',i,j)
            return self.widget.SetSelection(i,j)


        def _getYScrollPosition(self):
            return 0,0 # Could also return None.

        def _setYScrollPosition(self,i):
             pass
        #@-node:bob.20070826135428:bindings (TextCtrl)
        #@+node:bob.20070901040919:hide
        if 0:
            #@    @+others
            #@+node:bob.20070826170450:onChar
            # Don't even think of using key up/down events.
            # They don't work reliably and don't support auto-repeat.

            def onChar(self, event):

                c = self.c
                keycode = event.GetKeyCode()
                g.trace('richtext key=', keycode)

                event.leoWidget = self
                keysym = g.app.gui.eventKeysym(event)

                # if keysym:

                if keysym:
                    g.trace('base text: keysym:',repr(keysym))
                    result = c.k.masterKeyHandler(event,stroke=keysym)
                    g.trace( 'result:', result)

                    if result is None:
                        g.trace('propogate key event')
                        g.trace(event)
                        event.Skip()


            #@-node:bob.20070826170450:onChar
            #@-others
        #@nonl
        #@-node:bob.20070901040919:hide
        #@-others
    #@nonl
    #@-node:bob.20070813163332.143:richTextWidget (baseTextWidget)
    #@+node:bob.20070826133248:logTextWidget (richTextWidget)

    class logTextWidget(richTextWidget):

        '''A wrapper for log pane text widgets.'''

        #@    @+others
        #@+node:bob.20070901051401:onGainFocus

        def onGainFocus(self, event):
            """Respond to focus event for logTextWidget.

            We don't want focus, so send it back to where it
            came from.

            """

            self.c.focusManager.lastFocus()
            event.Skip()
            return True
        #@-node:bob.20070901051401:onGainFocus
        #@-others
    #@nonl
    #@-node:bob.20070826133248:logTextWidget (richTextWidget)
    #@-others
    #@nonl
    #@-node:bob.20070813163332.136:=== TEXT WIDGETS ===
    #@+node:bob.20070813163332.65:Find/Spell classes
    #@+node:bob.20070813163332.66:wxSearchWidget
    class wxSearchWidget:

        """A dummy widget class to pass to Leo's core find code."""

        #@    @+others
        #@+node:bob.20070813163332.67:wxSearchWidget.__init__
        def __init__ (self):

            self.insertPoint = 0
            self.selection = 0,0
            self.bodyCtrl = self
            self.body = self
            self.text = None
        #@nonl
        #@-node:bob.20070813163332.67:wxSearchWidget.__init__
        #@-others
    #@nonl
    #@-node:bob.20070813163332.66:wxSearchWidget
    #@+node:bob.20070813163332.95:wxFindTab class (leoFind.findTab)
    class wxFindTab (leoFind.findTab):

        '''A subclass of the findTab class containing all wxGui code.'''

        #@    @+others
        #@+node:bob.20070813163332.96:Birth
        #@+node:bob.20070813163332.98:initGui
        # Called from leoFind.findTab.ctor.

        def initGui (self):

            # g.trace('wxFindTab')

            self.svarDict = {} # Keys are ivar names, values are svar objects.

            for key in self.intKeys:
                self.svarDict[key] = self.svar() # Was Tk.IntVar.

            for key in self.newStringKeys:
                self.svarDict[key] = self.svar() # Was Tk.StringVar.
        #@-node:bob.20070813163332.98:initGui
        #@+node:bob.20070813163332.99:init (wxFindTab)
        # Called from leoFind.findTab.ctor.
        # We must override leoFind.init to init the checkboxes 'by hand' here.

        def init (self,c):
            #g.trace('wxFindTab',g.callers())

            # Separate c.ivars are much more convenient than a svarDict.
            for key in self.intKeys:
                # Get ivars from @settings.
                val = c.config.getBool(key)
                setattr(self,key,val)
                val = g.choose(val,1,0)
                svar = self.svarDict.get(key)
                if svar: svar.set(val)
                #g.trace(key,val)

            #@    << set find/change widgets >>
            #@+node:bob.20070813163332.100:<< set find/change widgets >>
            self.find_ctrl.delete(0,"end")
            self.change_ctrl.delete(0,"end")

            # Get setting from @settings.
            for w,setting,defaultText in (
                (self.find_ctrl,"find_text",''),
                (self.change_ctrl,"change_text",''),
            ):
                s = c.config.getString(setting)
                if not s: s = defaultText
                w.insert("end",s)
            #@-node:bob.20070813163332.100:<< set find/change widgets >>
            #@nl
            #@    << set radio buttons from ivars >>
            #@+node:bob.20070813163332.101:<< set radio buttons from ivars >>
            # In Tk, setting the var also sets the widget.
            # Here, we do so explicitly.
            d = self.widgetsDict
            for ivar,key in (
                ("pattern_match","pattern-search"),
                #("script_search","script-search")
            ):
                svar = self.svarDict[ivar].get()
                if svar:
                    self.svarDict["radio-find-type"].set(key)
                    w = d.get(key)
                    if w: w.SetValue(True)
                    break
            else:
                self.svarDict["radio-find-type"].set("plain-search")

            for ivar,key in (
                ("suboutline_only","suboutline-only"),
                ("node_only","node-only"),
                # ("selection_only","selection-only")
            ):
                svar = self.svarDict[ivar].get()
                if svar:
                    self.svarDict["radio-search-scope"].set(key)
                    break
            else:
                key = 'entire-outline'
                self.svarDict["radio-search-scope"].set(key)
                w = self.widgetsDict.get(key)
                if w: w.SetValue(True)
            #@-node:bob.20070813163332.101:<< set radio buttons from ivars >>
            #@nl
            #@    << set checkboxes from ivars >>
            #@+node:bob.20070813163332.102:<< set checkboxes from ivars >>
            for ivar in (
                'ignore_case',
                'mark_changes',
                'mark_finds',
                'pattern_match',
                'reverse',
                'search_body',
                'search_headline',
                'whole_word',
                'wrap',
            ):
                svar = self.svarDict[ivar].get()
                if svar:
                    w = self.widgetsDict.get(ivar)
                    if w: w.SetValue(True)
            #@-node:bob.20070813163332.102:<< set checkboxes from ivars >>
            #@nl
        #@-node:bob.20070813163332.99:init (wxFindTab)
        #@-node:bob.20070813163332.96:Birth
        #@+node:bob.20070813163332.103:class svar
        class svar:
            '''A class like Tk's IntVar and StringVar classes.'''
            def __init__(self):
                self.val = None
            def get (self):
                return self.val
            def set (self,val):
                self.val = val
        #@-node:bob.20070813163332.103:class svar
        #@+node:bob.20070813163332.104:createFrame (wxFindTab)
        def createFrame (self,parentFrame):

            self.parentFrame = self.top = parentFrame

            configName = 'log_pane_Find_tab_background_color'
            self.top.SetBackgroundColour(
                name2color(
                    self.c.config.getColor(configName) or 'MistyRose1'
                )
            )

            self.createFindChangeAreas()
            self.createBoxes()
            self.createButtons()
            self.layout()
            self.createBindings()
        #@+node:bob.20070813163332.105:createFindChangeAreas
        def createFindChangeAreas (self):

            f = self.top

            self.fLabel = \
                wx.StaticText(f,label='F',
                    style=wx.ALIGN_RIGHT)

            self.cLabel = \
                wx.StaticText(f,label='C',
                    style=wx.ALIGN_RIGHT)

            self.find_ctrl = \
                findTextWidget(self, f, name='find-text')

            self.change_ctrl = \
                findTextWidget(self, f, name='change-text')
        #@-node:bob.20070813163332.105:createFindChangeAreas
        #@+node:bob.20070813163332.106:layout
        def layout (self):

            f = self.top

            self.sizer = sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.AddSpacer(5)

            sizer2 = wx.FlexGridSizer(2, 2, vgap=5,hgap=5)
            sizer2.SetFlexibleDirection(wx.HORIZONTAL)
            sizer2.AddGrowableCol(1, 1)

            sizer2.Add(self.fLabel,0,wx.EXPAND)
            sizer2.Add(self.find_ctrl.widget,1,wx.EXPAND,border=5)
            sizer2.Add(self.cLabel,0,wx.EXPAND)
            sizer2.Add(self.change_ctrl.widget,1,wx.EXPAND,border=5)

            sizer.Add(sizer2,0,wx.EXPAND)
            sizer.AddSpacer(5)

            #label = wx.StaticBox(f,label='Find Options')
            #boxes = wx.StaticBoxSizer(label,wx.HORIZONTAL)

            boxes = wx.BoxSizer(wx.HORIZONTAL)
            lt_col = wx.BoxSizer(wx.VERTICAL)
            rt_col = wx.BoxSizer(wx.VERTICAL)

            for w in self.boxes [:6]:
                lt_col.Add(w,0)
            for w in self.boxes [6:]:
                rt_col.Add(w,0)

            boxes.Add(lt_col,0)
            boxes.Add(rt_col,0) #,wx.EXPAND)
            sizer.Add(boxes,0) #,wx.EXPAND)

            f.SetSizer(sizer)
        #@nonl
        #@-node:bob.20070813163332.106:layout
        #@+node:bob.20070813163332.107:createBoxes
        def createBoxes (self):

            '''Create two columns of radio buttons & check boxes.'''

            c = self.c ; f = self.parentFrame
            self.boxes = []
            self.widgetsDict = {} # Keys are ivars, values are checkboxes or radio buttons.

            data = ( # Leading star denotes a radio button.
                ('Whole &Word', 'whole_word',),
                ('&Ignore Case','ignore_case'),
                ('Wrap &Around','wrap'),
                ('&Reverse',    'reverse'),
                ('Rege&xp',     'pattern_match'),
                ('Mark &Finds', 'mark_finds'),
                ("*&Entire Outline","entire-outline"),
                ("*&Suboutline Only","suboutline-only"),
                ("*&Node Only","node-only"),
                ('Search &Headline','search_headline'),
                ('Search &Body','search_body'),
                ('Mark &Changes','mark_changes'),
            )

            # Important: changing these controls merely changes entries in self.svarDict.
            # First, leoFind.update_ivars sets the find ivars from self.svarDict.
            # Second, self.init sets the values of widgets from the ivars.

            def onBoxFocus(event):
                self.c.focusManager.lastFocus()
                event.Skip()

            inGroup = False
            for label,ivar in data:
                if label.startswith('*'):
                    label = label[1:]
                    style = g.choose(inGroup,0,wx.RB_GROUP)
                    inGroup = True
                    w = wx.RadioButton(f,label=label,style=style)
                    self.widgetsDict[ivar] = w

                    def radioButtonCallback(event=None,ivar=ivar):
                        svar = self.svarDict["radio-search-scope"]
                        svar.set(ivar)

                    w.Bind(wx.EVT_RADIOBUTTON,radioButtonCallback)
                    w.Bind(wx.EVT_SET_FOCUS, onBoxFocus)
                else:
                    w = wx.CheckBox(f,label=label)
                    self.widgetsDict[ivar] = w
                    def checkBoxCallback(event=None,ivar=ivar):
                        svar = self.svarDict.get(ivar)
                        val = svar.get()
                        svar.set(g.choose(val,False,True))
                        # g.trace(ivar,val)
                    w.Bind(wx.EVT_CHECKBOX,checkBoxCallback)
                    w.Bind(wx.EVT_SET_FOCUS, onBoxFocus)
                self.boxes.append(w)
        #@-node:bob.20070813163332.107:createBoxes
        #@+node:bob.20070813163332.108:createBindings TO DO
        def createBindings (self):

            return ### not ready yet

            def setFocus(w):
                c = self.c
                c.widgetWantsFocusNow(w)
                w.setSelectionRange(0,0)
                return "break"

            def toFind(event,w=ftxt): return setFocus(w)
            def toChange(event,w=ctxt): return setFocus(w)

            def insertTab(w):
                data = w.getSelectionRange()
                if data: start,end = data
                else: start = end = w.getInsertPoint()
                w.replace(start,end,"\t")
                return "break"

            def insertFindTab(event,w=ftxt): return insertTab(w)
            def insertChangeTab(event,w=ctxt): return insertTab(w)

            ftxt.bind("<Tab>",toChange)
            ctxt.bind("<Tab>",toFind)
            ftxt.bind("<Control-Tab>",insertFindTab)
            ctxt.bind("<Control-Tab>",insertChangeTab)
        #@-node:bob.20070813163332.108:createBindings TO DO
        #@+node:bob.20070813163332.109:createButtons (does nothing)
        def createButtons (self):

            '''Create two columns of buttons.'''

            # # Create the alignment panes.
            # buttons  = Tk.Frame(outer,background=bg)
            # buttons1 = Tk.Frame(buttons,bd=1,background=bg)
            # buttons2 = Tk.Frame(buttons,bd=1,background=bg)
            # buttons.pack(side='top',expand=1)
            # buttons1.pack(side='left')
            # buttons2.pack(side='right')

            # width = 15 ; defaultText = 'Find' ; buttons = []

            # for text,boxKind,frame,callback in (
                # # Column 1...
                # ('Find','button',buttons1,self.findButtonCallback),
                # ('Find All','button',buttons1,self.findAllButton),
                # # Column 2...
                # ('Change','button',buttons2,self.changeButton),
                # ('Change, Then Find','button',buttons2,self.changeThenFindButton),
                # ('Change All','button',buttons2,self.changeAllButton),
            # ):
                # w = underlinedTkButton(boxKind,frame,
                    # text=text,command=callback)
                # buttons.append(w)
                # if text == defaultText:
                    # w.button.configure(width=width-1,bd=4)
                # elif boxKind != 'check':
                    # w.button.configure(width=width)
                # w.button.pack(side='top',anchor='w',pady=2,padx=2)
        #@-node:bob.20070813163332.109:createButtons (does nothing)
        #@-node:bob.20070813163332.104:createFrame (wxFindTab)
        #@+node:bob.20070813163332.110:createBindings
        def createBindings (self):

            return ### not used in wxLeo.

            c = self.c ; k = c.k

            def resetWrapCallback(event,self=self,k=k):
                self.resetWrap(event)
                return k.masterKeyHandler(event)

            def findButtonBindingCallback(event=None,self=self):
                self.findButton()
                return 'break'

            table = (
                ('<Button-1>',  k.masterClickHandler),
                ('<Double-1>',  k.masterClickHandler),
                ('<Button-3>',  k.masterClickHandler),
                ('<Double-3>',  k.masterClickHandler),
                ('<Key>',       resetWrapCallback),
                ('<Return>',    findButtonBindingCallback),
                ("<Escape>",    self.hideTab),
            )

            for w in (self.find_ctrl,self.change_ctrl):
                for event, callback in table:
                    w.bind(event,callback)
        #@-node:bob.20070813163332.110:createBindings
        #@+node:bob.20070813163332.111:Support for minibufferFind class (wxFindTab)
        # This is the same as the Tk code because we simulate Tk svars.
        #@nonl
        #@+node:bob.20070813163332.112:getOption
        def getOption (self,ivar):

            var = self.svarDict.get(ivar)

            if var:
                val = var.get()
                # g.trace('%s = %s' % (ivar,val))
                return val
            else:
                g.trace('bad ivar name: %s' % ivar)
                return None
        #@-node:bob.20070813163332.112:getOption
        #@+node:bob.20070813163332.113:setOption
        def setOption (self,ivar,val):

            if ivar in self.intKeys:
                if val is not None:
                    var = self.svarDict.get(ivar)
                    var.set(val)
                    # g.trace('%s = %s' % (ivar,val))

            elif not g.app.unitTesting:
                g.trace('oops: bad find ivar %s' % ivar)
        #@-node:bob.20070813163332.113:setOption
        #@+node:bob.20070813163332.114:toggleOption
        def toggleOption (self,ivar):

            if ivar in self.intKeys:
                var = self.svarDict.get(ivar)
                val = not var.get()
                var.set(val)
                # g.trace('%s = %s' % (ivar,val),var)
            else:
                g.trace('oops: bad find ivar %s' % ivar)
        #@-node:bob.20070813163332.114:toggleOption
        #@-node:bob.20070813163332.111:Support for minibufferFind class (wxFindTab)
        #@+node:bob.20070901083131:toggleTextWidgetFocus

        def toggleTextWidgetFocus(self, widget):

            c = self.c

            g.trace(c.widget_name(widget), widget)
            if c.widget_name(widget) == 'find-text':
                #print 'change', self.change_ctrl
                self.change_ctrl.setFocus()
            else:
                #print 'find', self.find_ctrl
                self.find_ctrl.setFocus()

        #@-node:bob.20070901083131:toggleTextWidgetFocus
        #@-others
    #@nonl
    #@-node:bob.20070813163332.95:wxFindTab class (leoFind.findTab)
    #@+node:bob.20070813163332.115:class wxSpellTab TO DO
    class wxSpellTab:

        #@    @+others
        #@+node:bob.20070813163332.116:wxSpellTab.__init__
        def __init__ (self,c,tabName):

            self.c = c
            self.tabName = tabName

            self.createFrame()
            self.createBindings()
        #@-node:bob.20070813163332.116:wxSpellTab.__init__
        #@+node:bob.20070813163332.117:createBindings TO DO
        def createBindings (self):

            return ###

            c = self.c ; k = c.k
            widgets = (self.listBox, self.outerFrame)

            for w in widgets:

                # Bind shortcuts for the following commands...
                for commandName,func in (
                    ('full-command',            k.fullCommand),
                    ('hide-spell-tab',          self.handler.hide),
                    ('spell-add',               self.handler.add),
                    ('spell-find',              self.handler.find),
                    ('spell-ignore',            self.handler.ignore),
                    ('spell-change-then-find',  self.handler.changeThenFind),
                ):
                    junk, bunchList = c.config.getShortcut(commandName)
                    for bunch in bunchList:
                        accel = bunch.val
                        shortcut = k.shortcutFromSetting(accel)
                        if shortcut:
                            # g.trace(shortcut,commandName)
                            w.bind(shortcut,func)

            self.listBox.bind("<Double-1>",self.onChangeThenFindButton)
            self.listBox.bind("<Button-1>",self.onSelectListBox)
            self.listBox.bind("<Map>",self.onMap)
        #@nonl
        #@-node:bob.20070813163332.117:createBindings TO DO
        #@+node:bob.20070813163332.118:createFrame TO DO
        def createFrame (self):

            return ###

            c = self.c ; log = c.frame.log ; tabName = self.tabName

            parentFrame = log.frameDict.get(tabName)
            w = log.textDict.get(tabName)
            w.pack_forget()

            # Set the common background color.
            bg = c.config.getColor('log_pane_Spell_tab_background_color') or 'LightSteelBlue2'

            #@    << Create the outer frames >>
            #@+node:bob.20070813163332.119:<< Create the outer frames >>
            self.outerScrolledFrame = Pmw.ScrolledFrame(
                parentFrame,usehullsize = 1)

            self.outerFrame = outer = self.outerScrolledFrame.component('frame')
            self.outerFrame.configure(background=bg)

            for z in ('borderframe','clipper','frame','hull'):
                self.outerScrolledFrame.component(z).configure(
                    relief='flat',background=bg)
            #@-node:bob.20070813163332.119:<< Create the outer frames >>
            #@nl
            #@    << Create the text and suggestion panes >>
            #@+node:bob.20070813163332.120:<< Create the text and suggestion panes >>
            f2 = Tk.Frame(outer,bg=bg)
            f2.pack(side='top',expand=0,fill='x')

            self.wordLabel = Tk.Label(f2,text="Suggestions for:")
            self.wordLabel.pack(side='left')
            self.wordLabel.configure(font=('verdana',10,'bold'))

            fpane = Tk.Frame(outer,bg=bg,bd=2)
            fpane.pack(side='top',expand=1,fill='both')

            self.listBox = Tk.Listbox(fpane,height=6,width=10,selectmode="single")
            self.listBox.pack(side='left',expand=1,fill='both')
            self.listBox.configure(font=('verdana',11,'normal'))

            listBoxBar = Tk.Scrollbar(fpane,name='listBoxBar')

            bar, txt = listBoxBar, self.listBox
            txt ['yscrollcommand'] = bar.set
            bar ['command'] = txt.yview
            bar.pack(side='right',fill='y')
            #@-node:bob.20070813163332.120:<< Create the text and suggestion panes >>
            #@nl
            #@    << Create the spelling buttons >>
            #@+node:bob.20070813163332.121:<< Create the spelling buttons >>
            # Create the alignment panes
            buttons1 = Tk.Frame(outer,bd=1,bg=bg)
            buttons2 = Tk.Frame(outer,bd=1,bg=bg)
            buttons3 = Tk.Frame(outer,bd=1,bg=bg)
            for w in (buttons1,buttons2,buttons3):
                w.pack(side='top',expand=0,fill='x')

            buttonList = [] ; font = ('verdana',9,'normal') ; width = 12
            for frame, text, command in (
                (buttons1,"Find",self.onFindButton),
                (buttons1,"Add",self.onAddButton),
                (buttons2,"Change",self.onChangeButton),
                (buttons2,"Change, Find",self.onChangeThenFindButton),
                (buttons3,"Ignore",self.onIgnoreButton),
                (buttons3,"Hide",self.onHideButton),
            ):
                b = Tk.Button(frame,font=font,width=width,text=text,command=command)
                b.pack(side='left',expand=0,fill='none')
                buttonList.append(b)

            # Used to enable or disable buttons.
            (self.findButton,self.addButton,
             self.changeButton, self.changeFindButton,
             self.ignoreButton, self.hideButton) = buttonList
            #@-node:bob.20070813163332.121:<< Create the spelling buttons >>
            #@nl

            # Pack last so buttons don't get squished.
            self.outerScrolledFrame.pack(expand=1,fill='both',padx=2,pady=2)
        #@-node:bob.20070813163332.118:createFrame TO DO
        #@+node:bob.20070813163332.122:Event handlers
        #@+node:bob.20070813163332.123:onAddButton
        def onAddButton(self):
            """Handle a click in the Add button in the Check Spelling dialog."""

            self.handler.add()
        #@-node:bob.20070813163332.123:onAddButton
        #@+node:bob.20070813163332.124:onChangeButton & onChangeThenFindButton
        def onChangeButton(self,event=None):

            """Handle a click in the Change button in the Spell tab."""

            self.handler.change()
            self.updateButtons()


        def onChangeThenFindButton(self,event=None):

            """Handle a click in the "Change, Find" button in the Spell tab."""

            if self.change():
                self.find()
            self.updateButtons()
        #@-node:bob.20070813163332.124:onChangeButton & onChangeThenFindButton
        #@+node:bob.20070813163332.125:onFindButton
        def onFindButton(self):

            """Handle a click in the Find button in the Spell tab."""

            c = self.c
            self.handler.find()
            self.updateButtons()
            c.invalidateFocus()
            c.bodyWantsFocusNow()
        #@-node:bob.20070813163332.125:onFindButton
        #@+node:bob.20070813163332.126:onHideButton
        def onHideButton(self):

            """Handle a click in the Hide button in the Spell tab."""

            self.handler.hide()
        #@-node:bob.20070813163332.126:onHideButton
        #@+node:bob.20070813163332.127:onIgnoreButton
        def onIgnoreButton(self,event=None):

            """Handle a click in the Ignore button in the Check Spelling dialog."""

            self.handler.ignore()
        #@-node:bob.20070813163332.127:onIgnoreButton
        #@+node:bob.20070813163332.128:onMap
        def onMap (self, event=None):
            """Respond to a Tk <Map> event."""

            self.update(show= False, fill= False)
        #@-node:bob.20070813163332.128:onMap
        #@+node:bob.20070813163332.129:onSelectListBox
        def onSelectListBox(self, event=None):
            """Respond to a click in the selection listBox."""

            c = self.c
            self.updateButtons()
            c.bodyWantsFocus()
        #@-node:bob.20070813163332.129:onSelectListBox
        #@-node:bob.20070813163332.122:Event handlers
        #@+node:bob.20070813163332.130:Helpers
        #@+node:bob.20070813163332.131:bringToFront
        def bringToFront (self):

            self.c.frame.log.selectTab('Spell')
        #@-node:bob.20070813163332.131:bringToFront
        #@+node:bob.20070813163332.132:fillbox
        def fillbox(self, alts, word=None):
            """Update the suggestions listBox in the Check Spelling dialog."""

            self.suggestions = alts

            if not word:
                word = ""

            self.wordLabel.configure(text= "Suggestions for: " + word)
            self.listBox.delete(0, "end")

            for i in xrange(len(self.suggestions)):
                self.listBox.insert(i, self.suggestions[i])

            # This doesn't show up because we don't have focus.
            if len(self.suggestions):
                self.listBox.select_set(1)
        #@-node:bob.20070813163332.132:fillbox
        #@+node:bob.20070813163332.133:getSuggestion
        def getSuggestion(self):
            """Return the selected suggestion from the listBox."""

            # Work around an old Python bug.  Convert strings to ints.
            items = self.listBox.curselection()
            try:
                items = map(int, items)
            except ValueError: pass

            if items:
                n = items[0]
                suggestion = self.suggestions[n]
                return suggestion
            else:
                return None
        #@-node:bob.20070813163332.133:getSuggestion
        #@+node:bob.20070813163332.134:update
        def update(self,show=True,fill=False):

            """Update the Spell Check dialog."""

            c = self.c

            if fill:
                self.fillbox([])

            self.updateButtons()

            if show:
                self.bringToFront()
                c.bodyWantsFocus()
        #@-node:bob.20070813163332.134:update
        #@+node:bob.20070813163332.135:updateButtons (spellTab)
        def updateButtons (self):

            """Enable or disable buttons in the Check Spelling dialog."""

            c = self.c ; w = c.frame.body.bodyCtrl

            start, end = w.getSelectionRange()
            state = g.choose(self.suggestions and start,"normal","disabled")

            self.changeButton.configure(state=state)
            self.changeFindButton.configure(state=state)

            # state = g.choose(self.c.undoer.canRedo(),"normal","disabled")
            # self.redoButton.configure(state=state)
            # state = g.choose(self.c.undoer.canUndo(),"normal","disabled")
            # self.undoButton.configure(state=state)

            self.addButton.configure(state='normal')
            self.ignoreButton.configure(state='normal')
        #@-node:bob.20070813163332.135:updateButtons (spellTab)
        #@-node:bob.20070813163332.130:Helpers
        #@-others
    #@-node:bob.20070813163332.115:class wxSpellTab TO DO
    #@-node:bob.20070813163332.65:Find/Spell classes
    #@+node:bob.20070813163332.160:wxComparePanel class (not ready yet)
    """Leo's base compare class."""

    #@@language python
    #@@tabwidth -4
    #@@pagewidth 80

    import leoGlobals as g
    import leoCompare

    class wxComparePanel (leoCompare.leoCompare): #,leoWxDialog):

        """A class that creates Leo's compare panel."""

        #@    @+others
        #@+node:bob.20070813163332.161:Birth...
        #@+node:bob.20070813163332.162:wxComparePanel.__init__
        def __init__ (self,c):

            # Init the base class.
            leoCompare.leoCompare.__init__ (self,c)
            ###leoTkinterDialog.leoTkinterDialog.__init__(self,c,"Compare files and directories",resizeable=False)

            if g.app.unitTesting: return

            self.c = c

            if 0:
                #@        << init tkinter compare ivars >>
                #@+node:bob.20070813163332.163:<< init tkinter compare ivars >>
                # Ivars pointing to Tk elements.
                self.browseEntries = []
                self.extensionEntry = None
                self.countEntry = None
                self.printButtons = []

                # No corresponding ivar in the leoCompare class.
                self.useOutputFileVar = Tk.IntVar()

                # These all correspond to ivars in leoCompare
                self.appendOutputVar             = Tk.IntVar()

                self.ignoreBlankLinesVar         = Tk.IntVar()
                self.ignoreFirstLine1Var         = Tk.IntVar()
                self.ignoreFirstLine2Var         = Tk.IntVar()
                self.ignoreInteriorWhitespaceVar = Tk.IntVar()
                self.ignoreLeadingWhitespaceVar  = Tk.IntVar()
                self.ignoreSentinelLinesVar      = Tk.IntVar()

                self.limitToExtensionVar         = Tk.IntVar()
                self.makeWhitespaceVisibleVar    = Tk.IntVar()

                self.printBothMatchesVar         = Tk.IntVar()
                self.printMatchesVar             = Tk.IntVar()
                self.printMismatchesVar          = Tk.IntVar()
                self.printTrailingMismatchesVar  = Tk.IntVar()
                self.stopAfterMismatchVar        = Tk.IntVar()
                #@-node:bob.20070813163332.163:<< init tkinter compare ivars >>
                #@nl

            # These ivars are set from Entry widgets.
            self.limitCount = 0
            self.limitToExtension = None

            # The default file name in the "output file name" browsers.
            self.defaultOutputFileName = "CompareResults.txt"

            if 0:
                self.createTopFrame()
                self.createFrame()
        #@-node:bob.20070813163332.162:wxComparePanel.__init__
        #@+node:bob.20070813163332.164:finishCreate (tkComparePanel)
        # Initialize ivars from config parameters.

        def finishCreate (self):

            c = self.c

            # File names.
            for i,option in (
                (0,"compare_file_1"),
                (1,"compare_file_2"),
                (2,"output_file") ):

                name = c.config.getString(option)
                if name and len(name) > 0:
                    e = self.browseEntries[i]
                    e.delete(0,"end")
                    e.insert(0,name)

            name = c.config.getString("output_file")
            b = g.choose(name and len(name) > 0,1,0)
            self.useOutputFileVar.set(b)

            # File options.
            b = c.config.getBool("ignore_first_line_of_file_1")
            if b == None: b = 0
            self.ignoreFirstLine1Var.set(b)

            b = c.config.getBool("ignore_first_line_of_file_2")
            if b == None: b = 0
            self.ignoreFirstLine2Var.set(b)

            b = c.config.getBool("append_output_to_output_file")
            if b == None: b = 0
            self.appendOutputVar.set(b)

            ext = c.config.getString("limit_directory_search_extension")
            b = ext and len(ext) > 0
            b = g.choose(b and b != 0,1,0)
            self.limitToExtensionVar.set(b)
            if b:
                e = self.extensionEntry
                e.delete(0,"end")
                e.insert(0,ext)

            # Print options.
            b = c.config.getBool("print_both_lines_for_matches")
            if b == None: b = 0
            self.printBothMatchesVar.set(b)

            b = c.config.getBool("print_matching_lines")
            if b == None: b = 0
            self.printMatchesVar.set(b)

            b = c.config.getBool("print_mismatching_lines")
            if b == None: b = 0
            self.printMismatchesVar.set(b)

            b = c.config.getBool("print_trailing_lines")
            if b == None: b = 0
            self.printTrailingMismatchesVar.set(b)

            n = c.config.getInt("limit_count")
            b = n and n > 0
            b = g.choose(b and b != 0,1,0)
            self.stopAfterMismatchVar.set(b)
            if b:
                e = self.countEntry
                e.delete(0,"end")
                e.insert(0,str(n))

            # bool options...
            for option,var,default in (
                # Whitespace options.
                ("ignore_blank_lines",self.ignoreBlankLinesVar,1),
                ("ignore_interior_whitespace",self.ignoreInteriorWhitespaceVar,0),
                ("ignore_leading_whitespace",self.ignoreLeadingWhitespaceVar,0),
                ("ignore_sentinel_lines",self.ignoreSentinelLinesVar,0),
                ("make_whitespace_visible", self.makeWhitespaceVisibleVar,0),
            ):
                b = c.config.getBool(option)
                if b is None: b = default
                var.set(b)

            if 0: # old code
                b = c.config.getBool("ignore_blank_lines")
                if b == None: b = 1 # unusual default.
                self.ignoreBlankLinesVar.set(b)

                b = c.config.getBool("ignore_interior_whitespace")
                if b == None: b = 0
                self.ignoreInteriorWhitespaceVar.set(b)

                b = c.config.getBool("ignore_leading_whitespace")
                if b == None: b = 0
                self.ignoreLeadingWhitespaceVar.set(b)

                b = c.config.getBool("ignore_sentinel_lines")
                if b == None: b = 0
                self.ignoreSentinelLinesVar.set(b)

                b = c.config.getBool("make_whitespace_visible")
                if b == None: b = 0
                self.makeWhitespaceVisibleVar.set(b)
        #@-node:bob.20070813163332.164:finishCreate (tkComparePanel)
        #@+node:bob.20070813163332.165:createFrame (tkComparePanel)
        def createFrame (self):

            gui = g.app.gui ; top = self.top

            #@    << create the organizer frames >>
            #@+node:bob.20070813163332.166:<< create the organizer frames >>
            outer = Tk.Frame(self.frame, bd=2,relief="groove")
            outer.pack(pady=4)

            row1 = Tk.Frame(outer)
            row1.pack(pady=4)

            row2 = Tk.Frame(outer)
            row2.pack(pady=4)

            row3 = Tk.Frame(outer)
            row3.pack(pady=4)

            row4 = Tk.Frame(outer)
            row4.pack(pady=4,expand=1,fill="x") # for left justification.

            options = Tk.Frame(outer)
            options.pack(pady=4)

            ws = Tk.Frame(options)
            ws.pack(side="left",padx=4)

            pr = Tk.Frame(options)
            pr.pack(side="right",padx=4)

            lower = Tk.Frame(outer)
            lower.pack(pady=6)
            #@-node:bob.20070813163332.166:<< create the organizer frames >>
            #@nl
            #@    << create the browser rows >>
            #@+node:bob.20070813163332.167:<< create the browser rows >>
            for row,text,text2,command,var in (
                (row1,"Compare path 1:","Ignore first line",self.onBrowse1,self.ignoreFirstLine1Var),
                (row2,"Compare path 2:","Ignore first line",self.onBrowse2,self.ignoreFirstLine2Var),
                (row3,"Output file:",   "Use output file",  self.onBrowse3,self.useOutputFileVar) ):

                lab = Tk.Label(row,anchor="e",text=text,width=13)
                lab.pack(side="left",padx=4)

                e = Tk.Entry(row)
                e.pack(side="left",padx=2)
                self.browseEntries.append(e)

                b = Tk.Button(row,text="browse...",command=command)
                b.pack(side="left",padx=6)

                b = Tk.Checkbutton(row,text=text2,anchor="w",variable=var,width=15)
                b.pack(side="left")
            #@-node:bob.20070813163332.167:<< create the browser rows >>
            #@nl
            #@    << create the extension row >>
            #@+node:bob.20070813163332.168:<< create the extension row >>
            b = Tk.Checkbutton(row4,anchor="w",var=self.limitToExtensionVar,
                text="Limit directory compares to type:")
            b.pack(side="left",padx=4)

            self.extensionEntry = e = Tk.Entry(row4,width=6)
            e.pack(side="left",padx=2)

            b = Tk.Checkbutton(row4,anchor="w",var=self.appendOutputVar,
                text="Append output to output file")
            b.pack(side="left",padx=4)
            #@-node:bob.20070813163332.168:<< create the extension row >>
            #@nl
            #@    << create the whitespace options frame >>
            #@+node:bob.20070813163332.169:<< create the whitespace options frame >>
            w,f = gui.create_labeled_frame(ws,caption="Whitespace options",relief="groove")

            for text,var in (
                ("Ignore Leo sentinel lines", self.ignoreSentinelLinesVar),
                ("Ignore blank lines",        self.ignoreBlankLinesVar),
                ("Ignore leading whitespace", self.ignoreLeadingWhitespaceVar),
                ("Ignore interior whitespace",self.ignoreInteriorWhitespaceVar),
                ("Make whitespace visible",   self.makeWhitespaceVisibleVar) ):

                b = Tk.Checkbutton(f,text=text,variable=var)
                b.pack(side="top",anchor="w")

            spacer = Tk.Frame(f)
            spacer.pack(padx="1i")
            #@-node:bob.20070813163332.169:<< create the whitespace options frame >>
            #@nl
            #@    << create the print options frame >>
            #@+node:bob.20070813163332.170:<< create the print options frame >>
            w,f = gui.create_labeled_frame(pr,caption="Print options",relief="groove")

            row = Tk.Frame(f)
            row.pack(expand=1,fill="x")

            b = Tk.Checkbutton(row,text="Stop after",variable=self.stopAfterMismatchVar)
            b.pack(side="left",anchor="w")

            self.countEntry = e = Tk.Entry(row,width=4)
            e.pack(side="left",padx=2)
            e.insert(01,"1")

            lab = Tk.Label(row,text="mismatches")
            lab.pack(side="left",padx=2)

            for padx,text,var in (
                (0,  "Print matched lines",           self.printMatchesVar),
                (20, "Show both matching lines",      self.printBothMatchesVar),
                (0,  "Print mismatched lines",        self.printMismatchesVar),
                (0,  "Print unmatched trailing lines",self.printTrailingMismatchesVar) ):

                b = Tk.Checkbutton(f,text=text,variable=var)
                b.pack(side="top",anchor="w",padx=padx)
                self.printButtons.append(b)

            # To enable or disable the "Print both matching lines" button.
            b = self.printButtons[0]
            b.configure(command=self.onPrintMatchedLines)

            spacer = Tk.Frame(f)
            spacer.pack(padx="1i")
            #@-node:bob.20070813163332.170:<< create the print options frame >>
            #@nl
            #@    << create the compare buttons >>
            #@+node:bob.20070813163332.171:<< create the compare buttons >>
            for text,command in (
                ("Compare files",      self.onCompareFiles),
                ("Compare directories",self.onCompareDirectories) ):

                b = Tk.Button(lower,text=text,command=command,width=18)
                b.pack(side="left",padx=6)
            #@-node:bob.20070813163332.171:<< create the compare buttons >>
            #@nl

            gui.center_dialog(top) # Do this _after_ building the dialog!
            self.finishCreate()
            top.protocol("WM_DELETE_WINDOW", self.onClose)
        #@-node:bob.20070813163332.165:createFrame (tkComparePanel)
        #@+node:bob.20070813163332.172:setIvarsFromWidgets
        def setIvarsFromWidgets (self):

            # File paths: checks for valid file name.
            e = self.browseEntries[0]
            self.fileName1 = e.get()

            e = self.browseEntries[1]
            self.fileName2 = e.get()

            # Ignore first line settings.
            self.ignoreFirstLine1 = self.ignoreFirstLine1Var.get()
            self.ignoreFirstLine2 = self.ignoreFirstLine2Var.get()

            # Output file: checks for valid file name.
            if self.useOutputFileVar.get():
                e = self.browseEntries[2]
                name = e.get()
                if name != None and len(name) == 0:
                    name = None
                self.outputFileName = name
            else:
                self.outputFileName = None

            # Extension settings.
            if self.limitToExtensionVar.get():
                self.limitToExtension = self.extensionEntry.get()
                if len(self.limitToExtension) == 0:
                    self.limitToExtension = None
            else:
                self.limitToExtension = None

            self.appendOutput = self.appendOutputVar.get()

            # Whitespace options.
            self.ignoreBlankLines         = self.ignoreBlankLinesVar.get()
            self.ignoreInteriorWhitespace = self.ignoreInteriorWhitespaceVar.get()
            self.ignoreLeadingWhitespace  = self.ignoreLeadingWhitespaceVar.get()
            self.ignoreSentinelLines      = self.ignoreSentinelLinesVar.get()
            self.makeWhitespaceVisible    = self.makeWhitespaceVisibleVar.get()

            # Print options.
            self.printMatches            = self.printMatchesVar.get()
            self.printMismatches         = self.printMismatchesVar.get()
            self.printTrailingMismatches = self.printTrailingMismatchesVar.get()

            if self.printMatches:
                self.printBothMatches = self.printBothMatchesVar.get()
            else:
                self.printBothMatches = False

            if self.stopAfterMismatchVar.get():
                try:
                    count = self.countEntry.get()
                    self.limitCount = int(count)
                except: self.limitCount = 0
            else:
                self.limitCount = 0
        #@-node:bob.20070813163332.172:setIvarsFromWidgets
        #@-node:bob.20070813163332.161:Birth...
        #@+node:bob.20070813163332.173:bringToFront
        def bringToFront(self):

            self.top.deiconify()
            self.top.lift()
        #@-node:bob.20070813163332.173:bringToFront
        #@+node:bob.20070813163332.174:browser
        def browser (self,n):

            types = [
                ("C/C++ files","*.c"),
                ("C/C++ files","*.cpp"),
                ("C/C++ files","*.h"),
                ("C/C++ files","*.hpp"),
                ("Java files","*.java"),
                ("Lua files", "*.lua"),
                ("Pascal files","*.pas"),
                ("Python files","*.py"),
                ("Text files","*.txt"),
                ("All files","*") ]

            fileName = tkFileDialog.askopenfilename(
                title="Choose compare file" + n,
                filetypes=types,
                defaultextension=".txt")

            if fileName and len(fileName) > 0:
                # The dialog also warns about this, so this may never happen.
                if not g.os_path_exists(fileName):
                    self.show("not found: " + fileName)
                    fileName = None
            else: fileName = None

            return fileName
        #@-node:bob.20070813163332.174:browser
        #@+node:bob.20070813163332.175:Event handlers...
        #@+node:bob.20070813163332.176:onBrowse...
        def onBrowse1 (self):

            fileName = self.browser("1")
            if fileName:
                e = self.browseEntries[0]
                e.delete(0,"end")
                e.insert(0,fileName)
            self.top.deiconify()

        def onBrowse2 (self):

            fileName = self.browser("2")
            if fileName:
                e = self.browseEntries[1]
                e.delete(0,"end")
                e.insert(0,fileName)
            self.top.deiconify()

        def onBrowse3 (self): # Get the name of the output file.

            fileName = tkFileDialog.asksaveasfilename(
                initialfile = self.defaultOutputFileName,
                title="Set output file",
                filetypes=[("Text files", "*.txt")],
                defaultextension=".txt")

            if fileName and len(fileName) > 0:
                self.defaultOutputFileName = fileName
                self.useOutputFileVar.set(1) # The user will expect this.
                e = self.browseEntries[2]
                e.delete(0,"end")
                e.insert(0,fileName)
        #@-node:bob.20070813163332.176:onBrowse...
        #@+node:bob.20070813163332.177:onClose
        def onClose (self):

            self.top.withdraw()
        #@-node:bob.20070813163332.177:onClose
        #@+node:bob.20070813163332.178:onCompare...
        def onCompareDirectories (self):

            self.setIvarsFromWidgets()
            self.compare_directories(self.fileName1,self.fileName2)

        def onCompareFiles (self):

            self.setIvarsFromWidgets()
            self.compare_files(self.fileName1,self.fileName2)
        #@-node:bob.20070813163332.178:onCompare...
        #@+node:bob.20070813163332.179:onPrintMatchedLines
        def onPrintMatchedLines (self):

            v = self.printMatchesVar.get()
            b = self.printButtons[1]
            state = g.choose(v,"normal","disabled")
            b.configure(state=state)
        #@-node:bob.20070813163332.179:onPrintMatchedLines
        #@-node:bob.20070813163332.175:Event handlers...
        #@-others
    #@-node:bob.20070813163332.160:wxComparePanel class (not ready yet)
    #@+node:bob.20070813163332.180:wxGui class
    class wxGui(leoGui.leoGui):

        #@    @+others
        #@+node:bob.20070813163332.181:gui birth & death
        #@+node:bob.20070813163332.182: wxGui.__init__
        def __init__ (self):

            #g.trace("wxGui")

            # Initialize the base class.
            if 1: # in plugin
                leoGui.leoGui.__init__(self,"wxPython")
            else:
                leoGui.__init__(self,"wxPython")

            self.bitmap_name = None
            self.bitmap = None

            self.use_stc = stc

            self.bodyTextWidget = g.choose(self.use_stc,stcTextWidget,richTextWidget)
            self.plainTextWidget = plainTextWidget

            self.extendGlobals()

            self.Tk_Text = Tk_Text()


            #@    @+others
            #@+node:bob.20080105082712:nav_buttons declarations
            self.listBoxDialog = wxListBoxDialog
            self.marksDialog = wxMarksDialog
            self.recentSectionsDialog = wxRecentSectionsDialog
            #@-node:bob.20080105082712:nav_buttons declarations
            #@-others
        #@-node:bob.20070813163332.182: wxGui.__init__
        #@+node:bob.20070830054714.1:extendGlobals


        def extendGlobals(self):

            #@    @+others
            #@+node:bob.20070830070902:alert

            def alert(*args, **kw):
                caption = kw.get('caption', 'Alert')
                g.trace(*args)
                msg = ' '.join([str(a) for a in args])
                g.es('\n%s' % msg, color='darkgreen')
                try:
                    dlg = wx.MessageDialog(None,msg,'Alert')
                    dlg.ShowModal()
                    dlg.Destroy()
                except:
                    pass

            g.alert = alert
            #@-node:bob.20070830070902:alert
            #@+node:bob.20070830080924:Tabs

            def getTab(tabName='Log'):

                app = g.app
                log = app.log
                if app.killed or not log or log.isNull:
                    return

                return log.getTab(tabName)

            g.getTab = getTab

            #@-node:bob.20070830080924:Tabs
            #@+node:bob.20070902141515:trace

            # oldtrace = g.trace
            # def trace(*args, **kw):
                # try:
                    # oldtrace(*args, **kw)
                # except :
                    # print 'unicode error in trace'

            # g.trace = trace

            #@-node:bob.20070902141515:trace
            #@-others



        #@-node:bob.20070830054714.1:extendGlobals
        #@+node:bob.20070813163332.183:createKeyHandlerClass
        def createKeyHandlerClass (self,c,useGlobalKillbuffer=True,useGlobalRegisters=True):

            return wxKeyHandlerClass(c,useGlobalKillbuffer,useGlobalRegisters)
        #@nonl
        #@-node:bob.20070813163332.183:createKeyHandlerClass
        #@+node:bob.20070830121134:createFocusManagerClass
        def createFocusManagerClass(self,c):

            return wxFocusManagerClass(c)
        #@nonl
        #@-node:bob.20070830121134:createFocusManagerClass
        #@+node:bob.20070813163332.184:createRootWindow
        def createRootWindow(self):

            self.wxApp = wxLeoApp(None)
            self.wxFrame = None

            if 0: # Not ready yet.
                self.setDefaultIcon()
                self.getDefaultConfigFont(g.app.config)
                self.setEncoding()
                self.createGlobalWindows()

            return self.wxFrame
        #@nonl
        #@-node:bob.20070813163332.184:createRootWindow
        #@+node:bob.20070813163332.185:createLeoFrame
        def createLeoFrame(self,title):

            """Create a new Leo frame."""

            return wxLeoFrame(title)
        #@nonl
        #@-node:bob.20070813163332.185:createLeoFrame
        #@+node:bob.20070813163332.186:destroySelf
        def destroySelf(self):

            pass # Nothing more needs to be done once all windows have been destroyed.
        #@nonl
        #@-node:bob.20070813163332.186:destroySelf
        #@+node:bob.20070813163332.187:finishCreate
        def finishCreate (self):

            pass
            # g.trace('gui',g.callers())
        #@-node:bob.20070813163332.187:finishCreate
        #@+node:bob.20070813163332.188:killGui
        def killGui(self,exitFlag=True):

            """Destroy a gui and terminate Leo if exitFlag is True."""

            pass # Not ready yet.

        #@-node:bob.20070813163332.188:killGui
        #@+node:bob.20070813163332.189:recreateRootWindow
        def recreateRootWindow(self):

            """A do-nothing base class to create the hidden root window of a gui

            after a previous gui has terminated with killGui(False)."""

            # g.trace('wx gui')
        #@-node:bob.20070813163332.189:recreateRootWindow
        #@+node:bob.20070813163332.190:runMainLoop
        def runMainLoop(self):

            """Run wx's main loop."""

            # g.trace("wxGui")
            self.wxApp.MainLoop()
            # g.trace("done")
        #@nonl
        #@-node:bob.20070813163332.190:runMainLoop
        #@-node:bob.20070813163332.181:gui birth & death
        #@+node:bob.20070813163332.191:gui dialogs
        #@+node:bob.20070813163332.192:runAboutLeoDialog
        def runAboutLeoDialog(self,c,version,copyright,url,email):

            """Create and run a wxPython About Leo dialog."""

            if  g.app.unitTesting: return

            message = "%s\n\n%s\n\n%s\n\n%s" % (
                version.strip(),copyright.strip(),url.strip(),email.strip())

            message += '\n\nwxLeo version: %s'%__version__

            wx.MessageBox(message,"About Leo",wx.Center,self.root)
        #@-node:bob.20070813163332.192:runAboutLeoDialog
        #@+node:bob.20070813163332.193:runAskOkDialog
        def runAskOkDialog(self,c,title,message=None,text="Ok"):

            """Create and run a wxPython askOK dialog ."""

            if  g.app.unitTesting:
                return 'ok'
            d = wx.MessageDialog(self.root, message, title, wx.OK)
            d.ShowModal()
            return "ok"
        #@nonl
        #@-node:bob.20070813163332.193:runAskOkDialog
        #@+node:bob.20070813163332.194:runAskLeoIDDialog
        def runAskLeoIDDialog(self):

            """Create and run a dialog to get g.app.LeoID."""

            if  g.app.unitTesting: return 'ekr'

            ### to do
        #@nonl
        #@-node:bob.20070813163332.194:runAskLeoIDDialog
        #@+node:bob.20070813163332.195:runAskOkCancelNumberDialog (to do)
        def runAskOkCancelNumberDialog(self,c,title,message):

            """Create and run a wxPython askOkCancelNumber dialog ."""

            if g.app.unitTesting: return 666

            ### to do.
        #@nonl
        #@-node:bob.20070813163332.195:runAskOkCancelNumberDialog (to do)
        #@+node:bob.20070813163332.196:runAskOkCancelStringDialog (to do)
        def runAskOkCancelStringDialog(self,c,title,message):

            """Create and run a wxPython askOkCancelNumber dialog ."""

            if  g.app.unitTesting: return 'xyzzy'

            # to do
        #@-node:bob.20070813163332.196:runAskOkCancelStringDialog (to do)
        #@+node:bob.20070813163332.197:runAskYesNoDialog
        def runAskYesNoDialog(self,c,title,message=None):

            """Create and run a wxPython askYesNo dialog."""

            if  g.app.unitTesting: return 'yes'

            d = wx.MessageDialog(self.root,message,"Leo",wx.YES_NO)
            answer = d.ShowModal()

            return g.choose(answer==wx.YES,"yes","no")
        #@nonl
        #@-node:bob.20070813163332.197:runAskYesNoDialog
        #@+node:bob.20070813163332.198:runAskYesNoCancelDialog
        def runAskYesNoCancelDialog(self,c,title,
            message=None,yesMessage="Yes",noMessage="No",defaultButton="Yes"):

            """Create and run a wxPython askYesNoCancel dialog ."""

            if  g.app.unitTesting: return 'yes'

            d = wx.MessageDialog(self.root,message,"Leo",wx.YES_NO | wx.CANCEL)
            answer = d.ShowModal()

            if answer == wx.ID_YES:
                return "yes"
            elif answer == wx.ID_NO:
                return "no"
            else:
                assert(answer == wx.ID_CANCEL)
                return "cancel"
        #@nonl
        #@-node:bob.20070813163332.198:runAskYesNoCancelDialog
        #@+node:bob.20070813163332.199:runCompareDialog
        def runCompareDialog (self,c):

            if  g.app.unitTesting: return

            # To do
        #@nonl
        #@-node:bob.20070813163332.199:runCompareDialog
        #@+node:bob.20070813163332.200:runOpenFileDialog

        def runOpenFileDialog(self, title,
            filetypes, defaultextension, multiple=False
        ):

            """Create and run a wxPython open file dialog ."""

            if  g.app.unitTesting: return None

            wildcard = self.getWildcardList(filetypes)


            d = wx.FileDialog(
                parent=None, message=title,
                defaultDir="", defaultFile="",
                wildcard=wildcard,
                style= wx.OPEN | wx.CHANGE_DIR | wx.HIDE_READONLY | bool(multiple) & wx.MULTIPLE)

            val = d.ShowModal()
            if val == wx.ID_OK:
                if multiple:
                    result = d.GetPaths()
                else:
                    result = d.GetPath()
                return result
            else:
                return None
        #@-node:bob.20070813163332.200:runOpenFileDialog
        #@+node:bob.20070813163332.201:runSaveFileDialog
        def runSaveFileDialog(self,initialfile,title,filetypes,defaultextension):

            """Create and run a wxPython save file dialog ."""

            if  g.app.unitTesting: return None

            wildcard = self.getWildcardList(filetypes)

            d = wx.FileDialog(
                parent=None, message=title,
                defaultDir="", defaultFile="",
                wildcard=wildcard,
                style= wx.SAVE | wx.CHANGE_DIR | wx.OVERWRITE_PROMPT)

            val = d.ShowModal()
            if val == wx.ID_OK:
                file = d.GetFilename()
                return file
            else:
                return None
        #@nonl
        #@-node:bob.20070813163332.201:runSaveFileDialog
        #@+node:bob.20080105081220:plugins_menu
        #@+others
        #@+node:bob.20071209182132.2:runPropertiesDialog
        def runPropertiesDialog(self, title='Properties', data={}, callback=None, buttons=None):
            """Dispay a modal wxPropertiesDialog"""

            dialog = wxPropertiesDialog(title, data, callback, buttons)

            return dialog.result
        #@-node:bob.20071209182132.2:runPropertiesDialog
        #@+node:bob.20071209182238:runScrolledMessageDialog
        def runScrolledMessageDialog(self,title='Message', label= '', msg='', callback=None, buttons=None):
            """Display a modal wxScrolledMessageDialog."""

            dialog = wxScrolledMessageDialog(title, label, msg, callback, buttons)

            return dialog.result
        #@-node:bob.20071209182238:runScrolledMessageDialog
        #@-others
        #@-node:bob.20080105081220:plugins_menu
        #@+node:bob.20070813163332.202:simulateDialog
        def simulateDialog (self,key,defaultVal=None):

            return defaultVal
        #@nonl
        #@-node:bob.20070813163332.202:simulateDialog
        #@+node:bob.20070813163332.203:getWildcardList
        def getWildcardList (self,filetypes):

            """Create a wxWindows wildcard string for open/save dialogs."""

            if not filetypes:
                return "*.leo"

            if 1: # Too bad: this is sooo wimpy.
                    a,b = filetypes[0]
                    return b

            else: # This _sometimes_ works: wxWindows is driving me crazy!

                # wildcards = ["%s (%s)" % (a,b) for a,b in filetypes]
                wildcards = ["%s" % (b) for a,b in filetypes]
                wildcard = "|".join(wildcards)
                g.trace(wildcard)
                return wildcard
        #@nonl
        #@-node:bob.20070813163332.203:getWildcardList
        #@-node:bob.20070813163332.191:gui dialogs
        #@+node:bob.20070813163332.9:gui events
        #@+node:bob.20070813163332.10:event_generate
        def event_generate(self,w,kind,*args,**keys):
            '''Generate an event.'''
            return w.event_generate(kind,*args,**keys)
        #@-node:bob.20070813163332.10:event_generate
        #@+node:bob.20070813163332.11:class leoKeyEvent (wxGui)
        class leoKeyEvent:

            '''A gui-independent wrapper for gui events.'''

            def __init__ (self,event,c):
                gui = g.app.gui
                self.c              = c
                self.actualEvent    = event
                self.char           = gui.eventChar(event)
                self.keysym         = gui.eventKeysym(event)
                self.widget         = gui.eventWidget(event)
                self.x,self.y       = gui.eventXY(event)
                self.w = self.widget

            def __repr__ (self):
                return 'leoKeyEvent char: %s keysym: %s widget: %s' % (
                    repr(self.char),self.keysym,self.widget)
        #@-node:bob.20070813163332.11:class leoKeyEvent (wxGui)
        #@+node:bob.20070813163332.12:wxKeyDict
        wxKeyDict = {
            # Keys are wxWidgets key codes.  Values are the standard (Tk) names.
            wx.WXK_DECIMAL  : '.',
            wx.WXK_BACK     : 'BackSpace',
            wx.WXK_TAB      : 'Tab',
            wx.WXK_RETURN   : 'Return',
            wx.WXK_ESCAPE   : 'Escape',
            wx.WXK_SPACE    : ' ',
            wx.WXK_DELETE   : 'Delete',
            wx.WXK_LEFT     : 'Left',
            wx.WXK_UP       : 'Up',
            wx.WXK_RIGHT    : 'Right',
            wx.WXK_DOWN     : 'Down',
            wx.WXK_F1       : 'F1',
            wx.WXK_F2       : 'F2',
            wx.WXK_F3       : 'F3',
            wx.WXK_F4       : 'F4',
            wx.WXK_F5       : 'F5',
            wx.WXK_F6       : 'F6',
            wx.WXK_F7       : 'F7',
            wx.WXK_F8       : 'F8',
            wx.WXK_F9       : 'F9',
            wx.WXK_F10      : 'F10',
            wx.WXK_F11      : 'F11',
            wx.WXK_F12      : 'F12',
            wx.WXK_END                  : 'End',
            wx.WXK_HOME                 : 'Home',
            wx.WXK_PAGEUP               : 'Prior',
            wx.WXK_PAGEDOWN             : 'Next',
            wx.WXK_NUMPAD_DELETE        : 'Delete',
            wx.WXK_NUMPAD_SPACE         : ' ',
            wx.WXK_NUMPAD_TAB           : '\t', # 'Tab',
            wx.WXK_NUMPAD_ENTER         : '\n', # 'Return',
            wx.WXK_NUMPAD_PAGEUP        : 'Prior',
            wx.WXK_NUMPAD_PAGEDOWN      : 'Next',
            wx.WXK_NUMPAD_END           : 'End',
            wx.WXK_NUMPAD_BEGIN         : 'Home',
        }

        #@+at
        # These are by design not compatible with unicode characters.
        # If you want to get a unicode character from a key event use
        # wxKeyEvent::GetUnicodeKey instead.
        # 
        # WXK_START   = 300
        # WXK_LBUTTON
        # WXK_RBUTTON
        # WXK_CANCEL
        # WXK_MBUTTON
        # WXK_CLEAR
        # WXK_SHIFT
        # WXK_ALT
        # WXK_CONTROL
        # WXK_MENU
        # WXK_PAUSE
        # WXK_CAPITAL
        # WXK_SELECT
        # WXK_PRINT
        # WXK_EXECUTE
        # WXK_SNAPSHOT
        # WXK_INSERT
        # WXK_HELP
        # WXK_NUMPAD0
        # WXK_NUMPAD1
        # WXK_NUMPAD2
        # WXK_NUMPAD3
        # WXK_NUMPAD4
        # WXK_NUMPAD5
        # WXK_NUMPAD6
        # WXK_NUMPAD7
        # WXK_NUMPAD8
        # WXK_NUMPAD9
        # WXK_MULTIPLY
        # WXK_ADD
        # WXK_SEPARATOR
        # WXK_SUBTRACT
        # WXK_DECIMAL
        # WXK_DIVIDE
        # WXK_F13
        # WXK_F14
        # WXK_F15
        # WXK_F16
        # WXK_F17
        # WXK_F18
        # WXK_F19
        # WXK_F20
        # WXK_F21
        # WXK_F22
        # WXK_F23
        # WXK_F24
        # WXK_NUMLOCK
        # WXK_SCROLL
        # WXK_NUMPAD_F1,
        # WXK_NUMPAD_F2,
        # WXK_NUMPAD_F3,
        # WXK_NUMPAD_F4,
        # WXK_NUMPAD_HOME,
        # WXK_NUMPAD_LEFT,
        # WXK_NUMPAD_UP,
        # WXK_NUMPAD_RIGHT,
        # WXK_NUMPAD_DOWN,
        # WXK_NUMPAD_INSERT,
        # WXK_NUMPAD_EQUAL,
        # WXK_NUMPAD_MULTIPLY,
        # WXK_NUMPAD_ADD,
        # WXK_NUMPAD_SEPARATOR,
        # WXK_NUMPAD_SUBTRACT,
        # WXK_NUMPAD_DECIMAL,
        # WXK_NUMPAD_DIVIDE,
        # 
        # // the following key codes are only generated under Windows
        # currently
        # WXK_WINDOWS_LEFT,
        # WXK_WINDOWS_RIGHT,
        # WXK_WINDOWS_MENU,
        # WXK_COMMAND,
        # 
        # // Hardware-specific buttons
        # WXK_SPECIAL1 = 193,
        # WXK_SPECIAL2,
        # WXK_SPECIAL3,
        # WXK_SPECIAL4,
        # WXK_SPECIAL5,
        # WXK_SPECIAL6,
        # WXK_SPECIAL7,
        # WXK_SPECIAL8,
        # WXK_SPECIAL9,
        # WXK_SPECIAL10,
        # WXK_SPECIAL11,
        # WXK_SPECIAL12,
        # WXK_SPECIAL13,
        # WXK_SPECIAL14,
        # WXK_SPECIAL15,
        # WXK_SPECIAL16,
        # WXK_SPECIAL17,
        # WXK_SPECIAL18,
        # WXK_SPECIAL19,
        # WXK_SPECIAL20
        #@-at
        #@nonl
        #@-node:bob.20070813163332.12:wxKeyDict
        #@+node:bob.20070813163332.13:eventChar & eventKeysym & helper
        def eventChar (self,event):

            '''Return the char field of an event, either a wx event or a converted Leo event.'''

            if not event:
                return event

            if hasattr(event,'char'):
                return event.char # A leoKeyEvent.
            else:
                return self.keysymHelper(event,kind='char')

        def eventKeysym (self,event,c=None):

            if not event:
                return event

            if hasattr(event,'keysym'):
                return event.keysym # A leoKeyEvent: we have already computed the result.
            else:
                return self.keysymHelper(event,kind='keysym')
        #@+node:bob.20070813163332.14:keysymHelper & helpers

        # Modified from LogKeyEvent in wxPython demo.

        def keysymHelper(self,event,kind):

            keycode = event.GetKeyCode()
            #g.trace(keycode)
            if keycode in (wx.WXK_SHIFT,wx.WXK_ALT,wx.WXK_CONTROL):
                return ''

            alt,cmd,ctrl,meta,shift = self.getMods(event)
            special = alt or cmd or ctrl or meta
            if special and kind == 'char':
                return '' # The char for all special keys.

            unicode = "unicode" in wx.PlatformInfo

            if unicode:
                ucode = event.GetUnicodeKey()
                if ucode <= 127:
                    ucode = keycode
            else:
                ucode = keycode

            uchar = unichr(ucode)
            keyname = g.app.gui.wxKeyDict.get(keycode)
            w = self.eventWidget(event)

            #g.trace('code=%d, char=%s, isStc=%s, unichr=%s'%(ucode, uchar, isStc, unichr(event.GetUnicodeKey())))

            if keyname is None:
                if 0 < keycode < 27:
                    # EKR: Follow Tk conventions.
                    if shift:
                        keyname = chr(ord('A') + keycode-1) # Return Ctrl+Z
                    else:
                        keyname = chr(ord('a') + keycode-1) # Return Ctrl+z
                    shift = False ; ctrl = True ; special = True

                elif unicode:

                   keyname = uchar

                else:

                    g.trace('no unicode')
                    # No unicode support.
                    if keycode == 0:
                        keyname = "NUL" # dubious.
                    elif keycode < 256:
                        keyname = chr(keycode)
                    else:
                        keyname = "unknown (%s)" % keycode

            # Return Key- (not Key+) to match the corresponding Tk hack.
            if alt and keyname.isdigit():
                keyname = 'Key-' + keyname

            # Create a value compatible with Leo's core.
            val = (
                g.choose(alt,'Alt+','') +
                # g.choose(cmd,'Cmd+','') +
                g.choose(ctrl,'Ctrl+','') +
                g.choose(meta,'Meta+','') +
                g.choose(shift and (special or len(keyname)>1),'Shift+','') +
                keyname or ''
            )

            if 0:
                g.trace('shift',shift,
                    'keycode',repr(keycode),'ucode',ucode,
                    'uchar',repr(uchar),'keyname',repr(keyname),'val',repr(val))

            return val
        #@+node:bob.20070813163332.15:getMods
        def getMods (self,event):

            mods = event.GetModifiers()

            alt = event.AltDown()     or mods == wx.MOD_ALT
            cmd = event.CmdDown()     or mods == wx.MOD_CMD
            ctrl = event.ControlDown()or mods == wx.MOD_CONTROL
            meta = event.MetaDown()   or mods == wx.MOD_META
            shift = event.ShiftDown() or mods == wx.MOD_SHIFT

            return alt,cmd,ctrl,meta,shift
        #@-node:bob.20070813163332.15:getMods
        #@-node:bob.20070813163332.14:keysymHelper & helpers
        #@-node:bob.20070813163332.13:eventChar & eventKeysym & helper
        #@+node:bob.20070813163332.18:eventWidget
        def eventWidget (self,event):

            '''Return the widget field of an event.
            The event may be a wx event a converted Leo event or a manufactured event (a g.Bunch).'''

            if hasattr(event,'leoWidget'):
                return event.leoWidget
            elif isinstance(event,self.leoKeyEvent): # a leoKeyEvent.
                return event.widget
            elif isinstance(event,g.Bunch): # A manufactured event.
                if hasattr(event,'widget'):
                    w = event.widget
                    if hasattr(w,'leo_wrapper_object'):
                        # g.trace('Returning wrapper object',w.leo_wrapper_object)
                        return w.leo_wrapper_object
                    else:
                        return w
                if hasattr(event,'c'):
                    return event.c.frame.body.bodyCtrl
                else:
                    #g.trace('wx gui: k.generalModeHandler event: no event widget: event = %s' % (event),g.callers())
                    return None
            elif hasattr(event,'GetEventObject'): # A wx Event.
                # Return the wrapper class
                w = event.GetEventObject()
                if hasattr(w,'leo_wrapper_object'):
                    # g.trace('Returning wrapper object',w.leo_wrapper_object)
                    return w.leo_wrapper_object
                else:
                    return w
            else:
                g.trace('no event widget',event)
                return None
        #@-node:bob.20070813163332.18:eventWidget
        #@+node:bob.20070813163332.19:eventXY
        def eventXY (self,event,c=None):

            if hasattr(event,'x') and hasattr(event,'y'):
                return event.x,event.y
            if hasattr(event,'GetX') and hasattr(event,'GetY'):
                return event.GetX(),event.GetY()
            else:
                return 0,0
        #@-node:bob.20070813163332.19:eventXY
        #@-node:bob.20070813163332.9:gui events
        #@+node:bob.20070813163332.204:gui panels (to do)
        #@+node:bob.20070813163332.205:createColorPanel
        def createColorPanel(self,c):

            """Create Color panel."""

            g.trace("not ready yet")
        #@nonl
        #@-node:bob.20070813163332.205:createColorPanel
        #@+node:bob.20070813163332.206:createComparePanel
        def createComparePanel(self,c):

            """Create Compare panel."""

            g.trace("not ready yet")
        #@nonl
        #@-node:bob.20070813163332.206:createComparePanel
        #@+node:bob.20070813163332.207:createFindPanel
        def createFindPanel(self):

            """Create a hidden Find panel."""

            return wxFindFrame()
        #@nonl
        #@-node:bob.20070813163332.207:createFindPanel
        #@+node:bob.20070813163332.208:createFindTab
        def createFindTab (self,c,parentFrame):

            '''Create a wxWidgets find tab in the indicated frame.'''

            frame = c.frame

            if not frame.findTabHandler:
                frame.findTabHandler = wxFindTab(c,parentFrame)

            return frame.findTabHandler
        #@nonl
        #@-node:bob.20070813163332.208:createFindTab
        #@+node:bob.20070813163332.209:createFontPanel
        def createFontPanel(self,c):

            """Create a Font panel."""

            g.trace("not ready yet")
        #@nonl
        #@-node:bob.20070813163332.209:createFontPanel
        #@+node:bob.20070813163332.210:createSpellTab
        def createSpellTab (self,c,parentFrame):

            '''Create a wxWidgets spell tab in the indicated frame.'''

            frame = c.frame

            if not frame.spellTabHandler:
                frame.spellTabHandler = wxSpellTab(c,parentFrame)

            return frame.spellTabHandler
        #@-node:bob.20070813163332.210:createSpellTab
        #@+node:bob.20070813163332.211:destroyLeoFrame (NOT USED)
        def destroyLeoFrame (self,frame):

            frame.Close()
        #@nonl
        #@-node:bob.20070813163332.211:destroyLeoFrame (NOT USED)
        #@-node:bob.20070813163332.204:gui panels (to do)
        #@+node:bob.20070813163332.212:gui utils (must add several)
        #@+node:bob.20070813163332.213:Clipboard
        def replaceClipboardWith (self,s):
            #g.trace(s)

            cb = wx.TheClipboard
            if cb.Open():
                #g.trace('is open')
                cb.Clear()
                cb.SetData(wx.TextDataObject(s))
                cb.Close()
            else:
                #g.trace('is CLOSED')
                pass

        def getTextFromClipboard (self):

            cb = wx.TheClipboard
            if cb.Open():
                data = wx.TextDataObject()
                ok = cb.GetData(data)
                cb.Close()
                return ok and data.GetText() or ''
            else:
                return ''
        #@-node:bob.20070813163332.213:Clipboard
        #@+node:bob.20070813163332.214:Constants
        # g.es calls gui.color to do the translation,
        # so most code in Leo's core can simply use Tk color names.

        def color (self,color):
            '''Return the gui-specific color corresponding to the Tk color name.'''
            return name2color(color)
        #@-node:bob.20070813163332.214:Constants
        #@+node:bob.20070813163332.215:Dialog
        #@+node:bob.20070813163332.216:bringToFront
        def bringToFront (self,window):

            if window.IsIconized():
                window.Maximize()
            window.Raise()
            window.Show(True)
        #@nonl
        #@-node:bob.20070813163332.216:bringToFront
        #@+node:bob.20070813163332.217:get_window_info
        def get_window_info(self,window):

            # Get the information about top and the screen.
            x,y = window.GetPosition()
            w,h = window.GetSize()

            return w,h,x,y
        #@nonl
        #@-node:bob.20070813163332.217:get_window_info
        #@+node:bob.20070813163332.218:center_dialog
        def center_dialog(window):

            window.Center()
        #@nonl
        #@-node:bob.20070813163332.218:center_dialog
        #@-node:bob.20070813163332.215:Dialog
        #@+node:bob.20070813163332.219:Focus (gui)
        def get_focus(self,c):

            return c.frame.body.bodyCtrl.findFocus()

        def set_focus(self,c,w):

            c.frame.setFocus(w)
        #@-node:bob.20070813163332.219:Focus (gui)
        #@+node:bob.20070813163332.220:Font (wxGui) (to do)
        #@+node:bob.20070813163332.221:getFontFromParams
        def getFontFromParams(self,family,size,slant,weight):

            # g.trace(g.app.config.defaultFont)


            family_name = family

            try:
                #fake tkFont
                font = tkFont.Font(family=family,size=size,slant=slant,weight=weight)

                #g.trace(g.callers())
                #print '\t', family,size,slant,weight
                #print '\t', "actual_name:", font.cget("family")
                #print '\tdefault-font:', g.app.config.defaultFont
                #return g.app.config.defaultFont ##
                return font
            except:
                #g.es("family,size,slant,weight:"+
                #   `family`+':'+`size`+':'+`slant`+':'+`weight`)
                #g.es_exception()
                return g.app.config.defaultFont
        #@-node:bob.20070813163332.221:getFontFromParams
        #@-node:bob.20070813163332.220:Font (wxGui) (to do)
        #@+node:bob.20070813163332.226:Idle time (wxGui)
        #@+node:bob.20070813163332.227:setIdleTimeHook
        def setIdleTimeHook (self,idleTimeHookHandler,*args,**keys):

            wx.CallAfter(idleTimeHookHandler, *args, **keys)

        #@-node:bob.20070813163332.227:setIdleTimeHook
        #@+node:bob.20070813163332.228:setIdleTimeHookAfterDelay
        def setIdleTimeHookAfterDelay (self,idleTimeHookHandler,*args,**keys):

            wx.CallLater(g.app.idleTimeDelay,idleTimeHookHandler, *args, **keys)
        #@nonl
        #@-node:bob.20070813163332.228:setIdleTimeHookAfterDelay
        #@+node:bob.20080106175313:update_idletasks
        def update_idletasks(self, *args, **kw):
            #g.trace(g.callers())
            wx.SafeYield(onlyIfNeeded=True)
        #@nonl
        #@-node:bob.20080106175313:update_idletasks
        #@-node:bob.20070813163332.226:Idle time (wxGui)
        #@+node:bob.20070813163332.53:isTextWidget
        def isTextWidget (self,w):

            return isinstance(w, baseTextWidget)

        #@-node:bob.20070813163332.53:isTextWidget
        #@+node:bob.20070813163332.229:widget_name
        def widget_name (self,w):
            """Returns the name of widget w.

            First try the (gui)LeoObject getName method.
            Second try wx widgets GetName method.
            Third use repr(w)
            """

            #g.trace(w)

            if hasattr(w, 'getName'):
                #print '\t ', w.getName()
                return w.getName()

            if hasattr(w, 'GetName'):
                #print '\t', w.GetName()
                return w.GetName()


            #g.trace('Object Has no name:\n\t', w)
            #print '\trepr(w) = ', repr(w)
            return repr(w)
        #@-node:bob.20070813163332.229:widget_name
        #@-node:bob.20070813163332.212:gui utils (must add several)
        #@+node:bob.20080105181202:getImage
        def getImage (self, c, relPath, force=False):


            basepath = g.os_path_normpath(g.os_path_join(g.app.loadDir,"..","Icons"))


            if not force and relPath in globalImages:
                image = globalImages[relPath]
                g.es('cach ', image, image.GetHeight(), color='magenta')
                return image, image.GetHeight()

            try:
                path = g.os_path_normpath(g.os_path_join(g.app.loadDir,"..","Icons", relPath))
                globalImages[relPath] = image = wx.BitmapFromImage(wx.Image(path))
                return image

            except Exception:
                pass

            try:
                path = g.os_path_normpath(relPath)
                localImages[relPath] =  image = wx.BitmapFromImage(wx.Image(path))
                return image
            except Exception:
                pass

            return None
        #@-node:bob.20080105181202:getImage
        #@-others
    #@nonl
    #@-node:bob.20070813163332.180:wxGui class
    #@+node:bob.20070813163332.230:wxKeyHandlerClass (keyHandlerClass)
    class wxKeyHandlerClass (leoKeys.keyHandlerClass):

        '''wxWidgets overrides of base keyHandlerClass.'''

        #@    @+others
        #@+node:bob.20070813163332.231:__init__
        def __init__(self,c,useGlobalKillbuffer=False,useGlobalRegisters=False):

            #g.trace('wxKeyHandlerClass',g.callers())

            self.widget = None # Set in finishCreate.

            # Init the base class.
            leoKeys.keyHandlerClass.__init__(self,c,useGlobalKillbuffer,useGlobalRegisters)
        #@-node:bob.20070813163332.231:__init__
        #@+node:bob.20070813163332.232:finishCreate

        def finishCreate (self):

            k = self ; c = k.c



            leoKeys.keyHandlerClass.finishCreate(self) # Call the base class.

            # In the Tk version, this is done in the editor logic.
            c.frame.body.createBindings(w=c.frame.body.bodyCtrl)

            # k.dumpMasterBindingsDict()

            self.widget = c.frame.minibuffer.ctrl

            self.setLabelGrey()

        #@-node:bob.20070813163332.232:finishCreate
        #@+node:bob.20070823090727:propagateKeyEvent
        def propagateKeyEvent (self,event):
            g.trace()
            if event and event.actualEvent:
                event.actualEvent.Skip()
        #@nonl
        #@-node:bob.20070823090727:propagateKeyEvent
        #@+node:bob.20070829204339:fullCommand

        def fullCommand(self, *args, **kw):
            #g.trace('overidden')
            self.c.minibufferWantsFocus()
            return leoKeys.keyHandlerClass.fullCommand(self, *args, **kw)
        #@nonl
        #@-node:bob.20070829204339:fullCommand
        #@+node:bob.20070901124034:masterCommand
        def masterCommand(self, *args, **kw):
            # print
            # print
            # print '================='
            # g.trace('overidden')
            # print '================='
            # print pprint(args)
            # print '-----------------'
            # pprint(kw)
            # print '================='
            # print
            # print
            result =  leoKeys.keyHandlerClass.masterCommand(self, *args, **kw)
            self.c.beginUpdate()
            self.c.endUpdate()
            return result

        #@-node:bob.20070901124034:masterCommand
        #@+node:bob.20070830065423:universalDispatcher

        def universalDispatcher(self, *args, **kw):
            #g.trace('overidden')
            self.c.minibufferWantsFocus()
            return leoKeys.keyHandlerClass.universalDispatcher(self, *args, **kw)
        #@nonl
        #@-node:bob.20070830065423:universalDispatcher
        #@+node:bob.20070901065753:handleDefaultChar
        def handleDefaultChar(self,event,stroke):
            """Handle default actions for keystrokes not defined elsewhere.

            If event is not none then it will be used to find the window
            which caused the event otherwise the currently focused
            window will be used.

            If none is returned then the caller should call event.Skip()
            to allow the gui to handle the keystroke itself.

            """

            k = self ; c = k.c


            # try:
               # g.trace('=== eventwidget ===',event.widget)
               # g.trace('===   stroke    ===', stroke)
               # g.trace('callers:', g.callers())
            # except:
               # g.trace('no event!')
               # pass



            #g.trace('focus:', self.c.get_focus())

            if event:
                w = event.widget
            else:
                w = c.get_focus()

            #print '\ttarget:', w

            name = c.widget_name(w)

            #g.trace('NAME', name)



            if name.startswith('body'):

                #<< handle char for body

                #g.trace('body')
                action = k.unboundKeyAction
                if action in ('insert','overwrite'):
                    c.editCommands.selfInsertCommand(event,action=action)
                    return 'break'

                return None

                #>>

            elif name.startswith('head'):

                #<< handle chars for headlines

                #g.trace('head')
                c.frame.tree.onHeadlineKey(event)
                return 'break'

                #>>

            elif name.startswith('canvas'):

                #<< handle chars for tree canvas

                #g.trace('canvas')
                if not stroke: # Not exactly right, but it seems to be good enough.
                    c.onCanvasKey(event) # New in Leo 4.4.2
                return 'break'

                #>>

            elif name.startswith('log'):

                #<< handle chars for log panes

                #FIXME


                # c.onLogKey(event)
                #g.trace('log')
                pass

                #>>

            elif name.startswith('find') or name.startswith('change'):

                #<< handle chars for find\change entry

                #FIXME
                # c.onFindKey

                # Intercept return and tab chars.


                keysym = g.app.gui.eventKeysym(event)

                #g.trace('\tfind KEYSYM', keysym)

                if keysym == 'Return':
                    #g.trace('\tFOUND RETURN')
                    w.leoParent.findNextCommand()
                    return 'break'

                if keysym == 'Tab':
                    #g.trace('\tFOUND TAB')
                    w.leoParent.toggleTextWidgetFocus(w)
                    return 'break'


                #g.trace('NO SPECIAL CHARS FOUND FOR FIND')
                return None

                #>>

            else:
                # Allow wx to handle the event.
                # ch = event and event.char ; g.trace('to wx:',name,repr(ch))
                #g.trace('no default key handler')
                return None
        #@-node:bob.20070901065753:handleDefaultChar
        #@+node:bob.20070830134722:setLabel
        def setLabel (self,s,protect=False):

            k = self ; c = k.c

            self.isDisplay = False

            w = self.widget

            if not w:
                return

            trace = True or self.trace_minibuffer and not g.app.unitTesting

            trace and g.trace(repr(s),g.callers(30))

            w.setAllText(s)
            n = len(s)
            #w.SetFocus()
            c.minibufferWantsFocusNow()
            w.setSelectionRange(n,n,insert=n)
            #c.masterFocusHandler() # Restore to the previously requested focus.

            if protect:
                k.mb_prefix = s
        #@-node:bob.20070830134722:setLabel
        #@+node:bob.20070830175514:setLabelGrey
        def setLabelGrey (self,label=None):

            self.labelIsEmpty = bool(label and label.strip())
            self.isDisplay = True

            c = self.c; k = self ; w = self.widget
            if not w: return

            w.setBackgroundColor(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DFACE))

            if label is not None:
                k.setLabel(label)

            c.bodyWantsFocusNow()
            c.masterFocusHandler()

        setLabelGray = setLabelGrey
        #@-node:bob.20070830175514:setLabelGrey
        #@-others
    #@nonl
    #@-node:bob.20070813163332.230:wxKeyHandlerClass (keyHandlerClass)
    #@+node:bob.20070830121134.1:wxFocusManagerClass
    #@<< _focusHistory class >>
    #@+node:bob.20070901193129:<<_focusHistory class>>

    class _focusHistory(object):

        def __init__(self, max=None, log=False):
            self.__stk = []
            self.__log = bool(log)
            if not max:
                if log:
                    max = 100
                else:
                    max = 10
            self.__max = max

        def __str__(self):
            name = 'stack'
            if self.__log:
                name = 'log'
            return '<%s: %s>' % (name, self.__stk)
        __repr__ = __str__

        def push(self, item):
            stk = self.__stk
            if not stk or (stk[-1] is not item):
                stk.append(item)
            del stk[:-self.__max]

        def pop(self, o=None):
            stk = self.__stk
            if self.__log:
                return stk and stk[-1]
            return stk and (stk[-1] is o) and stk.pop(-1)

        def top(self):
            stk = self.__stk
            return stk and stk[-1]

        def clear(self):
            self.__stk = []


        stk = property(lambda self: self._skt[:])
        log = property(lambda self: self.__log)

    #@-node:bob.20070901193129:<<_focusHistory class>>
    #@nl

    class wxFocusManagerClass(object):

        #@    @+others
        #@+node:bob.20070901193129.1:__init__
        def __init__(self, c):

            self.c = c

            for s in (
                'stayInTreeAfterEditHeadline',
                'outline_pane_has_initial_focus',
                'stayInTreeAfterSelect'
            ):
                setattr(self, s, c.config.getBool(s))

            self.stack = _focusHistory()
            self.log = _focusHistory(log=True)



        #@-node:bob.20070901193129.1:__init__
        #@+node:bob.20070901193129.2:gotFocus

        def gotFocus(self, o, event):
            #g.trace(self.c.widget_name(o))

            self.log.push(o)
            self.stack.push(o)

            if 0:
                print
                g.trace( self.log)
                print
                #g.trace( self.stack)
                #print
            event.Skip()
        #@-node:bob.20070901193129.2:gotFocus
        #@+node:bob.20070901193129.3:lostFocus

        def lostFocus(self, o, event):
            #g.trace(o)

            self.stack.pop(o)
            if 0:
                print
                g.trace( self.log)
                print
                g.trace( self.stack)
                print
            event.Skip()


        #@-node:bob.20070901193129.3:lostFocus
        #@+node:bob.20070901193129.5:setFocus
        def setFocus(self, o):
             o.SetFocus()

        SetFocus = setFocus
        #@-node:bob.20070901193129.5:setFocus
        #@+node:bob.20070901193129.6:chooseBodyOfOutline
        def chooseBodyOrOutline(self):
            #g.trace()
            c = self.c
            c.set_focus(g.choose(
                self.outline_pane_has_initial_focus,
                c.frame.tree.treeCtrl, c.frame.body.bodyCtrl
            ))
        #@nonl
        #@-node:bob.20070901193129.6:chooseBodyOfOutline
        #@+node:bob.20080102183111:lastFocus
        def lastFocus(self):

            o = self.log.pop()
            self.setFocus(o)
        #@-node:bob.20080102183111:lastFocus
        #@-others


    #@-node:bob.20070830121134.1:wxFocusManagerClass
    #@+node:bob.20070813163332.234:wxLeoApp class
    class wxLeoApp (wx.App):
        #@    @+others
        #@+node:bob.20070813163332.5:OnInit  (wxLeoApp)
        def OnInit(self):

            self.SetAppName("Leo")

            wx.InitAllImageHandlers()

            #globals icons, plusBoxIcon, minusBoxIcon, appIcon
            self.loadIcons()

            #self.Bind(wx.EVT_CHAR, lambda event, type='app':onRogueChar(event, type))



            return True
        #@-node:bob.20070813163332.5:OnInit  (wxLeoApp)
        #@+node:bob.20070815070127:loadIcons


        def loadIcons(self):

            global icons, plusBoxIcon, minusBoxIcon, appIcon, namedIcons

            import cStringIO

            def loadIcon(fname, type=wx.BITMAP_TYPE_ANY):

                icon = wx.BitmapFromImage(wx.Image(fname, type))

                if icon and icon.GetWidth()>0:
                    return icon

                print 'Can not load icon from', fname

            icons = []
            namedIcons = {}


            path = g.os_path_abspath(g.os_path_join(g.app.loadDir, '..', 'Icons'))
            if g.os_path_exists(g.os_path_join(path, 'box01.GIF')):
                ext = '.GIF'
            else:
                ext = '.gif'

            for i in range(16):
                icon = loadIcon(g.os_path_join(path, 'box%02d'%i + ext))
                icons.append(icon)



            for name in (
                'lt_arrow_enabled',
                'rt_arrow_enabled',
                'lt_arrow_disabled',
                'rt_arrow_disabled'
            ):
                icon = loadIcon(g.os_path_join(path, name + '.gif'))
                if icon:
                    namedIcons[name] = icon



            plusnode_data = '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\t\x00\x00\x00\t\x08\x02\x00\x00\x00o\xf3\x91G\x00\x00\x00\x03sBIT\x08\x08\x08\xdb\xe1O\xe0\x00\x00\x00>IDAT\x08\x99\x85\x8f1\x0e\x00 \x08\x03[\xc3\xbf\xe9\xcfq`\x105h\xa7^.%\x81\xee\x8e&\x06@\xd2-$\x8d\xca$+\x0e\xf4\xb1c\x91%"\x96K \x99\xe5\x7fssu\x04\x80\x8f\xff&NC\x12\x11\x18\x0c\xfa\n\x00\x00\x00\x00IEND\xaeB`\x82'

            minusnode_data = '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\t\x00\x00\x00\t\x08\x02\x00\x00\x00o\xf3\x91G\x00\x00\x00\x03sBIT\x08\x08\x08\xdb\xe1O\xe0\x00\x00\x009IDAT\x08\x99\x95\x8f\xc1\n\x000\x08Bu\xf4\xdf\xf9\xe7\xed\xd0a\x83\x910/\x92\x0f\x03\x99\x99\x18\x14\x00$\xbd@\xd2\x9aJ\x00\x1c\x8b6\x92wZU\x87\xf5\xf1\xf1\xd31\x9a}\x1b\xb0\x07\x0c\x0e\x8e\xe2\xc5\xf1\x00\x00\x00\x00IEND\xaeB`\x82'

            def bitmapfromdata(data):
                return wx.BitmapFromImage(
                     wx.ImageFromStream(cStringIO.StringIO(data))
                )


            minusBoxIcon = bitmapfromdata(minusnode_data)
            plusBoxIcon = bitmapfromdata(plusnode_data)
        #@-node:bob.20070815070127:loadIcons
        #@+node:bob.20070813163332.235:OnExit
        def OnExit(self):

            return True
        #@-node:bob.20070813163332.235:OnExit
        #@-others
    #@-node:bob.20070813163332.234:wxLeoApp class
    #@+node:bob.20070813163332.236:wxLeoBody class (leoBody)
    class wxLeoBody (leoFrame.leoBody):

        """A class to create a wxPython body pane."""

        #@    @+others
        #@+node:bob.20070813163332.237:Birth & death (wxLeoBody)
        #@+node:bob.20070813163332.238:wxBody.__init__
        def __init__ (self, c, parentFrame):

            self.c = c
            frame = c.frame

            # Init the base class: calls createControl.
            leoFrame.leoBody.__init__(self,frame,parentFrame)

            self.trace_onBodyChanged = c.config.getBool('trace_onBodyChanged')
            self.bodyCtrl = self.createControl(frame,parentFrame)

            self.colorizer = leoColor.colorizer(self.c)

            self.keyDownModifiers = None
            self.forceFullRecolorFlag = False
        #@-node:bob.20070813163332.238:wxBody.__init__
        #@+node:bob.20070813163332.239:wxBody.createControl
        def createControl (self,frame,parentFrame):

            w = g.app.gui.bodyTextWidget(
                self,
                parentFrame,
                name='body' # Must be body for k.masterKeyHandler.
            )

            #w.widget.Bind(wx.EVT_LEFT_DOWN, self.onClick)


            return w
        #@-node:bob.20070813163332.239:wxBody.createControl
        #@+node:bob.20070813163332.240:wxBody.createBindings NOT USED AT PRESENT
        def createBindings (self,w=None):

            '''(wxBody) Create gui-dependent bindings.
            These are *not* made in nullBody instances.'''


            #FIXME

            return ###

            frame = self.frame ; c = self.c ; k = c.k
            if not w: w = self.bodyCtrl

            # g.trace('wxBody')

            w.bind('<Key>', k.masterKeyHandler)

            for kind,func,handler in (
                #('<Button-1>',  frame.OnBodyClick,          k.masterClickHandler),
                #('<Button-3>',  frame.OnBodyRClick,         k.masterClick3Handler),
                #('<Double-1>',  frame.OnBodyDoubleClick,    k.masterDoubleClickHandler),
                #('<Double-3>',  None,                       k.masterDoubleClick3Handler),
                #('<Button-2>',  frame.OnPaste,              k.masterClickHandler),
            ):
                def bodyClickCallback(event,handler=handler,func=func):
                    return handler(event,func)

                w.bind(kind,bodyClickCallback)
        #@nonl
        #@-node:bob.20070813163332.240:wxBody.createBindings NOT USED AT PRESENT
        #@+node:bob.20070813163332.241:wxBody.setEditorColors
        def setEditorColors (self,bg,fg):
            pass
        #@nonl
        #@-node:bob.20070813163332.241:wxBody.setEditorColors
        #@-node:bob.20070813163332.237:Birth & death (wxLeoBody)
        #@+node:bob.20070813163332.242:Tk wrappers (wxBody)

        def cget(self,*args,**keys):
            pass # to be removed from Leo's core.

        def configure (self,*args,**keys):
            pass # to be removed from Leo's core.

        def hasFocus (self):
            return self.bodyCtrl.getFocus()

        def setFocus (self):
            # g.trace('body')
            return self.bodyCtrl.setFocus()

        SetFocus = setFocus
        getFocus = hasFocus

        def getBodyPaneHeight (self):
            return self.bodyCtrl.GetCharHeight() # widget specific

        def getBodyPaneWidth (self):
            return self.bodyCtrl.GetCharWidth()  # widget specific

        def scheduleIdleTimeRoutine (self,function,*args,**keys):
            wx.CallAfter(function, *args, **keys)

        def tag_add (self,*args,**keys):
            #g.trace()
            return self.bodyCtrl.tag_add(*args,**keys)

        def tag_bind (self,*args,**keys):
            #g.trace()
            return self.bodyCtrl.tag_bind(*args,**keys)

        def tag_configure (self,*args,**keys):
            #g.trace()
            return self.bodyCtrl.tag_configure(*args,**keys)

        def tag_delete (self,*args,**keys):
            #g.trace()
            return self.bodyCtrl.tag_delete(*args,**keys)

        def tag_remove (self,*args,**keys):
            #g.trace()
            return self.bodyCtrl.tag_remove(*args,**keys)
        #@-node:bob.20070813163332.242:Tk wrappers (wxBody)
        #@+node:bob.20070813163332.243:onBodyChanged (wxBody: calls leoBody.onBodyChanged)
        #@@c
        def onBodyChanged (self,undoType,oldSel=None,oldText=None,oldYview=None):
            '''Update Leo after the body has been changed.'''
            #g.trace()
            if g.app.killed or self.c.frame.killed: return

            c = self.c ; w = c.frame.body.bodyCtrl
            if not c:  return g.trace('no c!')

            p = c.currentPosition()

            if not p: return g.trace('no p!')

            if self.frame.lockout > 0: return g.trace('lockout!',g.callers())

            #g.trace('undoType',undoType,'oldSel',oldSel,'len(oldText)',oldText and len(oldText) or 0)

            self.frame.lockout += 1
            try:
                # Call the base class method.
                leoFrame.leoBody.onBodyChanged(self,
                    undoType,oldSel=oldSel,oldText=oldText,oldYview=oldYview)
            finally:
                self.frame.lockout -= 1

        #@-node:bob.20070813163332.243:onBodyChanged (wxBody: calls leoBody.onBodyChanged)
        #@+node:bob.20070813163332.244:wxBody.forceFullRecolor
        def forceFullRecolor (self):

            self.forceFullRecolorFlag = True
        #@nonl
        #@-node:bob.20070813163332.244:wxBody.forceFullRecolor
        #@+node:bob.20071124165701:select/unselectLabel
        def unselectLabel (self,w):
            return


        def selectLabel (self,w):
            return
        #@-node:bob.20071124165701:select/unselectLabel
        #@-others
    #@nonl
    #@-node:bob.20070813163332.236:wxLeoBody class (leoBody)
    #@+node:bob.20070908081747:-- Object --
    #@+node:bob.20070908081747.1:leoObject class
    class leoObject(object):
        """A base class for all leo objects."""

        #@    @+others
        #@+node:bob.20070908081747.2:__init__
        def __init__(self, c):

            object.__init__(self)
            self.c = c

            #print 'Created leo object for ', self
        #@-node:bob.20070908081747.2:__init__
        #@+node:bob.20070908083151:__str__
        def __str__(self):
            return '%s [%s]'%(self.__class__.__name__, id(self))

        __repr__ = __str__
        #@nonl
        #@-node:bob.20070908083151:__str__
        #@-others
    #@-node:bob.20070908081747.1:leoObject class
    #@+node:bob.20070908081747.3:wxLeoObject class
    class wxLeoObject(object):
        """A base class mixin for all wxPython specific objects.

        """

        #@    @+others
        #@+node:bob.20070908081747.4:def __init__
        def __init__(self):

            object.__init__(self)
            #print 'created', self

        #@-node:bob.20070908081747.4:def __init__
        #@+node:bob.20070908084322:def __str__
        def __str__(self):
            return 'wxLeoObject: %s [%s]'%(self.__class__.__name__, id(self))

        __repr__ = __str__
        #@-node:bob.20070908084322:def __str__
        #@-others
    #@-node:bob.20070908081747.3:wxLeoObject class
    #@-node:bob.20070908081747:-- Object --
    #@+node:bob.20070908081747.6:-- Notebook --
    #@+node:bob.20070908081747.7:leoNotebook
    class leoNotebook(leoObject):

        #@    @+others
        #@+node:bob.20070908081747.8:__init__
        def __init__(self, c):

            leoObject.__init__(self, c)

            self.__tabs = []
        #@-node:bob.20070908081747.8:__init__
        #@+node:bob.20070908111527:appendTab
        def appendTab(self, tab):

            assert isinstance(tab, leoTab)

            if tab in self.__tabs:
                g.trace('\n\ttab already in notebook!')
                print '\ttab', tab
                print '\tnb', self.nb
                return self.__tabs.index(tab)

            else:
                self.__tabs.append(tab)
                return len(self.__tabs)

        #@-node:bob.20070908111527:appendTab
        #@+node:bob.20070908115245:Tabs Property
        def getTabs(self):
            return self.__tabs[:]

        tabs = property(getTabs)
        #@-node:bob.20070908115245:Tabs Property
        #@-others


    #@-node:bob.20070908081747.7:leoNotebook
    #@+node:bob.20070908081747.9:wxLeoNotebook class
    class wxLeoNotebook(wx.Notebook, wxLeoObject, leoNotebook):
        """A wxPython specific implementation of a leoNotebook."""
        #@    @+others
        #@+node:bob.20070908081747.10:__init__
        def __init__(self, c, parent, showTabs=False):


            leoNotebook.__init__(self, c)
            wxLeoObject.__init__(self)

            wx.Notebook.__init__(self, parent)


            #g.trace( self,' >> ', parent)

            self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onPageChanged)

            self.Bind(wx.EVT_SIZE, self.onSize)











        #@-node:bob.20070908081747.10:__init__
        #@+node:bob.20071212081425:__str__
        def __str__(self):
            return '%s [%s]'%(self.__class__.__name__, id(self))

        __repr__ = __str__
        #@nonl
        #@-node:bob.20071212081425:__str__
        #@+node:bob.20071230174704:onSize
        def onSize(self, event):
            """Handle EVT_SIZE for wx.Notebook."""

            #g.trace(myclass(self), self.GetClientSize())

            page = self.GetCurrentPage()

            if page:
                page.SetSize(self.GetClientSize())


            event.Skip()

        #@-node:bob.20071230174704:onSize
        #@+node:bob.20071230175001:onPageChanged
        def onPageChanged(self, event):
            """Handle EVT_NOTEBOOK_PAGE_CHANGED for wx.Notebook."""

            #g.trace()

            sel = event.GetSelection()

            if sel > -1:
                page = self.GetPage(sel)
                page.SetSize(self.GetClientSize())

            event.Skip()
        #@-node:bob.20071230175001:onPageChanged
        #@+node:bob.20070908104659.1:tabToRawIndex
        def tabToRawIndex(self, tab):
            """The index of the page in the native notebook."""

            if not tab.page:
                return None

            for i in range(self.GetPageCount()):
                if self.GetPage(i) is tab.page:
                    return i

            return None

        #@-node:bob.20070908104659.1:tabToRawIndex
        #@+node:bob.20070908111527.1:appendTab
        def appendTab(self, tab, select=False):

            assert isinstance(tab, wxLeoTab)

            n = super(wxLeoNotebook, self).appendTab(tab)

            idx = self.tabToRawIndex(tab)

            if idx is None:
                self.AddPage(tab.page, tab.tabName, select)
            else:
                g.trace('page can\'t be inserted twice')


        #@-node:bob.20070908111527.1:appendTab
        #@+node:bob.20070908103701.1:setPageText
        def setPageText(self, tab, text):
            """Set the text on the notebook tab.

            Gui specific method for internal use only.

            """
            #g.trace(text, tab, self)

            idx = self.tabToRawIndex(tab)
            #g.trace(idx, self)

            if idx is not None:
                self.SetPageText(idx, text)
        #@-node:bob.20070908103701.1:setPageText
        #@+node:bob.20070908111527.2:appendPage
        def appendPage(self, tabName, page, select=False):
            """Append a page that is not yet contained in a Tab.

            A new Tab is created to contain the page.

            Returns: The newly created Tab object.

            """

            tab = wxLeoTab(tabName, page)
            self.appendTab(tab, select)
            return tab
        #@-node:bob.20070908111527.2:appendPage
        #@-others
    #@nonl
    #@-node:bob.20070908081747.9:wxLeoNotebook class
    #@-node:bob.20070908081747.6:-- Notebook --
    #@+node:bob.20070908102321:-- Tab --
    #@+at
    # A Tab is an object that manages a page and a tab for notebooks.
    # 
    # It is independant of any particular notebook and can be moved
    # from one notebook to another or removed very easily.
    # 
    # It can exist on its own and need not be part of any notebook.
    # 
    # It manages a page which is a single gui object and handles all
    # issues with regard to the parenting of the object.
    #@-at
    #@@c
    #@nonl
    #@+node:bob.20070908102321.1:leoTab class
    class leoTab(leoObject):

        #@    @+others
        #@+node:bob.20070908102321.2:__init__

        def __init__(self, c, tabName=None, page=None, nb=None):

            """
            Create an instance of a notebook Tab object.

            tabName: The name to appear on the tab or None (not '') to indicate
                     that the name will be assigned later.

            page: The gui object (eg a Panel) to be managed or None to indicaate
                  that this will be assigned later.

            nb: The notebook to which this Tab will initially be attached or None to
                indicate that the tab does not initially belong to any notebook.

            """
            leoObject.__init__(self, c)

            self.__nb = None
            self.__tabName = None
            self.__page = None

            self.setTabName(tabName)
            self.setNotebook(nb)
            self.setPage(page)
        #@-node:bob.20070908102321.2:__init__
        #@+node:bob.20070908102321.3:TabName property
        def getTabName(self):
            return self.__tabName

        def setTabName(self, tabName):
            self.__tabName = tabName

        tabName = property(
            lambda self: self.getTabName(),
            lambda self, name: self.setTabName(name),
        )
        #@-node:bob.20070908102321.3:TabName property
        #@+node:bob.20070908102321.4:Notebook property
        def getNotebook(self):
            return self.__nb

        def setNotebook(self, nb):
            assert nb is None or isinstance(nb, leoNotebook)
            self.__nb = nb

        nb = property(
            lambda self: self.getNotebook(),
            lambda self, nb: self.setNotebook(nb),
        )
        notebook = nb

        #@-node:bob.20070908102321.4:Notebook property
        #@+node:bob.20070908102321.5:Page property
        def getPage(self):
            return self.__page

        def setPage(self, page):
            self.__page = page

        page = property(
            lambda self: self.getPage(),
            lambda self, page: self.setPage(page),
        )
        #@-node:bob.20070908102321.5:Page property
        #@-others
    #@-node:bob.20070908102321.1:leoTab class
    #@+node:bob.20070908102321.6:wxLeoTab class
    class wxLeoTab(wxLeoObject, leoTab):

        """wxPython implementation of leoTab."""
        #@    @+others
        #@+node:bob.20070908102321.7:__init__
        def __init__(self, c, tabName=None, page=None, nb=None):

            leoTab.__init__(self, c, tabName, page, nb)

            page.leoParent = self
        #@-node:bob.20070908102321.7:__init__
        #@+node:bob.20070908102321.8:TabName property
        def setTabName(self, tabName):

            super(wxLeoTab, self).setTabName(tabName)

            if self.nb:
                self.nb.setPageText(self, tabName)

            #g.trace(tabName, self)
        #@-node:bob.20070908102321.8:TabName property
        #@+node:bob.20070908102321.9:Notebook property
        def setNotebook(self, nb):

            assert nb is None or isinstance(nb, wxLeoNotebook)
            #g.trace('\n\t', self )

            super(wxLeoTab, self).setNotebook(nb)

        #@-node:bob.20070908102321.9:Notebook property
        #@+node:bob.20070908102321.10:Page property

        def setPage(self, page, init=False):

            #g.trace(page)
            assert page is None or isinstance(page, wx.Window)

            super(wxLeoTab, self).setPage(page)

            #g.trace(page, '\n\t', self)






        #@-node:bob.20070908102321.10:Page property
        #@-others
    #@-node:bob.20070908102321.6:wxLeoTab class
    #@-node:bob.20070908102321:-- Tab --
    #@+node:bob.20070908081747.5:-- Notebook Panel --
    #@+node:bob.20070908081747.11:leoNotebookPanel class
    class leoNotebookPanel(leoObject):
        """A class to manage a leoNotebook and any helper windows surrounding it.

        This class will contain methods to add and remove windows arround a
        central notebook.

        These helper windows might be toolbars, log windows ...

        This is a mixin class for the gui class which will provide the physical,
        gui specific, representation.

        """

        #@    @+others
        #@+node:bob.20070908081747.12:__init__
        def __init__(self, c):

            leoObject.__init__(self, c)
        #@-node:bob.20070908081747.12:__init__
        #@-others


    #@-node:bob.20070908081747.11:leoNotebookPanel class
    #@+node:bob.20070907202843:wxLeoNotebookPanel class

    class wxLeoNotebookPanel(wx.Panel, wxLeoObject, leoNotebookPanel ):
        """wxPython implementation of a leoNotebookPanel."""

        #@    @+others
        #@+node:bob.20070908081747.13:__init__
        def __init__(self, c, parent, showtabs=False):
            """A panel containing a Notebook.

            The base class of all body, tree and notebook panes.
            """

            wxLeoObject.__init__(self)
            leoNotebookPanel.__init__(self, c)

            wx.Panel.__init__(self, parent)

            self.sizer = sizer = wx.BoxSizer(wx.VERTICAL)

            self.nb = nb = wxLeoNotebook(c, self)

            self.log = wxLeoLog(c, self.nb)

            sizer.Add(self.nb, 1, wx.EXPAND)

            self.SetSizer(sizer)

            #self.Bind(wx.EVT_SIZE, self.onSize)

            #self.Bind(wx.EVT_CHAR, lambda event, type='leonotebookpanel':onRogueChar(event, type))


        #@-node:bob.20070908081747.13:__init__
        #@+node:bob.20071212080244:onSize
        def onSize(self, event):
            """Handle EVT_SIZE for wx.Panel."""

            #g.trace(myclass(self), self.GetClientSize())

            event.Skip()
        #@-node:bob.20071212080244:onSize
        #@-others




    #@-node:bob.20070907202843:wxLeoNotebookPanel class
    #@-node:bob.20070908081747.5:-- Notebook Panel --
    #@+node:bob.20070813163332.257:wxLeoFrame class (leoFrame)
    class wxLeoFrame(leoFrame.leoFrame):

        """A class to create a wxPython from for the main Leo window."""

        #@    @+others
        #@+node:bob.20070813163332.258:Birth & death (wxLeoFrame)
        #@+node:bob.20070813163332.259:__init__ (wxLeoFrame)
        def __init__ (self,title):

            # Init the base classes.

            leoFrame.leoFrame.__init__(self,g.app.gui) # Clears self.title.

            self.title = title

            self.line_height = 0


            # To be set in finishCreate.
            self.c = None
            #self.bodyCtrl = None

            self.logPanel = None
            self.treePanel = None
            self.bodyPanel = None
            self.splitter1 = None
            self.splitter2 = None

            self.minibuffer =None
            self.statusLine = None
            self.iconBar = None
            self.menuBar = None

            self.statusLineClass = wxLeoStatusLine
            self.minibufferClass = wxLeoMinibuffer
            self.iconBarClass = wxLeoIconBar

            self.findTabHandler = None
            self.spellTabHandler = None


            #g.trace("wxLeoFrame",title)

            self.activeFrame = None
            self.focusWidget = None


            self.killed = False
            self.lockout = 0 # Suppress further events
            self.quitting = False
            self.updateCount = 0
            self.treeIniting = False
            self.drawing = False # Lockout recursive draws.
            self.menuIdDict = {}

            self.ratio = 0.5
            self.secondary_ratio = 0.5
            self.startupWindow=True



            self.use_coloring = False # set True to enable coloring

            self._splitterOrientation = VERTICAL


        #@-node:bob.20070813163332.259:__init__ (wxLeoFrame)
        #@+node:bob.20070813163332.260:__repr__
        def __repr__ (self):

            return "wxLeoFrame: " + self.title
        #@nonl
        #@-node:bob.20070813163332.260:__repr__
        #@+node:bob.20070831063515:setStatusLine

        def setStatusLine(self, s, **keys):
            self.statusLine and self.statusLine.put(s, **keys)
        #@nonl
        #@-node:bob.20070831063515:setStatusLine
        #@+node:bob.20070813163332.261:finishCreate (wxLeoFrame)

        # temp redirects
        body = property(lambda self: self.bodyPanel)
        bodyCtrl = property(lambda self: self.bodyPanel.bodyCtrl)

        log = property(lambda self: self.logPanel.log)
        nb = property(lambda self: self.logPanel.nb)

        def finishCreate (self,c):

            # g.trace('wxLeoFrame')

            self.c = c
            c.frame = self
            c.chapterController = None

            self.trace_status_line = c.config.getBool('trace_status_line')
            self.use_chapters      = c.config.getBool('use_chapters')
            self.use_chapter_tabs  = c.config.getBool('use_chapter_tabs')

            c.focusManager = g.app.gui.createFocusManagerClass(self.c)

            if self.use_chapters:
                c.chapterController = cc = leoChapters.chapterController(c)

            self.topFrame = self.top = top = wx.Frame(
                parent=None, id=-1, title=self.title,
                pos = (100,50),size = (750, 520),
                style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE
            )

            #top.Bind(wx.EVT_CHAR, lambda event, type='leoframe':onRogueChar(self, event, type))


            self.hiddenWindow = hw = wx.Window(top)
            hw.Hide()

            # Set the official ivars.
            self.topFrame = self.top = self.outerFrame = top

            top.update_idletasks = g.app.gui.update_idletasks


            # Create the icon area.
            self.iconBar = wxLeoIconBar(c,parentFrame=top)

            # Create the main sizer
            box = wx.BoxSizer(wx.VERTICAL)


            # tree panel

            self.treePanel = self.createTreePanel()
            self.tree = self.treePanel


            # log panel

            self.logPanel = lp = self.createLogPanel()

            # redirects
            # self.nb = nb = lp.nb
            #  self.log = lp.log

            nb = self.nb

            g.app.setLog(self.log) # writeWaitingLog hangs without this(!)


            # body panel

            self.bodyPanel = self.createBodyPanel()

            # redirectes
            #   self.body = self.bodyPanel
            #   self.bodyCtrl = self.body.bodyCtrl


            # splitters

            s1, s2 = self.createSplitters()

            self.splitter1 = s1
            self.splitter2 = s2


            ##FIXME when panels finished
            #self.setupSplitters(self.treePanel, self.logPanel, self.bodyPanel, s1,s2)
            self.setupSplitters(self.tree.treeCtrl, self.logPanel, self.body.bodyCtrl, s1, s2)

            s1.Reparent(self.top)

            box.Add(s1, 1, wx.EXPAND)

            #@    << create and add status area >>
            #@+node:bob.20070825181313:<< create and add status area >>

            self.statusLine = self.createStatusLine()

            sizer = self.statusLine.finishCreate(top)
            box.Add(sizer, 0, wx.EXPAND | wx.TOP | wx.RIGHT, 3)
            #@nonl
            #@-node:bob.20070825181313:<< create and add status area >>
            #@nl
            #@    << create and add minibuffer area >>
            #@+node:bob.20070825182338:<< create and add minibuffer area >>

            self.minibuffer = self.createMinibuffer()

            sizer = self.minibuffer.finishCreate(top)
            box.Add(sizer, 0, wx.EXPAND | wx.TOP | wx.RIGHT, 3)
            #@-node:bob.20070825182338:<< create and add minibuffer area >>
            #@nl

            # Create the menus & icon.
            self.menu = wxLeoMenu(self)
            self.setWindowIcon()

            top.Show(True)

            self.colorizer = self.body.colorizer

            c.initVersion()
            self.signOnWithVersion()

            self.injectCallbacks()

            g.app.windowList.append(self)

            c.focusManager.chooseBodyOrOutline()

            # self.setFocus(g.choose(
                # c.config.getBool('outline_pane_has_initial_focus'),
                # self.tree.treeCtrl,self.bodyCtrl
            # ))

            self.createFirstTreeNode()


            self.setEventHandlers()

            self.top.SetSizer(box)

            self.top.Layout()

            wx.SafeYield(onlyIfNeeded=True)




        #@+node:bob.20070831060158:createMinibuffer

        def createMinibuffer (self):
            if not self.minibuffer:
                self.minibuffer  = self.minibufferClass(self.c)
            return self.minibuffer
        #@nonl
        #@-node:bob.20070831060158:createMinibuffer
        #@+node:bob.20070822073957:createFirstTreeNode
        def createFirstTreeNode (self):

            c = self.c

            t = leoNodes.tnode()
            v = leoNodes.vnode(t)
            p = leoNodes.position(v,[])
            v.initHeadString("NewHeadline")
            p.moveToRoot(oldRoot=None)
            c.setRootPosition(p) # New in 4.4.2.

        #@-node:bob.20070822073957:createFirstTreeNode
        #@+node:bob.20070813163332.262:setWindowIcon
        def setWindowIcon(self):

            path = os.path.join(g.app.loadDir,"..","Icons","LeoApp16.ico")
            icon = wx.Icon(path,wx.BITMAP_TYPE_ICO,16,16)
            self.top.SetIcon(icon)
        #@-node:bob.20070813163332.262:setWindowIcon
        #@-node:bob.20070813163332.261:finishCreate (wxLeoFrame)
        #@+node:bob.20070912144833.1:createSplitters
        def createSplitters(self, parent=None, style=wx.CLIP_CHILDREN|wx.SP_LIVE_UPDATE|wx.SP_3D):

            parent = parent or self.hiddenWindow

            return (
                wx.SplitterWindow(parent, style=style),
                wx.SplitterWindow(parent, style=style)
            )
        #@-node:bob.20070912144833.1:createSplitters
        #@+node:bob.20070912144833.2:setupSplitters
        def setupSplitters(self, tree, log, body, s1, s2):
            """Initial setup of splitters.


            This must be called with newly created splitters.
            """

            s2.Reparent(s1)
            body.Reparent(s1)
            tree.Reparent(s2)
            log.Reparent(s2)

            s1.SetSashGravity(0.33)
            s2.SetSashGravity(0.66)


            if self._splitterOrientation == HORIZONTAL:

                s2.SplitVertically(tree, log, 0)
                s1.SplitHorizontally(s2, body, 0)

            else:

                s2.SplitHorizontally(tree, log, 0)
                s1.SplitVertically(s2, body, 0)

            return s1
        #@-node:bob.20070912144833.2:setupSplitters
        #@+node:bob.20070813163332.264:initialRatios
        def initialRatios (self):

            config = g.app.config
            s = config.getWindowPref("initial_splitter_orientation")

            verticalFlag = s == None or (s != "h" and s != "horizontal")

            # Tweaked for tk.  Other tweaks may be best for wx.
            if verticalFlag:

                r = config.getFloatWindowPref("initial_vertical_ratio")
                if r == None or r < 0.0 or r > 1.0:
                    r = 0.5

                r2 = config.getFloatWindowPref("initial_vertical_secondary_ratio")
                if r2 == None or r2 < 0.0 or r2 > 1.0:
                    r2 = 0.8

            else:

                r = config.getFloatWindowPref("initial_horizontal_ratio")
                if r == None or r < 0.0 or r > 1.0:
                    r = 0.3

                r2 = config.getFloatWindowPref("initial_horizontal_secondary_ratio")
                if r2 == None or r2 < 0.0 or r2 > 1.0:
                    r2 = 0.8

            return verticalFlag,r,r2
        #@-node:bob.20070813163332.264:initialRatios
        #@+node:bob.20070813163332.265:injectCallbacks
        # ??? whats the point of this?

        def injectCallbacks(self):

            import leoNodes

            # Some callback is required.
            def doNothingCallback(*args,**keys):
                pass

            for name in (
                "OnBoxClick","OnDrag","OnEndDrag",
                "OnHeadlineClick","OnHeadlineRightClick","OnHeadlineKey",
                "OnHyperLinkControlClick","OnHyperLinkEnter","OnHyperLinkLeave",
                "OnIconClick","OnIconDoubleClick","OnIconRightClick"):

                # g.trace(f)
                g.funcToMethod(doNothingCallback,leoNodes.vnode,name=name)
        #@nonl
        #@-node:bob.20070813163332.265:injectCallbacks
        #@+node:bob.20070813163332.266:signOnWithVersion
        def signOnWithVersion (self):

            c = self.c
            color = c.config.getColor("log_error_color")
            signon = c.getSignOnLine()
            n1,n2,n3,junk,junk=sys.version_info

            g.es("Leo Log Window...",color=color)
            g.es(signon)
            g.es("Python %d.%d.%d wxWindows %s" % (n1,n2,n3,wx.VERSION_STRING))
            g.es('\nwxLeo version: %s\n\n'%__version__)


        #@-node:bob.20070813163332.266:signOnWithVersion
        #@+node:bob.20070813163332.267:setMinibufferBindings
        def setMinibufferBindings(self):

            pass

            # g.trace('to do')
        #@nonl
        #@-node:bob.20070813163332.267:setMinibufferBindings
        #@+node:bob.20070813163332.268:destroySelf
        def destroySelf(self):

            self.killed = True
            self.top.Destroy()
        #@nonl
        #@-node:bob.20070813163332.268:destroySelf
        #@-node:bob.20070813163332.258:Birth & death (wxLeoFrame)
        #@+node:bob.20070912144833.3:-- Panel Creation Factories --
        #@+node:bob.20070912132540:createTreePanel
        def createTreePanel(self, parent=None):

            parent = parent or self.hiddenWindow

            return wxLeoTree(self.c, parent)
        #@-node:bob.20070912132540:createTreePanel
        #@+node:bob.20070912144833.4:createBodyPanel
        def createBodyPanel(self, parent=None):

            parent = parent or self.hiddenWindow

            return wxLeoBody(self.c, parent)
        #@-node:bob.20070912144833.4:createBodyPanel
        #@+node:bob.20070912144833.5:createLogPanel
        def createLogPanel(self, parent=None):

            parent = parent or self.hiddenWindow

            return wxLeoNotebookPanel(self.c, parent)
        #@-node:bob.20070912144833.5:createLogPanel
        #@-node:bob.20070912144833.3:-- Panel Creation Factories --
        #@+node:bob.20070813163332.269:event handlers
        #@+node:bob.20070813163332.263:setEventHandlers
        def setEventHandlers (self):

            bind = self.top.Bind

            # Activate events exist only on Windows.
            if wx.Platform == "__WXMSW__":
                bind(wx.EVT_ACTIVATE, self.onActivate)
            else:
                bind(wx.EVT_SET_FOCUS, self.OnSetFocus)

            bind(wx.EVT_CLOSE, self.onCloseLeoFrame)

            bind(wx.EVT_SET_FOCUS, self.onGainFocus)
            bind(wx.EVT_KILL_FOCUS, self.onLoseFocus)

            #bind(wx.EVT_MENU_OPEN, self.updateAllMenus)#self.updateAllMenus)
            #bind(wx.EVT_MENU_OPEN, self.xupdateAllMenus)#self.updateAllMenus)

            bind(wx.EVT_CHAR,
                lambda event, self=self: onGlobalChar(self, event)
            )

            #bind(wx.EVT_KEY_UP, lambda event :self.tree.onKeyUp(event))
            #bind(wx.EVT_KEY_DOWN, lambda event: self.tree.onKeyDown(event))


        def onChar(self, event):
            g.trace('====================  Frame *****************')
            event.Skip()

        def xupdateAllMenus(self, event):
            g.trace('+++++++++++++++++++++++++++ ++ got a menu open event !!!')
            g.trace(event.GetEventType())
            event.Skip()
        #@-node:bob.20070813163332.263:setEventHandlers
        #@+node:bob.20070901130234.1:onLoseFocus
        def onLoseFocus(self, event):
            return self.c.focusManager.lostFocus(self, event)

        #@-node:bob.20070901130234.1:onLoseFocus
        #@+node:bob.20070901130234:onGainFocus
        def onGainFocus(self, event):
            return self.c.focusManager.gotFocus(self, event)

        #@-node:bob.20070901130234:onGainFocus
        #@+node:bob.20070813163332.270:onActivate & OnSetFocus
        if wx.Platform == '__WXMSW__':

            def onActivate(self,event):
                if g.app.killed or self.killed: return
                if event.GetActive():
                    self.activeFrame = self
                    if self.c:
                        pass ## self.c.checkAllFileDates()
        else:

            def OnSetFocus(self,event):
                if g.app.killed or self.killed: return
                self.activeFrame = self
                if self.c:
                    self.c.checkAllFileDates()
        #@-node:bob.20070813163332.270:onActivate & OnSetFocus
        #@+node:bob.20070813163332.271:onCloseLeoFrame
        def onCloseLeoFrame(self,event):

            frame = self

            # The g.app class does all the hard work now.
            if not g.app.closeLeoWindow(frame):
                if event.CanVeto():
                    event.Veto()
        #@nonl
        #@-node:bob.20070813163332.271:onCloseLeoFrame
        #@-node:bob.20070813163332.269:event handlers
        #@+node:bob.20070813163332.273:wxFrame dummy routines: (to do: minor)
        def after_idle(self, *args, **kw):
            wx.CallAfter(*args, **kw)

        def after(self, *args, **kw):
            wx.CallLater(self, *args, **kw)



        def bringToFront(self):
            pass

        def get_window_info (self):
            """Return the window information."""
            return g.app.gui.get_window_info(self.topFrame)

        def OnBodyRClick (self,event=None):
            pass

        def resizePanesToRatio(self,ratio1,ratio2):
            pass

        def setInitialWindowGeometry (self):
            pass

        def setTopGeometry (self,w,h,x,y,adjustSize=True):
            pass

        def setWrap (self,p):
            pass

        def lift (self):
            self.top.Raise()

        def update (self):
            pass
        #@-node:bob.20070813163332.273:wxFrame dummy routines: (to do: minor)
        #@+node:bob.20070813163332.274:Externally visible routines...
        #@+node:bob.20070813163332.275:deiconify
        def deiconify (self):

            self.top.Iconize(False)
        #@nonl
        #@-node:bob.20070813163332.275:deiconify
        #@+node:bob.20070813163332.276:getTitle
        def getTitle (self):

            return self.title
        #@-node:bob.20070813163332.276:getTitle
        #@+node:bob.20070813163332.277:setTitle
        def setTitle (self,title):

            self.title = title
            self.top.SetTitle(title) # Call the wx code.
        #@nonl
        #@-node:bob.20070813163332.277:setTitle
        #@-node:bob.20070813163332.274:Externally visible routines...
        #@+node:bob.20070813163332.278:Gui-dependent commands (to do)
        #@+node:bob.20070813163332.279:setFocus (wxFrame)
        def setFocus (self, w):
            self.c.focusManager.setFocus(w)


        SetFocus = setFocus
        #@nonl
        #@-node:bob.20070813163332.279:setFocus (wxFrame)
        #@+node:bob.20070813163332.280:Minibuffer commands... (wxFrame)
        #@+node:bob.20070813163332.281:contractPane
        def contractPane (self,event=None):

            '''Contract the selected pane.'''

            f = self ; c = f.c
            w = c.get_requested_focus()
            wname = c.widget_name(w)

            # g.trace(wname)
            if not w: return

            if wname.startswith('body'):
                f.contractBodyPane()
            elif wname.startswith('log'):
                f.contractLogPane()
            elif wname.startswith('head') or wname.startswith('canvas'):
                f.contractOutlinePane()
        #@-node:bob.20070813163332.281:contractPane
        #@+node:bob.20070813163332.282:expandPane
        def expandPane (self,event=None):

            '''Expand the selected pane.'''

            f = self ; c = f.c

            w = c.get_requested_focus()
            wname = c.widget_name(w)

            # g.trace(wname)
            if not w: return

            if wname.startswith('body'):
                f.expandBodyPane()
            elif wname.startswith('log'):
                f.expandLogPane()
            elif wname.startswith('head') or wname.startswith('canvas'):
                f.expandOutlinePane()
        #@-node:bob.20070813163332.282:expandPane
        #@+node:bob.20070813163332.283:fullyExpandPane
        def fullyExpandPane (self,event=None):

            '''Fully expand the selected pane.'''

            f = self ; c = f.c

            w = c.get_requested_focus()
            wname = c.widget_name(w)

            # g.trace(wname)
            if not w: return

            if wname.startswith('body'):
                f.fullyExpandBodyPane()
            elif wname.startswith('log'):
                f.fullyExpandLogPane()
            elif wname.startswith('head') or wname.startswith('canvas'):
                f.fullyExpandOutlinePane()
        #@-node:bob.20070813163332.283:fullyExpandPane
        #@+node:bob.20070813163332.284:hidePane
        def hidePane (self,event=None):

            '''Completely contract the selected pane.'''

            f = self ; c = f.c

            w = c.get_requested_focus()
            wname = c.widget_name(w)

            if not w: return

            if wname.startswith('body'):
                f.hideBodyPane()
                c.treeWantsFocusNow()
            elif wname.startswith('log'):
                f.hideLogPane()
                c.bodyWantsFocusNow()
            elif wname.startswith('head') or wname.startswith('canvas'):
                f.hideOutlinePane()
                c.bodyWantsFocusNow()
        #@-node:bob.20070813163332.284:hidePane
        #@+node:bob.20070813163332.285:expand/contract/hide...Pane
        #@+at
        # The first arg to divideLeoSplitter means the following:
        # 
        #     f.splitVerticalFlag: use the primary   (tree/body) ratio.
        # not f.splitVerticalFlag: use the secondary (tree/log) ratio.
        #@-at
        #@@c
        def contractBodyPane (self,event=None):
            '''Contract the body pane.'''
            f = self ; r = min(1.0,f.ratio+0.1)
            f.divideLeoSplitter(f.splitVerticalFlag,r)

        def contractLogPane (self,event=None):
            '''Contract the log pane.'''
            f = self ; r = min(1.0,f.ratio+0.1)
            f.divideLeoSplitter(not f.splitVerticalFlag,r)

        def contractOutlinePane (self,event=None):
            '''Contract the outline pane.'''
            f = self ; r = max(0.0,f.ratio-0.1)
            f.divideLeoSplitter(f.splitVerticalFlag,r)

        def expandBodyPane (self,event=None):
            '''Expand the body pane.'''
            self.contractOutlinePane()

        def expandLogPane(self,event=None):
            '''Expand the log pane.'''
            f = self ; r = max(0.0,f.ratio-0.1)
            f.divideLeoSplitter(not f.splitVerticalFlag,r)

        def expandOutlinePane (self,event=None):
            '''Expand the outline pane.'''
            self.contractBodyPane()
        #@-node:bob.20070813163332.285:expand/contract/hide...Pane
        #@+node:bob.20070813163332.286:fullyExpand/hide...Pane




        def fullyExpandBodyPane (self,event=None):
            '''Fully expand the body pane.'''
            f = self ; f.divideLeoSplitter(f.splitVerticalFlag,0.0)

        def fullyExpandLogPane (self,event=None):
            '''Fully expand the log pane.'''
            f = self ; f.divideLeoSplitter(not f.splitVerticalFlag,0.0)

        def fullyExpandOutlinePane (self,event=None):
            '''Fully expand the outline pane.'''
            f = self ; f.divideLeoSplitter(f.splitVerticalFlag,1.0)

        def hideBodyPane (self,event=None):
            '''Completely contract the body pane.'''
            f = self ; f.divideLeoSplitter(f.splitVerticalFlag,1.0)

        def hideLogPane (self,event=None):
            '''Completely contract the log pane.'''
            f = self ; f.divideLeoSplitter(not f.splitVerticalFlag,1.0)

        def hideOutlinePane (self,event=None):
            '''Completely contract the outline pane.'''
            f = self ; f.divideLeoSplitter(f.splitVerticalFlag,0.0)
        #@-node:bob.20070813163332.286:fullyExpand/hide...Pane
        #@-node:bob.20070813163332.280:Minibuffer commands... (wxFrame)
        #@+node:bob.20070813163332.287:Window Menu
        #@+node:bob.20070813163332.288:cascade
        def cascade(self,event=None):

            g.es("cascade not ready yet")
            return

            x,y,delta = 10,10,10
            for frame in g.app.windowList:
                top = frame.top
                # Compute w,h
                top.update_idletasks() # Required to get proper info.
                geom = top.geometry() # geom = "WidthxHeight+XOffset+YOffset"
                dim,junkx,junky = string.split(geom,'+')
                w,h = string.split(dim,'x')
                w,h = int(w),int(h)
                # Set new x,y and old w,h
                frame.setTopGeometry(w,h,x,y)
                # Compute the new offsets.
                x += 30 ; y += 30
                if x > 200:
                    x = 10 + delta ; y = 40 + delta
                    delta += 10
        #@nonl
        #@-node:bob.20070813163332.288:cascade
        #@+node:bob.20070813163332.289:equalSizedPanes
        def equalSizedPanes(self,event=None):

            g.es("equalSizedPanes not ready yet")
            return

            frame = self
            frame.resizePanesToRatio(0.5,frame.secondary_ratio)
        #@-node:bob.20070813163332.289:equalSizedPanes
        #@+node:bob.20070813163332.290:hideLogWindow
        def hideLogWindow (self,event=None):

            g.es("hideLogWindow not ready yet")
            return

            frame = self
            frame.divideLeoSplitter2(0.99, not frame.splitVerticalFlag)
        #@nonl
        #@-node:bob.20070813163332.290:hideLogWindow
        #@+node:bob.20070813163332.291:minimizeAll
        def minimizeAll(self,event=None):

            g.es("minimizeAll not ready yet")
            return

            self.minimize(g.app.findFrame)
            self.minimize(g.app.pythonFrame)
            for frame in g.app.windowList:
                self.minimize(frame)

        def minimize(self, frame):

            if frame:
                frame.Show(False)
        #@nonl
        #@-node:bob.20070813163332.291:minimizeAll
        #@+node:bob.20070813163332.292:toggleActivePane
        def toggleActivePane(self,event=None): # wxFrame.

            w = self.focusWidget or self.body.bodyCtrl

            w = g.choose(w == self.bodyCtrl,self.tree.treeCtrl,self.bodyCtrl)

            w.SetFocus()
            self.focusWidget = w
        #@nonl
        #@-node:bob.20070813163332.292:toggleActivePane
        #@+node:bob.20070813163332.293:toggleSplitDirection
        # The key invariant: self.splitVerticalFlag tells the alignment of the main splitter.
        def toggleSplitDirection(self,event=None):

            def po(o):
               g.trace(g.choose(o==VERTICAL, 'vertical', 'horizontal'))


            orient = self._splitterOrientation

            g.trace(po(orient))

            s1 = self.splitter1
            s2 = self.splitter2


            self._splitterOrientation = orient = g.choose(orient == VERTICAL, HORIZONTAL, VERTICAL)
            g.trace(po(orient))


            tree = s2.Window1
            log = s2.Window2
            body = s1.Window2

            s1.Unsplit()
            s2.Unsplit()

            if self._splitterOrientation == HORIZONTAL:

                s2.SplitVertically(tree, log, 0)
                s1.SplitHorizontally(s2, body, 0)

            else:

                s2.SplitHorizontally(tree, log, 0)
                s1.SplitVertically(s2, body, 0)

            return s1






            # Abbreviations.
            frame = self
            bar1 = self.bar1 ; bar2 = self.bar2
            split1Pane1,split1Pane2 = self.split1Pane1,self.split1Pane2
            split2Pane1,split2Pane2 = self.split2Pane1,self.split2Pane2



            # Switch directions.
            verticalFlag = self.splitVerticalFlag = not self.splitVerticalFlag
            orientation = g.choose(verticalFlag,"vertical","horizontal")
            g.app.config.setWindowPref("initial_splitter_orientation",orientation)
            # Reconfigure the bars.
            bar1.place_forget()
            bar2.place_forget()
            self.configureBar(bar1,verticalFlag)
            self.configureBar(bar2,not verticalFlag)
            # Make the initial placements again.
            self.placeSplitter(bar1,split1Pane1,split1Pane2,verticalFlag)
            self.placeSplitter(bar2,split2Pane1,split2Pane2,not verticalFlag)
            # Adjust the log and body panes to give more room around the bars.
            self.reconfigurePanes()
            # Redraw with an appropriate ratio.
            vflag,ratio,secondary_ratio = frame.initialRatios()
            self.resizePanesToRatio(ratio,secondary_ratio)
        #@-node:bob.20070813163332.293:toggleSplitDirection
        #@-node:bob.20070813163332.287:Window Menu
        #@+node:bob.20070813163332.294:Help Menu...
        #@+node:bob.20070813163332.295:leoHelp
        def leoHelp (self,event=None):

            g.es("leoHelp not ready yet")

            return ##

            file = os.path.join(g.app.loadDir,"..","doc","sbooks.chm")
            file = g.toUnicode(file,g.app.tkEncoding) # 10/20/03

            if os.path.exists(file):
                os.startfile(file)
            else:
                answer = g.app.gui.runAskYesNoDialog(c,
                    "Download Tutorial?",
                    "Download tutorial (sbooks.chm) from SourceForge?")

                if answer == "yes":
                    try:
                        if 0: # Download directly.  (showProgressBar needs a lot of work)
                            url = "http://umn.dl.sourceforge.net/sourceforge/leo/sbooks.chm"
                            import urllib
                            self.scale = None
                            urllib.urlretrieve(url,file,self.showProgressBar)
                            if self.scale:
                                self.scale.destroy()
                                self.scale = None
                        else:
                            url = "http://prdownloads.sourceforge.net/leo/sbooks.chm?download"
                            import webbrowser
                            os.chdir(g.app.loadDir)
                            webbrowser.open_new(url)
                    except:
                        g.es("exception dowloading sbooks.chm")
                        g.es_exception()
        #@nonl
        #@+node:bob.20070813163332.296:showProgressBar
        def showProgressBar (self,count,size,total):

            # g.trace("count,size,total:" + `count` + "," + `size` + "," + `total`)
            if self.scale == None:
                #@        << create the scale widget >>
                #@+node:bob.20070813163332.297:<< create the scale widget >>
                top = Tk.Toplevel()
                top.title("Download progress")
                self.scale = scale = Tk.Scale(top,state="normal",orient="horizontal",from_=0,to=total)
                scale.pack()
                top.lift()
                #@nonl
                #@-node:bob.20070813163332.297:<< create the scale widget >>
                #@nl
            self.scale.set(count*size)
            self.scale.update_idletasks()
        #@-node:bob.20070813163332.296:showProgressBar
        #@-node:bob.20070813163332.295:leoHelp
        #@-node:bob.20070813163332.294:Help Menu...
        #@-node:bob.20070813163332.278:Gui-dependent commands (to do)
        #@+node:bob.20070813163332.298:updateAllMenus (wxFrame)
        def updateAllMenus(self,event):

            """Called whenever any menu is pulled down."""

            # We define this routine to strip off the event param.
            #g.trace(g.callers())



            self.menu.updateAllMenus()
            event.Skip()
        #@-node:bob.20070813163332.298:updateAllMenus (wxFrame)
        #@-others
    #@nonl
    #@-node:bob.20070813163332.257:wxLeoFrame class (leoFrame)
    #@+node:bob.20070910194850:wxMenu
    class wxMenu(wx.Menu, wxLeoObject, leoObject):

        def __init__(self, c ):

            leoObject.__init__(self, c)
            wxLeoObject.__init__(self)
            wx.Menu.__init__(self)

            self.Bind(wx.EVT_CHAR, self.onChar)


        def onChar(self):
            print ('menu caught a key!')
            onGlobalChar(self, event)


    #@-node:bob.20070910194850:wxMenu
    #@+node:bob.20070813163332.333:wxLeoMenu class (leoMenu)
    class wxLeoMenu (leoMenu.leoMenu):

        #@    @+others
        #@+node:bob.20070813163332.334:  wxLeoMenu.__init__
        def __init__ (self,frame):

            # Init the base class.
            leoMenu.leoMenu.__init__(self,frame)

            # Init the ivars.
            self.c = frame.c
            self.frame = frame

            self.acceleratorDict = {}
                # Keys are menus, values are list of tuples used to create wx accelerator tables.
            self.menuDict = {}
        #@nonl
        #@-node:bob.20070813163332.334:  wxLeoMenu.__init__
        #@+node:bob.20070813163332.335:Accelerators
        #@+at
        # Accelerators are NOT SHOWN when the user opens the menu with the
        # mouse!
        # This is a wx bug.
        #@-at
        #@nonl
        #@+node:bob.20070813163332.336:createAccelLabel
        def createAccelLabel (self,keys):

            '''Create the menu label by inserting '&' at the underline spot.'''

            label    = keys.get('label')
            underline = keys.get('underline')
            accel = keys.get('accelerator')
            ch = 0 <= underline < len(label) and label[underline] or ''
            if ch: label = label[:underline] + '&' + label[underline:]
            if accel:
                # The accelerator actually creates a key binding by default.
                # Munge accel to make it invalid.
                d = {'BackSpace':'BkSpc','Return':'Rtn','Tab':'TabChr'}
                accel = d.get(accel,accel)
                accel = accel.replace('Alt+','Alt-').replace('Ctrl+','Ctrl-').replace('Shift+','Shift-')

                # *** Accelerators are NOT SHOWN when the user opens the menu with the mouse!
                label = label + '\t' + accel

            # g.trace(label)
            return ch,label
        #@-node:bob.20070813163332.336:createAccelLabel
        #@+node:bob.20070813163332.337:createAccelData (not needed)
        def createAccelData (self,menu,ch,accel,id,label):

            d = self.acceleratorDict
            aList = d.get(menu,[])
            data = ch,accel,id,label
            aList.append(data)
            d [menu] = aList
        #@-node:bob.20070813163332.337:createAccelData (not needed)
        #@+node:bob.20070813163332.338:createAcceleratorTables (not needed)
        def createAcceleratorTables (self):

            return ###

            d = self.acceleratorDict
            entries = []
            for menu in d.keys():
                aList = d.get(menu)
                for data in aList:
                    ch,accel,id,label = data
                    if ch:
                        # g.trace(ch,id,label)
                        entry = wx.AcceleratorEntry(wx.ACCEL_NORMAL,ord(ch),id)
                        entries.append(entry)
            table = wx.AcceleratorTable(entries)
            self.menuBar.SetAcceleratorTable(table)
        #@-node:bob.20070813163332.338:createAcceleratorTables (not needed)
        #@-node:bob.20070813163332.335:Accelerators
        #@+node:bob.20070813163332.339:Menu methods (Tk names)
        #@+node:bob.20070813163332.340:Not called
        def bind (self,bind_shortcut,callback):

            g.trace(bind_shortcut,callback)

        def delete (self,menu,readItemName):

            g.trace(menu,readItemName)

        def destroy (self,menu):

            g.trace(menu)
        #@-node:bob.20070813163332.340:Not called
        #@+node:bob.20070813163332.341:add_cascade
        def add_cascade (self,parent,label,menu,underline):

            """Create a menu with the given parent menu."""

            if parent:
                # Create a submenu of the parent menu.
                keys = {'label':label,'underline':underline}
                ch,label = self.createAccelLabel(keys)
                id = wx.NewId()
                parent.AppendMenu(id,label,menu,label)
                accel = None
                if ch: self.createAccelData(menu,ch,accel,id,label)
            else:
                # Create a top-level menu.
                self.menuBar.Append(menu,label)

        #@-node:bob.20070813163332.341:add_cascade
        #@+node:bob.20070813163332.54:add_command
        def add_command (self,menu,**keys):



            if not menu:
                return g.trace('Can not happen.  No menu')

            callback = keys.get('command')
            accel = keys.get('accelerator')
            ch,label = self.createAccelLabel(keys)
            #g.trace(keys.get('label'))
            def wxMenuCallback (event,callback=callback):
                #g.trace('\nevent',event)
                #print
                callback() # All args were bound when the callback was created.
                event.Skip()

            id = wx.NewId()

            item = menu.Append(id,label,label)

            id = item.GetId()

            key = (menu,label),

            self.menuDict[key] = id # Remember id

            wx.EVT_MENU(self.frame.top,id,wxMenuCallback)

            if ch:
                self.createAccelData(menu,ch,accel,id,label)

        #@-node:bob.20070813163332.54:add_command
        #@+node:bob.20070813163332.342:add_separator
        def add_separator(self,menu):

            if menu:
                menu.AppendSeparator()
            else:
                g.trace("null menu")
        #@nonl
        #@-node:bob.20070813163332.342:add_separator
        #@+node:bob.20070813163332.343:delete_range

        def delete_range (self,menu,n1,n2):
            """Delete a range of items in a menu.

            Items from min(n1, n2) to max(n1, n2) inclusive
            will be removed.

            """
            if not menu:
                return g.trace('Should not happen.  No menu')

            if n1 > n2:
                n2, n1 = n1, n2

            items = menu.GetMenuItems()

            for count, item in enumerate(items):
                if count >= n1 and count<= n2:
                    id = item.GetId()
                    item = menu.FindItemById(id)
                    menu.RemoveItem(item)

        #@-node:bob.20070813163332.343:delete_range
        #@+node:bob.20070813163332.344:index & invoke
        # It appears wxWidgets can't invoke a menu programmatically.
        # The workaround is to change the unit test.

        if 0:
            def index (self,name):
                '''Return the menu item whose name is given.'''

            def invoke (self,i):
                '''Invoke the menu whose index is i'''
        #@-node:bob.20070813163332.344:index & invoke
        #@+node:bob.20070813163332.345:insert
        def insert (self,menuName,position,label,command,underline=None):

            menu = self.getMenu(menuName)


            def wxMenuCallback (event,callback=command):
                #g.trace('\nevent',event)
                #print
                callback() # All args were bound when the callback was created.
                event.Skip()

            id = wx.NewId()

            item = menu.Insert(position, id, label,label)

            id = item.GetId()

            key = (menu,label),

            self.menuDict[key] = id # Remember id

            wx.EVT_MENU(self.frame.top,id,wxMenuCallback)

        #@-node:bob.20070813163332.345:insert
        #@+node:bob.20070813163332.346:insert_cascade
        def insert_cascade (self,parent,index,label,menu,underline):

            """Create a menu with the given parent menu."""

            if parent:
                # Create a submenu of the parent menu.
                keys = {'label':label,'underline':underline}
                ch,label = self.createAccelLabel(keys)
                id = wx.NewId()
                parent.InsertMenu(index, id,label,menu,label)
                accel = None
                if ch: self.createAccelData(menu,ch,accel,id,label)
            else:
                # Create a top-level menu.
                self.menuBar.Insert(indx, menu,label)
        #@-node:bob.20070813163332.346:insert_cascade
        #@+node:bob.20070813163332.347:new_menu
        def new_menu(self,parent,tearoff=0):
            return wxMenu(self.c)
        #@-node:bob.20070813163332.347:new_menu
        #@-node:bob.20070813163332.339:Menu methods (Tk names)
        #@+node:bob.20070813163332.348:Menu methods (non-Tk names)
        #@+node:bob.20070813163332.349:createMenuBar
        def createMenuBar(self,frame):

            self.menuBar = menuBar = wx.MenuBar()

            self.createMenusFromTables()

            self.createAcceleratorTables()

            frame.top.SetMenuBar(menuBar)


            # menuBar.SetAcceleratorTable(wx.NullAcceleratorTable)
        #@-node:bob.20070813163332.349:createMenuBar
        #@+node:bob.20071217225740:createOpenWithMenuFromTable & helper
        def createOpenWithMenuFromTable (self,table):

            '''Entries in the table passed to createOpenWithMenuFromTable are
        tuples of the form (commandName,shortcut,data).

        - command is one of "os.system", "os.startfile", "os.spawnl", "os.spawnv" or "exec".
        - shortcut is a string describing a shortcut, just as for createMenuItemsFromTable.
        - data is a tuple of the form (command,arg,ext).

        Leo executes command(arg+path) where path is the full path to the temp file.
        If ext is not None, the temp file has the given extension.
        Otherwise, Leo computes an extension based on the @language directive in effect.'''

            c = self.c
            g.app.openWithTable = table # Override any previous table.

            # Delete the previous entry.

            parent = self.getMenu("File")

            label = self.getRealMenuName("Open &With...")

            amp_index = label.find("&")
            label = label.replace("&","")

            ## FIXME to be gui independant
            index = 0;
            for item in parent.GetMenuItems():
                if item.GetLabelFromText(item.GetText()) == 'Open _With...':
                    parent.RemoveItem(item)
                    break
                index += 1

            # Create the Open With menu.
            openWithMenu = self.createOpenWithMenu(parent,label,index,amp_index)

            self.setMenu("Open With...",openWithMenu)
            # Create the menu items in of the Open With menu.
            for entry in table:
                if len(entry) != 3: # 6/22/03
                    g.es("createOpenWithMenuFromTable: invalid data",color="red")
                    return
            self.createOpenWithMenuItemsFromTable(openWithMenu,table)
        #@+node:bob.20071217225740.1:createOpenWithMenuItemsFromTable
        def createOpenWithMenuItemsFromTable (self,menu,table):

            '''Create an entry in the Open with Menu from the table.

            Each entry should be a sequence with 2 or 3 elements.'''

            c = self.c ; k = c.k

            if g.app.unitTesting: return

            for data in table:
                #@        << get label, accelerator & command or continue >>
                #@+node:bob.20071217225740.2:<< get label, accelerator & command or continue >>
                ok = (
                    type(data) in (type(()), type([])) and
                    len(data) in (2,3)
                )

                if ok:
                    if len(data) == 2:
                        label,openWithData = data ; accelerator = None
                    else:
                        label,accelerator,openWithData = data
                        accelerator = k.shortcutFromSetting(accelerator)
                        accelerator = accelerator and g.stripBrackets(k.prettyPrintKey(accelerator))
                else:
                    g.trace('bad data in Open With table: %s' % repr(data))
                    continue # Ignore bad data
                #@-node:bob.20071217225740.2:<< get label, accelerator & command or continue >>
                #@nl
                # g.trace(label,accelerator)
                realLabel = self.getRealMenuName(label)
                underline=realLabel.find("&")
                realLabel = realLabel.replace("&","")
                callback = self.defineOpenWithMenuCallback(openWithData)

                self.add_command(menu,label=realLabel,
                    accelerator=accelerator or '',
                    command=callback,underline=underline)
        #@-node:bob.20071217225740.1:createOpenWithMenuItemsFromTable
        #@-node:bob.20071217225740:createOpenWithMenuFromTable & helper
        #@+node:bob.20070813163332.351:defineMenuCallback
        def defineMenuCallback(self,command,name):

            # The first parameter must be event, and it must default to None.
            def callback(event=None,self=self,command=command,label=name):
                self.c.doCommand(command,label,event)

            return callback
        #@nonl
        #@-node:bob.20070813163332.351:defineMenuCallback
        #@+node:bob.20070813163332.352:defineOpenWithMenuCallback
        def defineOpenWithMenuCallback (self,command):

            # The first parameter must be event, and it must default to None.
            def wxOpenWithMenuCallback(event=None,command=command):
                try: self.c.openWith(data=command)
                except: print traceback.print_exc()

            return wxOpenWithMenuCallback
        #@-node:bob.20070813163332.352:defineOpenWithMenuCallback
        #@+node:bob.20071218074136:createOpenWithMenu
        def createOpenWithMenu(self,parent,label,index,amp_index):

            '''Create a submenu.'''
            menu = self.new_menu(parent)
            self.insert_cascade(parent, index, label=label,menu=menu,underline=amp_index)
            return menu
        #@-node:bob.20071218074136:createOpenWithMenu
        #@+node:bob.20070813163332.353:disableMenu
        def disableMenu (self,menu,name):

            if not menu:
                g.trace("no menu",name)
                return

            realName = self.getRealMenuName(name)
            realName = realName.replace("&","")
            id = menu.FindItem(realName)
            if id:
                item = menu.FindItemById(id)
                item.Enable(0)
            else:
                g.trace("no item",name,val)
        #@nonl
        #@-node:bob.20070813163332.353:disableMenu
        #@+node:bob.20070813163332.354:enableMenu
        def enableMenu (self,menu,name,val):

            if not menu:
                g.trace("no menu",name,val)
                return

            realName = self.getRealMenuName(name)
            realName = realName.replace("&","")
            id = menu.FindItem(realName)
            if id:
                item = menu.FindItemById(id)
                val = g.choose(val,1,0)
                item.Enable(val)
            else:
                g.trace("no item",name,val)
        #@nonl
        #@-node:bob.20070813163332.354:enableMenu
        #@+node:bob.20070813163332.356:setMenuLabel
        def setMenuLabel (self,menu,name,label,underline=-1):

            if not menu:
                g.trace("no menu",name)
                return

            if type(name) == type(0):
                # "name" is actually an index into the menu.
                items = menu.GetMenuItems() # GetItemByPosition does not exist.
                if items and len(items) > name :
                    id = items[name].GetId()
                else: id = None
            else:
                realName = self.getRealMenuName(name)
                realName = realName.replace("&","")
                id = menu.FindItem(realName)

            if id:
                item = menu.FindItemById(id)
                label = self.getRealMenuName(label)
                label = label.replace("&","")
                # g.trace(name,label)
                item.SetText(label)
            else:
                g.trace("no item",name,label)
        #@nonl
        #@-node:bob.20070813163332.356:setMenuLabel
        #@-node:bob.20070813163332.348:Menu methods (non-Tk names)
        #@-others
    #@nonl
    #@-node:bob.20070813163332.333:wxLeoMenu class (leoMenu)
    #@+node:bob.20070907191759:wxLeoLogMenu class
    class wxLeoLogMenu(wx.Menu, wxLeoObject, leoObject):

        def __init__(self, log, tabName, itemList):


            leoObject.__init__(self, log.c)
            wxLeoObject.__init__(self)

            self.log = log
            self.tabName = tabName

            wx.Menu.__init__(self)

            for text in itemList:
                item = self.Append(-1, text)
                self.Bind(wx.EVT_MENU, self.onPopupItemSelected, item)

        def onPopupItemSelected(self, event):

            item = self.FindItemById(event.GetId())
            text = 'onPopup' + item.GetText()

            method = getattr(self.log, text, None)

            if method:
                method(self.tabName)

        #@    @+others
        #@-others
    #@-node:bob.20070907191759:wxLeoLogMenu class
    #@+node:bob.20070813163332.308:wxLeoLog class (leoLog)
    class wxLeoLog (leoFrame.leoLog):

        """The base class for the log pane in Leo windows."""

        #@    @+others
        #@+node:bob.20070813163332.309:leoLog.__init__
        def __init__ (self, c, nb):

            self.c = c

            self.nb = nb

            self.isNull = False
            self.logCtrl = None
            self.newlines = 0
            self.frameDict = {} # Keys are log names, values are None or wx.Frames.
            self.textDict = {}  # Keys are log names, values are None or Text controls.

            self.createInitialTabs()
            self.setFontFromConfig()

            self.nb.Bind(wx.EVT_RIGHT_DOWN, self.onShowTabMenu)

            self.newChoices = ['New']







        #@+node:bob.20070813163332.2:leoLog.createInitialTabs
        def createInitialTabs (self):

            c = self.c ;  nb = self.nb

            # Create the Log tab.
            win = self.logCtrl = self.selectTab('Log')

            win.SetBackgroundColour(
                name2color(
                    c.config.getColor('log_pane_background_color'), 'leo blue'
                )
            )



            # Create the Find tab.
            win = self.createTab('Find',createText=False)

            c.frame.findTabHandler = g.app.gui.createFindTab(c,parentFrame=win)

            # Create the Spell tab.
            # win = self.createTab('Spell',createText=False)
            # color = name2color('leo pink')
            # win.SetBackgroundColour(color)
            # c.frame.spellTabHandler = g.app.gui.createSpellTab(c,parentFrame=win)

            # Make sure the Log is selected.
            self.selectTab('Log')
        #@-node:bob.20070813163332.2:leoLog.createInitialTabs
        #@+node:bob.20070813163332.310:leoLog.setTabBindings
        def setTabBindings (self,tag=None):

            pass # g.trace('wxLeoLog')

        def bind (self,*args,**keys):

            # No need to do this: we can set the master binding by hand.
            pass # g.trace('wxLeoLog',args,keys)
        #@nonl
        #@-node:bob.20070813163332.310:leoLog.setTabBindings
        #@-node:bob.20070813163332.309:leoLog.__init__
        #@+node:bob.20070813163332.311:Config
        #@+node:bob.20070813163332.312:leoLog.configure
        def configure (self,*args,**keys):

            g.trace(args,keys)
        #@nonl
        #@-node:bob.20070813163332.312:leoLog.configure
        #@+node:bob.20070813163332.313:leoLog.configureBorder
        def configureBorder(self,border):

            g.trace(border)
        #@-node:bob.20070813163332.313:leoLog.configureBorder
        #@+node:bob.20070813163332.314:leoLog.setLogFontFromConfig
        def setFontFromConfig (self):

            pass # g.trace()
        #@nonl
        #@-node:bob.20070813163332.314:leoLog.setLogFontFromConfig
        #@-node:bob.20070813163332.311:Config
        #@+node:bob.20070813163332.315:wxLog.put & putnl
        # All output to the log stream eventually comes here.

        def put (self, s, color=None, tabName=None, **keys):

            #print '[%s]'%s, color, tabName

            c = self.c ;

            if g.app.quitting or not c or not c.exists:
                return

            if tabName:
                self.selectTab(tabName)

            try:
                w = self.logCtrl.widget
            except:
                #g.alert('log.put, can\'t write to log widget!')
                w = None
                print 'log tabName:s'
                print

            if w:
                color  = color or keys.get('colour', '') or 'black'

                w.Delete((w.GetInsertionPoint(), w.GetLastPosition()))

                w.BeginTextColour(name2color(color))

                try:
                    w.WriteText(s)
                finally:
                    w.EndTextColour()

                pt = w.GetInsertionPoint()

                w.WriteText('\n')

                last = w.GetLastPosition()

                w.ShowPosition(last)

                w.SetInsertionPoint(pt)

                #self.logCtrl.update_idletasks()

                c.invalidateFocus()
                c.bodyWantsFocusNow()

                try:
                    wx.Yield()
                except:
                    print 'yield failed'
                    pass

            else:
                #@        << put s to logWaiting and print s >>
                #@+node:bob.20071230083410:<< put s to logWaiting and print s >>
                g.app.logWaiting.append((s,color),)

                print "Null log"

                if type(s) == type(u""):
                    s = g.toEncodedString(s,"ascii")

                print s
                #@-node:bob.20071230083410:<< put s to logWaiting and print s >>
                #@nl


        def putnl (self, tabName=None):

            self.put ('\n', tabName=tabName)
        #@-node:bob.20070813163332.315:wxLog.put & putnl
        #@+node:bob.20070907211310:Tab Popup Menu
        #@+node:bob.20070907191759.3:onShowTabMenu
        def onShowTabMenu(self, event):
            point = event.GetPosition()

            (idx, where) = self.nb.HitTest(point)



            choices = self.newChoices

            tabName = None

            #g.trace( where, where & wx.BK_HITTEST_NOWHERE)


            if idx == wx.NOT_FOUND:
                if not where & wx.BK_HITTEST_NOWHERE:
                    return
            else:
                tabName = self.nb.GetPageText(idx)

            choices = self.newChoices[:]



            if tabName not in ['Log', 'Find', 'Completions']:
                choices.append('Rename')

            if tabName not in ['Log', 'Find']:
                choices.append('Delete')

            menu = wxLeoLogMenu(self, tabName, choices)

            self.nb.PopupMenu(menu)

        #@-node:bob.20070907191759.3:onShowTabMenu
        #@+node:bob.20070907191759.1:onPopupDelete
        def onPopupDelete(self, text):
            if text is not None and text not in ['Log', 'Find']:
                self.deleteTab(text)
        #@nonl
        #@-node:bob.20070907191759.1:onPopupDelete
        #@+node:bob.20070907191759.2:onPopupNew
        def onPopupNew(self, tabName):

            dlg = wx.TextEntryDialog(None,
                'Enter a name for the new log tab:',
                'Create New Log Tab'
            )

            result = None
            if dlg.ShowModal() == wx.ID_OK:
                result = dlg.GetValue()

            dlg.Destroy()

            if result:
                self.selectTab(result)
        #@-node:bob.20070907191759.2:onPopupNew
        #@+node:bob.20070907211310.1:onPopupRename
        def onPopupRename(self, tabName):

            if tabName in ['Log', 'Find', 'Completions']:
                return

            dlg = wx.TextEntryDialog(None,
                'Enter a new name for the new log tab:',
                'Rename Log Tab',
                tabName
            )

            result = None
            if dlg.ShowModal() == wx.ID_OK:
                result = dlg.GetValue()

            dlg.Destroy()

            if result:
                self.renameTab(tabName, result)
        #@-node:bob.20070907211310.1:onPopupRename
        #@-node:bob.20070907211310:Tab Popup Menu
        #@+node:bob.20070813163332.316:Tab (wxLog)
        #@+node:bob.20070907223746.1:indexFromName
        def indexFromName(self, tabName):

            for i in xrange(self.nb.GetPageCount()):
                s = self.nb.GetPageText(i)
                if s == tabName:
                    return i

        #@-node:bob.20070907223746.1:indexFromName
        #@+node:bob.20070908114558:tabFromName
        def tabFromName(self, tabName):

            for tab in self.nb.tabs:
                if tabName == tab.tabName:
                    return tab
        #@nonl
        #@-node:bob.20070908114558:tabFromName
        #@+node:bob.20070830080924.1:getTabCtrl

        def getTabCtrl(self, tabName='Tab'):
            return self.textDict.get(tabName).widget
        #@-node:bob.20070830080924.1:getTabCtrl
        #@+node:bob.20070813163332.7:createTab

        def createTab (self, tabName, createText=True, wrap='none'):
            """Create a tab for the log pane notebook.

            """

            nb = self.nb
            # g.trace(tabName)
            if createText:

                w = logTextWidget(self, nb)

                tab = wxLeoTab(self.c, tabName, w.widget, nb)

                nb.appendTab(tab)

                w.setBackgroundColor('light green')

                self.textDict [tabName] = w
                self.frameDict [tabName] = w.widget

                return w

            else:

                win = wx.Panel(nb,name='tab:%s' % tabName)
                self.textDict [tabName] = None
                self.frameDict [tabName] = win
                nb.AddPage(win,tabName)
                return win

        #@-node:bob.20070813163332.7:createTab
        #@+node:bob.20070813163332.317:selectTab
        def selectTab(self, tabName, createText=True, wrap='none'):
            """Select a tab in the log pane notebook, creae the tab if necessary.

            """

            tabFrame = self.frameDict.get(tabName)

            if not tabFrame:
                self.createTab(tabName,createText=createText)

            # Update the status vars.
            self.tabName = tabName
            self.logCtrl = self.textDict.get(tabName)
            self.tabFrame = self.frameDict.get(tabName)

            nb = self.nb

            i = self.indexFromName(tabName)
            if i is not None:
                nb.SetSelection(i)
                assert nb.GetPage(i) == self.tabFrame

            #g.trace(self.nb.GetClientSize())
            self.tabFrame.SetSize(nb.GetClientSize())

            return self.tabFrame
        #@-node:bob.20070813163332.317:selectTab
        #@+node:bob.20070813163332.318:clearTab
        def clearTab (self,tabName,wrap='none'):

            self.selectTab(tabName,wrap=wrap)
            self.logCtrl.setAllText('')

        #@-node:bob.20070813163332.318:clearTab
        #@+node:bob.20070813163332.319:deleteTab
        def deleteTab(self, tabName):

            c = self.c ; nb = self.nb

            if tabName and tabName not in ('Log','Find','Spell'):
                i = self.indexFromName(tabName)
                if i is not None:
                    nb.DeletePage(i)
                    self.textDict [tabName] = None
                    self.frameDict [tabName] = False # A bit of a kludge.
                    self.tabName = None

            self.selectTab('Log')
            c.invalidateFocus()
            c.bodyWantsFocus()
        #@-node:bob.20070813163332.319:deleteTab
        #@+node:bob.20070813163332.326:renameTab
        def renameTab(self, oldName, newName):

            if newName:
                #g.trace(oldName, newName)
                self.tabFromName(oldName).tabName = newName

                self.frameDict[newName] = self.frameDict[oldName]
                self.textDict[newName] = self.textDict[oldName]
                del self.frameDict[oldName]
                del self.textDict[oldName]
        #@-node:bob.20070813163332.326:renameTab
        #@+node:bob.20070813163332.320:getSelectedTab
        def getSelectedTab (self):

            return self.tabName
        #@-node:bob.20070813163332.320:getSelectedTab
        #@+node:bob.20070813163332.321:hideTab
        def hideTab (self,tabName):

            __pychecker__ = '--no-argsused' # tabName

            self.selectTab('Log')
        #@-node:bob.20070813163332.321:hideTab
        #@+node:bob.20070813163332.322:numberOfVisibleTabs
        def numberOfVisibleTabs (self):

            return self.nb.GetPageCount()
        #@-node:bob.20070813163332.322:numberOfVisibleTabs
        #@+node:bob.20070813163332.323:Not used yet
        if 0:
            #@    @+others
            #@+node:bob.20070813163332.324:cycleTabFocus
            def cycleTabFocus (self,event=None,stop_w = None):

                '''Cycle keyboard focus between the tabs in the log pane.'''

                c = self.c ; d = self.frameDict # Keys are page names. Values are Tk.Frames.
                w = d.get(self.tabName)
                # g.trace(self.tabName,w)
                values = d.values()
                if self.numberOfVisibleTabs() > 1:
                    i = i2 = values.index(w) + 1
                    if i == len(values): i = 0
                    tabName = d.keys()[i]
                    self.selectTab(tabName)
                    return
            #@nonl
            #@-node:bob.20070813163332.324:cycleTabFocus
            #@+node:bob.20070813163332.325:lower/raiseTab
            def lowerTab (self,tabName):

                if tabName:
                    b = self.nb.tab(tabName) # b is a Tk.Button.
                    b.config(bg='grey80')
                self.c.invalidateFocus()
                self.c.bodyWantsFocus()

            def raiseTab (self,tabName):

                if tabName:
                    b = self.nb.tab(tabName) # b is a Tk.Button.
                    b.config(bg='LightSteelBlue1')
                self.c.invalidateFocus()
                self.c.bodyWantsFocus()
            #@-node:bob.20070813163332.325:lower/raiseTab
            #@-others
        #@nonl
        #@-node:bob.20070813163332.323:Not used yet
        #@-node:bob.20070813163332.316:Tab (wxLog)
        #@-others
    #@nonl
    #@-node:bob.20070813163332.308:wxLeoLog class (leoLog)
    #@+node:bob.20070902164500:== EXTRA WIDGETS
    #@+node:bob.20070824193757:wxLeoButton class
    class wxLeoButton(wx.Button):
        """A script button for leo's toolbar."""

        def __init__(self, parent,
                text='',
                command=None,
                bg='leo blue',
                size=(-1,24),
                statusLine=None,
                canRemove=True,
                **kw
        ):

            self.command = command
            self.parent = parent
            self.toolbar = parent.toolbar
            self.canRemove = canRemove

            wx.Button.__init__(self,
                self.toolbar,
                label=text,
                size=size,
                style = wx.BU_EXACTFIT
                )
            self.SetBackgroundColour(name2color(bg))

            if statusLine:
                self.SetToolTipString(statusLine)
                wx.ToolTip.Enable(True)
                wx.ToolTip.SetDelay(200)

            self.Bind(wx.EVT_BUTTON, self.onCommand)
            if canRemove:
                self.Bind(wx.EVT_RIGHT_UP, self.onDelete)

        def onDelete(self, event=None):
            self.toolbar.RemoveTool(self.GetId())

        def onCommand(self, event=None):
            if self.command:
                self.command(event=event)

    #@-node:bob.20070824193757:wxLeoButton class
    #@+node:bob.20080103194110:wxLeoIconButton class
    class wxLeoBitmapButton(wx.BitmapButton):
        """A bitmap script button for leo's toolbar."""

        def __init__(self, parent,
                bitmap,
                command=None,
                bg='leo blue',
                canRemove=True,
                statusLine=None,
                **kw
        ):

            self.command = command
            self.parent = parent
            self.toolbar = parent.toolbar

            wx.BitmapButton.__init__(self, self.toolbar,
                bitmap=bitmap,
                size=bitmap.GetSize()
            )
            self.SetBackgroundColour(name2color(bg))

            if statusLine:
                self.SetToolTipString(statusLine)
                wx.ToolTip.Enable(True)
                wx.ToolTip.SetDelay(200)

            self.Bind(wx.EVT_BUTTON, self.onCommand)
            if canRemove:
                self.Bind(wx.EVT_RIGHT_UP, self.onDelete)

        def onDelete(self, event=None):
            self.toolbar.RemoveTool(self.GetId())

        def onCommand(self, event=None):
            if self.command:
                self.command(event=event)
    #@-node:bob.20080103194110:wxLeoIconButton class
    #@+node:bob.20070824165956:wxLeoChapterSelector class

    class wxLeoChapterSelector(wx.ComboBox):
        """A class to manage a chapter selector widget for use in the toolbar."""

        def __init__(self, c, parent):

            self.c = c

            wx.ComboBox.__init__(self, parent,
                choices=[""],
                size=(100,-1),
                style=wx.CB_DROPDOWN | wx.CB_SORT
            )

            self.Bind(wx.EVT_COMBOBOX, self.onSelect)
            self.Bind(wx.EVT_TEXT_ENTER, self.onSelect)

        def cc(self):
            if self.c:
                return self.c.chapterController

        def onSelect(self, event):
            cc = self.cc()
            if cc:
                ch = event.GetString().strip()
                if not ch:
                    ch = 'main'
                if ch in cc.chaptersDict:
                    cc.selectChapterByName(ch)
                else:
                    cc.createChapterByName(ch, p=None, undoType='Create Chapter')

        def update(self):
            cc = self.cc()
            self.Clear()
            if cc:
                #g.trace(cc.selectedChapter)
                self.AppendItems(cc.chaptersDict.keys())
                if cc.selectedChapter:
                    self.SetStringSelection(cc.selectedChapter.name)
                else:
                    self.SetStringSelection('main')


    #@-node:bob.20070824165956:wxLeoChapterSelector class
    #@+node:bob.20070813163332.299:wxLeoIconBar class
    class wxLeoIconBar(object):

        '''An adaptor class that uses a wx.ToolBar for Leo's icon area.'''

        #@    @+others
        #@+node:bob.20070813163332.300:__init__ wxLeoIconBar
        def __init__ (self, c, parentFrame): # wxLeoIconBar

            self.c = c
            cc = c.chapterController

            self.widgets = []

            toolbar = parentFrame.CreateToolBar() # A wxFrame method

            self.toolbar =  self.iconFrame = toolbar

            self.toolbar.SetToolPacking(0)
            self.toolbar.SetMargins((0,0))

            #Insert a spacer to increase the height of the bar.
            # if True or wx.Platform == "__WXMSW__":
                # #tsize = (24,24)
                # path = os.path.join(g.app.loadDir,"..","Icons","LeoApp.ico")
                # bitmap = wx.Bitmap(path,wx.BITMAP_TYPE_ICO)
                # print 'bitmap size', bitmap.GetSize()
                # #toolbar.SetToolBitmapSize((16,16))
                # toolbar.AddLabelTool(-1,'',bitmap)


            if cc:
                cc.chapterSelector = wxLeoChapterSelector(c, toolbar)
                toolbar.AddControl(cc.chapterSelector)

            # Set the official ivar.
            c.frame.iconFrame = self.iconFrame
        #@-node:bob.20070813163332.300:__init__ wxLeoIconBar
        #@+node:bob.20070813163332.301:add
        def add(self,
            text='',
            command=None,
            bg='leo blue',
            size=(-1,24),
            statusLine=None,
            imagefile=None,
            image=None,
            canRemove=True,
            *args, **keys
        ):
            """Add a button containing text or a picture to the icon bar.

            Pictures take precedence over text

            `image` may be a wx.Bitmap or a name, if it is a name then
            the wx.Bitmap found in global namedIcons[image] will be used.

            If image is None and imagefile is loadable and a valid image
            that file will be loaded and converted to a wx.Bitmap.

            If neither image or imagefile are specifid, a text button will
            be created.

            """

            if not command:
                def command(*args,**kw):
                    print "command for widget %s"%text

            if not imagefile and not image and not text:
                return

            bitmap = None
            if isinstance(image, wx.Bitmap):
                bitmap = image

            elif isinstance(image, basestring) and image in namedIcons:
                bitmap = namedIcons[image]

            elif imagefile:
                try:
                    imagefile = g.os_path_join(g.app.loadDir,imagefile)
                    imagefile = g.os_path_normpath(imagefile)
                    image = wx.Image(imagefile)
                    bitmap = wx.BitmapFromImage(image)
                except:
                    bitmap = None

            if bitmap:
                control = wxLeoBitmapButton
            else:
                control = wxLeoButton

            b = control(self,
                text = text,
                bitmap=bitmap,
                command=command,
                bg=bg,
                size=size,
                canRemove=canRemove,
                statusLine=statusLine
            )

            self.widgets.append(b)

            tool = self.toolbar.AddControl(b)

            self.toolbar.Realize()

            return b
        #@-node:bob.20070813163332.301:add
        #@+node:bob.20070813163332.303:clear
        def clear(self):

            """Destroy all the widgets in the icon bar"""

            for w in self.widgets:
                self.toolbar.RemoveTool(w.GetId())
            self.widgets = []
        #@-node:bob.20070813163332.303:clear
        #@+node:bob.20070824202645:setCommandForButton

        def setCommandForButton(self, b, command):
            b.command = command
        #@nonl
        #@-node:bob.20070824202645:setCommandForButton
        #@+node:bob.20070824204145:deleteButton
        def deleteButton (self, w):
            w.onDelete()
        #@-node:bob.20070824204145:deleteButton
        #@+node:bob.20070813163332.305:getFrame
        def getFrame (self):

            return self.iconFrame
        #@-node:bob.20070813163332.305:getFrame
        #@+node:bob.20070813163332.307:show/hide (do nothings)
        def pack (self):    pass
        def unpack (self):  pass
        show = pack
        hide = unpack
        #@-node:bob.20070813163332.307:show/hide (do nothings)
        #@-others
    #@-node:bob.20070813163332.299:wxLeoIconBar class
    #@+node:bob.20070813163332.357:wxLeoMinibuffer class
    class wxLeoMinibuffer:

        #@    @+others
        #@+node:bob.20070813163332.358:__init__

        def __init__ (self,c):

            self.c = c
            self.keyDownModifiers = None
            self.parentFrame = None
            self.ctrl = None#self.createControl(parentFrame)
            self.sizer = None
            # Set the official ivars.
            c.frame.miniBufferWidget = self
            c.miniBufferWidget = self

        #@-node:bob.20070813163332.358:__init__
        #@+node:bob.20070831062824:finishCreate

        def finishCreate(self, parentFrame):

            assert not self.sizer, 'finishCreate already done'

            self.parentFrame = parentFrame

            self.sizer = wx.BoxSizer(wx.HORIZONTAL)

            label = wx.StaticText(
                parentFrame,
                label='mini-buffer  ',
                style=wx.ALIGN_LEFT
            )

            self.ctrl = self.createControl(parentFrame)

            label.SetForegroundColour(name2color('blue'))

            style = wx.ALIGN_CENTER_VERTICAL

            self.sizer.Add(label, 0, style)
            self.sizer.Add(self.ctrl.widget, 1, style)

            return self.sizer

        #@-node:bob.20070831062824:finishCreate
        #@+node:bob.20070831070730:bind
        def bind(self, *args, **kw):
            #g.trace('wxleominibuffer', g.callers())
            pass
        #@nonl
        #@-node:bob.20070831070730:bind
        #@+node:bob.20070813163332.359:createControl
        def createControl (self,parent):

            return minibufferTextWidget(
                self,
                parent,
                name = 'minibuffer',
                style = wx.NO_BORDER
            )
        #@-node:bob.20070813163332.359:createControl
        #@+node:bob.20070901050708:setFocus

        def setFocus(self):
            self.ctrl.setFocus()

        SetFocus = setFocus
        #@-node:bob.20070901050708:setFocus
        #@-others
    #@nonl
    #@-node:bob.20070813163332.357:wxLeoMinibuffer class
    #@+node:bob.20070813163332.360:wxLeoStatusLine class
    class wxLeoStatusLine(object):

        '''A class representing the status line.'''

        #@    @+others
        #@+node:bob.20070813163332.361:__init__
        def __init__ (self, c, *args, **kw):

            self.c = c
            self.parentFrame = None

            self.enabled = False
            self.isVisible = True
            self.lastRow = self.lastCol = 0 #??

            self.status = ''

            self.statusPos = None
            self.statusUNL = None

            self.sizer = None
        #@-node:bob.20070813163332.361:__init__
        #@+node:bob.20071217090205:setBindings
        def setBindings(self, *args, **kw):
            g.trace(myclass(self))
        #@nonl
        #@-node:bob.20071217090205:setBindings
        #@+node:bob.20070831060158.1:finishCreate
        def finishCreate(self, parentFrame):

            assert self.sizer is None, 'finishCreate already done'

            self.parentFrame = parentFrame

            self.sizer = wx.BoxSizer(wx.HORIZONTAL)

            self.statusPos = wx.StaticText(
                parentFrame,
                label='Line XXX, Col XXX',
                style=wx.ALIGN_LEFT
            )

            self.createControl(parentFrame)

            self.set('Loading ...')

            style = wx.ALIGN_CENTER_VERTICAL

            self.sizer.Add(self.statusPos, 0, style)
            self.sizer.Add(self.statusUNL.widget, 1, style)

            return self.sizer


        #@-node:bob.20070831060158.1:finishCreate
        #@+node:bob.20070831062824.1:createControl

        def createControl(self, parent):

           self.statusUNL = self.ctrl = statusTextWidget(
                self, parent,
                name='statusline',
                multiline=False,
                style=wx.NO_BORDER | wx.TE_READONLY,
            )
        #@-node:bob.20070831062824.1:createControl
        #@+node:bob.20070813163332.362:clear
        def clear (self):

            self.statusUNL.clear()
            self.update()
        #@-node:bob.20070813163332.362:clear
        #@+node:bob.20070813163332.363:enable, disable & isEnabled

        #?? what are these for

        def disable (self,background=None):
            self.enabled = False
            c.bodyWantsFocus()

        def enable (self,background="white"):
            self.enabled = True

        def isEnabled(self):
            return self.enabled
        #@nonl
        #@-node:bob.20070813163332.363:enable, disable & isEnabled
        #@+node:bob.20070813163332.364:get

        def get (self):

            if self.c.frame.killed:
                return

            return self.statusUNL.getAllText()
        #@-node:bob.20070813163332.364:get
        #@+node:bob.20070813163332.365:getFrame

        def getFrame (self):

            if self.c.frame.killed:
                return
            else:
                return self.statusFrame
        #@-node:bob.20070813163332.365:getFrame
        #@+node:bob.20070813163332.366:onActivate
        def onActivate (self,event=None):

            pass
        #@-node:bob.20070813163332.366:onActivate
        #@+node:bob.20070813163332.367:pack & show
        def pack (self):
            pass

        show = pack
        #@-node:bob.20070813163332.367:pack & show
        #@+node:bob.20070813163332.368:put
        def put(self, s, color=None, **keys):

            if self.c.frame.killed:
                return

            self.statusUNL.appendText(s)
            self.update()
        #@-node:bob.20070813163332.368:put
        #@+node:bob.20070831041059:set
        def set(self, s, **keys):

            if self.c.frame.killed:
                return

            self.statusUNL.setAllText(s)
        #@nonl
        #@-node:bob.20070831041059:set
        #@+node:bob.20070813163332.369:unpack & hide
        def unpack (self):
            pass

        hide = unpack
        #@-node:bob.20070813163332.369:unpack & hide
        #@+node:bob.20070813163332.370:update (statusLine)

        def update (self):

            if g.app.killed or not self.isVisible or self.c.frame.killed:
                return

            c = self.c
            bodyCtrl = c.frame.body.bodyCtrl

            s = bodyCtrl.getAllText()

            index = bodyCtrl.getInsertPoint()

            row,col = g.convertPythonIndexToRowCol(s,index)

            if col > 0:
                s2 = s[index-col:index]
                col = g.computeWidth (s2,c.tab_width)

            self.statusPos.SetLabel("line %d, col %d  " % (row,col))
            #try:
            self.statusPos.GetParent().GetSizer().Layout()
            #except:
             #   g.trace('leostatusline,================================= cant do layout')

            self.lastRow = row
            self.lastCol = col

        #@-node:bob.20070813163332.370:update (statusLine)
        #@-others
    #@-node:bob.20070813163332.360:wxLeoStatusLine class
    #@+node:bob.20080104144147:plugin menu dialogs
    #@+others
    #@+node:bob.20080104143928:class wxScrolledMessageDialog
    class wxScrolledMessageDialog(object):
        """A class to create and run a Scrolled Message dialog for wxPython"""
        #@    @+others
        #@+node:bob.20080104143928.1:__init__
        def __init__(self, title='Message', label= '', msg='', callback=None, buttons=None):

            """Create and run a modal dialog showing 'msg' in a scrollable window."""

            if buttons is None:
                buttons = []

            self.callback=callback

            self.result = ('Cancel', None)

            self.top = top = wx.Dialog(None, -1, title)

            sizer = wx.BoxSizer(wx.VERTICAL)

            ll = wx.StaticText(top, -1, label)
            sizer.Add(ll, 0, wx.ALIGN_CENTRE|wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.BOTTOM, 5)

            text = wx.TextCtrl(top, -1, msg, size=(400, 200), style=wx.TE_MULTILINE | wx.TE_READONLY)
            sizer.Add(text, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)

            line = wx.StaticLine(top, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
            sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL)

            btnsizer = wx.BoxSizer(wx.HORIZONTAL)

            for name in buttons:
                btn = wx.Button(top, -1, name)
                btn.Bind(wx.EVT_BUTTON, lambda e, self=self, name=name: self.onButton(name), btn)
                btnsizer.Add(btn, 0, wx.ALL, 10)

            btn = wx.Button(top, -1, 'Close')
            btn.Bind(wx.EVT_BUTTON, lambda e, self=self: self.onButton('Close'), btn)
            btn.SetDefault()
            btnsizer.Add(btn)

            #sizer.Add(btnsizer, 0, wx.GROW)
            sizer.Add(btnsizer, 0, wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

            self.top.SetSizerAndFit(sizer)
            top.CenterOnScreen(wx.BOTH)
            top.ShowModal()
        #@-node:bob.20080104143928.1:__init__
        #@+node:bob.20080104143928.2:onButton
        def onButton(self, name):
            """Event handler for all button clicks."""

            if name in ('Close',):
                self.top.Destroy()
                return

            if self.callback:
                retval = self.callback(name, data)
                if retval == 'close':
                    self.top.Destroy()
                else:
                    self.result = ('Cancel', None)
        #@nonl
        #@-node:bob.20080104143928.2:onButton
        #@-others


    #@-node:bob.20080104143928:class wxScrolledMessageDialog
    #@+node:bob.20080104144001:class wxPropertiesDialog
    class wxPropertiesDialog(object):

        """A class to create and run a Properties dialog"""

        #@    @+others
        #@+node:bob.20080104144001.1:__init__
        def __init__(self, title, data, callback=None, buttons=[]):
            #@    << docstring >>
            #@+node:bob.20080104144001.2:<< docstring >>
            """ Initialize and show a Properties dialog.

                'buttons' should be a list of names for buttons.

                'callback' should be None or a function of the form:

                    def cb(name, data)
                        ...
                        return 'close' # or anything other than 'close'

                where name is the name of the button clicked and data is
                a data structure representing the current state of the dialog.

                If a callback is provided then when a button (other than
                'OK' or 'Cancel') is clicked then the callback will be called
                with name and data as parameters.

                    If the literal string 'close' is returned from the callback
                    the dialog will be closed and self.result will be set to a
                    tuple (button, data).

                    If anything other than the literal string 'close' is returned
                    from the callback, the dialog will continue to be displayed.

                If no callback is provided then when a button is clicked the
                dialog will be closed and self.result set to  (button, data).

                The 'ok' and 'cancel' buttons (which are always provided) behave as
                if no callback was supplied.

            """
            #@-node:bob.20080104144001.2:<< docstring >>
            #@nl

            if buttons is None:
                buttons = []

            self.entries = []
            self.title = title
            self.callback = callback
            self.buttons = buttons
            self.data = data

            self.result = ('Cancel', None)
            self.top = top = wx.Dialog(None,  title=title)

            sizer = wx.BoxSizer(wx.VERTICAL)

            tp = self.createEntryPanel()
            sizer.Add(tp, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

            btnsizer = wx.BoxSizer(wx.HORIZONTAL)

            for name in buttons:
                btn = wx.Button(top, -1, name)
                btn.Bind(wx.EVT_BUTTON, lambda e, self=self, name=name: self.onButton(name), btn)
                btnsizer.Add(btn)

            btn = wx.Button(top, wx.ID_OK)
            btn.Bind(wx.EVT_BUTTON, lambda e, self=self: self.onButton('OK'), btn)
            btn.SetDefault()
            btnsizer.Add(btn, 0, wx.ALL, 5)

            btn = wx.Button(top, wx.ID_CANCEL)
            btnsizer.Add(btn, wx.ALL, 5)

            sizer.Add(btnsizer, 0, wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

            self.top.SetSizerAndFit(sizer)
            top.CenterOnScreen()
            val = top.ShowModal()

        #@-node:bob.20080104144001.1:__init__
        #@+node:bob.20080104144001.3:onButton

        def onButton(self, name):
            """Event handler for all button clicks."""

            data = self.getData()
            self.result = (name, data)

            if name in ('OK', 'Cancel'):
                self.top.Destroy()
                return

            if self.callback:
                retval = self.callback(name, data)
                if retval == 'close':
                    self.top.Destroy()
                else:
                    self.result = ('Cancel', None)


        #@-node:bob.20080104144001.3:onButton
        #@+node:bob.20080104144001.4:createEntryPanel
        def createEntryPanel(self):

            panel = wx.Panel(self.top, -1)

            data = self.data
            sections = data.keys()
            sections.sort()

            box = wx.BoxSizer(wx.VERTICAL)

            for section in sections:

                label = wx.StaticText(panel, -1, section)
                box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.BOTTOM, 5)

                options = data[section].keys()
                options.sort()

                lst = []
                for option in options:
                    ss = wx.StaticText(panel, -1, option),
                    tt = wx.TextCtrl(panel, -1, data[section][option], size=(200,-1))
                    lst.extend ((ss, (tt, 0, wx.EXPAND)))

                    self.entries.append((section, option, tt))

                sizer = wx.FlexGridSizer(cols=2, hgap=12, vgap=2)
                sizer.AddGrowableCol(1)
                sizer.AddMany(lst)

                box.Add(sizer, 0, wx.GROW|wx.ALL, 5)

                line = wx.StaticLine(panel, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
                box.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL)

            panel.SetSizer(box)
            panel.SetAutoLayout(True)
            return panel
        #@-node:bob.20080104144001.4:createEntryPanel
        #@+node:bob.20080104144001.5:getData
        def getData(self):
            """Return the modified configuration."""

            data = {}
            for section, option, entry in self.entries:
                if section not in data:
                    data[section] = {}
                s = entry.GetValue()
                s = g.toEncodedString(s,"ascii",reportErrors=True) # Config params had better be ascii.
                data[section][option] = s

            return data


        #@-node:bob.20080104144001.5:getData
        #@-others
    #@nonl
    #@-node:bob.20080104144001:class wxPropertiesDialog
    #@-others
    #@nonl
    #@-node:bob.20080104144147:plugin menu dialogs
    #@+node:bob.20080105082325:nav_buttons dialogs
    #@+others
    #@+node:bob.20080105082325.1:class wxListBoxDialog
    class wxListBoxDialog(wx.Frame):

        #@    @+others
        #@+node:bob.20080105082325.2:__init__
        def __init__(self, c, title, label='', buttons = [], log=None):

            self.c = c

            self.buttonSizer = buttonSizers = []
            self.buttonCtrls = buttonCtrls = {}

            self.defaultActions = {
                'Hide': self.hide,
                'Go': self.go
            }

            wx.Frame.__init__(self, c.frame.top,
               title=title, size=(300, 500)
            )

            if not log:
                log = lambda s: sys.stdout.write('\n%s'%s)
            self.log = log

            self.boxSizer = boxSizer = wx.BoxSizer(wx.VERTICAL)

            self.listbox = listbox = wx.ListBox(self, -1,
                choices=['zero', 'one', 'two', 'three'], style=wx.LB_EXTENDED
            )

            listbox.Bind(wx.EVT_LISTBOX, self.onClick)
            listbox.Bind(wx.EVT_LISTBOX_DCLICK, self.onDoubleClick)

            boxSizer.Add(listbox, 1, wx.EXPAND|wx.ALL, 5)


            #@    << add buttons >>
            #@+node:bob.20080105082325.3:<< add buttons >>


            for i, items in enumerate(buttons):

                buttonSizers.append(wx.BoxSizer(wx.HORIZONTAL))

                for name, retval, image  in items:

                    if not retval:
                        retval = name
                    if image:
                        b = wx.BitmapButton(self,
                            bitmap = namedIcons[image]
                        )
                    else:
                        b  = wx.Button(self, -1, name)

                    b.Bind(wx.EVT_BUTTON, lambda event, retval=retval: self.onButton(retval))

                    buttonSizers[i].Add( b, 0,
                        wx.ALL | wx.ALIGN_CENTER_VERTICAL,
                        5
                    )
                    self.buttonCtrls[name or retval] = b

            for sizer in buttonSizers:
                self.boxSizer.Add(sizer, 0,
                    wx.ALIGN_CENTRE | wx.ALIGN_CENTER_VERTICAL,
                    10
                )
            #@-node:bob.20080105082325.3:<< add buttons >>
            #@nl

            self.SetSizer(boxSizer)

            self.addIconBarButtons()

            self.Bind(wx.EVT_CLOSE, self.hide)
        #@-node:bob.20080105082325.2:__init__
        #@+node:bob.20080105082325.4:onDoubleClick
        def onDoubleClick(self, event):
            self.go(event)

        #@-node:bob.20080105082325.4:onDoubleClick
        #@+node:bob.20080105082325.5:onClick
        def onClick(self, event):
            print 'click', self.listbox.GetString(event.GetSelection())
            pass
        #@-node:bob.20080105082325.5:onClick
        #@+node:bob.20080105082325.6:onButton
        def onButton(self,retval):

            if retval in self.actions:
                return self.actions[retval]()

            if retval in self.defaultActions:
                return self.defaultActions[retval]()

            g.alert(retval)
        #@-node:bob.20080105082325.6:onButton
        #@+node:bob.20080105082325.7:go
        def go(self, event=None):

            """Handle clicks in the "go" button in a list box dialog."""

            # __pychecker__ = '--no-argsused' # the event param must be present.

            c = self.c ; listbox = self.listbox

            # Work around an old Python bug.  Convert strings to ints.
            if event:
                item = event.GetSelection()
            else:
                item = -1
                items = listbox.GetSelections()
                if len(items):
                    item = items[0]

            if item > -1:
                p = self.positionList[item]
                c.beginUpdate()
                try:
                    c.frame.tree.expandAllAncestors(p)
                    c.selectPosition(p,updateBeadList=True)
                        # A case could be made for updateBeadList=False
                finally:
                    c.endUpdate()
        #@-node:bob.20080105082325.7:go
        #@+node:bob.20080105082325.8:hide
        def hide(self, event=None):
            self.Show(False)



        #@-node:bob.20080105082325.8:hide
        #@-others



        def CloseWindow(self, event):
            self.Show(False)

    #@-node:bob.20080105082325.1:class wxListBoxDialog
    #@+node:bob.20080105082325.9:class marksDialog (listBoxDialog)
    class wxMarksDialog (wxListBoxDialog):

        """A class to create the marks dialog"""

        #@    @+others
        #@+node:bob.20080105082325.10: __init__
        def __init__ (self, c, images=None):

            """Create a Marks listbox dialog."""

            self.c = c
            self.bg = 'old lace'

            self.label = None
            self.title = 'Marks for %s' % g.shortFileName(c.mFileName) # c.frame.title

            self.actions = []

            buttons = [
                (
                    ('Go', '', ''),
                    ('Hide', '', '')
                ),
            ]

            wxListBoxDialog.__init__(self, c,
                self.title,
                self.label,
                buttons=buttons
            )

            #self.updateMarks()
            #if not marksInitiallyVisible:
            #   self.Show(False)
        #@-node:bob.20080105082325.10: __init__
        #@+node:bob.20080105082325.11:addIconBarButtons
        def addIconBarButtons (self):

            c = self.c ;

            # Add 'Marks' button to icon bar.

            def marksButtonCallback(*args,**keys):
                self.Show()
                self.Iconize(False)

            self.marks_button = c.frame.addIconButton(
                text="Marks",
                command=marksButtonCallback,
                bg=self.bg,
                canRemove = False
            )
        #@-node:bob.20080105082325.11:addIconBarButtons
        #@+node:bob.20080105082325.12:updateMarks
        def updateMarks(self, tag,keywords):

            '''Recreate the Marks listbox.'''

            # Warning: it is not correct to use self.c in hook handlers.

            c = keywords.get('c')

            try:
                if c != self.c:
                     return
            except:
                c = None

            if not c:
                return

            self.listbox.Clear()

            # Bug fix 5/12/05: Set self.positionList for use by tkinterListBoxDialog.go().
            i = 0 ; self.positionList = [] ; tnodeList = []

            items = []
            for p in c.allNodes_iter():
                if p.isMarked() and p.v.t not in tnodeList:
                    items.append(p.headString().strip())
                    tnodeList.append(p.v.t)
                    self.positionList.append(p.copy())

            self.listbox.AppendItems(items)
        #@-node:bob.20080105082325.12:updateMarks
        #@-others
    #@nonl
    #@-node:bob.20080105082325.9:class marksDialog (listBoxDialog)
    #@+node:bob.20080105082325.13:class wxRecentSectionsDialog (wxListBoxDialog)
    class wxRecentSectionsDialog (wxListBoxDialog):

        """A class to create the recent sections dialog"""

        #@    @+others
        #@+node:bob.20080105082325.14:__init__
        def __init__ (self,c,images=None):

            """Create a Recent Sections listbox dialog."""

            self.c = c
            self.bg = 'old lace'

            self.label = None
            self.title = "Recent nodes for %s" % g.shortFileName(c.mFileName)
            self.lt_nav_button = self.rt_nav_button = None # Created by createFrame.

            # Init the base class.
            # N.B.  The base class contains positionList ivar.

            self.actions = {
                'Clear All': self.clearAll,
                'Delete': self.deleteEntry,
                'backwards': c.goPrevVisitedNode,
                'forwards': c.goNextVisitedNode,
            }


            buttons = [
                (
                    ('', 'backwards', 'lt_arrow_enabled'),
                    ('', 'forwards', 'rt_arrow_enabled'),
                ),
                (
                    ('Go', '', ''),
                    ('Hide', '', '')
                ),
                (
                    ('Clear All', '', ''),
                    ('Delete', '', '')
                ),
            ]

            wxListBoxDialog.__init__(self,c,self.title,self.label, buttons=buttons)

            self.fillbox() # Must be done initially.

            if True or not recentInitiallyVisible:
                self.Show(False)

            self.updateButtons()
        #@-node:bob.20080105082325.14:__init__
        #@+node:bob.20080105082325.15:addIconBarButtons
        def addIconBarButtons (self):

            c = self.c ;

            # Add 'Recent' button to icon bar.

            def recentButtonCallback(*args,**keys):
                self.fillbox(forceUpdate=True)
                self.Show()
                self.Iconize(False)

            self.sections_button = c.frame.addIconButton(
                text="Recent",
                command=recentButtonCallback,
                bg=self.bg,
                canRemove=False
            )

            # Add left and right arrows to icon bar.

            self.lt_nav_iconFrame_button = c.frame.addIconButton(
                image= 'lt_arrow_disabled',
                command=c.goPrevVisitedNode,
                bg=self.bg,
                canRemove=False
            )

            self.rt_nav_iconFrame_button = c.frame.addIconButton(
                image = 'rt_arrow_disabled',
                command=c.goNextVisitedNode,
                bg=self.bg,
                canRemove=False
            )

            # Don't dim the button when it is inactive.
            #for b in (self.lt_nav_iconFrame_button, self.rt_nav_iconFrame_button):
            #   fg = b.cget("foreground")
            #   b.configure(disabledforeground=fg)

        #@-node:bob.20080105082325.15:addIconBarButtons
        #@+node:bob.20080105082325.16:clearAll
        def clearAll (self,event=None):

            """Handle clicks in the "Clear All" button of the Recent Sections listbox dialog."""

            c = self.c

            self.positionList = []
            c.nodeHistory.clear()
            self.fillbox()
        #@nonl
        #@-node:bob.20080105082325.16:clearAll
        #@+node:bob.20080105082325.17:deleteEntry
        def deleteEntry (self,event=None):
            """Handle clicks in the "Delete" button of a Recent Sections listbox dialog."""

            c = self.c
            items = self.listbox.GetSelections()
            newPositionList = []

            for n, p in enumerate(self.positionList):
                if n in items:
                    c.nodeHistory.remove(p)
                newPositionList.append(p)
                self.positionList = newPositionList
                self.fillbox()


        #@-node:bob.20080105082325.17:deleteEntry
        #@+node:bob.20080105082325.18:fillbox
        def fillbox(self,forceUpdate=False):

            """Update the Recent Sections listbox."""

            # Only fill the box if the dialog is visible.
            # This is an important protection against bad performance.

            #if not forceUpdate and self.top.state() != "normal":
            #    return

            self.listbox.Clear()
            c = self.c
            self.positionList = []
            tnodeList = []
            items = []
            for p in c.nodeHistory.visitedPositions():
                if c.positionExists(p) and p.v.t not in tnodeList:
                    items.append(p.headString().strip())
                    tnodeList.append(p.v.t)
                    self.positionList.append(p.copy())

            self.listbox.AppendItems(items)

        #@-node:bob.20080105082325.18:fillbox
        #@+node:bob.20080105082325.19:updateButtons
        def updateButtons (self):

            c = self.c

            for b, b2, enabled_image, disabled_image,cond in (
                (
                    self.buttonCtrls['backwards'],
                    self.lt_nav_iconFrame_button,

                    'lt_arrow_enabled',
                    'lt_arrow_disabled',

                    c.nodeHistory.canGoToPrevVisited()
                ),
                (
                    self.buttonCtrls['forwards'],
                    self.rt_nav_iconFrame_button,

                    'rt_arrow_enabled',
                    'rt_arrow_disabled',

                    c.nodeHistory.canGoToNextVisited()
                ),
            ):
                # Disabled state makes the icon look bad.

                if cond:
                    image = namedIcons[enabled_image]
                else:
                    image = namedIcons[disabled_image]

                b.SetBitmapLabel(image)
                b2.SetBitmapLabel(image)
        #@-node:bob.20080105082325.19:updateButtons
        #@+node:bob.20080105082325.20:updateRecent
        def updateRecent(self,tag,keywords):

            # Warning: it is not correct to use self.c in hook handlers.
            c = keywords.get('c')
            try:
                if c != self.c:
                    return
            except:
                c = None

            if not c:
                return

            forceUpdate = tag in ('new2','open2')
            self.fillbox(forceUpdate)
            self.updateButtons()
        #@nonl
        #@-node:bob.20080105082325.20:updateRecent
        #@-others
    #@nonl
    #@-node:bob.20080105082325.13:class wxRecentSectionsDialog (wxListBoxDialog)
    #@-others
    #@-node:bob.20080105082325:nav_buttons dialogs
    #@-node:bob.20070902164500:== EXTRA WIDGETS
    #@+node:bob.20070902164500.1:== TREE WIDGETS ==
    #@+node:bob.20070813163332.371:wxLeoTree class (leoFrame.leoTree):
    class wxLeoTree (leoFrame.leoTree):
        #@    @+others
        #@+node:bob.20070813163332.372:__init__
        def __init__ (self, c, parentFrame):


            self.c = c
            self.frame = c.frame

            # Init the base class.
            leoFrame.leoTree.__init__(self, self.frame)


            #@    << init config >>
            #@+node:bob.20070816202030:<< init config >>
            # Configuration and debugging settings.
            # ?? These must be defined here to eliminate memory leaks. ??

            c = self.c

            self.allow_clone_drags          = c.config.getBool('allow_clone_drags')
            self.center_selected_tree_node  = c.config.getBool('center_selected_tree_node')
            self.enable_drag_messages       = c.config.getBool("enable_drag_messages")
            self.expanded_click_area        = c.config.getBool('expanded_click_area')
            #self.gc_before_redraw           = c.config.getBool('gc_before_redraw')


            for item, default in (
                ('headline_text_editing_foreground_color', 'black'),
                ('headline_text_editing_background_color', 'white'),
                ('headline_text_editing_selection_foreground_color', None),
                ('headline_text_editing_selection_background_color', None),
                ('headline_text_selected_foreground_color', None),
                ('headline_text_selected_background_color', None),
                ('headline_text_editing_selection_foreground_color', None),
                ('headline_text_editing_selection_background_color', None),
                ('headline_text_unselected_foreground_color', None),
                ('headline_text_unselected_background_color', None),
                ('outline_pane_background_color', 'leo yellow')
            ):
                setattr(self, item, name2color(c.config.getColor(item), default))

            self.idle_redraw = c.config.getBool('idle_redraw')

            self.initialClickExpandsOrContractsNode = c.config.getBool(
                'initialClickExpandsOrContractsNode')
            self.look_for_control_drag_on_mouse_down = c.config.getBool(
                'look_for_control_drag_on_mouse_down')
            self.select_all_text_when_editing_headlines = c.config.getBool(
                'select_all_text_when_editing_headlines')

            self.stayInTree     = c.config.getBool('stayInTreeAfterSelect')
            self.trace          = c.config.getBool('trace_tree')
            #self.trace_alloc    = c.config.getBool('trace_tree_alloc')
            self.trace_chapters = c.config.getBool('trace_chapters')
            self.trace_edit     = c.config.getBool('trace_tree_edit')
            #self.trace_gc       = c.config.getBool('trace_tree_gc')
            self.trace_redraw   = c.config.getBool('trace_tree_redraw')
            self.trace_select   = c.config.getBool('trace_select')
            #self.trace_stats    = c.config.getBool('show_tree_stats')
            self.use_chapters   = c.config.getBool('use_chapters')
            #@-node:bob.20070816202030:<< init config >>
            #@nl

            #g.trace('tree', frame)


            # A dummy ivar used in c.treeWantsFocus, etc.
            self.canvas = self

            # A lockout that prevents event handlers from firing during redraws.
            self.drawing = False

            #self.effects = wx.Effects()

            self.keyDownModifiers = None

            self.updateCount = 0

            self.treeCtrl = None
            self.treeCtrl = self.createControl(parentFrame)

            self.drag_p = None
            self.dragging = None
            self.controlDrag = None







        #@+node:bob.20070813163332.373:createBindings

        def createBindings (self): # wxLeoTree
            pass

        #@-node:bob.20070813163332.373:createBindings
        #@+node:bob.20070813163332.6:createControl

        def createControl (self, parentFrame):
            """Create an OutlineCanvasPanel."""

            treeCtrl = OutlineCanvasPanel(
                parentFrame,
                leoTree=self,
                name='tree'
            )

            entry = treeCtrl._entry
            self.headlineTextWidget = hw = headlineTextWidget(self, widget=entry)


            entry.Bind(wx.EVT_KILL_FOCUS, self.entryLostFocus)
            entry.Bind(wx.EVT_SET_FOCUS, self.entryGotFocus)

            treeCtrl.Bind(wx.EVT_KILL_FOCUS, self.treeLostFocus)
            treeCtrl.Bind(wx.EVT_SET_FOCUS, self.treeGotFocus)


            return treeCtrl
        #@-node:bob.20070813163332.6:createControl
        #@+node:bob.20070813163332.375:setBindings
        def setBindings(self):

            pass # g.trace('wxLeoTree: to do')

        def bind(self,*args,**keys):

            pass # g.trace('wxLeoTree',args,keys)
        #@nonl
        #@-node:bob.20070813163332.375:setBindings
        #@-node:bob.20070813163332.372:__init__
        #@+node:bob.20070830132656:__str__ & __repr__

        def __repr__ (self):

            return "Tree %d" % id(self)

        __str__ = __repr__

        #@-node:bob.20070830132656:__str__ & __repr__
        #@+node:bob.20070818175928:edit_widget

        def edit_widget(self, p=None):
            """Return the headlineTextWidget."""

            return self.headlineTextWidget
        #@-node:bob.20070818175928:edit_widget
        #@+node:bob.20070823140954:Focus Gain/Lose

        def entryLostFocus(self, event):
            self.endEditLabel(event)

        def entryGotFocus(self, event):
            pass

        def treeGotFocus(self, event):
            #g.trace()
            if self.treeCtrl:
                self.treeCtrl.redraw()
            self.c.focusManager.gotFocus(self, event)

        def treeLostFocus(self, event):
            #g.trace()
            if self.treeCtrl:
                self.treeCtrl.redraw()
            self.c.focusManager.lostFocus(self, event)
            #g.trace()

        def hasFocus(self):
            if not self.treeCtrl:
                return None
            fw = wx.Window.FindFocus()
            return fw is self.treeCtrl #or fw is self.treeCtrl._canvas
        #@-node:bob.20070823140954:Focus Gain/Lose
        #@+node:bob.20070901202654:SetFocus
        def setFocus(self):

            if not self.treeCtrl or g.app.killed or self.c.frame.killed: return

            self.treeCtrl.SetFocus()

        SetFocus = setFocus

        #@-node:bob.20070901202654:SetFocus
        #@+node:bob.20070906201117:getCanvas
        def getCanvas(self):
            return self.treeCtrl._canvas
        #@nonl
        #@-node:bob.20070906201117:getCanvas
        #@+node:bob.20070907062229:getCanvasHeight
        def getCanvasHeight(self):
            print '++++++', self.treeCtrl._canvas._size.height
            return self.treeCtrl._canvas._size.height

        #@-node:bob.20070907062229:getCanvasHeight
        #@+node:bob.20080105224858:getLineHeight
        #@-node:bob.20080105224858:getLineHeight
        #@+node:bob.20070907054452:onScrollRelative
        def onScrollRelative(self, orient, value):
            self.treeCtrl.onScrollRelative(orient, value)
        #@nonl
        #@-node:bob.20070907054452:onScrollRelative
        #@+node:bob.20070906200727:HasCapture / Capture / Release Mouse
        def HasCapture(self):
            return self.getCanvas().HasCapture()

        def CaptureMouse(self):
            return self.getCanvas().CaptureMouse()

        def ReleaseMouse(self):
            return self.getCanvas().ReleaseMouse()
        #@-node:bob.20070906200727:HasCapture / Capture / Release Mouse
        #@+node:bob.20070906203543:setCursor
        def setCursor(self, cursor):
            if cursor == 'drag':
                self.getCanvas().SetCursor(wx.StockCursor(wx.CURSOR_HAND))
            else:
                self.getCanvas().SetCursor(wx.StockCursor(wx.CURSOR_ARROW))

        #@-node:bob.20070906203543:setCursor
        #@+node:bob.20080106181804:idle_redraw
        def idle_redraw(*args, **kw):
            return
        #@nonl
        #@-node:bob.20080106181804:idle_redraw
        #@+node:bob.20070813163332.376:Drawing
        #@+node:bob.20070813163332.379:beginUpdate
        def beginUpdate(self):

            self.updateCount += 1
        #@-node:bob.20070813163332.379:beginUpdate
        #@+node:bob.20070813163332.380:endUpdate
        def endUpdate(self, flag=True, scroll=False):

            assert(self.updateCount > 0)

            self.updateCount -= 1
            if flag and self.updateCount <= 0:
                self.redraw()

                if self.updateCount < 0:
                    g.trace("Can't happen: negative updateCount", g.callers())



        #@-node:bob.20070813163332.380:endUpdate
        #@+node:bob.20070813163332.36:redraw & redraw_now & helpers
        redrawCount = 0

        def redraw (self, scroll=True):

            c = self.c ;
            cc = c.chapterController
            tree = self.treeCtrl

            if c is None or self.drawing:
                return

            #self.redrawCount += 1
            #if not g.app.unitTesting: g.trace(self.redrawCount,g.callers())

            self.drawing = True # Disable event handlers.

            if cc and cc.chapterSelector:
                cc.chapterSelector.update()

            try:
                self.expandAllAncestors(c.currentPosition())
                tree.update()
                self.scrollTo()
            finally:
                self.drawing = False # Enable event handlers.

            #if not g.app.unitTesting: g.trace('done')

        redraw_now = redraw
        #@-node:bob.20070813163332.36:redraw & redraw_now & helpers
        #@+node:bob.20070823192054:scrollTo
        def scrollTo(self,p=None):
            """Scrolls the canvas so that p is in view.

            Assumes that the canvas is in a valid state.
            """

            __pychecker__ = '--no-argsused' # event not used.
            __pychecker__ = '--no-intdivide' # suppress warning about integer division.

            c = self.c
            tree = self.treeCtrl

            if not p or not c.positionExists(p):
                p = c.currentPosition()

            if not p or not c.positionExists(p):
                # g.trace('current p does not exist',p)
                p = c.rootPosition()

            if not p or not c.positionExists(p):
                # g.trace('no position')
                return

            target_p = p

            positions = tree.getPositions()

            #@    << virtual top for target >>
            #@+node:bob.20070823194625:<< virtual top for target >>

            #
            # Find the virtual top for node.
            #

            hoistFlag = bool(c.hoistStack)

            if hoistFlag:
                stk = [c.hoistStack[-1].p]
            else:
                stk = [c.rootPosition()]
            #g.trace('====================')
            count = 0
            while stk:

                p = stk.pop()

                while p:

                    if p == target_p:
                        stk = None
                        p = None
                        break

                    #g.trace('count', p)
                    if stk or not hoistFlag:
                        newp = p.next()
                    else:
                        newp = None

                    count += 1

                    if p.isExpanded() and p.hasFirstChild():
                        stk.append(newp)
                        p = p.firstChild()
                        continue

                    p = newp

            targetTop = count * tree._canvas._lineHeight
            #g.trace(targetTop, count)
            #@nonl
            #@-node:bob.20070823194625:<< virtual top for target >>
            #@nl

            if 1 and self.center_selected_tree_node:
                newtop = targetTop - (self.treeCtrl.GetClientSize().height)//2
                if newtop < 0:
                    newtop = 0

                #tree.onScroll(wx.VERTICAL, newtop)
                #g.trace(newtop, targetTop, self.treeCtrl.GetClientSize())
            else:
                assert False, 'FIXME - tree.ScrollTo'

        idle_scrollTo = scrollTo # For compatibility.
        #@-node:bob.20070823192054:scrollTo
        #@-node:bob.20070813163332.376:Drawing
        #@+node:bob.20070813163332.382:== Event handlers ==
        #@+node:bob.20070910164249.1:def onChar
        def onChar(self, event, keycode, keysym):
            pass
        #@nonl
        #@-node:bob.20070910164249.1:def onChar
        #@+node:bob.20070813163332.385:onHeadlineKey

        # k.handleDefaultChar calls onHeadlineKey.
        def onHeadlineKey (self, event):

            #g.trace(event)

            if g.app.killed or self.c.frame.killed:
                return

            if event and event.keysym:
                self.updateHead(event, event.widget)
        #@-node:bob.20070813163332.385:onHeadlineKey
        #@+node:bob.20070906100710:Drag
        #@+node:bob.20070906100710.1:startDrag
        def startDrag(self, p, event):

            c = self.c
            c.setLog()

            if not p:
                return
            #g.trace()


            self.startDragPoint = self.dragPoint = event.GetPosition()

            self.drag_p = p # don't copy as p is enhanced

            self.dragging = True

            #g.trace("\n\t*** start drag ***", self.drag_p.headString())

            #print '\tself.controlDrag', self.controlDrag

            if self.allow_clone_drags:
                self.controlDrag = c.frame.controlKeyIsDown
                if self.look_for_control_drag_on_mouse_down:
                    if self.enable_drag_messages:
                        if self.controlDrag:
                            g.es("dragged node will be cloned")
                        else:
                            g.es("dragged node will be moved")
            else:
                 self.controlDrag = False

            self.setCursor('drag')
        #@-node:bob.20070906100710.1:startDrag
        #@+node:bob.20070906194123:onDrag
        def onDrag(self, p, event):

            #print 'onDrag',

            c = self.c

            if not p:
                p = self.drag_p

            c.setLog()

            if not self.dragging:
                if not g.doHook("drag1",c=c,p=p,v=p,event=event):
                    self.startDrag(p, event)
                g.doHook("drag2",c=c,p=p,v=p,event=event)

            if not g.doHook("dragging1",c=c,p=p,v=p,event=event):
                self.continueDrag(p, event)
            g.doHook("dragging2",c=c,p=p,v=p,event=event)
        #@-node:bob.20070906194123:onDrag
        #@+node:bob.20070907050034:onEndDrag
        def onEndDrag(self, drop_p, event):

            """Tree end-of-drag handler."""

            c = self.c ; p = self.drag_p
            if not (drop_p and self.drag_p):
                self.cancelDrag()

            c.setLog()

            if not g.doHook("enddrag1",c=c,p=p,v=p,event=event):
                self.endDrag(drop_p, event)
            g.doHook("enddrag2",c=c,p=p,v=p,event=event)
        #@+node:bob.20070906100746:endDrag
        def endDrag (self, drop_p, event):

            """The official helper of the onEndDrag event handler."""

            c = self.c
            c.setLog()

            #g.trace()

            p = self.drag_p

            if not event:
                return

            c.beginUpdate()
            redrawFlag = False
            try:

                #@        << set drop_p, childFlag >>
                #@+node:bob.20070906100746.1:<< set drop_p, childFlag >>



                childFlag = drop_p and drop_p.hasChildren() and drop_p.isExpanded()
                #@-node:bob.20070906100746.1:<< set drop_p, childFlag >>
                #@nl
                if self.allow_clone_drags:
                    if not self.look_for_control_drag_on_mouse_down:
                        self.controlDrag = c.frame.controlKeyIsDown

                redrawFlag = drop_p and drop_p.v.t != p.v.t
                if redrawFlag: # Disallow drag to joined node.
                    #@            << drag p to drop_p >>
                    #@+node:bob.20070906100746.2:<< drag p to drop_p>>
                    #g.trace('\n')
                    #print '\tsource:', p.headString()
                    #print '\ttarget:', drop_p.headString()

                    if self.controlDrag: # Clone p and move the clone.
                        if childFlag:
                            c.dragCloneToNthChildOf(p, drop_p, 0)
                        else:
                            c.dragCloneAfter(p, drop_p)
                    else: # Just drag p.
                        if childFlag:
                            c.dragToNthChildOf(p, drop_p, 0)
                        else:
                            c.dragAfter(p,drop_p)
                    #@-node:bob.20070906100746.2:<< drag p to drop_p>>
                    #@nl
                elif self.trace and self.verbose:
                    g.trace("Cancel drag")

                # Reset the old cursor by brute force.
                self.setCursor('default')
                self.dragging = False
                self.drag_p = None
            finally:
                # Must set self.drag_p = None first.
                c.endUpdate(redrawFlag)
                c.recolor_now() # Dragging can affect coloring.
        #@-node:bob.20070906100746:endDrag
        #@-node:bob.20070907050034:onEndDrag
        #@+node:bob.20070906195449:cancelDrag
        def cancelDrag(self, p, event):

            #g.trace()

            if self.trace and self.verbose:
                g.trace("Cancel drag")

            # Reset the old cursor by brute force.
            self.setCursor('default')
            self.dragging = False
            self.drag_p = None
        #@-node:bob.20070906195449:cancelDrag
        #@+node:bob.20070906195449.1:continueDrag
        def continueDrag(self, p, event):

            #g.trace()

            p = self.drag_p
            if not p:
                return

            try:
                point = event.GetPosition()
                if self.dragging: # This gets cleared by onEndDrag()
                    self.dragPoint = point
                    #print 'ContiueDrag',
                    #@            << scroll the canvas as needed >>
                    #@+node:bob.20070906195449.2:<< scroll the canvas as needed >>

                    # Scroll the screen.

                    # TODO: This is rough, scrolling needs to be much smoother
                    # TODO: Use a timer instead of mouse motion

                    canvas = self.getCanvas()

                    treeHeight = canvas._treeHeight
                    top = canvas._virtualTop

                    width, height = canvas._size

                    pos = point.y
                    vpos = pos + top


                    updelta = max(1, vpos/treeHeight)
                    downdelta = max(1, (treeHeight - vpos)/treeHeight)

                    cx = canvas.GetPosition().x


                    diff = downdelta = updelta = 1
                    if pos < 10:
                        diff = (10 - pos)*5
                        self.onScrollRelative(wx.VERTICAL, -min(updelta*diff, 5000) )

                    elif pos > height - 10:
                        diff = (height - 10 - pos)*5
                        self.onScrollRelative(wx.VERTICAL, -min(downdelta*diff, 5000) )

                    if point.x + cx < 10:
                        self.onScrollRelative(wx.HORIZONTAL, -10)

                    elif point.x + cx > self.treeCtrl.GetClientSize().width:
                        self.onScrollRelative(wx.HORIZONTAL, 10)

                    #g.trace(updelta*diff, downdelta*diff, diff)
                    #@-node:bob.20070906195449.2:<< scroll the canvas as needed >>
                    #@nl
            except:
                g.es_event_exception("continue drag")
        #@-node:bob.20070906195449.1:continueDrag
        #@-node:bob.20070906100710:Drag
        #@+node:bob.20070813163332.386:Mouse Events
        """
        All mouse events are collected by the treeCtrl and sent
        to a dispatcher (onMouse).

        onMouse is called with dispatcher is called with a position,

        a 'source' which is the name of an region inside the headline
            this could be 'ClickBox', 'IconBox', 'TextBox' or a user supplied



        """


        #@+node:bob.20070827175321:onMouse (Dispatcher)
        def onMouse(self, event, type):
            '''
            Respond to mouse events and call appropriate handlers.

            'event' is the raw 'event' object from the original event.

            'type' is a string representing the type of event and may
            have one of the following values:

                + LeftDown, LeftUp, LeftDoubleClick
                + MiddleDown, MiddleUp, MiddleDoubleClick
                + RightDown, RightUp, RightDoubleClick
                + and Motion

            'source' is a string derived from 'event' which represents
            the position of the event in the headline and may have one
            of the following values:

                ClickBox, IconBox, TextBox, Headline.

            'source' may also have a user defined value representing,
            for example, a user defined icon.

            'sp' is leo position object, derived from event via HitTest,
            representing the node on which the event occured. It is
            called sp rather than the usual 'p' because it is 'special',
            in that it contains extra information.

            The value of 'source' and 'type' are combined and the
            following three methods are called in order for each event:

                + onPreMouse{type}(sp, event, source, type)
                + onMouse{source}{type}(sp, event, source, type)
                + onPostMouse{type}(sp, event, source, type)

            None of these methods need exist and are obviously not called
            if they don't.

            The 'source' value is always an empty string for
            Motion events.

            Note to self: Refrain from taking drugs while proramming.
            '''

            point = event.GetPosition()

            sp, source = self.hitTest(point)

            #g.trace(self, type, source, sp)

            if False and type != 'Motion':
                #@        << trace mouse >>
                #@+node:bob.20070906145200:<< trace mouse >>
                g.trace('\n\tsource:', source)
                print '\ttype:', type
                print '\theadline', sp and sp.headString()
                print

                s = 'onPreMouse' + type
                print '\t', s
                if hasattr(self, s):
                    getattr(self, s)(sp, event, source, type)

                s = 'onMouse' + source + type
                print '\t', s
                if hasattr(self, s):
                    getattr(self, s)(sp, event, source, type)

                s = 'onPostMouse' + type
                print '\t', s
                if hasattr(self, s):
                    getattr(self, s)(sp, event, source, type)

                #@-node:bob.20070906145200:<< trace mouse >>
                #@nl
            else:

                s = 'onPreMouse' + type
                if hasattr(self, s):
                    getattr(self, s)(sp, event, source, type)

                if type == 'Motion':
                    s='onMouseMotion'
                    if hasattr(self, s):
                        getattr(self, s)(sp, event, source, type)
                else:
                    s = 'onMouse' + source + type
                    if hasattr(self, s):
                        #print 'ok for ', source, type
                        getattr(self, s)(sp, event, source, type)
                    else:
                        #print 'fail for ', source, type
                        pass
                s = 'onPostMouse' + type
                if hasattr(self, s):
                    getattr(self, s)(sp, event, source, type)

        #@-node:bob.20070827175321:onMouse (Dispatcher)
        #@+node:bob.20070906102229.1:HitTest
        def hitTest(self, point):
            return self.treeCtrl._canvas.hitTest(point)



        #@-node:bob.20070906102229.1:HitTest
        #@+node:bob.20070906105804:Pre
        #@+node:bob.20070906105804.1:onPreMouseLeftDown
        def onPreMouseLeftDown(self, sp, event, source, type):
            #g.trace('source:', source, 'type:', type, 'Position:', sp and sp.headString())

            self.setFocus()
        #@-node:bob.20070906105804.1:onPreMouseLeftDown
        #@+node:bob.20070906105804.2:onPreMouseLeftUp
        #@+at
        # def onPreMouseLeftUp(self, sp, event, source, type):
        #     g.trace('source:', source, 'type:', type, 'Position:', sp and
        # sp.headString())
        #@-at
        #@-node:bob.20070906105804.2:onPreMouseLeftUp
        #@+node:bob.20070906105804.4:onPreMouseRightDown
        #@+at
        # def onPreMouseRightDown(self, sp, event, source, type):
        #     g.trace('source:', source, 'type:', type, 'Position:', sp and
        # sp.headString())
        #@-at
        #@-node:bob.20070906105804.4:onPreMouseRightDown
        #@+node:bob.20070906105804.3:onPreMouseRightUp
        #@+at
        # def onPreMouseRightUp(self, sp, event, source, type):
        #     g.trace('source:', source, 'type:', type, 'Position:', sp and
        # sp.headString())
        #@-at
        #@-node:bob.20070906105804.3:onPreMouseRightUp
        #@+node:bob.20070907040940:onPreMouseMotion
        #@-node:bob.20070907040940:onPreMouseMotion
        #@-node:bob.20070906105804:Pre
        #@+node:bob.20070906105339.1:Post
        #@+node:bob.20070827164653.3:onPostMouseLeftDown
        #@+at
        # def onPostMouseLeftDown(self, sp, event, source, type):
        #     g.trace('source:', source, 'type:', type, 'Position:', sp and
        # sp.headString())
        #@-at
        #@-node:bob.20070827164653.3:onPostMouseLeftDown
        #@+node:bob.20070906105444:onPostMouseLeftUp
        def onPostMouseLeftUp(self, sp, event, source, type):
            #g.trace('source:', source, 'type:', type, 'Position:', sp and sp.headString())

            self.setCursor('default')
            if self.HasCapture():
                self.ReleaseMouse()

            #If we are still dragging here something as gone wrong.
            if self.dragging:
                self.cancelDrag(sp, event)
        #@-node:bob.20070906105444:onPostMouseLeftUp
        #@+node:bob.20070906105339.2:onPostMouseRightDown
        #@+at
        # def onPostMouseRightDown(self, sp, event, source, type):
        #     g.trace('source:', source, 'type:', type, 'Position:', sp and
        # sp.headString())
        # 
        #@-at
        #@-node:bob.20070906105339.2:onPostMouseRightDown
        #@+node:bob.20070906105444.1:onPostMouseRightUp
        #@+at
        # def onPostMouseRightUp(self, sp, event, source, type):
        #     g.trace('source:', source, 'type:', type, 'Position:', sp and
        # sp.headString())
        # 
        #@-at
        #@-node:bob.20070906105444.1:onPostMouseRightUp
        #@+node:bob.20070907040940.1:onPostMouseMotion
        #@-node:bob.20070907040940.1:onPostMouseMotion
        #@-node:bob.20070906105339.1:Post
        #@+node:bob.20070906204641:Motion
        def onMouseMotion(self, p, event, source, type):
            if self.dragging:
                self.onDrag(p, event)
        #@-node:bob.20070906204641:Motion
        #@+node:bob.20070814091106:Click Box
        #@+node:bob.20070814083933:onMouseClickBoxLeftDown
        def onMouseClickBoxLeftDown (self, p, event, source, type):
            """React to leftMouseDown event on ClickBox.

            Toggles expanded status for this node.

            """

            c = self.c

            p1 = c.currentPosition()
            #g.trace(source, type, p)
            c.beginUpdate()
            try:
                if not g.doHook("boxclick1", c=c, p=p, v=p, event=event):

                    self.endEditLabel()

                    if p == p1 or self.initialClickExpandsOrContractsNode:
                        if p.isExpanded():
                            p.contract()
                        else:
                            p.expand()

                    self.select(p)

                    if c.frame.findPanel:
                        c.frame.findPanel.handleUserClick(p)
                    if self.stayInTree:
                        c.treeWantsFocus()
                    else:
                        c.bodyWantsFocus()

                g.doHook("boxclick2", c=c, p=p, v=p, event=event)

            finally:
                c.endUpdate()


        #@-node:bob.20070814083933:onMouseClickBoxLeftDown
        #@-node:bob.20070814091106:Click Box
        #@+node:bob.20070814090359:Icon Box...
        #@+node:bob.20070814090359.1:onMouseIconBoxLeftDown
        def onMouseIconBoxLeftDown(self, p, event, source , type):
            """React to leftMouseDown event on the icon box."""

            #g.trace(source, type)
            c = self.c
            c.setLog()

            if not self.HasCapture():
                self.CaptureMouse()

            c.beginUpdate()
            try:
                if not g.doHook("iconclick1", c=c, p=p, v=p, event=event):

                    self.endEditLabel()
                    self.onDrag(p, event)

                    self.select(p)

                    if c.frame.findPanel:
                        c.frame.findPanel.handleUserClick(p)
                    if self.stayInTree:
                        c.treeWantsFocus()
                    else:
                        c.bodyWantsFocus()

                g.doHook("iconclick2", c=c, p=p, v=p, event=event)

            finally:
                c.endUpdate()

        #@-node:bob.20070814090359.1:onMouseIconBoxLeftDown
        #@+node:bob.20070906193733.1:onMouseIconBoxLeftUp

        def onMouseIconBoxLeftUp(self, sp, event, source, type):
            #g.trace('\n\tDrop:', self.drag_p, '\n\tOn:', sp and sp.headString())

            if self.dragging:
                self.onEndDrag(sp, event)
        #@nonl
        #@-node:bob.20070906193733.1:onMouseIconBoxLeftUp
        #@+node:bob.20071210205301:onMouseIconBoxLeftDoubleClick
        def onMouseIconBoxLeftDoubleClick(self, sp, event, source, type):

            c = self.c

            assert sp

            #g.trace()

            if self.trace and self.verbose: g.trace()

            try:
                if not g.doHook("icondclick1",c=c,p=sp,v=sp,event=event):
                    self.endEditLabel() # Bug fix: 11/30/05
                    self.OnIconDoubleClick(sp) # Call the method in the base class.
                g.doHook("icondclick2",c=c,p=sp,v=sp,event=event)
            except:
                g.es_event_exception("icondclick")
        #@-node:bob.20071210205301:onMouseIconBoxLeftDoubleClick
        #@-node:bob.20070814090359:Icon Box...
        #@+node:bob.20070816213833:Text Box
        #@+node:bob.20070818153826:onMouseTextBoxLeftDown

        def onMouseTextBoxLeftDown(self, p, event, source, type):
            """React to leftMouseDown event on the label of a headline."""

            c = self.c
            c.setLog()

            c.beginUpdate()
            try:
                if c.isCurrentPosition(p):

                    self.editLabel(p)

                else:
                    if not g.doHook("headclick1",c=c,p=p,v=p,event=event):

                        self.endEditLabel()
                        self.select(p)

                        if c.frame.findPanel:
                            c.frame.findPanel.handleUserClick(p)

                        if self.stayInTree:
                            c.treeWantsFocus()
                        else:
                            c.bodyWantsFocus()
                    g.doHook("headclick2",c=c,p=p,v=p,event=event)
            finally:
                c.endUpdate()

        #@-node:bob.20070818153826:onMouseTextBoxLeftDown
        #@-node:bob.20070816213833:Text Box
        #@+node:bob.20070816213833.1:Headline
        #@+node:bob.20070816212714.1:onMouseHeadlineLeftDown

        def onMouseHeadlineLeftDown(self, sp, event, source, type):
            """React to leftMouseDown event outside of main headline regions."""

            #g.trace('FIXME')
            if not self.expanded_click_area:

                return
            self.onMouseClickBoxLeftDown(sp, event, source, type)
        #@-node:bob.20070816212714.1:onMouseHeadlineLeftDown
        #@-node:bob.20070816213833.1:Headline
        #@-node:bob.20070813163332.386:Mouse Events
        #@-node:bob.20070813163332.382:== Event handlers ==
        #@+node:bob.20070813163332.24:editLabel
        def editLabel (self,p,selectAll=False):
            '''The edit-label command.'''

            #g.trace(g.callers())

            if g.app.killed or self.c.frame.killed: return

            c = self.c

            entry = self.headlineTextWidget

            if p:

                c.beginUpdate()
                try:
                    self.endEditLabel()
                    self.setEditPosition(p)
                    #g.trace('ep', self.editPosition())
                finally:
                    c.endUpdate()

                # Help for undo.
                self.revertHeadline = s = p.headString()

                self.setEditLabelState(p)

                entry.setAllText(s)

                selectAll = selectAll or self.select_all_text_when_editing_headlines
                if selectAll:
                    entry.ctrl.SetSelection(-1, -1)
                else:
                    entry.ctrl.SetInsertionPointEnd()
                entry.ctrl.SetFocus()
                c.headlineWantsFocus(p)
        #@-node:bob.20070813163332.24:editLabel
        #@+node:bob.20070820132718:endEditLabel
        def endEditLabel (self, event=None):
            '''End editing of a headline and update p.headString().'''

            c = self.c

            if event:
                #g.trace('kill focus')
                pass

            if g.app.killed or c.frame.killed:
                return

            w = self.headlineTextWidget

            ep = self.editPosition()
            if not ep:
                return

            s = w.getAllText()

            h = ep.headString()

            #g.trace('old:',h,'new:',s)

            # Don't clear the headline by default.
            if s and s != h:
                self.onHeadChanged(ep,undoType='Typing',s=s)

            self.setEditPosition(None)
            c.beginUpdate()
            c.endUpdate()

            if c.config.getBool('stayInTreeAfterEditHeadline'):
                c.treeWantsFocusNow()
            else:
                c.bodyWantsFocusNow()

            if event:
                event.Skip()
        #@-node:bob.20070820132718:endEditLabel
        #@+node:bob.20070813163332.398:tree.setHeadline (new in 4.4b2)
        def setHeadline (self,p,s):

            '''Set the actual text of the headline widget.

            This is called from the undo/redo logic to change the text before redrawing.'''

            w = self.editPosition() and self.headlineTextWidget

            w = self.edit_widget(p)
            if w:
                w.setAllText(s)
                self.revertHeadline = s
            elif g.app.killed or self.c.frame.killed:
                return
            else:
                g.trace('#'*20,'oops')
        #@-node:bob.20070813163332.398:tree.setHeadline (new in 4.4b2)
        #@+node:bob.20070818090003:tree.set...LabelState
        #@+node:bob.20070818090003.1:setEditLabelState
        def setEditLabelState(self, p, selectAll=False):

            #g.trace()
            pass

        #@-node:bob.20070818090003.1:setEditLabelState
        #@+node:bob.20070818090003.2:setSelectedLabelState

        def setSelectedLabelState(self, p):

            # g.trace(p, g.callers())

            if p:
                p.setSelected()

        #@-node:bob.20070818090003.2:setSelectedLabelState
        #@+node:bob.20070818090003.3:setUnselectedLabelState

        def setUnselectedLabelState(self,p): # not selected.

            # g.trace(p, g.callers())

            if p:
                # clear 'selected' status flag
                p.v.statusBits &= ~ p.v.selectedBit

        #@-node:bob.20070818090003.3:setUnselectedLabelState
        #@-node:bob.20070818090003:tree.set...LabelState
        #@+node:bob.20070813163332.399:do nothings
        def headWidth (self,p=None,s=''): return 0

        # Colors.
        def setDisabledHeadlineColors (self,p):             pass
        def setEditHeadlineColors (self,p):                 pass
        def setUnselectedHeadlineColors (self,p):           pass


        # Focus
        def focus_get (self):
            return self.FindFocus()

        def setFocus (self):
            self.treeCtrl.SetFocusIgnoringChildren()

        SetFocus = setFocus


        #@-node:bob.20070813163332.399:do nothings
        #@+node:bob.20070901120931:GetName
        def GetName(self):
            return 'canvas'

        getName = GetName
        #@-node:bob.20070901120931:GetName
        #@+node:bob.20070912132828:Reparent
        def reparent(self, parent):
            self.treeCtrl.Reparent(parent)

        Reparent = reparent
        #@-node:bob.20070912132828:Reparent
        #@+node:bob.20070908231221:Font Property
        def getFont(self):
            g.trace('not ready')

        def setFont(self):
            g.trace('not ready')

        font = property(getFont, setFont)



        #@-node:bob.20070908231221:Font Property
        #@+node:bob.20070908222657:requestLineHeight
        def requestLineHeight(height):
            self.getCanvas().requestLineHeight(height)
        #@nonl
        #@-node:bob.20070908222657:requestLineHeight
        #@+node:bob.20080105225910:line_height property
        def getLineHeight(self):
            return self.treeCtrl._canvas._lineHeight

        line_height = property(getLineHeight)
        #@nonl
        #@-node:bob.20080105225910:line_height property
        #@-others
    #@nonl
    #@-node:bob.20070813163332.371:wxLeoTree class (leoFrame.leoTree):
    #@+node:bob.20070813173446:class OutlineCanvasPanel

    class OutlineCanvasPanel(wx.PyPanel):
        """A class to mimic a scrolled window to contain an OutlineCanvas."""
        #@    @+others
        #@+node:bob.20070813173446.1:__init__

        def __init__(self, parent, leoTree, name):
            """Create an OutlineCanvasPanel instance."""

            #g.trace('OutlineCanvasPanel')

            wx.PyPanel.__init__(self, parent, -1, name=name,
                style= wx.VSCROLL | wx.WANTS_CHARS | wx.HSCROLL | wx.NO_BORDER
            )

            self._leoTree = leoTree
            self.c = self._c = leoTree.c

            self._x = 0
            self._y = 0

            self.SetScrollbar(wx.HORIZONTAL, 0, 0, 100, True)
            self.SetScrollbar(wx.VERTICAL, 0, 0, 100, True)

            self._canvas = OutlineCanvas(self)

            self._entry = wx.TextCtrl(self._canvas,
                style = wx.SIMPLE_BORDER | wx.WANTS_CHARS
            )

            self._entry._virtualTop = -1000
            self._entry.Hide()
            self._canvas._widgets.append(self._entry)

            self._canvas.update()

            self.Bind(wx.EVT_SCROLLWIN_THUMBTRACK, self.onScrollThumbtrack)
            self.Bind(wx.EVT_SCROLLWIN_LINEUP, self.onScrollLineup)
            self.Bind(wx.EVT_SCROLLWIN_LINEDOWN, self.onScrollLinedown)
            self.Bind(wx.EVT_SCROLLWIN_PAGEUP, self.onScrollPageup)
            self.Bind(wx.EVT_SCROLLWIN_PAGEDOWN, self.onScrollPagedown)

            self.Bind(wx.EVT_SIZE, self.onSize)



            self.SetBackgroundColour(self._leoTree.outline_pane_background_color)

            self.Bind(wx.EVT_CHAR,
                lambda event, self=self._leoTree: onGlobalChar(self, event)
            )

            self.onScroll(wx.HORIZONTAL, 0)

        #@-node:bob.20070813173446.1:__init__
        #@+node:bob.20070819054707.1:showEntry
        showcount = 0
        def showEntry(self):

            # self.showcount +=1

            # print
            # g.trace(self.showcount, g.callers(20))
            # print

            entry = self._entry
            canvas = self._canvas

            ep = self._leoTree.editPosition()

            if not ep:
                return self.hideEntry()


            for sp in canvas._positions:
                if ep == sp:
                    break
            else:
                return self.hideEntry()

            x, y, width, height = sp._textBoxRect
            #print '\t', x, y, width , height

            entry._virtualTop = canvas._virtualTop + y -2

            entry.MoveXY(x - 2, y -2)
            entry.SetSize((max(width + 4, 100), -1))

            tw = self._leoTree.headlineTextWidget

            range = tw.getSelectionRange()
            tw.setInsertPoint(0)
            #tw.setInsertPoint(len(sp.headString()))
            tw.setSelectionRange(*range)
            entry.Show()
        #@-node:bob.20070819054707.1:showEntry
        #@+node:bob.20070819054707:hideEntry

        def hideEntry(self):

            entry = self._entry
            entry._virtualTop = -1000
            entry.MoveXY(0, -1000)

            entry.Hide()
        #@-node:bob.20070819054707:hideEntry
        #@+node:bob.20070828070933:getPositions

        def getPositions(self):
            return self._canvas._positions
        #@nonl
        #@-node:bob.20070828070933:getPositions
        #@+node:bob.20070813173446.3:onScrollThumbtrack

        def onScrollThumbtrack(self, event):
            """React to changes in the position of the scrollbars."""
            return self.onScroll(event.GetOrientation(), event.GetPosition())
        #@nonl
        #@-node:bob.20070813173446.3:onScrollThumbtrack
        #@+node:bob.20070813173446.4:onScrollLineup

        def onScrollLineup(self, event):
            """Scroll the outline up by one page."""
            orient = event.GetOrientation()
            return self.onScroll(orient, self.GetScrollPos(orient) - 10)
        #@nonl
        #@-node:bob.20070813173446.4:onScrollLineup
        #@+node:bob.20070813173446.5:onScrollLinedown

        def onScrollLinedown(self, event):
            """Scroll the outline down by one line."""
            orient = event.GetOrientation()
            return self.onScroll(orient, self.GetScrollPos(orient) + 10)
        #@nonl
        #@-node:bob.20070813173446.5:onScrollLinedown
        #@+node:bob.20070813173446.6:onScrollPageup

        def onScrollPageup(self, event):
            """Scroll the outline up one page."""
            orient = event.GetOrientation()
            offset = self.GetClientSize()[orient == wx.VERTICAL] * 0.9
            return self.onScroll(orient, self.GetScrollPos(orient) - int(offset))
        #@nonl
        #@-node:bob.20070813173446.6:onScrollPageup
        #@+node:bob.20070813173446.7:onScrollPagedown

        def onScrollPagedown(self, event):
            """Scroll the outline down by one page."""
            orient = event.GetOrientation()
            offset = self.GetClientSize()[orient == wx.VERTICAL] * 0.9
            return self.onScroll(orient, self.GetScrollPos(orient) + int(offset))


        #@-node:bob.20070813173446.7:onScrollPagedown
        #@+node:bob.20070813173446.8:onScroll
        def onScroll(self, orient, newpos):
            """Scroll the outline vertically or horizontally to a new position."""
            #print 'onscroll', newpos

            if orient == wx.VERTICAL:
                #print 'vertical', pos
                self._canvas.vscrollTo(newpos)
            else:
                #print 'horizontal', pos
                self._x = newpos
                self._canvas.MoveXY(-newpos, 0)

            self.SetScrollPos(orient, newpos)
        #@-node:bob.20070813173446.8:onScroll
        #@+node:bob.20070907054452.1:onScrollRelative

        def onScrollRelative(self, orient, value):

            return self.onScroll(orient, self.GetScrollPos(orient) + value)
        #@-node:bob.20070907054452.1:onScrollRelative
        #@+node:bob.20070813173446.9:onSize
        def onSize(self, event=None):
            """React to changes in the size of the outlines display area."""

            c = self.c
            c.beginUpdate()
            try:
                self.vscrollUpdate()
                self._canvas.resize(self.GetClientSize().height)
            finally:
                c.endUpdate(False)
                event.Skip()
        #@-node:bob.20070813173446.9:onSize
        #@+node:bob.20070813173446.10:vscrollUpdate

        def vscrollUpdate(self):
            """Set the vertical scroll bar to match current conditions."""

            oldtop = top = self._canvas._virtualTop
            canvasHeight = self.GetClientSize().height
            treeHeight = self._canvas._treeHeight

            if (treeHeight - top) < canvasHeight:
                top = treeHeight - canvasHeight

            if top < 0 :
                top = 0

            if oldtop != top:
                self._canvas._virtualTop = top
                self._canvas.resize()

            #self.showEntry()

            self.SetScrollbar(wx.VERTICAL, top, canvasHeight, treeHeight, True)

            #print 'vScrollUpdate', top,  canvasHeight, treeHeight
        #@-node:bob.20070813173446.10:vscrollUpdate
        #@+node:bob.20070813173446.11:hscrollUpdate

        def hscrollUpdate(self):
            """Set the horizontal scroll bar to match current conditions."""

            self.SetScrollbar(wx.HORIZONTAL,
                 -self._canvas.GetPosition().x,
                 self.GetClientSize().width,
                 self._canvas.GetSize().width,
                 True
            )

        #@-node:bob.20070813173446.11:hscrollUpdate
        #@+node:bob.20070816191238:update

        def update(self):
            self._canvas.update()


        #@-node:bob.20070816191238:update
        #@+node:bob.20070817063331:redraw

        def redraw(self):
            self._canvas.redraw()
        #@nonl
        #@-node:bob.20070817063331:redraw
        #@+node:bob.20070906162709:refresh
        def refresh(self):
            self._canvas.refresh()
        #@nonl
        #@-node:bob.20070906162709:refresh
        #@+node:bob.20070901152316:GetName
        def GetName(self):
            return 'canvas'

        getName = GetName
        #@nonl
        #@-node:bob.20070901152316:GetName
        #@-others
    #@-node:bob.20070813173446:class OutlineCanvasPanel
    #@+node:bob.20070813173446.12:class OutlineCanvas
    class OutlineCanvas(wx.Window):
        """Implements a virtual view of a leo outline tree.

        The class uses an off-screen buffer for drawing which it
        blits to the window during paint calls for expose events, etc,

        A redraw is only required when the height of the canvas changes,
        a vertical scroll event occurs, or if the outline changes.

        """
        #@    @+others
        #@+node:bob.20070813173446.13:__init__
        def __init__(self, parent):
            """Create an OutlineCanvas instance."""

            #g.trace('OutlineCanvas')

            self._c = self.c = parent._c
            self._parent = parent
            self._leoTree = parent._leoTree

            #@    << define ivars >>
            #@+node:bob.20070828070933.1:<< define ivars >>
            self._icons = icons

            self._widgets = []

            self.drag_p = None

            self._size = wx.Size(100, 100)

            self.__virtualTop = 0

            self._textIndent = 30

            self._xPad = 30
            self._yPad = 2

            self._treeHeight = 10

            self._positions = []

            self._fontHeight = None
            self._iconSize = None

            self._clickBoxSize = None
            self._lineHeight =  10
            self._requestedLineHeight = 10

            self._yTextOffset = None
            self._yIconOffset = None

            self._clickBoxCenterOffset = None

            self._clickBoxOffset = None


            #@-node:bob.20070828070933.1:<< define ivars >>
            #@nl

            wx.Window.__init__(self, parent, -1, size=self._size, style=wx.WANTS_CHARS | wx.NO_BORDER )

            self._createNewBuffer(self._size)

            self.contextChanged()

            self.Bind(wx.EVT_PAINT, self.onPaint)

            for o in (self, parent):
                #@        << create  bindings >>
                #@+node:bob.20070906162528:<< create bindings >>
                onmouse = self._leoTree.onMouse

                for e, s in (
                   ( wx.EVT_LEFT_DOWN,     'LeftDown'),
                   ( wx.EVT_LEFT_UP,       'LeftUp'),
                   ( wx.EVT_LEFT_DCLICK,   'LeftDoubleClick'),
                   ( wx.EVT_MIDDLE_DOWN,   'MiddleDown'),
                   ( wx.EVT_MIDDLE_UP,     'MiddleUp'),
                   ( wx.EVT_MIDDLE_DCLICK, 'MiddleDoubleClick'),
                   ( wx.EVT_RIGHT_DOWN,    'RightDown'),
                   ( wx.EVT_RIGHT_UP,      'RightUp'),
                   ( wx.EVT_RIGHT_DCLICK,  'RightDoubleClick'),
                   ( wx.EVT_MOTION,        'Motion')
                ):
                    o.Bind(e, lambda event, type=s: onmouse(event, type))



                #self.Bind(wx.EVT_KEY_UP, self._leoTree.onChar)
                #self.Bind(wx.EVT_KEY_DOWN, lambda event: self._leoTree.onKeyDown(event))

                self.Bind(wx.EVT_CHAR,
                    lambda event, self=self._leoTree: onGlobalChar(self, event)
                )
                #@-node:bob.20070906162528:<< create bindings >>
                #@nl

        #@+at
        # self.box_padding = 5 # extra padding between box and icon
        # self.box_width = 9 + self.box_padding
        # self.icon_width = 20
        # self.text_indent = 4 # extra padding between icon and tex
        # 
        # self.hline_y = 7 # Vertical offset of horizontal line
        # self.root_left = 7 + self.box_width
        # self.root_top = 2
        # 
        # self.default_line_height = 17 + 2 # default if can't set line_height 
        # from font.
        # self.line_height = self.default_line_height
        # 
        #@-at
        #@-node:bob.20070813173446.13:__init__
        #@+node:bob.20070909060610:virtualTop property


        def getVirtualTop(self):
            return self.__virtualTop

        def setVirtualTop(self, virtualTop):
            self.__virtualTop = virtualTop

            #self._parent.showEntry()

        _virtualTop = property (getVirtualTop, setVirtualTop)

        #@-node:bob.20070909060610:virtualTop property
        #@+node:bob.20070829195118:hitTest
        def hitTest(self, point):
            result = self._hitTest(point)
            g.trace(result)
            return result

        def hitTest(self, point):

            point = wx.Point(*point)

            for sp in self._positions:
                if point.y < (sp._top + self._lineHeight):
                    if sp._clickBoxRect.Contains(point):
                        return sp, 'ClickBox'
                    if sp._iconBoxRect.Contains(point):
                        return sp, 'IconBox'
                    if sp._textBoxRect.Contains(point):
                        return sp, 'TextBox'
                    for type, region in sp._clickRegions:

                        if region.Contains(point):

                            return sp, type
                    return sp, 'Headline'

            return None, 'Canvas'

        #@-node:bob.20070829195118:hitTest
        #@+node:bob.20070813173446.16:_createNewBuffer
        def _createNewBuffer(self, size):
            """Create a new buffer for drawing."""

            self._buffer = b = wx.MemoryDC()
            self._bitmap = wx.EmptyBitmap(*size)
            b.SelectObject(self._bitmap)
            b.SetMapMode(wx.MM_TEXT)



        #@-node:bob.20070813173446.16:_createNewBuffer
        #@+node:bob.20070813173446.17:vscrollTo

        def vscrollTo(self, pos):
            """Scroll the canvas vertically to the specified position."""

            if (self._treeHeight - self._size.height) < pos :
                pos = self._treeHeight - self._size.height

            if pos < 0:
                pos = 0

            self._virtualTop = pos

            self.resize()
        #@-node:bob.20070813173446.17:vscrollTo
        #@+node:bob.20070813173446.18:resize / redraw

        def resize(self, height=None, width=None):
            """Resize the outline canvas and, if required, create and draw on a new buffer."""

            c = self.c

            #c.beginUpdate()     #lock out events
            if 1: #try:
                if height is not None:
                    self._size.height = height
                if width is not None and self._size.width < width:
                    self._size.width = width

                self.SetSize(self._size)

                # TODO: decide if need to create new buffer?
                self._createNewBuffer(self._size)

                self._parent.hscrollUpdate()
                self.draw()
                self.refresh()



            #finally:
            #    c.endUpdate(False)


            return True

        redraw = resize



        #@-node:bob.20070813173446.18:resize / redraw
        #@+node:bob.20070813173446.21:refresh

        def refresh(self):
            """Renders the offscreen buffer to the outline canvas."""

            #print 'refresh'
            wx.ClientDC(self).BlitPointSize((0,0), self._size, self._buffer, (0, 0))

        #@-node:bob.20070813173446.21:refresh
        #@+node:bob.20070813173446.19:update

        def update(self):
            """Do a full update assuming the tree has been changed."""

            c = self._c

            hoistFlag = bool(self._c.hoistStack)

            if hoistFlag:
                stk = [self._c.hoistStack[-1].p]
            else:
                stk = [self._c.rootPosition()]

            #@    << find height of tree and position of currentNode >>
            #@+node:bob.20070813173446.20:<< find height of tree and position of currentNode >>

            # Find the number of visible nodes in the outline.

            cp = c.currentPosition().copy()
            cpCount = None

            count = 0
            while stk:

                p = stk.pop()

                while p:


                    if stk or not hoistFlag:
                        newp = p.next()
                    else:
                        newp = None

                    if cp and cp == p:
                        cpCount = count
                        cp = False

                    count += 1

                    #@        << if p.isExpanded() and p.hasFirstChild():>>
                    #@+node:bob.20070828213559:<< if p.isExpanded() and p.hasFirstChild():>>
                    ## if p.isExpanded() and p.hasFirstChild():

                    v=p.v
                    if v.statusBits & v.expandedBit and v.t._firstChild:
                    #@nonl
                    #@-node:bob.20070828213559:<< if p.isExpanded() and p.hasFirstChild():>>
                    #@nl
                        stk.append(newp)
                        p = p.firstChild()
                        continue

                    p = newp

            lineHeight = self._lineHeight

            self._treeHeight = count * lineHeight

            if cpCount is not None:
                cpTop = cpCount * lineHeight

                if cpTop < self._virtualTop:
                    self._virtualTop = cpTop

                elif cpTop + lineHeight > self._virtualTop + self._size.height:
                    self._virtualTop += (cpTop + lineHeight) - (self._virtualTop + self._size.height)



            #@-node:bob.20070813173446.20:<< find height of tree and position of currentNode >>
            #@nl

            #< < if height from top to bottom is less than canvas height: >>
            if (self._treeHeight - self._virtualTop) < self._size.height:
                self._virtualTop = self._treeHeight - self._size.height

            self.contextChanged()

            self.resize()
            self._parent.vscrollUpdate()


        #@-node:bob.20070813173446.19:update
        #@+node:bob.20070813173446.22:onPaint

        def onPaint(self, event):
            """Renders the off-screen buffer to the outline canvas."""

            #print 'on paint'
            wx.PaintDC(self).BlitPointSize((0,0), self._size, self._buffer, (0, 0))
        #@-node:bob.20070813173446.22:onPaint
        #@+node:bob.20070813173446.23:contextChanged
        def contextChanged(self):
            """Adjust canvas attributes after a change in context.

            This should be called after setting or changing fonts or icon size or
            anything that effects the tree display.

            """


            self._fontHeight = self._buffer.GetTextExtent('Wy')[1]
            self._iconSize = wx.Size(icons[0].GetWidth(), icons[0].GetHeight())

            self._clickBoxSize = wx.Size(plusBoxIcon.GetWidth(), plusBoxIcon.GetHeight())

            self._lineHeight = max(
                self._fontHeight,
                self._iconSize.height,
                self._requestedLineHeight
            ) + 2 * self._yPad

            # y offsets

            self._yTextOffset = (self._lineHeight - self._fontHeight)//2

            self._yIconOffset = (self._lineHeight - self._iconSize.height)//2

            self._clickBoxCenterOffset = wx.Point(
                -self._textIndent*2 + self._iconSize.width//2,
                self._lineHeight//2
            )

            self._clickBoxOffset = wx.Point(
                self._clickBoxCenterOffset.x - self._clickBoxSize.width//2,
                (self._lineHeight  - self._clickBoxSize.height)//2
            )


        #@-node:bob.20070813173446.23:contextChanged
        #@+node:bob.20070908222657.1:requestLineHeight
        def requestLineHeight(height):
            """Request a minimum height for lines."""

            assert int(height) and height < 200
            self.requestedHeight = height
            self.beginUpdate()
            self.endUpdate()
        #@-node:bob.20070908222657.1:requestLineHeight
        #@+node:bob.20070813173446.24:def draw

        def draw(self, showCurrentPosition=False):
            """Draw the outline on the off-screen buffer."""

            #print 'on draw', count()

            dc = self._buffer
            c = self._c

            brush = wx.Brush(self._leoTree.outline_pane_background_color)
            dc.SetBackground(brush)
            dc.Clear()

            top = self._virtualTop
            if top < 0:
                self._virtualTop = top = 0

            height = self._size.height
            bottom = top + height

            textIndent = self._textIndent

            yPad = self._yPad
            xPad = self._xPad

            yIconOffset = self._yIconOffset

            yTextOffset = self._yTextOffset

            clickBoxOffset = self._clickBoxOffset
            clickBoxCenterOffset = self._clickBoxCenterOffset
            clickBoxSize = self._clickBoxSize

            iconSize = self._iconSize

            lineHeight = self._lineHeight
            halfLineHeight = lineHeight//2

            canvasWidth = self._size.width

            #@    << draw tree >>
            #@+node:bob.20070813173446.25:<< draw tree >>
            y = 0

            hoistFlag = bool(c.hoistStack)

            if hoistFlag:
                stk = [c.hoistStack[-1].p]
            else:
                stk = [c.rootPosition()]

            self._positions = positions = []

            while stk:

                p = stk.pop()

                while p:

                    if stk or not hoistFlag:
                        newp = p.next()
                    else:
                        newp = None

                    mytop = y
                    y = y + lineHeight

                    if mytop > bottom:
                        stk = []
                        p = None
                        break

                    if y > top:

                        sp = p.copy()

                        #@            << setup object >>
                        #@+node:bob.20070813173446.26:<< set up object >>
                        # depth: the depth of indentation relative to the current hoist.
                        sp._depth = len(stk)

                        # virtualTop: top of the line in virtual canvas coordinates
                        sp._virtualTop =  mytop

                        # top: top of the line in real canvas coordinates
                        sp._top = mytop - top

                        textSize = wx.Size(*dc.GetTextExtent(sp.headString()+'>'))

                        xTextOffset = ((sp._depth +1) * textIndent) + xPad

                        textPos = wx.Point( xTextOffset,  sp._top + yTextOffset )
                        iconPos = textPos  + (-textIndent,  yIconOffset)
                        clickBoxPos = textPos + clickBoxOffset

                        sp._clickBoxCenter = clickBoxPos + clickBoxCenterOffset

                        sp._textBoxRect = wx.RectPS(textPos, textSize)
                        sp._iconBoxRect = wx.RectPS(iconPos, iconSize)
                        sp._clickBoxRect = wx.RectPS(clickBoxPos, clickBoxSize)

                        sp._icon = icons[p.v.computeIcon()]

                        if sp.hasFirstChild():
                            sp._clickBoxIcon = plusBoxIcon
                            if sp.isExpanded():
                                sp._clickBoxIcon = minusBoxIcon
                        else:
                            sp._clickBoxIcon = None

                        sp._clickRegions = []

                        #@-node:bob.20070813173446.26:<< set up object >>
                        #@nl

                        positions.append(sp)

                        canvasWidth = max(canvasWidth, textSize.width + xTextOffset + 100)

                    #@        << if p.isExpanded() and p.hasFirstChild():>>
                    #@+node:bob.20070828213559:<< if p.isExpanded() and p.hasFirstChild():>>
                    ## if p.isExpanded() and p.hasFirstChild():

                    v=p.v
                    if v.statusBits & v.expandedBit and v.t._firstChild:
                    #@nonl
                    #@-node:bob.20070828213559:<< if p.isExpanded() and p.hasFirstChild():>>
                    #@nl
                        stk.append(newp)
                        p = p.firstChild()
                        continue

                    p = newp

            if canvasWidth > self._size.width:
                self.resize(None, canvasWidth)

            if not positions:
                #g.trace('No positions!')
                return

            self._virtualTop =  positions[0]._virtualTop

            # try:
                # result = self._leoTree.drawTreeHook(self)
                # print 'result =', result
            # except:
                # result = False
                # print 'result is False'

            if hasattr(self._leoTree, 'drawTreeHook'):
                try:
                    result = self._leoTree.drawTreeHook(self)
                except:
                    result = False
            else:
                #print 'drawTreeHook not known'
                result = None

            if not result:

                #@    << draw text >>
                #@+node:bob.20070823184701:<< draw text >>

                current = c.currentPosition()

                #dc.SetBrush(wx.TRANSPARENT_BRUSH)
                #dc.SetPen(wx.BLACK_PEN)

                for sp in positions:

                    #@    << draw user icons >>
                    #@+node:bob.20080105192650:<< draw user icons >>
                    #if hasattr(sp.v.t,'unknownAttributes'):
                    try:
                        iconsList = sp.v.t.unknownAttributes.get('icons', [])
                    except:
                        iconsList = None


                    if iconsList:

                            pos = sp._textBoxRect.position

                            for usrIcon in iconsList:
                                try:
                                    image = globalImages[usrIcon['relPath']]
                                except KeyError:
                                    path = usrIcon['relPath']
                                    image = g.app.gui.getImage(c, path)

                                dc.DrawBitmapPoint(image, pos)

                                pos = pos + (image.GetWidth() + 5, 0)

                            sp._textBoxRect.position = pos
                    #@nonl
                    #@-node:bob.20080105192650:<< draw user icons >>
                    #@nl

                    if current and current == sp:
                        dc.SetBrush(wx.LIGHT_GREY_BRUSH)
                        dc.SetPen(wx.LIGHT_GREY_PEN)
                        dc.DrawRectangleRect(
                            wx.Rect(*sp._textBoxRect).Inflate(3, 3)
                        )
                        current = False
                        #dc.SetBrush(wx.TRANSPARENT_BRUSH)
                        #dc.SetPen(wx.BLACK_PEN)

                    dc.DrawTextPoint(sp.headString(), sp._textBoxRect.position)
                #@-node:bob.20070823184701:<< draw text >>
                #@nl
                #@    << draw lines >>
                #@+node:bob.20070813173446.27:<< draw lines >>
                #@-node:bob.20070813173446.27:<< draw lines >>
                #@nl
                #@    << draw bitmaps >>
                #@+node:bob.20070823184701.1:<< draw bitmaps >>

                for sp in positions:


                    dc.DrawBitmapPoint(
                        sp._icon,
                        sp._iconBoxRect.position
                    )

                    if sp._clickBoxIcon:
                        dc.DrawBitmapPoint(
                            sp._clickBoxIcon,
                            sp._clickBoxRect.position,
                            True
                        )
                #@-node:bob.20070823184701.1:<< draw bitmaps >>
                #@nl

            #@<< draw focus >>
            #@+node:bob.20070824082600:<< draw focus >>

            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            if self._leoTree.hasFocus():
                dc.SetPen(wx.BLACK_PEN)
            #else:
            #    dc.SetPen(wx.GREEN_PEN)
                dc.DrawRectanglePointSize( (0,0), self.GetSize())
            #@nonl
            #@-node:bob.20070824082600:<< draw focus >>
            #@nl




            #@-node:bob.20070813173446.25:<< draw tree >>
            #@nl

            self._parent.showEntry()






        #@-node:bob.20070813173446.24:def draw
        #@-others
    #@-node:bob.20070813173446.12:class OutlineCanvas
    #@-node:bob.20070902164500.1:== TREE WIDGETS ==
    #@-others
#@-node:bob.20070910154126.2:@thin __wx_alt_gui.py
#@-leo
