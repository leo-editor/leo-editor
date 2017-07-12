#@+leo-ver=5-thin
#@+node:ekr.20170428084207.303: * @file ../external/npyscreen/fmPopup.py
#!/usr/bin/python
# encoding: utf-8

#@+others
#@+node:ekr.20170428084207.304: ** Declarations
from . import fmForm
from . import fmActionFormV2
# import curses


#@+node:ekr.20170428084207.305: ** class Popup
class Popup(fmForm.Form):
    DEFAULT_LINES      = 12
    DEFAULT_COLUMNS    = 60
    SHOW_ATX           = 10
    SHOW_ATY           = 2

#@+node:ekr.20170428084207.306: ** class ActionPopup
class ActionPopup(fmActionFormV2.ActionFormV2):
    DEFAULT_LINES      = 12
    DEFAULT_COLUMNS    = 60
    SHOW_ATX           = 10
    SHOW_ATY           = 2


#@+node:ekr.20170428084207.307: ** class MessagePopup
class MessagePopup(Popup):
    #@+others
    #@+node:ekr.20170428084207.308: *3* __init__
    def __init__(self, *args, **keywords):
        from . import wgmultiline as multiline
        super(MessagePopup, self).__init__(*args, **keywords)
        self.TextWidget = self.add(multiline.Pager, scroll_exit=True, max_height=self.widget_useable_space()[0]-2)

    #@-others
#@+node:ekr.20170428084207.309: ** class PopupWide
class PopupWide(Popup):
    DEFAULT_LINES      = 14
    DEFAULT_COLUMNS    = None
    SHOW_ATX           = 0
    SHOW_ATY           = 0

#@+node:ekr.20170428084207.310: ** class ActionPopupWide
class ActionPopupWide(fmActionFormV2.ActionFormV2):
    DEFAULT_LINES      = 14
    DEFAULT_COLUMNS    = None
    SHOW_ATX           = 0
    SHOW_ATY           = 0
#@-others
#@@language python
#@@tabwidth -4
#@-leo
