#@+leo-ver=4-thin
#@+node:ekr.20081121105001.1111:@thin experimental/__wx_alt_gui.py
#@@language python
#@@tabwidth -4

#@<< docstring >>
#@+node:ekr.20081121105001.1112:<< docstring >>
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
#@-node:ekr.20081121105001.1112:<< docstring >>
#@nl

import re

__revision__ = re.sub(r'^\D+([\d\.]+)\D+$', r'\1', "$Revision: 1.13 $")

__version__ = '0.2.%s'% __revision__

__plugin_name__ = " wxPython GUI"

#@<< version history >>
#@+node:ekr.20081121105001.1113:<< version history >>
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
#@-node:ekr.20081121105001.1113:<< version history >>
#@nl
#@<< bug list & to-do >>
#@+node:ekr.20081121105001.1114:<< bug list & to-do >>
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






#@-node:ekr.20081121105001.1114:<< bug list & to-do >>
#@nl

#@<< imports >>
#@+node:ekr.20081121105001.1115:<< imports >>
import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

import leo.core.leoColor as leoColor
import leo.core.leoCommands as leoCommands
import leo.core.leoFind as leoFind
import leo.core.leoFrame as leoFrame
import leo.core.leoGui as leoGui
import leo.core.leoKeys as leoKeys
import leo.core.leoMenu as leoMenu
import leo.core.leoNodes as leoNodes
import leo.core.leoUndo as leoUndo

import leo.core.leoChapters as leoChapters

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

#@-node:ekr.20081121105001.1115:<< imports >>
#@nl

#@<< define module level functions >>
#@+node:ekr.20081121105001.1116:<< define module level functions >>
#@+others
#@+node:ekr.20081121105001.1117: init
def init():

    return False

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
        #@+node:ekr.20081121105001.1118:<< over rides >>

        # import leo.core.leoAtFile as leoAtFile

        # old = leoAtFile.atFile.openFileForReading

        # def wxOpenFileForReading(self,fileName,*args, **kw):
            # #g.trace( fileName)
            # old(self, fileName, *args, **kw)
            # #wx.SafeYield(onlyIfNeeded=True)

        # leoAtFile.atFile.openFileForReading = wxOpenFileForReading
        import leo.core.leoEditCommands as leoEditCommands
        g.funcToMethod(getImage, leoEditCommands.editCommandsClass)
        #@-node:ekr.20081121105001.1118:<< over rides >>
        #@nl
        pass

    return ok
#@-node:ekr.20081121105001.1117: init
#@+node:ekr.20081121105001.1119:name2color
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

#@-node:ekr.20081121105001.1119:name2color
#@+node:ekr.20081121105001.1120:getImage
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
#@-node:ekr.20081121105001.1120:getImage
#@+node:ekr.20081121105001.1121:myclass
def myclass(self):
    try:
        return self.__class__.__name__
    except:
        return '< no class name! >'

#@-node:ekr.20081121105001.1121:myclass
#@+node:ekr.20081121105001.1122:test subs
def _(s):
     ts = type(s)
     return '\n\tText[%s]\n\ttype: %s' % (s[:20].replace('\n', '\\n'),ts)

def _split(i, s):
    return '[%s] [%s]' % (s[:i], s[i:])
#@-node:ekr.20081121105001.1122:test subs
#@+node:ekr.20081121105001.1123:onGlobalChar
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
#@-node:ekr.20081121105001.1123:onGlobalChar
#@+node:ekr.20081121105001.1124:onRogueChar
def onRogueChar(self, event, type):
    g.trace(type, g.callers())

    onGlobalChar(self, event)
#@-node:ekr.20081121105001.1124:onRogueChar
#@-others
#@nonl
#@-node:ekr.20081121105001.1116:<< define module level functions >>
#@nl

