#@+leo-ver=5-thin
#@+node:ekr.20170428084207.248: * @file ../external/npyscreen/fmFormMutt.py
#/usr/bin/env python
#@+others
#@+node:ekr.20170428084207.249: ** Declarations
import curses
from . import fmForm
from . import fmFormWithMenus
from . import wgtextbox
from . import wgmultiline
#import grid
#import editmultiline


#@+node:ekr.20170428084207.250: ** class FormMutt
class FormMutt(fmForm.FormBaseNew):
    BLANK_LINES_BASE     = 0
    BLANK_COLUMNS_RIGHT  = 0
    DEFAULT_X_OFFSET = 2
    FRAMED = False
    MAIN_WIDGET_CLASS   = wgmultiline.MultiLine
    MAIN_WIDGET_CLASS_START_LINE = 1
    STATUS_WIDGET_CLASS = wgtextbox.Textfield
    STATUS_WIDGET_X_OFFSET = 0
    COMMAND_WIDGET_CLASS= wgtextbox.Textfield
    COMMAND_WIDGET_NAME = None
    COMMAND_WIDGET_BEGIN_ENTRY_AT = None
    COMMAND_ALLOW_OVERRIDE_BEGIN_ENTRY_AT = True
    #MAIN_WIDGET_CLASS = grid.SimpleGrid
    #MAIN_WIDGET_CLASS = editmultiline.MultiLineEdit
    #@+others
    #@+node:ekr.20170428084207.251: *3* __init__
    def __init__(self, cycle_widgets = True, *args, **keywords):
        super(FormMutt, self).__init__(cycle_widgets=cycle_widgets, *args, **keywords)


    #@+node:ekr.20170428084207.252: *3* draw_form
    def draw_form(self):
        MAXY, MAXX = self.lines, self.columns #self.curses_pad.getmaxyx()
        self.curses_pad.hline(0, 0, curses.ACS_HLINE, MAXX-1)
        self.curses_pad.hline(MAXY-2-self.BLANK_LINES_BASE, 0, curses.ACS_HLINE, MAXX-1)

    #@+node:ekr.20170428084207.253: *3* create
    def create(self):

        MAXY = self.lines

        self.wStatus1 = self.add(self.__class__.STATUS_WIDGET_CLASS,  rely=0,
                                        relx=self.__class__.STATUS_WIDGET_X_OFFSET,
                                        editable=False,
                                        )

        if self.__class__.MAIN_WIDGET_CLASS:
            self.wMain    = self.add(self.__class__.MAIN_WIDGET_CLASS,
                                            rely=self.__class__.MAIN_WIDGET_CLASS_START_LINE,
                                            relx=0,     max_height = -2,
                                            )
        self.wStatus2 = self.add(self.__class__.STATUS_WIDGET_CLASS,  rely=MAXY-2-self.BLANK_LINES_BASE,
                                        relx=self.__class__.STATUS_WIDGET_X_OFFSET,
                                        editable=False,
                                        )

        if not self.__class__.COMMAND_WIDGET_BEGIN_ENTRY_AT:
            self.wCommand = self.add(self.__class__.COMMAND_WIDGET_CLASS, name=self.__class__.COMMAND_WIDGET_NAME,
                                    rely = MAXY-1-self.BLANK_LINES_BASE, relx=0,)
        else:
            self.wCommand = self.add(
                self.__class__.COMMAND_WIDGET_CLASS, name=self.__class__.COMMAND_WIDGET_NAME,
                                    rely = MAXY-1-self.BLANK_LINES_BASE, relx=0,
                                    begin_entry_at = self.__class__.COMMAND_WIDGET_BEGIN_ENTRY_AT,
                                    allow_override_begin_entry_at = self.__class__.COMMAND_ALLOW_OVERRIDE_BEGIN_ENTRY_AT
                                    )

        self.wStatus1.important = True
        self.wStatus2.important = True
        self.nextrely = 2

    #@+node:ekr.20170428084207.254: *3* h_display
    def h_display(self, input):
        super(FormMutt, self).h_display(input)
        if hasattr(self, 'wMain'):
            if not self.wMain.hidden:
                self.wMain.display()

    #@+node:ekr.20170428084207.255: *3* resize
    def resize(self):
        super(FormMutt, self).resize()
        MAXY = self.lines
        self.wStatus2.rely = MAXY-2-self.BLANK_LINES_BASE
        self.wCommand.rely = MAXY-1-self.BLANK_LINES_BASE

    #@-others
#@+node:ekr.20170428084207.256: ** class FormMuttWithMenus
class FormMuttWithMenus(FormMutt, fmFormWithMenus.FormBaseNewWithMenus):
    #@+others
    #@+node:ekr.20170428084207.257: *3* __init__
    def __init__(self, *args, **keywords):
        super(FormMuttWithMenus, self).__init__(*args, **keywords)
        self.initialize_menus()
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