if wx:

    #@    << constants >>
    #@+node:ekr.20081121105001.1125:<< constants >>
    if wx:
        HORIZONTAL = wx.HORIZONTAL
        VERTICAL = wx.VERTICAL

    #@-node:ekr.20081121105001.1125:<< constants >>
    #@nl

    #@    @+others
    #@+node:ekr.20081121105001.1126:tkFont.Font
    class tkFont(object):
        """class to emulate tkFont module"""

        class Font(object):
            """class to emulate tkFont.Font object."""

            #@        @+others
            #@+node:ekr.20081121105001.1127:__init__ (tkFont.Font)
            def __init__(self,*args, **kw):
                #g.pr(myclass(self), args, kw)

                self.kw = kw




            #@-node:ekr.20081121105001.1127:__init__ (tkFont.Font)
            #@+node:ekr.20081121105001.1128:actual
            def actual(self, key=None):

                if not key:
                    return self.kw

                else:
                    return self.kw.get(key, None)

            #@-node:ekr.20081121105001.1128:actual
            #@+node:ekr.20081121105001.1129:configure
            def configure(self, **kw):

                self.kw.update(kw)
                #g.trace(self.kw)

            config = configure
            #@-node:ekr.20081121105001.1129:configure
            #@-others
    #@-node:ekr.20081121105001.1126:tkFont.Font
    #@+node:ekr.20081121105001.1130:Tk_Text
    class Tk_Text(object):

        #@    @+others
        #@+node:ekr.20081121105001.1131:__init__
        def __init__(self):

            pass

        #@-node:ekr.20081121105001.1131:__init__
        #@+node:ekr.20081121105001.1132:tag_add
        def tag_add(self, w, tag, start, stop):
            g.trace( w, tag, start, stop)
        #@nonl
        #@-node:ekr.20081121105001.1132:tag_add
        #@+node:ekr.20081121105001.1133:tag_ranges
        def tag_ranges(self, w, name):
            g.trace(w, name)
            return tuple()
        #@nonl
        #@-node:ekr.20081121105001.1133:tag_ranges
        #@+node:ekr.20081121105001.1134:tag_remove
        def tag_remove(self, w, tagName, x_i, x_j):
            g.trace( w, tagName, x_i, x_j)
        #@nonl
        #@-node:ekr.20081121105001.1134:tag_remove
        #@+node:ekr.20081121105001.1135:showcalls
        def showcalls(self, name, *args, **kw):
            g.trace( 'showcalls', name, args, kw)
        #@nonl
        #@-node:ekr.20081121105001.1135:showcalls
        #@+node:ekr.20081121105001.1136:__getattr__
        def __getattr__(self, name):

           return lambda *args, **kw : self.showcalls(name, *args, **kw)
        #@-node:ekr.20081121105001.1136:__getattr__
        #@-others
    #@-node:ekr.20081121105001.1130:Tk_Text
    #@+node:ekr.20081121105001.1137:=== TEXT WIDGETS ===
    #@<< baseTextWidget class >>
    #@+node:ekr.20081121105001.1138:<< baseTextWidget class >>

    class baseTextWidget (leoFrame.baseTextWidget):

        """The base class for all text wrapper classes."""

        #@    @+others
        #@+node:ekr.20081121105001.1139:__init__

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



        #@-node:ekr.20081121105001.1139:__init__
        #@+node:ekr.20081121105001.1140:setWidget
        #@-node:ekr.20081121105001.1140:setWidget
        #@+node:ekr.20081121105001.1141:getName

        def getName(self):
            return self.name or self.widget.GetName()

        GetName = getName
        #@-node:ekr.20081121105001.1141:getName
        #@+node:ekr.20081121105001.1142:== Focus ==
        #@+node:ekr.20081121105001.1143:onGlobalGainFocus

        def onGlobalGainFocus(self, event):
            if self.onGainFocus(event):
                return
            self.c.focusManager.gotFocus(self, event)


        #@-node:ekr.20081121105001.1143:onGlobalGainFocus
        #@+node:ekr.20081121105001.1144:onGainFocus

        def onGainFocus(self, event):
            return
        #@nonl
        #@-node:ekr.20081121105001.1144:onGainFocus
        #@+node:ekr.20081121105001.1145:onGlobalLoseFocus

        def onGlobalLoseFocus(self, event):
            if self.onLoseFocus(event):
                return
            self.c.focusManager.lostFocus(self, event)
        #@nonl
        #@-node:ekr.20081121105001.1145:onGlobalLoseFocus
        #@+node:ekr.20081121105001.1146:onLoseFocus

        def onLoseFocus(self, event):
            return
        #@nonl
        #@-node:ekr.20081121105001.1146:onLoseFocus
        #@-node:ekr.20081121105001.1142:== Focus ==
        #@+node:ekr.20081121105001.1147:clear

        def clear(self):
            """Remove all text from the text widget."""

            self._setAllText('')
        #@-node:ekr.20081121105001.1147:clear
        #@+node:ekr.20081121105001.1148:after_idle
        def after_idle(self, *args, **kw):
            wx.CallAfter(*args, **kw)
        #@nonl
        #@-node:ekr.20081121105001.1148:after_idle
        #@+node:ekr.20081121105001.1149:after

        def after(self, *args, **kw):
            wx.CallLater(*args, **kw)
        #@-node:ekr.20081121105001.1149:after
        #@+node:ekr.20081121105001.1150:setBackgroundColor & SetBackgroundColour
        def setBackgroundColor (self,color):

            return self._setBackgroundColor(name2color(color))


        #@-node:ekr.20081121105001.1150:setBackgroundColor & SetBackgroundColour
        #@-others
    #@-node:ekr.20081121105001.1138:<< baseTextWidget class >>
    #@nl

    #@+others
    #@+node:ekr.20081121105001.1151:plainTextWidget (baseTextWidget)
    class plainTextWidget (baseTextWidget):

        """The base class for all wxTextCtrl wrappers."""

        #@    @+others
        #@+node:ekr.20081121105001.1152:__init__
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


        #@-node:ekr.20081121105001.1152:__init__
        #@+node:ekr.20081121105001.1153:bindings (TextCtrl)

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
        #@-node:ekr.20081121105001.1153:bindings (TextCtrl)
        #@-others
    #@nonl
    #@-node:ekr.20081121105001.1151:plainTextWidget (baseTextWidget)
    #@+node:ekr.20081121105001.1154:stcTextWidget (baseTextWidget)

    class stcTextWidget (stc.StyledTextCtrl, baseTextWidget):

        '''A wrapper for wx.StyledTextCtrl.'''

        # The signatures of tag_add and insert are different from the Tk.Text signatures.

        #@    @+others
        #@+node:ekr.20081121105001.1155:__init__

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



        #@-node:ekr.20081121105001.1155:__init__
        #@+node:ekr.20081121105001.1156:__str__
        def __str__(self):
            return myclass(self) + str(id(self))


        __repr__ = __str__
        #@-node:ekr.20081121105001.1156:__str__
        #@+node:ekr.20081121105001.1157:initStc
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

        #@-node:ekr.20081121105001.1157:initStc
        #@+node:ekr.20081121105001.1158:Wrapper methods
        #@+node:ekr.20081121105001.1159:bindings (stc)
        # Specify the names of widget-specific methods.
        # These particular names are the names of wx.TextCtrl methods.



        def _appendText(self,s):
            #g.trace('stc:', _(s))
            self.widget.AppendText(s)
            #g.pr('\t', _(self.widget.Text))

        def _get(self,i,j):
            #g.trace( 'i: %s j:%s' %(i, j))
            py = self.toStcIndex
            w = self.widget
            s = w.Text
            ii, jj = py(i,s),py(j,s)
            #g.pr('	ii=', ii, ' jj=', jj)
            result = self.widget.GetTextRange(ii, jj)
            #g.pr('\n\t', type(result), 'len:', len(result))
            #g.pr(_(result))
            return result

        def _getAllText(self):
            text = self.widget.Text
            #g.trace(_(text))
            #g.pr('\t', g.callers())
            return text

        def _getFocus(self):
            #g.trace()
            result = wx.Window.FindFocus()
            #g.trace('stc:',result)
            return result

        def _getInsertPoint(self):
            w = self.widget
            text = w.Text
            # g.pr('\n---------------------')
            # g.trace(type(w.Text), type(w.TextUTF8), type(w.TextRaw))
            # g.trace(w.CurrentPos, text)
            result = self.fromStcIndex(w.CurrentPos, text)
            # g.trace(result, '[%s] [%s]' % (text[:result], text[result:]))
            # g.pr('---------------------\n')
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
            #g.pr('\t', _(self.widget.Text))

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
            #g.pr'\tWant FirstVisible:', wantfirst)

            w.LineScroll(0, wantfirst - first)
            #g.pr('')
            #g.pr('\tLines to scroll:', wantfirst - first)
            #g.pr('\tNew FirstVisible:', w.FirstVisibleLine
            #g.pr('')
        #@-node:ekr.20081121105001.1159:bindings (stc)
        #@+node:ekr.20081121105001.1160:Overrides of baseTextWidget methods
        #@+node:ekr.20081121105001.1161:toStcIndex
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

            #g.pr('\n\tChar-codes: [', ' | '.join([str(ord(ch)) for ch in s]), ']')

            result =  len(s[:i].encode('utf8'))

            #g.pr('\n\t result', result)
            return result

        def fromStcIndex(self, i, s):
            """Translate from stc positions to python positions.

            s must obviously be a unicode string .
            """
            #g.trace('\n\tencoding:', type(s), i)
            try:
                result = s.encode('utf8')[:i]
                #g.pr('YAY encoded ok: type is ', type(result))
                #g.pr('\n\t len:', len(result),newline=False)
                #g.pr('\n\t chars:[',  ' | '.join([str(ord(ch)) for ch in result]), ']')
            except:
                g.pr('encoding error ============================')
                g.pr(g.callers())

            try:
                result = result.decode('utf8')
                #g.pr('YAY DECODING ok: type is ', type(result))
                #g.pr('\n\t len:', len(result),newline=False)
                #g.pr('\n\t chars:[',  ' | '.join([str(ord(ch)) for ch in result]), ']')
            except:
                g.pr('decoding error #######################################')

            result = len(result)
            #g.pr('\n\tinput:%s result:%s'%(i, result))
            return result

        #@-node:ekr.20081121105001.1161:toStcIndex
        #@+node:ekr.20081121105001.1162:appendText
        def appendText (self,s):

            #g.trace('stc:', _(s))
            self.widget.AppendText(s)
            #g.pr('\t', _(self.widget.Text))

        #@-node:ekr.20081121105001.1162:appendText
        #@+node:ekr.20081121105001.1163:delete
        def delete(self,i,j=None):

            w = self.widget
            py = self.toStcIndex

            s = w.Text

            if j is None:
                j = i+ 1

            w.SetSelection(py(i,s), py(j,s))
            w.DeleteBack()
        #@-node:ekr.20081121105001.1163:delete
        #@+node:ekr.20081121105001.1164:see & seeInsertPoint


        def see(self, i):

            #g.trace( i, g.callers(20))

            w = self.widget

            s = w.Text

            #top = w.FirstVisibleLine
            #line = w.LineFromPosition(w.CurrentPos)

            #g.trace( '\n\ttop:', w.FirstVisibleLine)
            #g.pr('\tcurrent line:', w.LineFromPosition(w.CurrentPos))


            ii = self.toStcIndex(i, s)
            #g.pr('\ttarget line:', w.LineFromPosition(ii))
            w.ScrollToLine(w.LineFromPosition(ii))

        def seeInsertPoint(self):

            #g.trace()
            #w = self.widget
            #w.ScrollToLine(w.LineFromPosition(w.CurrentPos))
            pass

        #@-node:ekr.20081121105001.1164:see & seeInsertPoint
        #@+node:ekr.20081121105001.1165:insert
        def insert(self,i, s):

            topy = self.fromStcIndex

            '''Override the baseTextWidget insert method.'''

            #print

            #g.trace('py-index:', i, 'insert[%s]'%s)# g.callers())

            #g.pr('\t\t', g.callers())

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
        #@-node:ekr.20081121105001.1165:insert
        #@+node:ekr.20081121105001.1166:stc.setInsertPoint
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
        #@-node:ekr.20081121105001.1166:stc.setInsertPoint
        #@+node:ekr.20081121105001.1167:stc.setSelectionRange
        def setSelectionRange (self,i,j,insert=None):

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
        #@-node:ekr.20081121105001.1167:stc.setSelectionRange
        #@+node:ekr.20081121105001.1168:xyToGui/PythonIndex (to do)
        def xyToPythonIndex (self,x,y):

            w = self

            data = w.widget.PositionFromPoint(wx.Point(x,y))
            #g.trace('data',data)

            return 0 ### ?? Non-zero value may loop.
        #@-node:ekr.20081121105001.1168:xyToGui/PythonIndex (to do)
        #@+node:ekr.20081121105001.1169:tags (to-do)
        #@+node:ekr.20081121105001.1170:mark_set (to be removed)
        def mark_set(self,markName,i):

            g.trace('stc', markName, i)
            return

            w = self
            i = self.toStcIndex(i)

            ### Tk.Text.mark_set(w,markName,i)
        #@-node:ekr.20081121105001.1170:mark_set (to be removed)
        #@+node:ekr.20081121105001.1171:init_colorizer
        def init_colorizer(self, col):

            #g.trace()

            col.removeOldTags = lambda *args: self.ClearDocumentStyle()

            col.removeAllTags = lambda  : self.ClearDocumentStyle()
        #@-node:ekr.20081121105001.1171:init_colorizer
        #@+node:ekr.20081121105001.1172:putNewTags
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

        #@-node:ekr.20081121105001.1172:putNewTags
        #@+node:ekr.20081121105001.1173:tag_add
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
        #@-node:ekr.20081121105001.1173:tag_add
        #@+node:ekr.20081121105001.1174:start_tag_configure
        def start_tag_configure(self):
            #g.trace()
            self.leo_tags = {}
            self.leo_styles = {}
        #@nonl
        #@-node:ekr.20081121105001.1174:start_tag_configure
        #@+node:ekr.20081121105001.1175:tag_configure
        def tag_configure (self,tagName,**kw):

            #g.trace('stc', tagName, kw)

            try:
                thistag = self.leo_tags[tagName]
            except KeyError:
                thistag = self.leo_tags[tagName] = {}

            thistag.update(kw)

        tag_config = tag_configure
        #@-node:ekr.20081121105001.1175:tag_configure
        #@+node:ekr.20081121105001.1176:end_tag_configure
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
        #@-node:ekr.20081121105001.1176:end_tag_configure
        #@+node:ekr.20081121105001.1177:tag_delete (NEW)
        def tag_delete (self,tagName,*args,**keys):
            #g.trace('stc', tagName,args,keys)
            pass
        #@nonl
        #@-node:ekr.20081121105001.1177:tag_delete (NEW)
        #@+node:ekr.20081121105001.1178:tag_names
        def tag_names (self, *args):
            #g.trace('stc', args)
            return []
        #@-node:ekr.20081121105001.1178:tag_names
        #@+node:ekr.20081121105001.1179:tag_ranges
        def tag_ranges(self,tagName):
            #g.trace('stc', tagName)
            return tuple() ###

            w = self
            aList = Tk.Text.tag_ranges(w,tagName)
            aList = [w.toPythonIndex(z) for z in aList]
            return tuple(aList)
        #@-node:ekr.20081121105001.1179:tag_ranges
        #@+node:ekr.20081121105001.1180:tag_remove
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
        #@-node:ekr.20081121105001.1180:tag_remove
        #@-node:ekr.20081121105001.1169:tags (to-do)
        #@-node:ekr.20081121105001.1160:Overrides of baseTextWidget methods
        #@+node:ekr.20081121105001.1181:Wrapper methods (widget-independent)
        # These methods are widget-independent because they call the corresponding _xxx methods.

        if 0:
            #@    @+others
            #@+node:ekr.20081121105001.1182:appendText
            def appendText (self,s):

                w = self
                w._appendText(s)
            #@-node:ekr.20081121105001.1182:appendText
            #@+node:ekr.20081121105001.1183:bind
            def bind (self,kind,*args,**keys):

                w = self

                pass # g.trace('wxLeoText',kind,args[0].__name__)
            #@nonl
            #@-node:ekr.20081121105001.1183:bind
            #@+node:ekr.20081121105001.1184:clipboard_clear & clipboard_append
            def clipboard_clear (self):

                g.app.gui.replaceClipboardWith('')

            def clipboard_append(self,s):

                s1 = g.app.gui.getTextFromClipboard()

                g.app.gui.replaceClipboardWith(s1 + s)
            #@-node:ekr.20081121105001.1184:clipboard_clear & clipboard_append
            #@+node:ekr.20081121105001.1185:delete
            def delete(self,i,j=None):

                w = self
                i = w.toPythonIndex(i)
                if j is None: j = i+ 1
                j = w.toPythonIndex(j)

                # g.trace(i,j,len(s),repr(s[:20]))
                s = w.getAllText()
                w.setAllText(s[:i] + s[j:])
            #@-node:ekr.20081121105001.1185:delete
            #@+node:ekr.20081121105001.1186:deleteTextSelection
            def deleteTextSelection (self):

                w = self
                i,j = w._getSelectionRange()
                if i == j: return

                s = w._getAllText()
                s = s[i:] + s[j:]

                # g.trace(len(s),repr(s[:20]))
                w._setAllText(s)
            #@-node:ekr.20081121105001.1186:deleteTextSelection
            #@+node:ekr.20081121105001.1187:event_generate (baseTextWidget)
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
            #@-node:ekr.20081121105001.1187:event_generate (baseTextWidget)
            #@+node:ekr.20081121105001.1188:flashCharacter (to do)
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
            #@-node:ekr.20081121105001.1188:flashCharacter (to do)
            #@+node:ekr.20081121105001.1189:getFocus (baseText)
            def getFocus (self):

                w = self
                w2 = w._getFocus()
                # g.trace('w',w,'focus',w2)
                return w2

            findFocus = getFocus
            #@-node:ekr.20081121105001.1189:getFocus (baseText)
            #@+node:ekr.20081121105001.1190:get
            def get(self,i,j=None):

                w = self

                i = w.toPythonIndex(i)
                if j is None: j = i+ 1
                j = w.toPythonIndex(j)

                s = w._get(i,j)
                return g.toUnicode(s,g.app.tkEncoding)
            #@-node:ekr.20081121105001.1190:get
            #@+node:ekr.20081121105001.1191:getAllText
            def getAllText (self):

                w = self

                s = w._getAllText()
                return g.toUnicode(s,g.app.tkEncoding)
            #@-node:ekr.20081121105001.1191:getAllText
            #@+node:ekr.20081121105001.1192:getInsertPoint (baseText)
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
            #@-node:ekr.20081121105001.1192:getInsertPoint (baseText)
            #@+node:ekr.20081121105001.1193:getName & GetName
            def GetName(self):
                return self.name

            getName = GetName
            #@nonl
            #@-node:ekr.20081121105001.1193:getName & GetName
            #@+node:ekr.20081121105001.1194:getSelectedText
            def getSelectedText (self):

                w = self
                s = w._getSelectedText()
                return g.toUnicode(s,g.app.tkEncoding)
            #@-node:ekr.20081121105001.1194:getSelectedText
            #@+node:ekr.20081121105001.1195:getSelectionRange (baseText)
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
            #@-node:ekr.20081121105001.1195:getSelectionRange (baseText)
            #@+node:ekr.20081121105001.1196:getYScrollPosition
            def getYScrollPosition (self):

                 w = self
                 return w._getYScrollPosition()
            #@-node:ekr.20081121105001.1196:getYScrollPosition
            #@+node:ekr.20081121105001.1197:getWidth
            def getWidth (self):

                '''Return the width of the widget.
                This is only called for headline widgets,
                and gui's may choose not to do anything here.'''

                w = self
                return 0
            #@-node:ekr.20081121105001.1197:getWidth
            #@+node:ekr.20081121105001.1198:hasSelection
            def hasSelection (self):

                w = self
                i,j = w.getSelectionRange()
                return i != j
            #@-node:ekr.20081121105001.1198:hasSelection
            #@+node:ekr.20081121105001.1199:insert
            # The signature is more restrictive than the Tk.Text.insert method.

            def insert(self,i,s):

                w = self
                i = w.toPythonIndex(i)
                # w._setInsertPoint(i)
                w._insertText(i,s)
            #@-node:ekr.20081121105001.1199:insert
            #@+node:ekr.20081121105001.1200:indexIsVisible
            def indexIsVisible (self,i):

                return False # Code will loop if this returns True forever.
            #@nonl
            #@-node:ekr.20081121105001.1200:indexIsVisible
            #@+node:ekr.20081121105001.1201:replace
            def replace (self,i,j,s):

                w = self
                w.delete(i,j)
                w.insert(i,s)
            #@-node:ekr.20081121105001.1201:replace
            #@+node:ekr.20081121105001.1202:scrollLines
            def scrollLines (self,n):

                w = self
                w._scrollLines(n)
            #@nonl
            #@-node:ekr.20081121105001.1202:scrollLines
            #@+node:ekr.20081121105001.1203:see & seeInsertPoint
            def see(self,index):

                w = self
                i = self.toPythonIndex(index)
                w._see(i)

            def seeInsertPoint(self):

                w = self
                i = w._getInsertPoint()
                w._see(i)
            #@-node:ekr.20081121105001.1203:see & seeInsertPoint
            #@+node:ekr.20081121105001.1204:selectAllText
            def selectAllText (self,insert=None):

                '''Select all text of the widget.'''

                w = self
                w.setSelectionRange(0,'end',insert=insert)
            #@-node:ekr.20081121105001.1204:selectAllText
            #@+node:ekr.20081121105001.1205:setAllText
            def setAllText (self,s):

                w = self
                w._setAllText(s)
            #@nonl
            #@-node:ekr.20081121105001.1205:setAllText
            #@+node:ekr.20081121105001.1206:setBackgroundColor & SetBackgroundColour
            def setBackgroundColor (self,color):

                w = self

                # Translate tk colors to wx colors.
                d = { 'lightgrey': 'light grey', 'lightblue': 'leo blue',}

                color = d.get(color,color)

                return w._setBackgroundColor(color)

            SetBackgroundColour = setBackgroundColor
            #@nonl
            #@-node:ekr.20081121105001.1206:setBackgroundColor & SetBackgroundColour
            #@+node:ekr.20081121105001.1207:setFocus (baseText)
            def setFocus (self):

                w = self
                # g.trace('baseText')
                return w._setFocus()

            SetFocus = setFocus
            #@-node:ekr.20081121105001.1207:setFocus (baseText)
            #@+node:ekr.20081121105001.1208:setInsertPoint (baseText)
            def setInsertPoint (self,pos):

                w = self
                w.virtualInsertPoint = i = w.toPythonIndex(pos)
                # g.trace(self,i)
                w._setInsertPoint(i)
            #@-node:ekr.20081121105001.1208:setInsertPoint (baseText)
            #@+node:ekr.20081121105001.1209:setSelectionRange (baseText)
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
            #@-node:ekr.20081121105001.1209:setSelectionRange (baseText)
            #@+node:ekr.20081121105001.1210:setWidth
            def setWidth (self,width):

                '''Set the width of the widget.
                This is only called for headline widgets,
                and gui's may choose not to do anything here.'''

                w = self
                pass
            #@-node:ekr.20081121105001.1210:setWidth
            #@+node:ekr.20081121105001.1211:setYScrollPosition
            def setYScrollPosition (self,i):

                 w = self
                 w._setYScrollPosition(i)
            #@nonl
            #@-node:ekr.20081121105001.1211:setYScrollPosition
            #@+node:ekr.20081121105001.1212:xyToGui/PythonIndex
            def xyToPythonIndex (self,x,y):
                return 0
            #@-node:ekr.20081121105001.1212:xyToGui/PythonIndex
            #@+node:ekr.20081121105001.1213:yview
            def yview (self,*args):

                '''w.yview('moveto',y) or w.yview()'''

                return 0,0
            #@nonl
            #@-node:ekr.20081121105001.1213:yview
            #@-others
        #@nonl
        #@-node:ekr.20081121105001.1181:Wrapper methods (widget-independent)
        #@-node:ekr.20081121105001.1158:Wrapper methods
        #@-others
    #@nonl
    #@-node:ekr.20081121105001.1154:stcTextWidget (baseTextWidget)
    #@+node:ekr.20081121105001.1214:findTextWidget (plainTextWidget)

    class findTextWidget (plainTextWidget):

        """A wrapper for text widgets used in the 'Find' panel."""

        #@    @+others
        #@+node:ekr.20081121105001.1215:__init__

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
        #@-node:ekr.20081121105001.1215:__init__
        #@-others
    #@nonl
    #@-node:ekr.20081121105001.1214:findTextWidget (plainTextWidget)
    #@+node:ekr.20081121105001.1216:statusTextWidget (plainTextWidget)

    class statusTextWidget (plainTextWidget):

        """A wrapper for text widgets used as status lines."""

        #@    @+others
        #@+node:ekr.20081121105001.1217:pass
        pass
        #@nonl
        #@-node:ekr.20081121105001.1217:pass
        #@-others
    #@-node:ekr.20081121105001.1216:statusTextWidget (plainTextWidget)
    #@+node:ekr.20081121105001.1218:headlineTextWidget (plainTextWidget)

    class headlineTextWidget (plainTextWidget):

        """A wrapper for  text widgets used to edit headlines."""

        #@    @+others
        #@+node:ekr.20081121105001.1219:__init__

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

        #@-node:ekr.20081121105001.1219:__init__
        #@-others
    #@nonl
    #@-node:ekr.20081121105001.1218:headlineTextWidget (plainTextWidget)
    #@+node:ekr.20081121105001.1220:minibufferTextWidget (plainTextWidget)

    class minibufferTextWidget (plainTextWidget):

        '''A wrapper for the minibuffer text widgets.'''

        #@    @+others
        #@+node:ekr.20081121105001.1221:__init__

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


        #@-node:ekr.20081121105001.1221:__init__
        #@-others
    #@nonl
    #@-node:ekr.20081121105001.1220:minibufferTextWidget (plainTextWidget)
    #@+node:ekr.20081121105001.1222:richTextWidget (baseTextWidget)

    class richTextWidget (baseTextWidget):

        '''A class wrapping wx.richtext.RichTextCtrl widgets.'''

        #@    @+others
        #@+node:ekr.20081121105001.1223:__init__

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



        #@-node:ekr.20081121105001.1223:__init__
        #@+node:ekr.20081121105001.1224:onSize
        def onSize(self, event):
            """Handle EVT_SIZE for RichTextCtrl."""

            w = self.widget

            #g.trace(myclass(self), w.GetClientSize())
            w.ShowPosition(w.GetInsertionPoint())

            event.Skip()
        #@-node:ekr.20081121105001.1224:onSize
        #@+node:ekr.20081121105001.1225:bindings (TextCtrl)

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
        #@-node:ekr.20081121105001.1225:bindings (TextCtrl)
        #@+node:ekr.20081121105001.1226:hide
        if 0:
            #@    @+others
            #@+node:ekr.20081121105001.1227:onChar
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


            #@-node:ekr.20081121105001.1227:onChar
            #@-others
        #@nonl
        #@-node:ekr.20081121105001.1226:hide
        #@-others
    #@nonl
    #@-node:ekr.20081121105001.1222:richTextWidget (baseTextWidget)
    #@+node:ekr.20081121105001.1228:logTextWidget (richTextWidget)

    class logTextWidget(richTextWidget):

        '''A wrapper for log pane text widgets.'''

        #@    @+others
        #@+node:ekr.20081121105001.1229:onGainFocus

        def onGainFocus(self, event):
            """Respond to focus event for logTextWidget.

            We don't want focus, so send it back to where it
            came from.

            """

            self.c.focusManager.lastFocus()
            event.Skip()
            return True
        #@-node:ekr.20081121105001.1229:onGainFocus
        #@-others
    #@nonl
    #@-node:ekr.20081121105001.1228:logTextWidget (richTextWidget)
    #@-others
    #@nonl
    #@-node:ekr.20081121105001.1137:=== TEXT WIDGETS ===
    #@+node:ekr.20081121105001.1230:Find/Spell classes
    #@+node:ekr.20081121105001.1231:wxSearchWidget
    class wxSearchWidget:

        """A dummy widget class to pass to Leo's core find code."""

        #@    @+others
        #@+node:ekr.20081121105001.1232:wxSearchWidget.__init__
        def __init__ (self):

            self.insertPoint = 0
            self.selection = 0,0
            self.bodyCtrl = self
            self.body = self
            self.text = None
        #@nonl
        #@-node:ekr.20081121105001.1232:wxSearchWidget.__init__
        #@-others
    #@nonl
    #@-node:ekr.20081121105001.1231:wxSearchWidget
    #@+node:ekr.20081121105001.1233:wxFindTab class (leoFind.findTab)
    class wxFindTab (leoFind.findTab):

        '''A subclass of the findTab class containing all wxGui code.'''

        #@    @+others
        #@+node:ekr.20081121105001.1234:Birth
        #@+node:ekr.20081121105001.1235:initGui
        # Called from leoFind.findTab.ctor.

        def initGui (self):

            # g.trace('wxFindTab')

            self.svarDict = {} # Keys are ivar names, values are svar objects.

            for key in self.intKeys:
                self.svarDict[key] = self.svar()

            for key in self.newStringKeys:
                self.svarDict[key] = self.svar()
        #@-node:ekr.20081121105001.1235:initGui
        #@+node:ekr.20081121105001.1236:init (wxFindTab)
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
            #@+node:ekr.20081121105001.1237:<< set find/change widgets >>
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
            #@-node:ekr.20081121105001.1237:<< set find/change widgets >>
            #@nl
            #@    << set radio buttons from ivars >>
            #@+node:ekr.20081121105001.1238:<< set radio buttons from ivars >>
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
            #@-node:ekr.20081121105001.1238:<< set radio buttons from ivars >>
            #@nl
            #@    << set checkboxes from ivars >>
            #@+node:ekr.20081121105001.1239:<< set checkboxes from ivars >>
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
            #@-node:ekr.20081121105001.1239:<< set checkboxes from ivars >>
            #@nl
        #@-node:ekr.20081121105001.1236:init (wxFindTab)
        #@-node:ekr.20081121105001.1234:Birth
        #@+node:ekr.20081121105001.1240:class svar
        class svar:
            '''A class like Tk's IntVar and StringVar classes.'''
            def __init__(self):
                self.val = None
            def get (self):
                return self.val
            def set (self,val):
                self.val = val
        #@-node:ekr.20081121105001.1240:class svar
        #@+node:ekr.20081121105001.1241:createFrame (wxFindTab)
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
        #@+node:ekr.20081121105001.1242:createFindChangeAreas
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
        #@-node:ekr.20081121105001.1242:createFindChangeAreas
        #@+node:ekr.20081121105001.1243:layout
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
        #@-node:ekr.20081121105001.1243:layout
        #@+node:ekr.20081121105001.1244:createBoxes
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
        #@-node:ekr.20081121105001.1244:createBoxes
        #@+node:ekr.20081121105001.1245:createBindings TO DO
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
        #@-node:ekr.20081121105001.1245:createBindings TO DO
        #@+node:ekr.20081121105001.1246:createButtons (does nothing)
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
        #@-node:ekr.20081121105001.1246:createButtons (does nothing)
        #@-node:ekr.20081121105001.1241:createFrame (wxFindTab)
        #@+node:ekr.20081121105001.1247:createBindings
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
        #@-node:ekr.20081121105001.1247:createBindings
        #@+node:ekr.20081121105001.1248:Support for minibufferFind class (wxFindTab)
        # This is the same as the Tk code because we simulate Tk svars.
        #@nonl
        #@+node:ekr.20081121105001.1249:getOption
        def getOption (self,ivar):

            var = self.svarDict.get(ivar)

            if var:
                val = var.get()
                # g.trace('%s = %s' % (ivar,val))
                return val
            else:
                g.trace('bad ivar name: %s' % ivar)
                return None
        #@-node:ekr.20081121105001.1249:getOption
        #@+node:ekr.20081121105001.1250:setOption
        def setOption (self,ivar,val):

            if ivar in self.intKeys:
                if val is not None:
                    var = self.svarDict.get(ivar)
                    var.set(val)
                    # g.trace('%s = %s' % (ivar,val))

            elif not g.app.unitTesting:
                g.trace('oops: bad find ivar %s' % ivar)
        #@-node:ekr.20081121105001.1250:setOption
        #@+node:ekr.20081121105001.1251:toggleOption
        def toggleOption (self,ivar):

            if ivar in self.intKeys:
                var = self.svarDict.get(ivar)
                val = not var.get()
                var.set(val)
                # g.trace('%s = %s' % (ivar,val),var)
            else:
                g.trace('oops: bad find ivar %s' % ivar)
        #@-node:ekr.20081121105001.1251:toggleOption
        #@-node:ekr.20081121105001.1248:Support for minibufferFind class (wxFindTab)
        #@+node:ekr.20081121105001.1252:toggleTextWidgetFocus

        def toggleTextWidgetFocus(self, widget):

            c = self.c

            g.trace(c.widget_name(widget), widget)
            if c.widget_name(widget) == 'find-text':
                #print 'change', self.change_ctrl
                self.change_ctrl.setFocus()
            else:
                #print 'find', self.find_ctrl
                self.find_ctrl.setFocus()

        #@-node:ekr.20081121105001.1252:toggleTextWidgetFocus
        #@-others
    #@nonl
    #@-node:ekr.20081121105001.1233:wxFindTab class (leoFind.findTab)
    #@+node:ekr.20081121105001.1253:class wxSpellTab TO DO
    class wxSpellTab:

        #@    @+others
        #@+node:ekr.20081121105001.1254:wxSpellTab.__init__
        def __init__ (self,c,tabName):

            self.c = c
            self.tabName = tabName

            self.createFrame()
            self.createBindings()
        #@-node:ekr.20081121105001.1254:wxSpellTab.__init__
        #@+node:ekr.20081121105001.1255:createBindings TO DO
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
        #@-node:ekr.20081121105001.1255:createBindings TO DO
        #@+node:ekr.20081121105001.1256:createFrame TO DO
        def createFrame (self):

            return ###

            c = self.c ; log = c.frame.log ; tabName = self.tabName

            parentFrame = log.frameDict.get(tabName)
            w = log.textDict.get(tabName)
            w.pack_forget()

            # Set the common background color.
            bg = c.config.getColor('log_pane_Spell_tab_background_color') or 'LightSteelBlue2'

            #@    << Create the outer frames >>
            #@+node:ekr.20081121105001.1257:<< Create the outer frames >>
            self.outerScrolledFrame = Pmw.ScrolledFrame(
                parentFrame,usehullsize = 1)

            self.outerFrame = outer = self.outerScrolledFrame.component('frame')
            self.outerFrame.configure(background=bg)

            for z in ('borderframe','clipper','frame','hull'):
                self.outerScrolledFrame.component(z).configure(
                    relief='flat',background=bg)
            #@-node:ekr.20081121105001.1257:<< Create the outer frames >>
            #@nl
            #@    << Create the text and suggestion panes >>
            #@+node:ekr.20081121105001.1258:<< Create the text and suggestion panes >>
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
            #@-node:ekr.20081121105001.1258:<< Create the text and suggestion panes >>
            #@nl
            #@    << Create the spelling buttons >>
            #@+node:ekr.20081121105001.1259:<< Create the spelling buttons >>
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
            #@-node:ekr.20081121105001.1259:<< Create the spelling buttons >>
            #@nl

            # Pack last so buttons don't get squished.
            self.outerScrolledFrame.pack(expand=1,fill='both',padx=2,pady=2)
        #@-node:ekr.20081121105001.1256:createFrame TO DO
        #@+node:ekr.20081121105001.1260:Event handlers
        #@+node:ekr.20081121105001.1261:onAddButton
        def onAddButton(self):
            """Handle a click in the Add button in the Check Spelling dialog."""

            self.handler.add()
        #@-node:ekr.20081121105001.1261:onAddButton
        #@+node:ekr.20081121105001.1262:onChangeButton & onChangeThenFindButton
        def onChangeButton(self,event=None):

            """Handle a click in the Change button in the Spell tab."""

            self.handler.change()
            self.updateButtons()


        def onChangeThenFindButton(self,event=None):

            """Handle a click in the "Change, Find" button in the Spell tab."""

            if self.change():
                self.find()
            self.updateButtons()
        #@-node:ekr.20081121105001.1262:onChangeButton & onChangeThenFindButton
        #@+node:ekr.20081121105001.1263:onFindButton
        def onFindButton(self):

            """Handle a click in the Find button in the Spell tab."""

            c = self.c
            self.handler.find()
            self.updateButtons()
            c.invalidateFocus()
            c.bodyWantsFocusNow()
        #@-node:ekr.20081121105001.1263:onFindButton
        #@+node:ekr.20081121105001.1264:onHideButton
        def onHideButton(self):

            """Handle a click in the Hide button in the Spell tab."""

            self.handler.hide()
        #@-node:ekr.20081121105001.1264:onHideButton
        #@+node:ekr.20081121105001.1265:onIgnoreButton
        def onIgnoreButton(self,event=None):

            """Handle a click in the Ignore button in the Check Spelling dialog."""

            self.handler.ignore()
        #@-node:ekr.20081121105001.1265:onIgnoreButton
        #@+node:ekr.20081121105001.1266:onMap
        def onMap (self, event=None):
            """Respond to a Tk <Map> event."""

            self.update(show= False, fill= False)
        #@-node:ekr.20081121105001.1266:onMap
        #@+node:ekr.20081121105001.1267:onSelectListBox
        def onSelectListBox(self, event=None):
            """Respond to a click in the selection listBox."""

            c = self.c
            self.updateButtons()
            c.bodyWantsFocus()
        #@-node:ekr.20081121105001.1267:onSelectListBox
        #@-node:ekr.20081121105001.1260:Event handlers
        #@+node:ekr.20081121105001.1268:Helpers
        #@+node:ekr.20081121105001.1269:bringToFront
        def bringToFront (self):

            self.c.frame.log.selectTab('Spell')
        #@-node:ekr.20081121105001.1269:bringToFront
        #@+node:ekr.20081121105001.1270:fillbox
        def fillbox(self, alts, word=None):
            """Update the suggestions listBox in the Check Spelling dialog."""

            self.suggestions = alts

            if not word:
                word = ""

            self.wordLabel.configure(text= "Suggestions for: " + word)
            self.listBox.delete(0, "end")

            for i in range(len(self.suggestions)):
                self.listBox.insert(i, self.suggestions[i])

            # This doesn't show up because we don't have focus.
            if len(self.suggestions):
                self.listBox.select_set(1)
        #@-node:ekr.20081121105001.1270:fillbox
        #@+node:ekr.20081121105001.1271:getSuggestion
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
        #@-node:ekr.20081121105001.1271:getSuggestion
        #@+node:ekr.20081121105001.1272:update
        def update(self,show=True,fill=False):

            """Update the Spell Check dialog."""

            c = self.c

            if fill:
                self.fillbox([])

            self.updateButtons()

            if show:
                self.bringToFront()
                c.bodyWantsFocus()
        #@-node:ekr.20081121105001.1272:update
        #@+node:ekr.20081121105001.1273:updateButtons (spellTab)
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
        #@-node:ekr.20081121105001.1273:updateButtons (spellTab)
        #@-node:ekr.20081121105001.1268:Helpers
        #@-others
    #@-node:ekr.20081121105001.1253:class wxSpellTab TO DO
    #@-node:ekr.20081121105001.1230:Find/Spell classes
    #@+node:ekr.20081121105001.1274:wxComparePanel class (not ready yet)
    """Leo's base compare class."""

    #@@language python
    #@@tabwidth -4
    #@@pagewidth 80

    import leo.core.leoGlobals as g
    import leo.core.leoCompare as leoCompare

    class wxComparePanel (leoCompare.leoCompare): #,leoWxDialog):

        """A class that creates Leo's compare panel."""

        #@    @+others
        #@+node:ekr.20081121105001.1275:Birth...
        #@+node:ekr.20081121105001.1276:wxComparePanel.__init__
        def __init__ (self,c):

            # Init the base class.
            leoCompare.leoCompare.__init__ (self,c)
            ###leoTkinterDialog.leoTkinterDialog.__init__(self,c,"Compare files and directories",resizeable=False)

            if g.app.unitTesting: return

            self.c = c

            if 0:
                #@        << init tkinter compare ivars >>
                #@+node:ekr.20081121105001.1277:<< init tkinter compare ivars >>
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
                #@-node:ekr.20081121105001.1277:<< init tkinter compare ivars >>
                #@nl

            # These ivars are set from Entry widgets.
            self.limitCount = 0
            self.limitToExtension = None

            # The default file name in the "output file name" browsers.
            self.defaultOutputFileName = "CompareResults.txt"

            if 0:
                self.createTopFrame()
                self.createFrame()
        #@-node:ekr.20081121105001.1276:wxComparePanel.__init__
        #@+node:ekr.20081121105001.1278:finishCreate (tkComparePanel)
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
        #@-node:ekr.20081121105001.1278:finishCreate (tkComparePanel)
        #@+node:ekr.20081121105001.1279:createFrame (tkComparePanel)
        def createFrame (self):

            gui = g.app.gui ; top = self.top

            #@    << create the organizer frames >>
            #@+node:ekr.20081121105001.1280:<< create the organizer frames >>
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
            #@-node:ekr.20081121105001.1280:<< create the organizer frames >>
            #@nl
            #@    << create the browser rows >>
            #@+node:ekr.20081121105001.1281:<< create the browser rows >>
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
            #@-node:ekr.20081121105001.1281:<< create the browser rows >>
            #@nl
            #@    << create the extension row >>
            #@+node:ekr.20081121105001.1282:<< create the extension row >>
            b = Tk.Checkbutton(row4,anchor="w",var=self.limitToExtensionVar,
                text="Limit directory compares to type:")
            b.pack(side="left",padx=4)

            self.extensionEntry = e = Tk.Entry(row4,width=6)
            e.pack(side="left",padx=2)

            b = Tk.Checkbutton(row4,anchor="w",var=self.appendOutputVar,
                text="Append output to output file")
            b.pack(side="left",padx=4)
            #@-node:ekr.20081121105001.1282:<< create the extension row >>
            #@nl
            #@    << create the whitespace options frame >>
            #@+node:ekr.20081121105001.1283:<< create the whitespace options frame >>
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
            #@-node:ekr.20081121105001.1283:<< create the whitespace options frame >>
            #@nl
            #@    << create the print options frame >>
            #@+node:ekr.20081121105001.1284:<< create the print options frame >>
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
            #@-node:ekr.20081121105001.1284:<< create the print options frame >>
            #@nl
            #@    << create the compare buttons >>
            #@+node:ekr.20081121105001.1285:<< create the compare buttons >>
            for text,command in (
                ("Compare files",      self.onCompareFiles),
                ("Compare directories",self.onCompareDirectories) ):

                b = Tk.Button(lower,text=text,command=command,width=18)
                b.pack(side="left",padx=6)
            #@-node:ekr.20081121105001.1285:<< create the compare buttons >>
            #@nl

            gui.center_dialog(top) # Do this _after_ building the dialog!
            self.finishCreate()
            top.protocol("WM_DELETE_WINDOW", self.onClose)
        #@-node:ekr.20081121105001.1279:createFrame (tkComparePanel)
        #@+node:ekr.20081121105001.1286:setIvarsFromWidgets
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
        #@-node:ekr.20081121105001.1286:setIvarsFromWidgets
        #@-node:ekr.20081121105001.1275:Birth...
        #@+node:ekr.20081121105001.1287:bringToFront
        def bringToFront(self):

            self.top.deiconify()
            self.top.lift()
        #@-node:ekr.20081121105001.1287:bringToFront
        #@+node:ekr.20081121105001.1288:browser
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
        #@-node:ekr.20081121105001.1288:browser
        #@+node:ekr.20081121105001.1289:Event handlers...
        #@+node:ekr.20081121105001.1290:onBrowse...
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
        #@-node:ekr.20081121105001.1290:onBrowse...
        #@+node:ekr.20081121105001.1291:onClose
        def onClose (self):

            self.top.withdraw()
        #@-node:ekr.20081121105001.1291:onClose
        #@+node:ekr.20081121105001.1292:onCompare...
        def onCompareDirectories (self):

            self.setIvarsFromWidgets()
            self.compare_directories(self.fileName1,self.fileName2)

        def onCompareFiles (self):

            self.setIvarsFromWidgets()
            self.compare_files(self.fileName1,self.fileName2)
        #@-node:ekr.20081121105001.1292:onCompare...
        #@+node:ekr.20081121105001.1293:onPrintMatchedLines
        def onPrintMatchedLines (self):

            v = self.printMatchesVar.get()
            b = self.printButtons[1]
            state = g.choose(v,"normal","disabled")
            b.configure(state=state)
        #@-node:ekr.20081121105001.1293:onPrintMatchedLines
        #@-node:ekr.20081121105001.1289:Event handlers...
        #@-others
    #@-node:ekr.20081121105001.1274:wxComparePanel class (not ready yet)
    #@+node:ekr.20081121105001.1294:wxGui class
    class wxGui(leoGui.leoGui):

        #@    @+others
        #@+node:ekr.20081121105001.1295:gui birth & death
        #@+node:ekr.20081121105001.1296: wxGui.__init__
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
            #@+node:ekr.20081121105001.1297:nav_buttons declarations
            self.listBoxDialog = wxListBoxDialog
            self.marksDialog = wxMarksDialog
            self.recentSectionsDialog = wxRecentSectionsDialog
            #@-node:ekr.20081121105001.1297:nav_buttons declarations
            #@-others
        #@-node:ekr.20081121105001.1296: wxGui.__init__
        #@+node:ekr.20081121105001.1298:extendGlobals


        def extendGlobals(self):

            #@    @+others
            #@+node:ekr.20081121105001.1299:alert

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
            #@-node:ekr.20081121105001.1299:alert
            #@+node:ekr.20081121105001.1300:Tabs

            def getTab(tabName='Log'):

                app = g.app
                log = app.log
                if app.killed or not log or log.isNull:
                    return

                return log.getTab(tabName)

            g.getTab = getTab

            #@-node:ekr.20081121105001.1300:Tabs
            #@+node:ekr.20081121105001.1301:trace

            # oldtrace = g.trace
            # def trace(*args, **kw):
                # try:
                    # oldtrace(*args, **kw)
                # except :
                    # print 'unicode error in trace'

            # g.trace = trace

            #@-node:ekr.20081121105001.1301:trace
            #@-others



        #@-node:ekr.20081121105001.1298:extendGlobals
        #@+node:ekr.20081121105001.1302:createKeyHandlerClass
        def createKeyHandlerClass (self,c,useGlobalKillbuffer=True,useGlobalRegisters=True):

            return wxKeyHandlerClass(c,useGlobalKillbuffer,useGlobalRegisters)
        #@nonl
        #@-node:ekr.20081121105001.1302:createKeyHandlerClass
        #@+node:ekr.20081121105001.1303:createFocusManagerClass
        def createFocusManagerClass(self,c):

            return wxFocusManagerClass(c)
        #@nonl
        #@-node:ekr.20081121105001.1303:createFocusManagerClass
        #@+node:ekr.20081121105001.1304:createRootWindow
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
        #@-node:ekr.20081121105001.1304:createRootWindow
        #@+node:ekr.20081121105001.1305:createLeoFrame
        def createLeoFrame(self,title):

            """Create a new Leo frame."""

            return wxLeoFrame(title)
        #@nonl
        #@-node:ekr.20081121105001.1305:createLeoFrame
        #@+node:ekr.20081121105001.1306:destroySelf
        def destroySelf(self):

            pass # Nothing more needs to be done once all windows have been destroyed.
        #@nonl
        #@-node:ekr.20081121105001.1306:destroySelf
        #@+node:ekr.20081121105001.1307:finishCreate
        def finishCreate (self):

            pass
            # g.trace('gui',g.callers())
        #@-node:ekr.20081121105001.1307:finishCreate
        #@+node:ekr.20081121105001.1308:killGui
        def killGui(self,exitFlag=True):

            """Destroy a gui and terminate Leo if exitFlag is True."""

            pass # Not ready yet.

        #@-node:ekr.20081121105001.1308:killGui
        #@+node:ekr.20081121105001.1309:recreateRootWindow
        def recreateRootWindow(self):

            """A do-nothing base class to create the hidden root window of a gui

            after a previous gui has terminated with killGui(False)."""

            # g.trace('wx gui')
        #@-node:ekr.20081121105001.1309:recreateRootWindow
        #@+node:ekr.20081121105001.1310:runMainLoop
        def runMainLoop(self):

            """Run wx's main loop."""

            # g.trace("wxGui")
            self.wxApp.MainLoop()
            # g.trace("done")
        #@nonl
        #@-node:ekr.20081121105001.1310:runMainLoop
        #@-node:ekr.20081121105001.1295:gui birth & death
        #@+node:ekr.20081121105001.1311:gui dialogs
        #@+node:ekr.20081121105001.1312:runAboutLeoDialog
        def runAboutLeoDialog(self,c,version,copyright,url,email):

            """Create and run a wxPython About Leo dialog."""

            if  g.app.unitTesting: return

            message = "%s\n\n%s\n\n%s\n\n%s" % (
                version.strip(),copyright.strip(),url.strip(),email.strip())

            message += '\n\nwxLeo version: %s'%__version__

            wx.MessageBox(message,"About Leo",wx.Center,self.root)
        #@-node:ekr.20081121105001.1312:runAboutLeoDialog
        #@+node:ekr.20081121105001.1313:runAskOkDialog
        def runAskOkDialog(self,c,title,message=None,text="Ok"):

            """Create and run a wxPython askOK dialog ."""

            if  g.app.unitTesting:
                return 'ok'
            d = wx.MessageDialog(self.root, message, title, wx.OK)
            d.ShowModal()
            return "ok"
        #@nonl
        #@-node:ekr.20081121105001.1313:runAskOkDialog
        #@+node:ekr.20081121105001.1314:runAskLeoIDDialog
        def runAskLeoIDDialog(self):

            """Create and run a dialog to get g.app.LeoID."""

            if  g.app.unitTesting: return 'ekr'

            ### to do
        #@nonl
        #@-node:ekr.20081121105001.1314:runAskLeoIDDialog
        #@+node:ekr.20081121105001.1315:runAskOkCancelNumberDialog (to do)
        def runAskOkCancelNumberDialog(self,c,title,message):

            """Create and run a wxPython askOkCancelNumber dialog ."""

            if g.app.unitTesting: return 666

            ### to do.
        #@nonl
        #@-node:ekr.20081121105001.1315:runAskOkCancelNumberDialog (to do)
        #@+node:ekr.20081121105001.1316:runAskOkCancelStringDialog (to do)
        def runAskOkCancelStringDialog(self,c,title,message):

            """Create and run a wxPython askOkCancelNumber dialog ."""

            if  g.app.unitTesting: return 'xyzzy'

            # to do
        #@-node:ekr.20081121105001.1316:runAskOkCancelStringDialog (to do)
        #@+node:ekr.20081121105001.1317:runAskYesNoDialog
        def runAskYesNoDialog(self,c,title,message=None):

            """Create and run a wxPython askYesNo dialog."""

            if  g.app.unitTesting: return 'yes'

            d = wx.MessageDialog(self.root,message,"Leo",wx.YES_NO)
            answer = d.ShowModal()

            return g.choose(answer==wx.YES,"yes","no")
        #@nonl
        #@-node:ekr.20081121105001.1317:runAskYesNoDialog
        #@+node:ekr.20081121105001.1318:runAskYesNoCancelDialog
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
        #@-node:ekr.20081121105001.1318:runAskYesNoCancelDialog
        #@+node:ekr.20081121105001.1319:runCompareDialog
        def runCompareDialog (self,c):

            if  g.app.unitTesting: return

            # To do
        #@nonl
        #@-node:ekr.20081121105001.1319:runCompareDialog
        #@+node:ekr.20081121105001.1320:runOpenFileDialog

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
        #@-node:ekr.20081121105001.1320:runOpenFileDialog
        #@+node:ekr.20081121105001.1321:runSaveFileDialog
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
        #@-node:ekr.20081121105001.1321:runSaveFileDialog
        #@+node:ekr.20081121105001.1322:plugins_menu
        #@+others
        #@+node:ekr.20081121105001.1323:runPropertiesDialog
        def runPropertiesDialog(self, title='Properties', data={}, callback=None, buttons=None):
            """Dispay a modal wxPropertiesDialog"""

            dialog = wxPropertiesDialog(title, data, callback, buttons)

            return dialog.result
        #@-node:ekr.20081121105001.1323:runPropertiesDialog
        #@+node:ekr.20081121105001.1324:runScrolledMessageDialog
        def runScrolledMessageDialog(self,title='Message', label= '', msg='', callback=None, buttons=None):
            """Display a modal wxScrolledMessageDialog."""

            dialog = wxScrolledMessageDialog(title, label, msg, callback, buttons)

            return dialog.result
        #@-node:ekr.20081121105001.1324:runScrolledMessageDialog
        #@-others
        #@-node:ekr.20081121105001.1322:plugins_menu
        #@+node:ekr.20081121105001.1325:simulateDialog
        def simulateDialog (self,key,defaultVal=None):

            return defaultVal
        #@nonl
        #@-node:ekr.20081121105001.1325:simulateDialog
        #@+node:ekr.20081121105001.1326:getWildcardList
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
        #@-node:ekr.20081121105001.1326:getWildcardList
        #@-node:ekr.20081121105001.1311:gui dialogs
        #@+node:ekr.20081121105001.1327:gui events
        #@+node:ekr.20081121105001.1328:event_generate
        def event_generate(self,w,kind,*args,**keys):
            '''Generate an event.'''
            return w.event_generate(kind,*args,**keys)
        #@-node:ekr.20081121105001.1328:event_generate
        #@+node:ekr.20081121105001.1329:class leoKeyEvent (wxGui)
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
        #@-node:ekr.20081121105001.1329:class leoKeyEvent (wxGui)
        #@+node:ekr.20081121105001.1330:wxKeyDict
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
        #@-node:ekr.20081121105001.1330:wxKeyDict
        #@+node:ekr.20081121105001.1331:eventChar & eventKeysym & helper
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
        #@+node:ekr.20081121105001.1332:keysymHelper & helpers

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
        #@+node:ekr.20081121105001.1333:getMods
        def getMods (self,event):

            mods = event.GetModifiers()

            alt = event.AltDown()     or mods == wx.MOD_ALT
            cmd = event.CmdDown()     or mods == wx.MOD_CMD
            ctrl = event.ControlDown()or mods == wx.MOD_CONTROL
            meta = event.MetaDown()   or mods == wx.MOD_META
            shift = event.ShiftDown() or mods == wx.MOD_SHIFT

            return alt,cmd,ctrl,meta,shift
        #@-node:ekr.20081121105001.1333:getMods
        #@-node:ekr.20081121105001.1332:keysymHelper & helpers
        #@-node:ekr.20081121105001.1331:eventChar & eventKeysym & helper
        #@+node:ekr.20081121105001.1334:eventWidget
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
        #@-node:ekr.20081121105001.1334:eventWidget
        #@+node:ekr.20081121105001.1335:eventXY
        def eventXY (self,event,c=None):

            if hasattr(event,'x') and hasattr(event,'y'):
                return event.x,event.y
            if hasattr(event,'GetX') and hasattr(event,'GetY'):
                return event.GetX(),event.GetY()
            else:
                return 0,0
        #@-node:ekr.20081121105001.1335:eventXY
        #@-node:ekr.20081121105001.1327:gui events
        #@+node:ekr.20081121105001.1336:gui panels (to do)
        #@+node:ekr.20081121105001.1337:createColorPanel
        def createColorPanel(self,c):

            """Create Color panel."""

            g.trace("not ready yet")
        #@nonl
        #@-node:ekr.20081121105001.1337:createColorPanel
        #@+node:ekr.20081121105001.1338:createComparePanel
        def createComparePanel(self,c):

            """Create Compare panel."""

            g.trace("not ready yet")
        #@nonl
        #@-node:ekr.20081121105001.1338:createComparePanel
        #@+node:ekr.20081121105001.1339:createFindPanel
        def createFindPanel(self):

            """Create a hidden Find panel."""

            return wxFindFrame()
        #@nonl
        #@-node:ekr.20081121105001.1339:createFindPanel
        #@+node:ekr.20081121105001.1340:createFindTab
        def createFindTab (self,c,parentFrame):

            '''Create a wxWidgets find tab in the indicated frame.'''

            frame = c.frame

            if not frame.findTabHandler:
                frame.findTabHandler = wxFindTab(c,parentFrame)

            return frame.findTabHandler
        #@nonl
        #@-node:ekr.20081121105001.1340:createFindTab
        #@+node:ekr.20081121105001.1341:createFontPanel
        def createFontPanel(self,c):

            """Create a Font panel."""

            g.trace("not ready yet")
        #@nonl
        #@-node:ekr.20081121105001.1341:createFontPanel
        #@+node:ekr.20081121105001.1342:createSpellTab
        def createSpellTab (self,c,parentFrame):

            '''Create a wxWidgets spell tab in the indicated frame.'''

            frame = c.frame

            if not frame.spellTabHandler:
                frame.spellTabHandler = wxSpellTab(c,parentFrame)

            return frame.spellTabHandler
        #@-node:ekr.20081121105001.1342:createSpellTab
        #@+node:ekr.20081121105001.1343:destroyLeoFrame (NOT USED)
        def destroyLeoFrame (self,frame):

            frame.Close()
        #@nonl
        #@-node:ekr.20081121105001.1343:destroyLeoFrame (NOT USED)
        #@-node:ekr.20081121105001.1336:gui panels (to do)
        #@+node:ekr.20081121105001.1344:gui utils (must add several)
        #@+node:ekr.20081121105001.1345:Clipboard
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
        #@-node:ekr.20081121105001.1345:Clipboard
        #@+node:ekr.20081121105001.1346:Constants
        # g.es calls gui.color to do the translation,
        # so most code in Leo's core can simply use Tk color names.

        def color (self,color):
            '''Return the gui-specific color corresponding to the Tk color name.'''
            return name2color(color)
        #@-node:ekr.20081121105001.1346:Constants
        #@+node:ekr.20081121105001.1347:Dialog
        #@+node:ekr.20081121105001.1348:bringToFront
        def bringToFront (self,window):

            if window.IsIconized():
                window.Maximize()
            window.Raise()
            window.Show(True)
        #@nonl
        #@-node:ekr.20081121105001.1348:bringToFront
        #@+node:ekr.20081121105001.1349:get_window_info
        def get_window_info(self,window):

            # Get the information about top and the screen.
            x,y = window.GetPosition()
            w,h = window.GetSize()

            return w,h,x,y
        #@nonl
        #@-node:ekr.20081121105001.1349:get_window_info
        #@+node:ekr.20081121105001.1350:center_dialog
        def center_dialog(window):

            window.Center()
        #@nonl
        #@-node:ekr.20081121105001.1350:center_dialog
        #@-node:ekr.20081121105001.1347:Dialog
        #@+node:ekr.20081121105001.1351:Focus (gui)
        def get_focus(self,c):

            return c.frame.body.bodyCtrl.findFocus()

        def set_focus(self,c,w):

            c.frame.setFocus(w)
        #@-node:ekr.20081121105001.1351:Focus (gui)
        #@+node:ekr.20081121105001.1352:Font (wxGui) (to do)
        #@+node:ekr.20081121105001.1353:getFontFromParams
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
        #@-node:ekr.20081121105001.1353:getFontFromParams
        #@-node:ekr.20081121105001.1352:Font (wxGui) (to do)
        #@+node:ekr.20081121105001.1354:Idle time (wxGui)
        #@+node:ekr.20081121105001.1355:setIdleTimeHook
        def setIdleTimeHook (self,idleTimeHookHandler,*args,**keys):

            wx.CallAfter(idleTimeHookHandler, *args, **keys)

        #@-node:ekr.20081121105001.1355:setIdleTimeHook
        #@+node:ekr.20081121105001.1356:setIdleTimeHookAfterDelay
        def setIdleTimeHookAfterDelay (self,idleTimeHookHandler,*args,**keys):

            wx.CallLater(g.app.idleTimeDelay,idleTimeHookHandler, *args, **keys)
        #@nonl
        #@-node:ekr.20081121105001.1356:setIdleTimeHookAfterDelay
        #@+node:ekr.20081121105001.1357:update_idletasks
        def update_idletasks(self, *args, **kw):
            #g.trace(g.callers())
            wx.SafeYield(onlyIfNeeded=True)
        #@nonl
        #@-node:ekr.20081121105001.1357:update_idletasks
        #@-node:ekr.20081121105001.1354:Idle time (wxGui)
        #@+node:ekr.20081121105001.1358:isTextWidget
        def isTextWidget (self,w):

            return isinstance(w, baseTextWidget)

        #@-node:ekr.20081121105001.1358:isTextWidget
        #@+node:ekr.20081121105001.1359:widget_name
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
        #@-node:ekr.20081121105001.1359:widget_name
        #@-node:ekr.20081121105001.1344:gui utils (must add several)
        #@+node:ekr.20081121105001.1360:getImage
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
        #@-node:ekr.20081121105001.1360:getImage
        #@-others
    #@nonl
    #@-node:ekr.20081121105001.1294:wxGui class
    #@+node:ekr.20081121105001.1361:wxKeyHandlerClass (keyHandlerClass)
    class wxKeyHandlerClass (leoKeys.keyHandlerClass):

        '''wxWidgets overrides of base keyHandlerClass.'''

        #@    @+others
        #@+node:ekr.20081121105001.1362:__init__
        def __init__(self,c,useGlobalKillbuffer=False,useGlobalRegisters=False):

            #g.trace('wxKeyHandlerClass',g.callers())

            self.widget = None # Set in finishCreate.

            # Init the base class.
            leoKeys.keyHandlerClass.__init__(self,c,useGlobalKillbuffer,useGlobalRegisters)
        #@-node:ekr.20081121105001.1362:__init__
        #@+node:ekr.20081121105001.1363:finishCreate

        def finishCreate (self):

            k = self ; c = k.c



            leoKeys.keyHandlerClass.finishCreate(self) # Call the base class.

            # In the Tk version, this is done in the editor logic.
            c.frame.body.createBindings(w=c.frame.body.bodyCtrl)

            # k.dumpMasterBindingsDict()

            self.widget = c.frame.minibuffer.ctrl

            self.setLabelGrey()

        #@-node:ekr.20081121105001.1363:finishCreate
        #@+node:ekr.20081121105001.1364:propagateKeyEvent
        def propagateKeyEvent (self,event):
            g.trace()
            if event and event.actualEvent:
                event.actualEvent.Skip()
        #@nonl
        #@-node:ekr.20081121105001.1364:propagateKeyEvent
        #@+node:ekr.20081121105001.1365:fullCommand

        def fullCommand(self, *args, **kw):
            #g.trace('overidden')
            self.c.minibufferWantsFocus()
            return leoKeys.keyHandlerClass.fullCommand(self, *args, **kw)
        #@nonl
        #@-node:ekr.20081121105001.1365:fullCommand
        #@+node:ekr.20081121105001.1366:masterCommand
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
            self.c.redraw()
            return result

        #@-node:ekr.20081121105001.1366:masterCommand
        #@+node:ekr.20081121105001.1367:universalDispatcher

        def universalDispatcher(self, *args, **kw):
            #g.trace('overidden')
            self.c.minibufferWantsFocus()
            return leoKeys.keyHandlerClass.universalDispatcher(self, *args, **kw)
        #@nonl
        #@-node:ekr.20081121105001.1367:universalDispatcher
        #@+node:ekr.20081121105001.1368:handleDefaultChar
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
        #@-node:ekr.20081121105001.1368:handleDefaultChar
        #@+node:ekr.20081121105001.1369:setLabel
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
        #@-node:ekr.20081121105001.1369:setLabel
        #@+node:ekr.20081121105001.1370:setLabelGrey
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
        #@-node:ekr.20081121105001.1370:setLabelGrey
        #@-others
    #@nonl
    #@-node:ekr.20081121105001.1361:wxKeyHandlerClass (keyHandlerClass)
    #@+node:ekr.20081121105001.1371:wxFocusManagerClass
    #@<< _focusHistory class >>
    #@+node:ekr.20081121105001.1372:<<_focusHistory class>>

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

    #@-node:ekr.20081121105001.1372:<<_focusHistory class>>
    #@nl

    class wxFocusManagerClass(object):

        #@    @+others
        #@+node:ekr.20081121105001.1373:__init__
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



        #@-node:ekr.20081121105001.1373:__init__
        #@+node:ekr.20081121105001.1374:gotFocus

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
        #@-node:ekr.20081121105001.1374:gotFocus
        #@+node:ekr.20081121105001.1375:lostFocus

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


        #@-node:ekr.20081121105001.1375:lostFocus
        #@+node:ekr.20081121105001.1376:setFocus
        def setFocus(self, o):
             o.SetFocus()

        SetFocus = setFocus
        #@-node:ekr.20081121105001.1376:setFocus
        #@+node:ekr.20081121105001.1377:chooseBodyOfOutline
        def chooseBodyOrOutline(self):
            #g.trace()
            c = self.c
            c.set_focus(g.choose(
                self.outline_pane_has_initial_focus,
                c.frame.tree.treeCtrl, c.frame.body.bodyCtrl
            ))
        #@nonl
        #@-node:ekr.20081121105001.1377:chooseBodyOfOutline
        #@+node:ekr.20081121105001.1378:lastFocus
        def lastFocus(self):

            o = self.log.pop()
            self.setFocus(o)
        #@-node:ekr.20081121105001.1378:lastFocus
        #@-others


    #@-node:ekr.20081121105001.1371:wxFocusManagerClass
    #@+node:ekr.20081121105001.1379:wxLeoApp class
    class wxLeoApp (wx.App):
        #@    @+others
        #@+node:ekr.20081121105001.1380:OnInit  (wxLeoApp)
        def OnInit(self):

            self.SetAppName("Leo")

            wx.InitAllImageHandlers()

            #globals icons, plusBoxIcon, minusBoxIcon, appIcon
            self.loadIcons()

            #self.Bind(wx.EVT_CHAR, lambda event, type='app':onRogueChar(event, type))



            return True
        #@-node:ekr.20081121105001.1380:OnInit  (wxLeoApp)
        #@+node:ekr.20081121105001.1381:loadIcons


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
        #@-node:ekr.20081121105001.1381:loadIcons
        #@+node:ekr.20081121105001.1382:OnExit
        def OnExit(self):

            return True
        #@-node:ekr.20081121105001.1382:OnExit
        #@-others
    #@-node:ekr.20081121105001.1379:wxLeoApp class
    #@+node:ekr.20081121105001.1383:wxLeoBody class (leoBody)
    class wxLeoBody (leoFrame.leoBody):

        """A class to create a wxPython body pane."""

        #@    @+others
        #@+node:ekr.20081121105001.1384:Birth & death (wxLeoBody)
        #@+node:ekr.20081121105001.1385:wxBody.__init__
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
        #@-node:ekr.20081121105001.1385:wxBody.__init__
        #@+node:ekr.20081121105001.1386:wxBody.createControl
        def createControl (self,frame,parentFrame):

            w = g.app.gui.bodyTextWidget(
                self,
                parentFrame,
                name='body' # Must be body for k.masterKeyHandler.
            )

            #w.widget.Bind(wx.EVT_LEFT_DOWN, self.onClick)


            return w
        #@-node:ekr.20081121105001.1386:wxBody.createControl
        #@+node:ekr.20081121105001.1387:wxBody.createBindings NOT USED AT PRESENT
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
        #@-node:ekr.20081121105001.1387:wxBody.createBindings NOT USED AT PRESENT
        #@+node:ekr.20081121105001.1388:wxBody.setEditorColors
        def setEditorColors (self,bg,fg):
            pass
        #@nonl
        #@-node:ekr.20081121105001.1388:wxBody.setEditorColors
        #@-node:ekr.20081121105001.1384:Birth & death (wxLeoBody)
        #@+node:ekr.20081121105001.1389:Tk wrappers (wxBody)

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
        #@-node:ekr.20081121105001.1389:Tk wrappers (wxBody)
        #@+node:ekr.20081121105001.1390:onBodyChanged (wxBody: calls leoBody.onBodyChanged)
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

        #@-node:ekr.20081121105001.1390:onBodyChanged (wxBody: calls leoBody.onBodyChanged)
        #@+node:ekr.20081121105001.1391:wxBody.forceFullRecolor
        def forceFullRecolor (self):

            self.forceFullRecolorFlag = True
        #@nonl
        #@-node:ekr.20081121105001.1391:wxBody.forceFullRecolor
        #@+node:ekr.20081121105001.1392:select/unselectLabel
        def unselectLabel (self,w):
            return


        def selectLabel (self,w):
            return
        #@-node:ekr.20081121105001.1392:select/unselectLabel
        #@-others
    #@nonl
    #@-node:ekr.20081121105001.1383:wxLeoBody class (leoBody)
    #@+node:ekr.20081121105001.1393:-- Object --
    #@+node:ekr.20081121105001.1394:leoObject class
    class leoObject(object):
        """A base class for all leo objects."""

        #@    @+others
        #@+node:ekr.20081121105001.1395:__init__
        def __init__(self, c):

            object.__init__(self)
            self.c = c

            #print 'Created leo object for ', self
        #@-node:ekr.20081121105001.1395:__init__
        #@+node:ekr.20081121105001.1396:__str__
        def __str__(self):
            return '%s [%s]'%(self.__class__.__name__, id(self))

        __repr__ = __str__
        #@nonl
        #@-node:ekr.20081121105001.1396:__str__
        #@-others
    #@-node:ekr.20081121105001.1394:leoObject class
    #@+node:ekr.20081121105001.1397:wxLeoObject class
    class wxLeoObject(object):
        """A base class mixin for all wxPython specific objects.

        """

        #@    @+others
        #@+node:ekr.20081121105001.1398:def __init__
        def __init__(self):

            object.__init__(self)
            #print 'created', self

        #@-node:ekr.20081121105001.1398:def __init__
        #@+node:ekr.20081121105001.1399:def __str__
        def __str__(self):
            return 'wxLeoObject: %s [%s]'%(self.__class__.__name__, id(self))

        __repr__ = __str__
        #@-node:ekr.20081121105001.1399:def __str__
        #@-others
    #@-node:ekr.20081121105001.1397:wxLeoObject class
    #@-node:ekr.20081121105001.1393:-- Object --
    #@+node:ekr.20081121105001.1400:-- Notebook --
    #@+node:ekr.20081121105001.1401:leoNotebook
    class leoNotebook(leoObject):

        #@    @+others
        #@+node:ekr.20081121105001.1402:__init__
        def __init__(self, c):

            leoObject.__init__(self, c)

            self.__tabs = []
        #@-node:ekr.20081121105001.1402:__init__
        #@+node:ekr.20081121105001.1403:appendTab
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

        #@-node:ekr.20081121105001.1403:appendTab
        #@+node:ekr.20081121105001.1404:Tabs Property
        def getTabs(self):
            return self.__tabs[:]

        tabs = property(getTabs)
        #@-node:ekr.20081121105001.1404:Tabs Property
        #@-others


    #@-node:ekr.20081121105001.1401:leoNotebook
    #@+node:ekr.20081121105001.1405:wxLeoNotebook class
    class wxLeoNotebook(wx.Notebook, wxLeoObject, leoNotebook):
        """A wxPython specific implementation of a leoNotebook."""
        #@    @+others
        #@+node:ekr.20081121105001.1406:__init__
        def __init__(self, c, parent, showTabs=False):


            leoNotebook.__init__(self, c)
            wxLeoObject.__init__(self)

            wx.Notebook.__init__(self, parent)


            #g.trace( self,' >> ', parent)

            self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onPageChanged)

            self.Bind(wx.EVT_SIZE, self.onSize)











        #@-node:ekr.20081121105001.1406:__init__
        #@+node:ekr.20081121105001.1407:__str__
        def __str__(self):
            return '%s [%s]'%(self.__class__.__name__, id(self))

        __repr__ = __str__
        #@nonl
        #@-node:ekr.20081121105001.1407:__str__
        #@+node:ekr.20081121105001.1408:onSize
        def onSize(self, event):
            """Handle EVT_SIZE for wx.Notebook."""

            #g.trace(myclass(self), self.GetClientSize())

            page = self.GetCurrentPage()

            if page:
                page.SetSize(self.GetClientSize())


            event.Skip()

        #@-node:ekr.20081121105001.1408:onSize
        #@+node:ekr.20081121105001.1409:onPageChanged
        def onPageChanged(self, event):
            """Handle EVT_NOTEBOOK_PAGE_CHANGED for wx.Notebook."""

            #g.trace()

            sel = event.GetSelection()

            if sel > -1:
                page = self.GetPage(sel)
                page.SetSize(self.GetClientSize())

            event.Skip()
        #@-node:ekr.20081121105001.1409:onPageChanged
        #@+node:ekr.20081121105001.1410:tabToRawIndex
        def tabToRawIndex(self, tab):
            """The index of the page in the native notebook."""

            if not tab.page:
                return None

            for i in range(self.GetPageCount()):
                if self.GetPage(i) is tab.page:
                    return i

            return None

        #@-node:ekr.20081121105001.1410:tabToRawIndex
        #@+node:ekr.20081121105001.1411:appendTab
        def appendTab(self, tab, select=False):

            assert isinstance(tab, wxLeoTab)

            n = super(wxLeoNotebook, self).appendTab(tab)

            idx = self.tabToRawIndex(tab)

            if idx is None:
                self.AddPage(tab.page, tab.tabName, select)
            else:
                g.trace('page can\'t be inserted twice')


        #@-node:ekr.20081121105001.1411:appendTab
        #@+node:ekr.20081121105001.1412:setPageText
        def setPageText(self, tab, text):
            """Set the text on the notebook tab.

            Gui specific method for internal use only.

            """
            #g.trace(text, tab, self)

            idx = self.tabToRawIndex(tab)
            #g.trace(idx, self)

            if idx is not None:
                self.SetPageText(idx, text)
        #@-node:ekr.20081121105001.1412:setPageText
        #@+node:ekr.20081121105001.1413:appendPage
        def appendPage(self, tabName, page, select=False):
            """Append a page that is not yet contained in a Tab.

            A new Tab is created to contain the page.

            Returns: The newly created Tab object.

            """

            tab = wxLeoTab(tabName, page)
            self.appendTab(tab, select)
            return tab
        #@-node:ekr.20081121105001.1413:appendPage
        #@-others
    #@nonl
    #@-node:ekr.20081121105001.1405:wxLeoNotebook class
    #@-node:ekr.20081121105001.1400:-- Notebook --
    #@+node:ekr.20081121105001.1414:-- Tab --
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
    #@+node:ekr.20081121105001.1415:leoTab class
    class leoTab(leoObject):

        #@    @+others
        #@+node:ekr.20081121105001.1416:__init__

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
        #@-node:ekr.20081121105001.1416:__init__
        #@+node:ekr.20081121105001.1417:TabName property
        def getTabName(self):
            return self.__tabName

        def setTabName(self, tabName):
            self.__tabName = tabName

        tabName = property(
            lambda self: self.getTabName(),
            lambda self, name: self.setTabName(name),
        )
        #@-node:ekr.20081121105001.1417:TabName property
        #@+node:ekr.20081121105001.1418:Notebook property
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

        #@-node:ekr.20081121105001.1418:Notebook property
        #@+node:ekr.20081121105001.1419:Page property
        def getPage(self):
            return self.__page

        def setPage(self, page):
            self.__page = page

        page = property(
            lambda self: self.getPage(),
            lambda self, page: self.setPage(page),
        )
        #@-node:ekr.20081121105001.1419:Page property
        #@-others
    #@-node:ekr.20081121105001.1415:leoTab class
    #@+node:ekr.20081121105001.1420:wxLeoTab class
    class wxLeoTab(wxLeoObject, leoTab):

        """wxPython implementation of leoTab."""
        #@    @+others
        #@+node:ekr.20081121105001.1421:__init__
        def __init__(self, c, tabName=None, page=None, nb=None):

            leoTab.__init__(self, c, tabName, page, nb)

            page.leoParent = self
        #@-node:ekr.20081121105001.1421:__init__
        #@+node:ekr.20081121105001.1422:TabName property
        def setTabName(self, tabName):

            super(wxLeoTab, self).setTabName(tabName)

            if self.nb:
                self.nb.setPageText(self, tabName)

            #g.trace(tabName, self)
        #@-node:ekr.20081121105001.1422:TabName property
        #@+node:ekr.20081121105001.1423:Notebook property
        def setNotebook(self, nb):

            assert nb is None or isinstance(nb, wxLeoNotebook)
            #g.trace('\n\t', self )

            super(wxLeoTab, self).setNotebook(nb)

        #@-node:ekr.20081121105001.1423:Notebook property
        #@+node:ekr.20081121105001.1424:Page property

        def setPage(self, page, init=False):

            #g.trace(page)
            assert page is None or isinstance(page, wx.Window)

            super(wxLeoTab, self).setPage(page)

            #g.trace(page, '\n\t', self)






        #@-node:ekr.20081121105001.1424:Page property
        #@-others
    #@-node:ekr.20081121105001.1420:wxLeoTab class
    #@-node:ekr.20081121105001.1414:-- Tab --
    #@+node:ekr.20081121105001.1425:-- Notebook Panel --
    #@+node:ekr.20081121105001.1426:leoNotebookPanel class
    class leoNotebookPanel(leoObject):
        """A class to manage a leoNotebook and any helper windows surrounding it.

        This class will contain methods to add and remove windows arround a
        central notebook.

        These helper windows might be toolbars, log windows ...

        This is a mixin class for the gui class which will provide the physical,
        gui specific, representation.

        """

        #@    @+others
        #@+node:ekr.20081121105001.1427:__init__
        def __init__(self, c):

            leoObject.__init__(self, c)
        #@-node:ekr.20081121105001.1427:__init__
        #@-others


    #@-node:ekr.20081121105001.1426:leoNotebookPanel class
    #@+node:ekr.20081121105001.1428:wxLeoNotebookPanel class

    class wxLeoNotebookPanel(wx.Panel, wxLeoObject, leoNotebookPanel ):
        """wxPython implementation of a leoNotebookPanel."""

        #@    @+others
        #@+node:ekr.20081121105001.1429:__init__
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


        #@-node:ekr.20081121105001.1429:__init__
        #@+node:ekr.20081121105001.1430:onSize
        def onSize(self, event):
            """Handle EVT_SIZE for wx.Panel."""

            #g.trace(myclass(self), self.GetClientSize())

            event.Skip()
        #@-node:ekr.20081121105001.1430:onSize
        #@-others




    #@-node:ekr.20081121105001.1428:wxLeoNotebookPanel class
    #@-node:ekr.20081121105001.1425:-- Notebook Panel --
    #@+node:ekr.20081121105001.1431:wxLeoFrame class (leoFrame)
    class wxLeoFrame(leoFrame.leoFrame):

        """A class to create a wxPython from for the main Leo window."""

        #@    @+others
        #@+node:ekr.20081121105001.1432:Birth & death (wxLeoFrame)
        #@+node:ekr.20081121105001.1433:__init__ (wxLeoFrame)
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


        #@-node:ekr.20081121105001.1433:__init__ (wxLeoFrame)
        #@+node:ekr.20081121105001.1434:__repr__
        def __repr__ (self):

            return "wxLeoFrame: " + self.title
        #@nonl
        #@-node:ekr.20081121105001.1434:__repr__
        #@+node:ekr.20081121105001.1435:setStatusLine

        def setStatusLine(self, s, **keys):
            self.statusLine and self.statusLine.put(s, **keys)
        #@nonl
        #@-node:ekr.20081121105001.1435:setStatusLine
        #@+node:ekr.20081121105001.1436:finishCreate (wxLeoFrame)

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
            #@+node:ekr.20081121105001.1437:<< create and add status area >>

            self.statusLine = self.createStatusLine()

            sizer = self.statusLine.finishCreate(top)
            box.Add(sizer, 0, wx.EXPAND | wx.TOP | wx.RIGHT, 3)
            #@nonl
            #@-node:ekr.20081121105001.1437:<< create and add status area >>
            #@nl
            #@    << create and add minibuffer area >>
            #@+node:ekr.20081121105001.1438:<< create and add minibuffer area >>

            self.minibuffer = self.createMinibuffer()

            sizer = self.minibuffer.finishCreate(top)
            box.Add(sizer, 0, wx.EXPAND | wx.TOP | wx.RIGHT, 3)
            #@-node:ekr.20081121105001.1438:<< create and add minibuffer area >>
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




        #@+node:ekr.20081121105001.1439:createMinibuffer

        def createMinibuffer (self):
            if not self.minibuffer:
                self.minibuffer  = self.minibufferClass(self.c)
            return self.minibuffer
        #@nonl
        #@-node:ekr.20081121105001.1439:createMinibuffer
        #@+node:ekr.20081121105001.1440:createFirstTreeNode
        def createFirstTreeNode (self):

            c = self.c

            t = leoNodes.tnode()
            v = leoNodes.vnode(context=c,t=t)
            p = leoNodes.position(v)
            v.initHeadString("NewHeadline")
            p.moveToRoot(oldRoot=None)
            c.setRootPosition(p) # New in 4.4.2.

        #@-node:ekr.20081121105001.1440:createFirstTreeNode
        #@+node:ekr.20081121105001.1441:setWindowIcon
        def setWindowIcon(self):

            path = os.path.join(g.app.loadDir,"..","Icons","LeoApp16.ico")
            icon = wx.Icon(path,wx.BITMAP_TYPE_ICO,16,16)
            self.top.SetIcon(icon)
        #@-node:ekr.20081121105001.1441:setWindowIcon
        #@-node:ekr.20081121105001.1436:finishCreate (wxLeoFrame)
        #@+node:ekr.20081121105001.1442:createSplitters
        def createSplitters(self, parent=None, style=wx.CLIP_CHILDREN|wx.SP_LIVE_UPDATE|wx.SP_3D):

            parent = parent or self.hiddenWindow

            return (
                wx.SplitterWindow(parent, style=style),
                wx.SplitterWindow(parent, style=style)
            )
        #@-node:ekr.20081121105001.1442:createSplitters
        #@+node:ekr.20081121105001.1443:setupSplitters
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
        #@-node:ekr.20081121105001.1443:setupSplitters
        #@+node:ekr.20081121105001.1444:initialRatios
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
        #@-node:ekr.20081121105001.1444:initialRatios
        #@+node:ekr.20081121105001.1445:injectCallbacks
        # ??? whats the point of this?

        def injectCallbacks(self):

            import leo.core.leoNodes as leoNodes

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
        #@-node:ekr.20081121105001.1445:injectCallbacks
        #@+node:ekr.20081121105001.1446:signOnWithVersion
        def signOnWithVersion (self):

            c = self.c
            color = c.config.getColor("log_error_color")
            signon = c.getSignOnLine()
            n1,n2,n3,junk,junk=sys.version_info

            g.es("Leo Log Window...",color=color)
            g.es(signon)
            g.es("Python %d.%d.%d wxWindows %s" % (n1,n2,n3,wx.VERSION_STRING))
            g.es('\nwxLeo version: %s\n\n'%__version__)


        #@-node:ekr.20081121105001.1446:signOnWithVersion
        #@+node:ekr.20081121105001.1447:setMinibufferBindings
        def setMinibufferBindings(self):

            pass

            # g.trace('to do')
        #@nonl
        #@-node:ekr.20081121105001.1447:setMinibufferBindings
        #@+node:ekr.20081121105001.1448:destroySelf
        def destroySelf(self):

            self.killed = True
            self.top.Destroy()
        #@nonl
        #@-node:ekr.20081121105001.1448:destroySelf
        #@-node:ekr.20081121105001.1432:Birth & death (wxLeoFrame)
        #@+node:ekr.20081121105001.1449:-- Panel Creation Factories --
        #@+node:ekr.20081121105001.1450:createTreePanel
        def createTreePanel(self, parent=None):

            parent = parent or self.hiddenWindow

            return wxLeoTree(self.c, parent)
        #@-node:ekr.20081121105001.1450:createTreePanel
        #@+node:ekr.20081121105001.1451:createBodyPanel
        def createBodyPanel(self, parent=None):

            parent = parent or self.hiddenWindow

            return wxLeoBody(self.c, parent)
        #@-node:ekr.20081121105001.1451:createBodyPanel
        #@+node:ekr.20081121105001.1452:createLogPanel
        def createLogPanel(self, parent=None):

            parent = parent or self.hiddenWindow

            return wxLeoNotebookPanel(self.c, parent)
        #@-node:ekr.20081121105001.1452:createLogPanel
        #@-node:ekr.20081121105001.1449:-- Panel Creation Factories --
        #@+node:ekr.20081121105001.1453:event handlers
        #@+node:ekr.20081121105001.1454:setEventHandlers
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
        #@-node:ekr.20081121105001.1454:setEventHandlers
        #@+node:ekr.20081121105001.1455:onLoseFocus
        def onLoseFocus(self, event):
            return self.c.focusManager.lostFocus(self, event)

        #@-node:ekr.20081121105001.1455:onLoseFocus
        #@+node:ekr.20081121105001.1456:onGainFocus
        def onGainFocus(self, event):
            return self.c.focusManager.gotFocus(self, event)

        #@-node:ekr.20081121105001.1456:onGainFocus
        #@+node:ekr.20081121105001.1457:onActivate & OnSetFocus
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
        #@-node:ekr.20081121105001.1457:onActivate & OnSetFocus
        #@+node:ekr.20081121105001.1458:onCloseLeoFrame
        def onCloseLeoFrame(self,event):

            frame = self

            # The g.app class does all the hard work now.
            if not g.app.closeLeoWindow(frame):
                if event.CanVeto():
                    event.Veto()
        #@nonl
        #@-node:ekr.20081121105001.1458:onCloseLeoFrame
        #@-node:ekr.20081121105001.1453:event handlers
        #@+node:ekr.20081121105001.1459:wxFrame dummy routines: (to do: minor)
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
        #@-node:ekr.20081121105001.1459:wxFrame dummy routines: (to do: minor)
        #@+node:ekr.20081121105001.1460:Externally visible routines...
        #@+node:ekr.20081121105001.1461:deiconify
        def deiconify (self):

            self.top.Iconize(False)
        #@nonl
        #@-node:ekr.20081121105001.1461:deiconify
        #@+node:ekr.20081121105001.1462:getTitle
        def getTitle (self):

            return self.title
        #@-node:ekr.20081121105001.1462:getTitle
        #@+node:ekr.20081121105001.1463:setTitle
        def setTitle (self,title):

            self.title = title
            self.top.SetTitle(title) # Call the wx code.
        #@nonl
        #@-node:ekr.20081121105001.1463:setTitle
        #@-node:ekr.20081121105001.1460:Externally visible routines...
        #@+node:ekr.20081121105001.1464:Gui-dependent commands (to do)
        #@+node:ekr.20081121105001.1465:setFocus (wxFrame)
        def setFocus (self, w):
            self.c.focusManager.setFocus(w)


        SetFocus = setFocus
        #@nonl
        #@-node:ekr.20081121105001.1465:setFocus (wxFrame)
        #@+node:ekr.20081121105001.1466:Minibuffer commands... (wxFrame)
        #@+node:ekr.20081121105001.1467:contractPane
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
        #@-node:ekr.20081121105001.1467:contractPane
        #@+node:ekr.20081121105001.1468:expandPane
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
        #@-node:ekr.20081121105001.1468:expandPane
        #@+node:ekr.20081121105001.1469:fullyExpandPane
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
        #@-node:ekr.20081121105001.1469:fullyExpandPane
        #@+node:ekr.20081121105001.1470:hidePane
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
        #@-node:ekr.20081121105001.1470:hidePane
        #@+node:ekr.20081121105001.1471:expand/contract/hide...Pane
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
        #@-node:ekr.20081121105001.1471:expand/contract/hide...Pane
        #@+node:ekr.20081121105001.1472:fullyExpand/hide...Pane




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
        #@-node:ekr.20081121105001.1472:fullyExpand/hide...Pane
        #@-node:ekr.20081121105001.1466:Minibuffer commands... (wxFrame)
        #@+node:ekr.20081121105001.1473:Window Menu
        #@+node:ekr.20081121105001.1474:cascade
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
        #@-node:ekr.20081121105001.1474:cascade
        #@+node:ekr.20081121105001.1475:equalSizedPanes
        def equalSizedPanes(self,event=None):

            g.es("equalSizedPanes not ready yet")
            return

            frame = self
            frame.resizePanesToRatio(0.5,frame.secondary_ratio)
        #@-node:ekr.20081121105001.1475:equalSizedPanes
        #@+node:ekr.20081121105001.1476:hideLogWindow
        def hideLogWindow (self,event=None):

            g.es("hideLogWindow not ready yet")
            return

            frame = self
            frame.divideLeoSplitter2(0.99, not frame.splitVerticalFlag)
        #@nonl
        #@-node:ekr.20081121105001.1476:hideLogWindow
        #@+node:ekr.20081121105001.1477:minimizeAll
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
        #@-node:ekr.20081121105001.1477:minimizeAll
        #@+node:ekr.20081121105001.1478:toggleActivePane
        def toggleActivePane(self,event=None): # wxFrame.

            w = self.focusWidget or self.body.bodyCtrl

            w = g.choose(w == self.bodyCtrl,self.tree.treeCtrl,self.bodyCtrl)

            w.SetFocus()
            self.focusWidget = w
        #@nonl
        #@-node:ekr.20081121105001.1478:toggleActivePane
        #@+node:ekr.20081121105001.1479:toggleSplitDirection
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
        #@-node:ekr.20081121105001.1479:toggleSplitDirection
        #@-node:ekr.20081121105001.1473:Window Menu
        #@+node:ekr.20081121105001.1480:Help Menu...
        #@+node:ekr.20081121105001.1481:leoHelp
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
        #@+node:ekr.20081121105001.1482:showProgressBar
        def showProgressBar (self,count,size,total):

            # g.trace("count,size,total:" + `count` + "," + `size` + "," + `total`)
            if self.scale == None:
                #@        << create the scale widget >>
                #@+node:ekr.20081121105001.1483:<< create the scale widget >>
                top = Tk.Toplevel()
                top.title("Download progress")
                self.scale = scale = Tk.Scale(top,state="normal",orient="horizontal",from_=0,to=total)
                scale.pack()
                top.lift()
                #@nonl
                #@-node:ekr.20081121105001.1483:<< create the scale widget >>
                #@nl
            self.scale.set(count*size)
            self.scale.update_idletasks()
        #@-node:ekr.20081121105001.1482:showProgressBar
        #@-node:ekr.20081121105001.1481:leoHelp
        #@-node:ekr.20081121105001.1480:Help Menu...
        #@-node:ekr.20081121105001.1464:Gui-dependent commands (to do)
        #@+node:ekr.20081121105001.1484:updateAllMenus (wxFrame)
        def updateAllMenus(self,event):

            """Called whenever any menu is pulled down."""

            # We define this routine to strip off the event param.
            #g.trace(g.callers())



            self.menu.updateAllMenus()
            event.Skip()
        #@-node:ekr.20081121105001.1484:updateAllMenus (wxFrame)
        #@-others
    #@nonl
    #@-node:ekr.20081121105001.1431:wxLeoFrame class (leoFrame)
    #@+node:ekr.20081121105001.1485:wxMenu
    class wxMenu(wx.Menu, wxLeoObject, leoObject):

        def __init__(self, c ):

            leoObject.__init__(self, c)
            wxLeoObject.__init__(self)
            wx.Menu.__init__(self)

            self.Bind(wx.EVT_CHAR, self.onChar)


        def onChar(self):
            print ('menu caught a key!')
            onGlobalChar(self, event)


    #@-node:ekr.20081121105001.1485:wxMenu
    #@+node:ekr.20081121105001.1486:wxLeoMenu class (leoMenu)
    class wxLeoMenu (leoMenu.leoMenu):

        #@    @+others
        #@+node:ekr.20081121105001.1487:  wxLeoMenu.__init__
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
        #@-node:ekr.20081121105001.1487:  wxLeoMenu.__init__
        #@+node:ekr.20081121105001.1488:Accelerators
        #@+at
        # Accelerators are NOT SHOWN when the user opens the menu with the
        # mouse!
        # This is a wx bug.
        #@-at
        #@nonl
        #@+node:ekr.20081121105001.1489:createAccelLabel
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
        #@-node:ekr.20081121105001.1489:createAccelLabel
        #@+node:ekr.20081121105001.1490:createAccelData (not needed)
        def createAccelData (self,menu,ch,accel,id,label):

            d = self.acceleratorDict
            aList = d.get(menu,[])
            data = ch,accel,id,label
            aList.append(data)
            d [menu] = aList
        #@-node:ekr.20081121105001.1490:createAccelData (not needed)
        #@+node:ekr.20081121105001.1491:createAcceleratorTables (not needed)
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
        #@-node:ekr.20081121105001.1491:createAcceleratorTables (not needed)
        #@-node:ekr.20081121105001.1488:Accelerators
        #@+node:ekr.20081121105001.1492:Menu methods (Tk names)
        #@+node:ekr.20081121105001.1493:Not called
        def bind (self,bind_shortcut,callback):

            g.trace(bind_shortcut,callback)

        def delete (self,menu,readItemName):

            g.trace(menu,readItemName)

        def destroy (self,menu):

            g.trace(menu)
        #@-node:ekr.20081121105001.1493:Not called
        #@+node:ekr.20081121105001.1494:add_cascade
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

        #@-node:ekr.20081121105001.1494:add_cascade
        #@+node:ekr.20081121105001.1495:add_command
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

        #@-node:ekr.20081121105001.1495:add_command
        #@+node:ekr.20081121105001.1496:add_separator
        def add_separator(self,menu):

            if menu:
                menu.AppendSeparator()
            else:
                g.trace("null menu")
        #@nonl
        #@-node:ekr.20081121105001.1496:add_separator
        #@+node:ekr.20081121105001.1497:delete_range

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

        #@-node:ekr.20081121105001.1497:delete_range
        #@+node:ekr.20081121105001.1498:index & invoke
        # It appears wxWidgets can't invoke a menu programmatically.
        # The workaround is to change the unit test.

        if 0:
            def index (self,name):
                '''Return the menu item whose name is given.'''

            def invoke (self,i):
                '''Invoke the menu whose index is i'''
        #@-node:ekr.20081121105001.1498:index & invoke
        #@+node:ekr.20081121105001.1499:insert
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

        #@-node:ekr.20081121105001.1499:insert
        #@+node:ekr.20081121105001.1500:insert_cascade
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
        #@-node:ekr.20081121105001.1500:insert_cascade
        #@+node:ekr.20081121105001.1501:new_menu
        def new_menu(self,parent,tearoff=0):
            return wxMenu(self.c)
        #@-node:ekr.20081121105001.1501:new_menu
        #@-node:ekr.20081121105001.1492:Menu methods (Tk names)
        #@+node:ekr.20081121105001.1502:Menu methods (non-Tk names)
        #@+node:ekr.20081121105001.1503:createMenuBar
        def createMenuBar(self,frame):

            self.menuBar = menuBar = wx.MenuBar()

            self.createMenusFromTables()

            self.createAcceleratorTables()

            frame.top.SetMenuBar(menuBar)


            # menuBar.SetAcceleratorTable(wx.NullAcceleratorTable)
        #@-node:ekr.20081121105001.1503:createMenuBar
        #@+node:ekr.20081121105001.1504:createOpenWithMenuFromTable & helper
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
        #@+node:ekr.20081121105001.1505:createOpenWithMenuItemsFromTable
        def createOpenWithMenuItemsFromTable (self,menu,table):

            '''Create an entry in the Open with Menu from the table.

            Each entry should be a sequence with 2 or 3 elements.'''

            c = self.c ; k = c.k

            if g.app.unitTesting: return

            for data in table:
                #@        << get label, accelerator & command or continue >>
                #@+node:ekr.20081121105001.1506:<< get label, accelerator & command or continue >>
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
                #@-node:ekr.20081121105001.1506:<< get label, accelerator & command or continue >>
                #@nl
                # g.trace(label,accelerator)
                realLabel = self.getRealMenuName(label)
                underline=realLabel.find("&")
                realLabel = realLabel.replace("&","")
                callback = self.defineOpenWithMenuCallback(openWithData)

                self.add_command(menu,label=realLabel,
                    accelerator=accelerator or '',
                    command=callback,underline=underline)
        #@-node:ekr.20081121105001.1505:createOpenWithMenuItemsFromTable
        #@-node:ekr.20081121105001.1504:createOpenWithMenuFromTable & helper
        #@+node:ekr.20081121105001.1507:defineMenuCallback
        def defineMenuCallback(self,command,name):

            # The first parameter must be event, and it must default to None.
            def callback(event=None,self=self,command=command,label=name):
                self.c.doCommand(command,label,event)

            return callback
        #@nonl
        #@-node:ekr.20081121105001.1507:defineMenuCallback
        #@+node:ekr.20081121105001.1508:defineOpenWithMenuCallback
        def defineOpenWithMenuCallback (self,command):

            # The first parameter must be event, and it must default to None.
            def wxOpenWithMenuCallback(event=None,command=command):
                try: self.c.openWith(data=command)
                except: print traceback.print_exc()

            return wxOpenWithMenuCallback
        #@-node:ekr.20081121105001.1508:defineOpenWithMenuCallback
        #@+node:ekr.20081121105001.1509:createOpenWithMenu
        def createOpenWithMenu(self,parent,label,index,amp_index):

            '''Create a submenu.'''
            menu = self.new_menu(parent)
            self.insert_cascade(parent, index, label=label,menu=menu,underline=amp_index)
            return menu
        #@-node:ekr.20081121105001.1509:createOpenWithMenu
        #@+node:ekr.20081121105001.1510:disableMenu
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
        #@-node:ekr.20081121105001.1510:disableMenu
        #@+node:ekr.20081121105001.1511:enableMenu
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
        #@-node:ekr.20081121105001.1511:enableMenu
        #@+node:ekr.20081121105001.1512:setMenuLabel
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
        #@-node:ekr.20081121105001.1512:setMenuLabel
        #@-node:ekr.20081121105001.1502:Menu methods (non-Tk names)
        #@-others
    #@nonl
    #@-node:ekr.20081121105001.1486:wxLeoMenu class (leoMenu)
    #@+node:ekr.20081121105001.1513:wxLeoLogMenu class
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
    #@-node:ekr.20081121105001.1513:wxLeoLogMenu class
    #@+node:ekr.20081121105001.1514:wxLeoLog class (leoLog)
    class wxLeoLog (leoFrame.leoLog):

        """The base class for the log pane in Leo windows."""

        #@    @+others
        #@+node:ekr.20081121105001.1515:leoLog.__init__
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







        #@+node:ekr.20081121105001.1516:leoLog.createInitialTabs
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
        #@-node:ekr.20081121105001.1516:leoLog.createInitialTabs
        #@+node:ekr.20081121105001.1517:leoLog.setTabBindings
        def setTabBindings (self,tag=None):

            pass # g.trace('wxLeoLog')

        def bind (self,*args,**keys):

            # No need to do this: we can set the master binding by hand.
            pass # g.trace('wxLeoLog',args,keys)
        #@nonl
        #@-node:ekr.20081121105001.1517:leoLog.setTabBindings
        #@-node:ekr.20081121105001.1515:leoLog.__init__
        #@+node:ekr.20081121105001.1518:Config
        #@+node:ekr.20081121105001.1519:leoLog.configure
        def configure (self,*args,**keys):

            g.trace(args,keys)
        #@nonl
        #@-node:ekr.20081121105001.1519:leoLog.configure
        #@+node:ekr.20081121105001.1520:leoLog.configureBorder
        def configureBorder(self,border):

            g.trace(border)
        #@-node:ekr.20081121105001.1520:leoLog.configureBorder
        #@+node:ekr.20081121105001.1521:leoLog.setLogFontFromConfig
        def setFontFromConfig (self):

            pass # g.trace()
        #@nonl
        #@-node:ekr.20081121105001.1521:leoLog.setLogFontFromConfig
        #@-node:ekr.20081121105001.1518:Config
        #@+node:ekr.20081121105001.1522:wxLog.put & putnl
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
                #@+node:ekr.20081121105001.1523:<< put s to logWaiting and print s >>
                g.app.logWaiting.append((s,color),)

                print "Null log"

                if type(s) == type(u""):
                    s = g.toEncodedString(s,"ascii")

                print s
                #@-node:ekr.20081121105001.1523:<< put s to logWaiting and print s >>
                #@nl


        def putnl (self, tabName=None):

            self.put ('\n', tabName=tabName)
        #@-node:ekr.20081121105001.1522:wxLog.put & putnl
        #@+node:ekr.20081121105001.1524:Tab Popup Menu
        #@+node:ekr.20081121105001.1525:onShowTabMenu
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

        #@-node:ekr.20081121105001.1525:onShowTabMenu
        #@+node:ekr.20081121105001.1526:onPopupDelete
        def onPopupDelete(self, text):
            if text is not None and text not in ['Log', 'Find']:
                self.deleteTab(text)
        #@nonl
        #@-node:ekr.20081121105001.1526:onPopupDelete
        #@+node:ekr.20081121105001.1527:onPopupNew
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
        #@-node:ekr.20081121105001.1527:onPopupNew
        #@+node:ekr.20081121105001.1528:onPopupRename
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
        #@-node:ekr.20081121105001.1528:onPopupRename
        #@-node:ekr.20081121105001.1524:Tab Popup Menu
        #@+node:ekr.20081121105001.1529:Tab (wxLog)
        #@+node:ekr.20081121105001.1530:indexFromName
        def indexFromName(self, tabName):

            for i in range(self.nb.GetPageCount()):
                s = self.nb.GetPageText(i)
                if s == tabName:
                    return i

        #@-node:ekr.20081121105001.1530:indexFromName
        #@+node:ekr.20081121105001.1531:tabFromName
        def tabFromName(self, tabName):

            for tab in self.nb.tabs:
                if tabName == tab.tabName:
                    return tab
        #@nonl
        #@-node:ekr.20081121105001.1531:tabFromName
        #@+node:ekr.20081121105001.1532:getTabCtrl

        def getTabCtrl(self, tabName='Tab'):
            return self.textDict.get(tabName).widget
        #@-node:ekr.20081121105001.1532:getTabCtrl
        #@+node:ekr.20081121105001.1533:createTab

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

        #@-node:ekr.20081121105001.1533:createTab
        #@+node:ekr.20081121105001.1534:selectTab
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
        #@-node:ekr.20081121105001.1534:selectTab
        #@+node:ekr.20081121105001.1535:clearTab
        def clearTab (self,tabName,wrap='none'):

            self.selectTab(tabName,wrap=wrap)
            self.logCtrl.setAllText('')

        #@-node:ekr.20081121105001.1535:clearTab
        #@+node:ekr.20081121105001.1536:deleteTab
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
        #@-node:ekr.20081121105001.1536:deleteTab
        #@+node:ekr.20081121105001.1537:renameTab
        def renameTab(self, oldName, newName):

            if newName:
                #g.trace(oldName, newName)
                self.tabFromName(oldName).tabName = newName

                self.frameDict[newName] = self.frameDict[oldName]
                self.textDict[newName] = self.textDict[oldName]
                del self.frameDict[oldName]
                del self.textDict[oldName]
        #@-node:ekr.20081121105001.1537:renameTab
        #@+node:ekr.20081121105001.1538:getSelectedTab
        def getSelectedTab (self):

            return self.tabName
        #@-node:ekr.20081121105001.1538:getSelectedTab
        #@+node:ekr.20081121105001.1539:hideTab
        def hideTab (self,tabName):

            self.selectTab('Log')
        #@-node:ekr.20081121105001.1539:hideTab
        #@+node:ekr.20081121105001.1540:numberOfVisibleTabs
        def numberOfVisibleTabs (self):

            return self.nb.GetPageCount()
        #@-node:ekr.20081121105001.1540:numberOfVisibleTabs
        #@+node:ekr.20081121105001.1541:Not used yet
        if 0:
            #@    @+others
            #@+node:ekr.20081121105001.1542:cycleTabFocus
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
            #@-node:ekr.20081121105001.1542:cycleTabFocus
            #@+node:ekr.20081121105001.1543:lower/raiseTab
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
            #@-node:ekr.20081121105001.1543:lower/raiseTab
            #@-others
        #@nonl
        #@-node:ekr.20081121105001.1541:Not used yet
        #@-node:ekr.20081121105001.1529:Tab (wxLog)
        #@-others
    #@nonl
    #@-node:ekr.20081121105001.1514:wxLeoLog class (leoLog)
    #@+node:ekr.20081121105001.1544:== EXTRA WIDGETS
    #@+node:ekr.20081121105001.1545:wxLeoButton class
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

    #@-node:ekr.20081121105001.1545:wxLeoButton class
    #@+node:ekr.20081121105001.1546:wxLeoIconButton class
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
    #@-node:ekr.20081121105001.1546:wxLeoIconButton class
    #@+node:ekr.20081121105001.1547:wxLeoChapterSelector class

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


    #@-node:ekr.20081121105001.1547:wxLeoChapterSelector class
    #@+node:ekr.20081121105001.1548:wxLeoIconBar class
    class wxLeoIconBar(object):

        '''An adaptor class that uses a wx.ToolBar for Leo's icon area.'''

        #@    @+others
        #@+node:ekr.20081121105001.1549:__init__ wxLeoIconBar
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
        #@-node:ekr.20081121105001.1549:__init__ wxLeoIconBar
        #@+node:ekr.20081121105001.1550:add
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
        #@-node:ekr.20081121105001.1550:add
        #@+node:ekr.20081121105001.1551:clear
        def clear(self):

            """Destroy all the widgets in the icon bar"""

            for w in self.widgets:
                self.toolbar.RemoveTool(w.GetId())
            self.widgets = []
        #@-node:ekr.20081121105001.1551:clear
        #@+node:ekr.20081121105001.1552:setCommandForButton

        def setCommandForButton(self, b, command):
            b.command = command
        #@nonl
        #@-node:ekr.20081121105001.1552:setCommandForButton
        #@+node:ekr.20081121105001.1553:deleteButton
        def deleteButton (self, w):
            w.onDelete()
        #@-node:ekr.20081121105001.1553:deleteButton
        #@+node:ekr.20081121105001.1554:getFrame
        def getFrame (self):

            return self.iconFrame
        #@-node:ekr.20081121105001.1554:getFrame
        #@+node:ekr.20081121105001.1555:show/hide (do nothings)
        def pack (self):    pass
        def unpack (self):  pass
        show = pack
        hide = unpack
        #@-node:ekr.20081121105001.1555:show/hide (do nothings)
        #@-others
    #@-node:ekr.20081121105001.1548:wxLeoIconBar class
    #@+node:ekr.20081121105001.1556:wxLeoMinibuffer class
    class wxLeoMinibuffer:

        #@    @+others
        #@+node:ekr.20081121105001.1557:__init__

        def __init__ (self,c):

            self.c = c
            self.keyDownModifiers = None
            self.parentFrame = None
            self.ctrl = None#self.createControl(parentFrame)
            self.sizer = None
            # Set the official ivars.
            c.frame.miniBufferWidget = self
            c.miniBufferWidget = self

        #@-node:ekr.20081121105001.1557:__init__
        #@+node:ekr.20081121105001.1558:finishCreate

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

        #@-node:ekr.20081121105001.1558:finishCreate
        #@+node:ekr.20081121105001.1559:bind
        def bind(self, *args, **kw):
            #g.trace('wxleominibuffer', g.callers())
            pass
        #@nonl
        #@-node:ekr.20081121105001.1559:bind
        #@+node:ekr.20081121105001.1560:createControl
        def createControl (self,parent):

            return minibufferTextWidget(
                self,
                parent,
                name = 'minibuffer',
                style = wx.NO_BORDER
            )
        #@-node:ekr.20081121105001.1560:createControl
        #@+node:ekr.20081121105001.1561:setFocus

        def setFocus(self):
            self.ctrl.setFocus()

        SetFocus = setFocus
        #@-node:ekr.20081121105001.1561:setFocus
        #@-others
    #@nonl
    #@-node:ekr.20081121105001.1556:wxLeoMinibuffer class
    #@+node:ekr.20081121105001.1562:wxLeoStatusLine class
    class wxLeoStatusLine(object):

        '''A class representing the status line.'''

        #@    @+others
        #@+node:ekr.20081121105001.1563:__init__
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
        #@-node:ekr.20081121105001.1563:__init__
        #@+node:ekr.20081121105001.1564:setBindings
        def setBindings(self, *args, **kw):
            g.trace(myclass(self))
        #@nonl
        #@-node:ekr.20081121105001.1564:setBindings
        #@+node:ekr.20081121105001.1565:finishCreate
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


        #@-node:ekr.20081121105001.1565:finishCreate
        #@+node:ekr.20081121105001.1566:createControl

        def createControl(self, parent):

           self.statusUNL = self.ctrl = statusTextWidget(
                self, parent,
                name='statusline',
                multiline=False,
                style=wx.NO_BORDER | wx.TE_READONLY,
            )
        #@-node:ekr.20081121105001.1566:createControl
        #@+node:ekr.20081121105001.1567:clear
        def clear (self):

            self.statusUNL.clear()
            self.update()
        #@-node:ekr.20081121105001.1567:clear
        #@+node:ekr.20081121105001.1568:enable, disable & isEnabled

        #?? what are these for

        def disable (self,background=None):
            self.enabled = False
            c.bodyWantsFocus()

        def enable (self,background="white"):
            self.enabled = True

        def isEnabled(self):
            return self.enabled
        #@nonl
        #@-node:ekr.20081121105001.1568:enable, disable & isEnabled
        #@+node:ekr.20081121105001.1569:get

        def get (self):

            if self.c.frame.killed:
                return

            return self.statusUNL.getAllText()
        #@-node:ekr.20081121105001.1569:get
        #@+node:ekr.20081121105001.1570:getFrame

        def getFrame (self):

            if self.c.frame.killed:
                return
            else:
                return self.statusFrame
        #@-node:ekr.20081121105001.1570:getFrame
        #@+node:ekr.20081121105001.1571:onActivate
        def onActivate (self,event=None):

            pass
        #@-node:ekr.20081121105001.1571:onActivate
        #@+node:ekr.20081121105001.1572:pack & show
        def pack (self):
            pass

        show = pack
        #@-node:ekr.20081121105001.1572:pack & show
        #@+node:ekr.20081121105001.1573:put
        def put(self, s, color=None, **keys):

            if self.c.frame.killed:
                return

            self.statusUNL.appendText(s)
            self.update()
        #@-node:ekr.20081121105001.1573:put
        #@+node:ekr.20081121105001.1574:set
        def set(self, s, **keys):

            if self.c.frame.killed:
                return

            self.statusUNL.setAllText(s)
        #@nonl
        #@-node:ekr.20081121105001.1574:set
        #@+node:ekr.20081121105001.1575:unpack & hide
        def unpack (self):
            pass

        hide = unpack
        #@-node:ekr.20081121105001.1575:unpack & hide
        #@+node:ekr.20081121105001.1576:update (statusLine)

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

        #@-node:ekr.20081121105001.1576:update (statusLine)
        #@-others
    #@-node:ekr.20081121105001.1562:wxLeoStatusLine class
    #@+node:ekr.20081121105001.1577:plugin menu dialogs
    #@+others
    #@+node:ekr.20081121105001.1578:class wxScrolledMessageDialog
    class wxScrolledMessageDialog(object):
        """A class to create and run a Scrolled Message dialog for wxPython"""
        #@    @+others
        #@+node:ekr.20081121105001.1579:__init__
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
        #@-node:ekr.20081121105001.1579:__init__
        #@+node:ekr.20081121105001.1580:onButton
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
        #@-node:ekr.20081121105001.1580:onButton
        #@-others


    #@-node:ekr.20081121105001.1578:class wxScrolledMessageDialog
    #@+node:ekr.20081121105001.1581:class wxPropertiesDialog
    class wxPropertiesDialog(object):

        """A class to create and run a Properties dialog"""

        #@    @+others
        #@+node:ekr.20081121105001.1582:__init__
        def __init__(self, title, data, callback=None, buttons=[]):
            #@    << docstring >>
            #@+node:ekr.20081121105001.1583:<< docstring >>
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
            #@-node:ekr.20081121105001.1583:<< docstring >>
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

        #@-node:ekr.20081121105001.1582:__init__
        #@+node:ekr.20081121105001.1584:onButton

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


        #@-node:ekr.20081121105001.1584:onButton
        #@+node:ekr.20081121105001.1585:createEntryPanel
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
        #@-node:ekr.20081121105001.1585:createEntryPanel
        #@+node:ekr.20081121105001.1586:getData
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


        #@-node:ekr.20081121105001.1586:getData
        #@-others
    #@nonl
    #@-node:ekr.20081121105001.1581:class wxPropertiesDialog
    #@-others
    #@nonl
    #@-node:ekr.20081121105001.1577:plugin menu dialogs
    #@-node:ekr.20081121105001.1544:== EXTRA WIDGETS
    #@+node:ekr.20081121105001.1587:== TREE WIDGETS ==
    #@+node:ekr.20081121105001.1588:wxLeoTree class (leoFrame.leoTree):
    class wxLeoTree (leoFrame.leoTree):
        #@    @+others
        #@+node:ekr.20081121105001.1589:__init__
        def __init__ (self, c, parentFrame):


            self.c = c
            self.frame = c.frame

            # Init the base class.
            leoFrame.leoTree.__init__(self, self.frame)


            #@    << init config >>
            #@+node:ekr.20081121105001.1590:<< init config >>
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
            #@-node:ekr.20081121105001.1590:<< init config >>
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







        #@+node:ekr.20081121105001.1591:createBindings

        def createBindings (self): # wxLeoTree
            pass

        #@-node:ekr.20081121105001.1591:createBindings
        #@+node:ekr.20081121105001.1592:createControl

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
        #@-node:ekr.20081121105001.1592:createControl
        #@+node:ekr.20081121105001.1593:setBindings
        def setBindings(self):

            pass # g.trace('wxLeoTree: to do')

        def bind(self,*args,**keys):

            pass # g.trace('wxLeoTree',args,keys)
        #@nonl
        #@-node:ekr.20081121105001.1593:setBindings
        #@-node:ekr.20081121105001.1589:__init__
        #@+node:ekr.20081121105001.1594:__str__ & __repr__

        def __repr__ (self):

            return "Tree %d" % id(self)

        __str__ = __repr__

        #@-node:ekr.20081121105001.1594:__str__ & __repr__
        #@+node:ekr.20081121105001.1595:edit_widget

        def edit_widget(self, p=None):
            """Return the headlineTextWidget."""

            return self.headlineTextWidget
        #@-node:ekr.20081121105001.1595:edit_widget
        #@+node:ekr.20081121105001.1596:Focus Gain/Lose

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
        #@-node:ekr.20081121105001.1596:Focus Gain/Lose
        #@+node:ekr.20081121105001.1597:SetFocus
        def setFocus(self):

            if not self.treeCtrl or g.app.killed or self.c.frame.killed: return

            self.treeCtrl.SetFocus()

        SetFocus = setFocus

        #@-node:ekr.20081121105001.1597:SetFocus
        #@+node:ekr.20081121105001.1598:getCanvas
        def getCanvas(self):
            return self.treeCtrl._canvas
        #@nonl
        #@-node:ekr.20081121105001.1598:getCanvas
        #@+node:ekr.20081121105001.1599:getCanvasHeight
        def getCanvasHeight(self):
            print '++++++', self.treeCtrl._canvas._size.height
            return self.treeCtrl._canvas._size.height

        #@-node:ekr.20081121105001.1599:getCanvasHeight
        #@+node:ekr.20081121105001.1600:getLineHeight
        #@-node:ekr.20081121105001.1600:getLineHeight
        #@+node:ekr.20081121105001.1601:onScrollRelative
        def onScrollRelative(self, orient, value):
            self.treeCtrl.onScrollRelative(orient, value)
        #@nonl
        #@-node:ekr.20081121105001.1601:onScrollRelative
        #@+node:ekr.20081121105001.1602:HasCapture / Capture / Release Mouse
        def HasCapture(self):
            return self.getCanvas().HasCapture()

        def CaptureMouse(self):
            return self.getCanvas().CaptureMouse()

        def ReleaseMouse(self):
            return self.getCanvas().ReleaseMouse()
        #@-node:ekr.20081121105001.1602:HasCapture / Capture / Release Mouse
        #@+node:ekr.20081121105001.1603:setCursor
        def setCursor(self, cursor):
            if cursor == 'drag':
                self.getCanvas().SetCursor(wx.StockCursor(wx.CURSOR_HAND))
            else:
                self.getCanvas().SetCursor(wx.StockCursor(wx.CURSOR_ARROW))

        #@-node:ekr.20081121105001.1603:setCursor
        #@+node:ekr.20081121105001.1604:idle_redraw
        def idle_redraw(*args, **kw):
            return
        #@nonl
        #@-node:ekr.20081121105001.1604:idle_redraw
        #@+node:ekr.20081121105001.1605:Drawing
        #@+node:ekr.20081121105001.1606:beginUpdate
        def beginUpdate(self):

            self.updateCount += 1
        #@-node:ekr.20081121105001.1606:beginUpdate
        #@+node:ekr.20081121105001.1607:endUpdate
        def endUpdate(self, flag=True, scroll=False):

            assert(self.updateCount > 0)

            self.updateCount -= 1
            if flag and self.updateCount <= 0:
                self.redraw()

                if self.updateCount < 0:
                    g.trace("Can't happen: negative updateCount", g.callers())



        #@-node:ekr.20081121105001.1607:endUpdate
        #@+node:ekr.20081121105001.1608:redraw & redraw_now & helpers
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
                c.expandAllAncestors(c.currentPosition())
                tree.update()
                self.scrollTo()
            finally:
                self.drawing = False # Enable event handlers.

            #if not g.app.unitTesting: g.trace('done')

        redraw_now = redraw
        #@-node:ekr.20081121105001.1608:redraw & redraw_now & helpers
        #@+node:ekr.20081121105001.1609:scrollTo
        def scrollTo(self,p=None):
            """Scrolls the canvas so that p is in view.

            Assumes that the canvas is in a valid state.
            """

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
            #@+node:ekr.20081121105001.1610:<< virtual top for target >>

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
            #@-node:ekr.20081121105001.1610:<< virtual top for target >>
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
        #@-node:ekr.20081121105001.1609:scrollTo
        #@-node:ekr.20081121105001.1605:Drawing
        #@+node:ekr.20081121105001.1611:== Event handlers ==
        #@+node:ekr.20081121105001.1612:def onChar
        def onChar(self, event, keycode, keysym):
            pass
        #@nonl
        #@-node:ekr.20081121105001.1612:def onChar
        #@+node:ekr.20081121105001.1613:onHeadlineKey

        # k.handleDefaultChar calls onHeadlineKey.
        def onHeadlineKey (self, event):

            #g.trace(event)

            if g.app.killed or self.c.frame.killed:
                return

            if event and event.keysym:
                self.updateHead(event, event.widget)
        #@-node:ekr.20081121105001.1613:onHeadlineKey
        #@+node:ekr.20081121105001.1614:Drag
        #@+node:ekr.20081121105001.1615:startDrag
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
        #@-node:ekr.20081121105001.1615:startDrag
        #@+node:ekr.20081121105001.1616:onDrag
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
        #@-node:ekr.20081121105001.1616:onDrag
        #@+node:ekr.20081121105001.1617:onEndDrag
        def onEndDrag(self, drop_p, event):

            """Tree end-of-drag handler."""

            c = self.c ; p = self.drag_p
            if not (drop_p and self.drag_p):
                self.cancelDrag()

            c.setLog()

            if not g.doHook("enddrag1",c=c,p=p,v=p,event=event):
                self.endDrag(drop_p, event)
            g.doHook("enddrag2",c=c,p=p,v=p,event=event)
        #@+node:ekr.20081121105001.1618:endDrag
        def endDrag (self, drop_p, event):

            """The official helper of the onEndDrag event handler."""

            c = self.c
            c.setLog()

            #g.trace()

            p = self.drag_p

            if not event:
                return

            redrawFlag = False
            #@    << set drop_p, childFlag >>
            #@+node:ekr.20081121105001.1619:<< set drop_p, childFlag >>



            childFlag = drop_p and drop_p.hasChildren() and drop_p.isExpanded()
            #@-node:ekr.20081121105001.1619:<< set drop_p, childFlag >>
            #@nl
            if self.allow_clone_drags:
                if not self.look_for_control_drag_on_mouse_down:
                    self.controlDrag = c.frame.controlKeyIsDown

            redrawFlag = drop_p and drop_p.v.t != p.v.t
            if redrawFlag: # Disallow drag to joined node.
                #@        << drag p to drop_p >>
                #@+node:ekr.20081121105001.1620:<< drag p to drop_p>>
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
                #@-node:ekr.20081121105001.1620:<< drag p to drop_p>>
                #@nl
            elif self.trace and self.verbose:
                g.trace("Cancel drag")

            # Reset the old cursor by brute force.
            self.setCursor('default')
            self.dragging = False
            self.drag_p = None

            # Must set self.drag_p = None first.
            if redrawFlag: c.redraw()
            c.recolor_now() # Dragging can affect coloring.
        #@-node:ekr.20081121105001.1618:endDrag
        #@-node:ekr.20081121105001.1617:onEndDrag
        #@+node:ekr.20081121105001.1621:cancelDrag
        def cancelDrag(self, p, event):

            #g.trace()

            if self.trace and self.verbose:
                g.trace("Cancel drag")

            # Reset the old cursor by brute force.
            self.setCursor('default')
            self.dragging = False
            self.drag_p = None
        #@-node:ekr.20081121105001.1621:cancelDrag
        #@+node:ekr.20081121105001.1622:continueDrag
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
                    #@+node:ekr.20081121105001.1623:<< scroll the canvas as needed >>

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
                    #@-node:ekr.20081121105001.1623:<< scroll the canvas as needed >>
                    #@nl
            except:
                g.es_event_exception("continue drag")
        #@-node:ekr.20081121105001.1622:continueDrag
        #@-node:ekr.20081121105001.1614:Drag
        #@+node:ekr.20081121105001.1624:Mouse Events
        """
        All mouse events are collected by the treeCtrl and sent
        to a dispatcher (onMouse).

        onMouse is called with dispatcher is called with a position,

        a 'source' which is the name of an region inside the headline
            this could be 'ClickBox', 'IconBox', 'TextBox' or a user supplied



        """


        #@+node:ekr.20081121105001.1625:onMouse (Dispatcher)
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
                #@+node:ekr.20081121105001.1626:<< trace mouse >>
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

                #@-node:ekr.20081121105001.1626:<< trace mouse >>
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

        #@-node:ekr.20081121105001.1625:onMouse (Dispatcher)
        #@+node:ekr.20081121105001.1627:HitTest
        def hitTest(self, point):
            return self.treeCtrl._canvas.hitTest(point)



        #@-node:ekr.20081121105001.1627:HitTest
        #@+node:ekr.20081121105001.1628:Pre
        #@+node:ekr.20081121105001.1629:onPreMouseLeftDown
        def onPreMouseLeftDown(self, sp, event, source, type):
            #g.trace('source:', source, 'type:', type, 'Position:', sp and sp.headString())

            self.setFocus()
        #@-node:ekr.20081121105001.1629:onPreMouseLeftDown
        #@+node:ekr.20081121105001.1630:onPreMouseLeftUp
        #@+at
        # def onPreMouseLeftUp(self, sp, event, source, type):
        #     g.trace('source:', source, 'type:', type, 'Position:', sp and
        # sp.headString())
        #@-at
        #@-node:ekr.20081121105001.1630:onPreMouseLeftUp
        #@+node:ekr.20081121105001.1631:onPreMouseRightDown
        #@+at
        # def onPreMouseRightDown(self, sp, event, source, type):
        #     g.trace('source:', source, 'type:', type, 'Position:', sp and
        # sp.headString())
        #@-at
        #@-node:ekr.20081121105001.1631:onPreMouseRightDown
        #@+node:ekr.20081121105001.1632:onPreMouseRightUp
        #@+at
        # def onPreMouseRightUp(self, sp, event, source, type):
        #     g.trace('source:', source, 'type:', type, 'Position:', sp and
        # sp.headString())
        #@-at
        #@-node:ekr.20081121105001.1632:onPreMouseRightUp
        #@+node:ekr.20081121105001.1633:onPreMouseMotion
        #@-node:ekr.20081121105001.1633:onPreMouseMotion
        #@-node:ekr.20081121105001.1628:Pre
        #@+node:ekr.20081121105001.1634:Post
        #@+node:ekr.20081121105001.1635:onPostMouseLeftDown
        #@+at
        # def onPostMouseLeftDown(self, sp, event, source, type):
        #     g.trace('source:', source, 'type:', type, 'Position:', sp and
        # sp.headString())
        #@-at
        #@-node:ekr.20081121105001.1635:onPostMouseLeftDown
        #@+node:ekr.20081121105001.1636:onPostMouseLeftUp
        def onPostMouseLeftUp(self, sp, event, source, type):
            #g.trace('source:', source, 'type:', type, 'Position:', sp and sp.headString())

            self.setCursor('default')
            if self.HasCapture():
                self.ReleaseMouse()

            #If we are still dragging here something as gone wrong.
            if self.dragging:
                self.cancelDrag(sp, event)
        #@-node:ekr.20081121105001.1636:onPostMouseLeftUp
        #@+node:ekr.20081121105001.1637:onPostMouseRightDown
        #@+at
        # def onPostMouseRightDown(self, sp, event, source, type):
        #     g.trace('source:', source, 'type:', type, 'Position:', sp and
        # sp.headString())
        # 
        #@-at
        #@-node:ekr.20081121105001.1637:onPostMouseRightDown
        #@+node:ekr.20081121105001.1638:onPostMouseRightUp
        #@+at
        # def onPostMouseRightUp(self, sp, event, source, type):
        #     g.trace('source:', source, 'type:', type, 'Position:', sp and
        # sp.headString())
        # 
        #@-at
        #@-node:ekr.20081121105001.1638:onPostMouseRightUp
        #@+node:ekr.20081121105001.1639:onPostMouseMotion
        #@-node:ekr.20081121105001.1639:onPostMouseMotion
        #@-node:ekr.20081121105001.1634:Post
        #@+node:ekr.20081121105001.1640:Motion
        def onMouseMotion(self, p, event, source, type):
            if self.dragging:
                self.onDrag(p, event)
        #@-node:ekr.20081121105001.1640:Motion
        #@+node:ekr.20081121105001.1641:Click Box
        #@+node:ekr.20081121105001.1642:onMouseClickBoxLeftDown
        def onMouseClickBoxLeftDown (self, p, event, source, type):
            """React to leftMouseDown event on ClickBox.

            Toggles expanded status for this node.

            """

            c = self.c

            p1 = c.currentPosition()
            #g.trace(source, type, p)
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
            c.redraw()


        #@-node:ekr.20081121105001.1642:onMouseClickBoxLeftDown
        #@-node:ekr.20081121105001.1641:Click Box
        #@+node:ekr.20081121105001.1643:Icon Box...
        #@+node:ekr.20081121105001.1644:onMouseIconBoxLeftDown
        def onMouseIconBoxLeftDown(self, p, event, source , type):
            """React to leftMouseDown event on the icon box."""

            #g.trace(source, type)
            c = self.c
            c.setLog()

            if not self.HasCapture():
                self.CaptureMouse()

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
            c.redraw()

        #@-node:ekr.20081121105001.1644:onMouseIconBoxLeftDown
        #@+node:ekr.20081121105001.1645:onMouseIconBoxLeftUp

        def onMouseIconBoxLeftUp(self, sp, event, source, type):
            #g.trace('\n\tDrop:', self.drag_p, '\n\tOn:', sp and sp.headString())

            if self.dragging:
                self.onEndDrag(sp, event)
        #@nonl
        #@-node:ekr.20081121105001.1645:onMouseIconBoxLeftUp
        #@+node:ekr.20081121105001.1646:onMouseIconBoxLeftDoubleClick
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
        #@-node:ekr.20081121105001.1646:onMouseIconBoxLeftDoubleClick
        #@-node:ekr.20081121105001.1643:Icon Box...
        #@+node:ekr.20081121105001.1647:Text Box
        #@+node:ekr.20081121105001.1648:onMouseTextBoxLeftDown

        def onMouseTextBoxLeftDown(self, p, event, source, type):
            """React to leftMouseDown event on the label of a headline."""

            c = self.c
            c.setLog()

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
            c.redraw()

        #@-node:ekr.20081121105001.1648:onMouseTextBoxLeftDown
        #@-node:ekr.20081121105001.1647:Text Box
        #@+node:ekr.20081121105001.1649:Headline
        #@+node:ekr.20081121105001.1650:onMouseHeadlineLeftDown

        def onMouseHeadlineLeftDown(self, sp, event, source, type):
            """React to leftMouseDown event outside of main headline regions."""

            #g.trace('FIXME')
            if not self.expanded_click_area:

                return
            self.onMouseClickBoxLeftDown(sp, event, source, type)
        #@-node:ekr.20081121105001.1650:onMouseHeadlineLeftDown
        #@-node:ekr.20081121105001.1649:Headline
        #@-node:ekr.20081121105001.1624:Mouse Events
        #@-node:ekr.20081121105001.1611:== Event handlers ==
        #@+node:ekr.20081121105001.1651:editLabel
        def editLabel (self,p,selectAll=False,selection=None):
            '''The edit-label command.'''

            #g.trace(g.callers())

            if g.app.killed or self.c.frame.killed: return

            c = self.c

            entry = self.headlineTextWidget

            if p:

                self.endEditLabel()
                self.setEditPosition(p)
                #g.trace('ep', self.editPosition())
                c.redraw()

                # Help for undo.
                self.revertHeadline = s = p.headString()

                self.setEditLabelState(p)

                entry.setAllText(s)

                selectAll = selectAll or self.select_all_text_when_editing_headlines
                if selection:
                    i,j,ins = selection
                    entry.ctrl.setSelection(i,j,insert=ins)
                elif selectAll:
                    entry.ctrl.SetSelection(-1, -1)
                else:
                    entry.ctrl.SetInsertionPointEnd()
                entry.ctrl.SetFocus()
                c.headlineWantsFocus(p)
        #@-node:ekr.20081121105001.1651:editLabel
        #@+node:ekr.20081121105001.1652:endEditLabel
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
            c.redraw()

            if c.config.getBool('stayInTreeAfterEditHeadline'):
                c.treeWantsFocusNow()
            else:
                c.bodyWantsFocusNow()

            if event:
                event.Skip()
        #@-node:ekr.20081121105001.1652:endEditLabel
        #@+node:ekr.20081121105001.1654:tree.set...LabelState
        #@+node:ekr.20081121105001.1655:setEditLabelState
        def setEditLabelState(self, p, selectAll=False):

            #g.trace()
            pass

        #@-node:ekr.20081121105001.1655:setEditLabelState
        #@+node:ekr.20081121105001.1656:setSelectedLabelState

        def setSelectedLabelState(self, p):

            # g.trace(p, g.callers())

            if p:
                p.setSelected()

        #@-node:ekr.20081121105001.1656:setSelectedLabelState
        #@+node:ekr.20081121105001.1657:setUnselectedLabelState

        def setUnselectedLabelState(self,p): # not selected.

            # g.trace(p, g.callers())

            if p:
                # clear 'selected' status flag
                p.v.statusBits &= ~ p.v.selectedBit

        #@-node:ekr.20081121105001.1657:setUnselectedLabelState
        #@-node:ekr.20081121105001.1654:tree.set...LabelState
        #@+node:ekr.20081121105001.1658:do nothings
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


        #@-node:ekr.20081121105001.1658:do nothings
        #@+node:ekr.20081121105001.1659:GetName
        def GetName(self):
            return 'canvas'

        getName = GetName
        #@-node:ekr.20081121105001.1659:GetName
        #@+node:ekr.20081121105001.1660:Reparent
        def reparent(self, parent):
            self.treeCtrl.Reparent(parent)

        Reparent = reparent
        #@-node:ekr.20081121105001.1660:Reparent
        #@+node:ekr.20081121105001.1661:Font Property
        def getFont(self):
            g.trace('not ready')

        def setFont(self):
            g.trace('not ready')

        font = property(getFont, setFont)



        #@-node:ekr.20081121105001.1661:Font Property
        #@+node:ekr.20081121105001.1662:requestLineHeight
        def requestLineHeight(height):
            self.getCanvas().requestLineHeight(height)
        #@nonl
        #@-node:ekr.20081121105001.1662:requestLineHeight
        #@+node:ekr.20081121105001.1663:line_height property
        def getLineHeight(self):
            return self.treeCtrl._canvas._lineHeight

        line_height = property(getLineHeight)
        #@nonl
        #@-node:ekr.20081121105001.1663:line_height property
        #@-others
    #@nonl
    #@-node:ekr.20081121105001.1588:wxLeoTree class (leoFrame.leoTree):
    #@+node:ekr.20081121105001.1664:class OutlineCanvasPanel

    class OutlineCanvasPanel(wx.PyPanel):
        """A class to mimic a scrolled window to contain an OutlineCanvas."""
        #@    @+others
        #@+node:ekr.20081121105001.1665:__init__

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

        #@-node:ekr.20081121105001.1665:__init__
        #@+node:ekr.20081121105001.1666:showEntry
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
        #@-node:ekr.20081121105001.1666:showEntry
        #@+node:ekr.20081121105001.1667:hideEntry

        def hideEntry(self):

            entry = self._entry
            entry._virtualTop = -1000
            entry.MoveXY(0, -1000)

            entry.Hide()
        #@-node:ekr.20081121105001.1667:hideEntry
        #@+node:ekr.20081121105001.1668:getPositions

        def getPositions(self):
            return self._canvas._positions
        #@nonl
        #@-node:ekr.20081121105001.1668:getPositions
        #@+node:ekr.20081121105001.1669:onScrollThumbtrack

        def onScrollThumbtrack(self, event):
            """React to changes in the position of the scrollbars."""
            return self.onScroll(event.GetOrientation(), event.GetPosition())
        #@nonl
        #@-node:ekr.20081121105001.1669:onScrollThumbtrack
        #@+node:ekr.20081121105001.1670:onScrollLineup

        def onScrollLineup(self, event):
            """Scroll the outline up by one page."""
            orient = event.GetOrientation()
            return self.onScroll(orient, self.GetScrollPos(orient) - 10)
        #@nonl
        #@-node:ekr.20081121105001.1670:onScrollLineup
        #@+node:ekr.20081121105001.1671:onScrollLinedown

        def onScrollLinedown(self, event):
            """Scroll the outline down by one line."""
            orient = event.GetOrientation()
            return self.onScroll(orient, self.GetScrollPos(orient) + 10)
        #@nonl
        #@-node:ekr.20081121105001.1671:onScrollLinedown
        #@+node:ekr.20081121105001.1672:onScrollPageup

        def onScrollPageup(self, event):
            """Scroll the outline up one page."""
            orient = event.GetOrientation()
            offset = self.GetClientSize()[orient == wx.VERTICAL] * 0.9
            return self.onScroll(orient, self.GetScrollPos(orient) - int(offset))
        #@nonl
        #@-node:ekr.20081121105001.1672:onScrollPageup
        #@+node:ekr.20081121105001.1673:onScrollPagedown

        def onScrollPagedown(self, event):
            """Scroll the outline down by one page."""
            orient = event.GetOrientation()
            offset = self.GetClientSize()[orient == wx.VERTICAL] * 0.9
            return self.onScroll(orient, self.GetScrollPos(orient) + int(offset))


        #@-node:ekr.20081121105001.1673:onScrollPagedown
        #@+node:ekr.20081121105001.1674:onScroll
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
        #@-node:ekr.20081121105001.1674:onScroll
        #@+node:ekr.20081121105001.1675:onScrollRelative

        def onScrollRelative(self, orient, value):

            return self.onScroll(orient, self.GetScrollPos(orient) + value)
        #@-node:ekr.20081121105001.1675:onScrollRelative
        #@+node:ekr.20081121105001.1676:onSize
        def onSize(self, event=None):
            """React to changes in the size of the outlines display area."""

            c = self.c

            self.vscrollUpdate()
            self._canvas.resize(self.GetClientSize().height)
            event.Skip()
        #@-node:ekr.20081121105001.1676:onSize
        #@+node:ekr.20081121105001.1677:vscrollUpdate

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
        #@-node:ekr.20081121105001.1677:vscrollUpdate
        #@+node:ekr.20081121105001.1678:hscrollUpdate

        def hscrollUpdate(self):
            """Set the horizontal scroll bar to match current conditions."""

            self.SetScrollbar(wx.HORIZONTAL,
                 -self._canvas.GetPosition().x,
                 self.GetClientSize().width,
                 self._canvas.GetSize().width,
                 True
            )

        #@-node:ekr.20081121105001.1678:hscrollUpdate
        #@+node:ekr.20081121105001.1679:update

        def update(self):
            self._canvas.update()


        #@-node:ekr.20081121105001.1679:update
        #@+node:ekr.20081121105001.1680:redraw

        def redraw(self):
            self._canvas.redraw()
        #@nonl
        #@-node:ekr.20081121105001.1680:redraw
        #@+node:ekr.20081121105001.1681:refresh
        def refresh(self):
            self._canvas.refresh()
        #@nonl
        #@-node:ekr.20081121105001.1681:refresh
        #@+node:ekr.20081121105001.1682:GetName
        def GetName(self):
            return 'canvas'

        getName = GetName
        #@nonl
        #@-node:ekr.20081121105001.1682:GetName
        #@-others
    #@-node:ekr.20081121105001.1664:class OutlineCanvasPanel
    #@+node:ekr.20081121105001.1683:class OutlineCanvas
    class OutlineCanvas(wx.Window):
        """Implements a virtual view of a leo outline tree.

        The class uses an off-screen buffer for drawing which it
        blits to the window during paint calls for expose events, etc,

        A redraw is only required when the height of the canvas changes,
        a vertical scroll event occurs, or if the outline changes.

        """
        #@    @+others
        #@+node:ekr.20081121105001.1684:__init__
        def __init__(self, parent):
            """Create an OutlineCanvas instance."""

            #g.trace('OutlineCanvas')

            self._c = self.c = parent._c
            self._parent = parent
            self._leoTree = parent._leoTree

            #@    << define ivars >>
            #@+node:ekr.20081121105001.1685:<< define ivars >>
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


            #@-node:ekr.20081121105001.1685:<< define ivars >>
            #@nl

            wx.Window.__init__(self, parent, -1, size=self._size, style=wx.WANTS_CHARS | wx.NO_BORDER )

            self._createNewBuffer(self._size)

            self.contextChanged()

            self.Bind(wx.EVT_PAINT, self.onPaint)

            for o in (self, parent):
                #@        << create  bindings >>
                #@+node:ekr.20081121105001.1686:<< create bindings >>
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
                #@-node:ekr.20081121105001.1686:<< create bindings >>
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
        #@-node:ekr.20081121105001.1684:__init__
        #@+node:ekr.20081121105001.1687:virtualTop property


        def getVirtualTop(self):
            return self.__virtualTop

        def setVirtualTop(self, virtualTop):
            self.__virtualTop = virtualTop

            #self._parent.showEntry()

        _virtualTop = property (getVirtualTop, setVirtualTop)

        #@-node:ekr.20081121105001.1687:virtualTop property
        #@+node:ekr.20081121105001.1688:hitTest
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

        #@-node:ekr.20081121105001.1688:hitTest
        #@+node:ekr.20081121105001.1689:_createNewBuffer
        def _createNewBuffer(self, size):
            """Create a new buffer for drawing."""

            self._buffer = b = wx.MemoryDC()
            self._bitmap = wx.EmptyBitmap(*size)
            b.SelectObject(self._bitmap)
            b.SetMapMode(wx.MM_TEXT)



        #@-node:ekr.20081121105001.1689:_createNewBuffer
        #@+node:ekr.20081121105001.1690:vscrollTo

        def vscrollTo(self, pos):
            """Scroll the canvas vertically to the specified position."""

            if (self._treeHeight - self._size.height) < pos :
                pos = self._treeHeight - self._size.height

            if pos < 0:
                pos = 0

            self._virtualTop = pos

            self.resize()
        #@-node:ekr.20081121105001.1690:vscrollTo
        #@+node:ekr.20081121105001.1691:resize / redraw

        def resize(self, height=None, width=None):
            """Resize the outline canvas and, if required, create and draw on a new buffer."""

            c = self.c

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
            return True

        redraw = resize



        #@-node:ekr.20081121105001.1691:resize / redraw
        #@+node:ekr.20081121105001.1692:refresh

        def refresh(self):
            """Renders the offscreen buffer to the outline canvas."""

            #print 'refresh'
            wx.ClientDC(self).BlitPointSize((0,0), self._size, self._buffer, (0, 0))

        #@-node:ekr.20081121105001.1692:refresh
        #@+node:ekr.20081121105001.1693:update

        def update(self):
            """Do a full update assuming the tree has been changed."""

            c = self._c

            hoistFlag = bool(self._c.hoistStack)

            if hoistFlag:
                stk = [self._c.hoistStack[-1].p]
            else:
                stk = [self._c.rootPosition()]

            #@    << find height of tree and position of currentNode >>
            #@+node:ekr.20081121105001.1694:<< find height of tree and position of currentNode >>

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
                    #@+node:ekr.20081121105001.1695:<< if p.isExpanded() and p.hasFirstChild():>>
                    ## if p.isExpanded() and p.hasFirstChild():

                    v=p.v
                    if v.statusBits & v.expandedBit and v.t._firstChild:
                    #@nonl
                    #@-node:ekr.20081121105001.1695:<< if p.isExpanded() and p.hasFirstChild():>>
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



            #@-node:ekr.20081121105001.1694:<< find height of tree and position of currentNode >>
            #@nl

            #< < if height from top to bottom is less than canvas height: >>
            if (self._treeHeight - self._virtualTop) < self._size.height:
                self._virtualTop = self._treeHeight - self._size.height

            self.contextChanged()

            self.resize()
            self._parent.vscrollUpdate()


        #@-node:ekr.20081121105001.1693:update
        #@+node:ekr.20081121105001.1696:onPaint

        def onPaint(self, event):
            """Renders the off-screen buffer to the outline canvas."""

            #print 'on paint'
            wx.PaintDC(self).BlitPointSize((0,0), self._size, self._buffer, (0, 0))
        #@-node:ekr.20081121105001.1696:onPaint
        #@+node:ekr.20081121105001.1697:contextChanged
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


        #@-node:ekr.20081121105001.1697:contextChanged
        #@+node:ekr.20081121105001.1698:requestLineHeight
        def requestLineHeight(height):
            """Request a minimum height for lines."""

            assert int(height) and height < 200
            self.requestedHeight = height
            self.beginUpdate()
            self.endUpdate()
        #@-node:ekr.20081121105001.1698:requestLineHeight
        #@+node:ekr.20081121105001.1699:def draw

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
            #@+node:ekr.20081121105001.1700:<< draw tree >>
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
                        #@+node:ekr.20081121105001.1701:<< set up object >>
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

                        #@-node:ekr.20081121105001.1701:<< set up object >>
                        #@nl

                        positions.append(sp)

                        canvasWidth = max(canvasWidth, textSize.width + xTextOffset + 100)

                    #@        << if p.isExpanded() and p.hasFirstChild():>>
                    #@+node:ekr.20081121105001.1695:<< if p.isExpanded() and p.hasFirstChild():>>
                    ## if p.isExpanded() and p.hasFirstChild():

                    v=p.v
                    if v.statusBits & v.expandedBit and v.t._firstChild:
                    #@nonl
                    #@-node:ekr.20081121105001.1695:<< if p.isExpanded() and p.hasFirstChild():>>
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
                #@+node:ekr.20081121105001.1702:<< draw text >>

                current = c.currentPosition()

                #dc.SetBrush(wx.TRANSPARENT_BRUSH)
                #dc.SetPen(wx.BLACK_PEN)

                for sp in positions:

                    #@    << draw user icons >>
                    #@+node:ekr.20081121105001.1703:<< draw user icons >>
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
                    #@-node:ekr.20081121105001.1703:<< draw user icons >>
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
                #@-node:ekr.20081121105001.1702:<< draw text >>
                #@nl
                #@    << draw lines >>
                #@+node:ekr.20081121105001.1704:<< draw lines >>
                #@-node:ekr.20081121105001.1704:<< draw lines >>
                #@nl
                #@    << draw bitmaps >>
                #@+node:ekr.20081121105001.1705:<< draw bitmaps >>

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
                #@-node:ekr.20081121105001.1705:<< draw bitmaps >>
                #@nl

            #@<< draw focus >>
            #@+node:ekr.20081121105001.1706:<< draw focus >>

            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            if self._leoTree.hasFocus():
                dc.SetPen(wx.BLACK_PEN)
            #else:
            #    dc.SetPen(wx.GREEN_PEN)
                dc.DrawRectanglePointSize( (0,0), self.GetSize())
            #@nonl
            #@-node:ekr.20081121105001.1706:<< draw focus >>
            #@nl




            #@-node:ekr.20081121105001.1700:<< draw tree >>
            #@nl

            self._parent.showEntry()






        #@-node:ekr.20081121105001.1699:def draw
        #@-others
    #@-node:ekr.20081121105001.1683:class OutlineCanvas
    #@-node:ekr.20081121105001.1587:== TREE WIDGETS ==
    #@-others
#@-node:ekr.20081121105001.1111:@thin experimental/__wx_alt_gui.py
#@-leo
