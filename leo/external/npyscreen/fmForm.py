#@+leo-ver=5-thin
#@+node:ekr.20170428084207.174: * @file ../external/npyscreen/fmForm.py
#!/usr/bin/python
# pylint: disable=no-member
from leo.core import leoGlobals as g
assert g
#@+others
#@+node:ekr.20170428084207.175: ** Declarations
from . import proto_fm_screen_area
from . import wgwidget as widget
from . import wgbutton as button
import weakref
# from . import npyspmfuncs as pmfuncs
#import Menu
import curses
import _curses
from . import npysGlobalOptions
from . import wgwidget_proto
from . import fm_form_edit_loop as form_edit_loop
from . import util_viewhelp
from . import npysGlobalOptions as GlobalOptions
from .eveventhandler import EventHandler
from .globals import DISABLE_RESIZE_SYSTEM

#@+node:ekr.20170428084207.176: ** class _FormBase
class _FormBase(proto_fm_screen_area.ScreenArea,
        widget.InputHandler,
        wgwidget_proto._LinePrinter,
        EventHandler):
    BLANK_COLUMNS_RIGHT = 2
    BLANK_LINES_BASE = 2
    OK_BUTTON_TEXT = 'OK'
    OK_BUTTON_BR_OFFSET = (2, 6)
    OKBUTTON_TYPE = button.MiniButton
    DEFAULT_X_OFFSET = 2
    PRESERVE_SELECTED_WIDGET_DEFAULT = False  # Preserve cursor location between displays?
    FRAMED = True
    ALLOW_RESIZE = True
    FIX_MINIMUM_SIZE_WHEN_CREATED = True
    WRAP_HELP = True


    #@+others
    #@+node:ekr.20170428084207.177: *3* _FormBase.__init__
    def __init__(self, name=None, parentApp=None, framed=None, help=None, color='FORMDEFAULT',
                    widget_list=None, cycle_widgets=False, *args, **keywords):
        super(_FormBase, self).__init__(*args, **keywords)
        self.initialize_event_handling()
        self.preserve_selected_widget = self.__class__.PRESERVE_SELECTED_WIDGET_DEFAULT
        if parentApp:
            try:
                self.parentApp = weakref.proxy(parentApp)
            except Exception:
                self.parentApp = parentApp
            try:
                self.keypress_timeout = self.parentApp.keypress_timeout_default
            except AttributeError:
                pass
        if framed is None:
            self.framed = self.__class__.FRAMED
        else:
            self.framed = framed
        self.name = name
        self.editing = False
        ## OLD MENU CODE REMOVED self.__menus  = []
        self._clear_all_widgets()

        self.help = help

        self.color = color

        self.cycle_widgets = cycle_widgets

        self.set_up_handlers()
        self.set_up_exit_condition_handlers()
        if hasattr(self, 'initialWidgets'):
            self.create_widgets_from_list(self.__class__.initialWidgets)
        if widget_list:
            self.create_widgets_from_list(widget_list)
        self.create()

        if self.FIX_MINIMUM_SIZE_WHEN_CREATED:
            self.min_l = self.lines
            self.min_c = self.columns


    #@+node:ekr.20170428084207.178: *3* resize
    def resize(self):
        pass

    #@+node:ekr.20170428084207.179: *3* _FormBase._clear_all_widgets
    def _clear_all_widgets(self,):
        self._widgets__ = []
        self._widgets_by_id = {}
        self._next_w_id = 0
        self.nextrely = self.DEFAULT_NEXTRELY
        self.nextrelx = self.DEFAULT_X_OFFSET
        self.editw = 0  # Index of widget to edit.

    #@+node:ekr.20170428084207.180: *3* create_widgets_from_list
    def create_widgets_from_list(self, widget_list):
        # This code is currently experimental, and the API may change in future releases
        # (npyscreen.TextBox, {'rely': 2, 'relx': 7, 'editable': False})
        for line in widget_list:
            w_type = line[0]
            keywords = line[1]
            self.add_widget(w_type, **keywords)

    #@+node:ekr.20170428084207.181: *3* set_value
    def set_value(self, value):
        self.value = value
        for _w in self._widgets__:
            if hasattr(_w, 'when_parent_changes_value'):
                _w.when_parent_changes_value()

    #@+node:ekr.20170428084207.182: *3* _resize
    def _resize(self, *args):
        # global DISABLE_RESIZE_SYSTEM
        # EKR: This is an imported symbol, not a global!
        if DISABLE_RESIZE_SYSTEM:
            return False

        if not self.ALLOW_RESIZE:
            return False

        if hasattr(self, 'parentApp'):
            self.parentApp.resize()

        self._create_screen()
        self.resize()
        for w in self._widgets__:
            w._resize()
        self.DISPLAY()



    #@+node:ekr.20170428084207.183: *3* create
    def create(self):
        """Programmers should over-ride this in derived classes, creating widgets here"""
        pass

    #@+node:ekr.20170428084207.184: *3* set_up_handlers
    def set_up_handlers(self):
        '''FormBase.set_up_handlers.'''
        self.complex_handlers = []
        self.handlers = {
            curses.KEY_F1: self.h_display_help,
            "KEY_F(1)": self.h_display_help,
            "^O": self.h_display_help,
            "^L": self.h_display,
            curses.KEY_RESIZE: self._resize,
        }
    #@+node:ekr.20170428084207.185: *3* _FormBase.set_up_exit_condition_handlers
    def set_up_exit_condition_handlers(self):
        # What happens when widgets exit?
        # each widget will set it's how_exited value: this should
        # be used to look up the following table.

        self.how_exited_handers = {
            widget.EXITED_DOWN: self.find_next_editable,
            widget.EXITED_RIGHT: self.find_next_editable,
            widget.EXITED_UP: self.find_previous_editable,
            widget.EXITED_LEFT: self.find_previous_editable,
            widget.EXITED_ESCAPE: self.do_nothing,
            True: self.find_next_editable,  # A default value
            widget.EXITED_MOUSE: self.get_and_use_mouse_event,
            False: self.do_nothing,
            None: self.do_nothing,
            }

    #@+node:ekr.20170428084207.186: *3* _FormBase.handle_exiting_widgets
    def handle_exiting_widgets(self, condition):
        trace = False and not g.unitTesting
        trace_handlers = False
        func = self.how_exited_handers[condition]
        if trace:
            g.pr('-' * 70)
            g.trace('(_FormBase:%s) how_exited: %r %s.%s' % (
                self.__class__.__name__,
                condition,
                func.__self__.__class__.__name__ if hasattr(func, '__self__') else 'function',
                func.__name__,
            ))
            if trace_handlers:
                g.trace('_FormBase.how_exited_handlers...')
                d = self.how_exited_handers
                g.printDict({key: d.get(key).__name__ for key in d})
                # g.printDict(d)
        func()
    #@+node:ekr.20170428084207.187: *3* do_nothing
    def do_nothing(self, *args, **keywords):
        pass

    #@+node:ekr.20170428084207.188: *3* _FormBase.exit_editing
    def exit_editing(self, *args, **keywords):

        trace = False and not g.unitTesting
        self.editing = False
        try:
            if trace: g.trace('(_FormBase)')
            self._widgets__[self.editw].entry_widget.editing = False
        except Exception:
            pass
        try:
            self._widgets__[self.editw].editing = False
        except Exception:
            pass

    #@+node:ekr.20170428084207.189: *3* adjust_widgets
    def adjust_widgets(self):
        """This method can be overloaded by derived classes. It is called when editing any widget, as opposed to
        the while_editing() method, which may only be called when moving between widgets.  Since it is called for
        every keypress, and perhaps more, be careful when selecting what should be done here."""


    #@+node:ekr.20170428084207.190: *3* while_editing
    def while_editing(self, *args, **keywords):
        """This function gets called during the edit loop, on each iteration
        of the loop.  It does nothing: it is here to make customizing the loop
        as easy as overriding this function. A proxy to the currently selected widget is
        passed to the function."""

    #@+node:ekr.20170428084207.191: *3* on_screen
    def on_screen(self):
        # is the widget in editw on screen at the moment?
        # if not, alter screen so that it is.

        w = weakref.proxy(self._widgets__[self.editw])

        max_y, max_x = self._max_physical()

        w_my, w_mx = w.calculate_area_needed()

        # always try to show the top of the screen.
        self.show_from_y = 0
        self.show_from_x = 0

        while w.rely + w_my - 1 > self.show_from_y + max_y:
            self.show_from_y += 1

        while w.rely < self.show_from_y:
            self.show_from_y -= 1


        while w.relx + w_mx - 1 > self.show_from_x + max_x:
            self.show_from_x += 1

        while w.relx < self.show_from_x:
            self.show_from_x -= 1

    #@+node:ekr.20170428084207.192: *3* h_display_help
    def h_display_help(self, input):
        if self.help == None: return
        if self.name:
            help_name = "%s Help" % (self.name)
        else: help_name = None
        curses.flushinp()
        util_viewhelp.view_help(self.help, title=help_name, autowrap=self.WRAP_HELP)
        #select.ViewText(self.help, name=help_name)
        self.display()
        return True

    #@+node:ekr.20170428084207.193: *3* _FormBase.DISPLAY
    def DISPLAY(self):

        # g.trace('===== (_FormBase)', self.display)
        self.curses_pad.redrawwin()
        self.erase()
        self.display()
        self.display(clear=False)
        if self.editing and self.editw is not None:
            self._widgets__[self.editw].display()


    #@+node:ekr.20170428084207.194: *3* h_display
    def h_display(self, input):
        self._resize()
        self.DISPLAY()

    #@+node:ekr.20170428084207.195: *3* safe_get_mouse_event
    def safe_get_mouse_event(self):
        try:
            mouse_event = curses.getmouse()
            return mouse_event
        except _curses.error:
            return None

    #@+node:ekr.20170428084207.196: *3* get_and_use_mouse_event
    def get_and_use_mouse_event(self):
        mouse_event = self.safe_get_mouse_event()
        if mouse_event:
            self.use_mouse_event(mouse_event)

    #@+node:ekr.20170428084207.197: *3* use_mouse_event
    def use_mouse_event(self, mouse_event):
        wg = self.find_mouse_handler(mouse_event)
        if wg:
            self.set_editing(wg)
            if hasattr(wg, 'handle_mouse_event'):
                wg.handle_mouse_event(mouse_event)
        else:
            curses.beep()

    #@+node:ekr.20170428084207.198: *3* find_mouse_handler
    def find_mouse_handler(self, mouse_event):
        #mouse_id, x, y, z, bstate = mouse_event
        for wd in self._widgets__:
            try:
                if wd.intersted_in_mouse_event(mouse_event) == True:
                    return wd
            except AttributeError:
                pass
        return None

    #@+node:ekr.20170428084207.199: *3* _FormBase.set_editing
    def set_editing(self, wdg):
        try:
            self.editw = self._widgets__.index(wdg)
        except ValueError:
            pass


    #@+node:ekr.20170428084207.200: *3* _FormBase.find_next_editable
    def find_next_editable(self, *args):
        # This is the ONLY usable version of this method.
        trace = False and not g.unitTesting
        old_n = self.editw
        if not self.cycle_widgets:
            r = list(range(self.editw + 1, len(self._widgets__)))
        else:
            r = list(range(self.editw + 1, len(self._widgets__))) + list(range(0, self.editw))
        for n in r:
            if self._widgets__[n].editable and not self._widgets__[n].hidden:
                self.editw = n
                break
        if trace:
            w = self._widgets__[n]
            g.trace('(_FormBase:%s) FOUND: %s --> %s %s' % (
                self.__class__.__name__, old_n, n, w.__class__.__name__))
        self.display()
    #@+node:ekr.20170428084207.201: *3* _FormBase.find_previous_editable
    def find_previous_editable(self, *args):
        if self.editw != 0:
            # remember that xrange does not return the 'last' value,
            # so go to -1, not 0! (fence post error in reverse)
            for n in range(self.editw - 1, -1, -1):
                if self._widgets__[n].editable and not self._widgets__[n].hidden:
                    self.editw = n
                    break

    #def widget_useable_space(self, rely=0, relx=0):
    #    #Slightly misreports space available.
    #    mxy, mxx = self.lines-1, self.columns-1
    #    return (mxy-1-rely, mxx-1-relx)

    #@+node:ekr.20170428084207.202: *3* center_on_display
    def center_on_display(self):
        my, mx = self._max_physical()
        if self.lines < my:
            self.show_aty = (my - self.lines) // 2
        else:
            self.show_aty = 0

        if self.columns < mx:
            self.show_atx = (mx - self.columns) // 2
        else:
            self.show_atx = 0


    #@+node:ekr.20170428084207.203: *3* _FormBase.display
    def display(self, clear=False):
        #APPLICATION_THEME_MANAGER.setTheme(self)
        if curses.has_colors() and not npysGlobalOptions.DISABLE_ALL_COLORS:
            self.curses_pad.attrset(0)
            color_attribute = self.theme_manager.findPair(self, self.color)
            self.curses_pad.bkgdset(' ', color_attribute)
            self.curses_pad.attron(color_attribute)
        self.curses_pad.erase()
        self.draw_form()
        for w in [wg for wg in self._widgets__ if wg.hidden]:
            w.clear()
        for w in [wg for wg in self._widgets__ if not wg.hidden]:
            w.update(clear=clear)

        self.refresh()

    #@+node:ekr.20170428084207.204: *3* draw_title_and_help
    def draw_title_and_help(self):
        try:
            if self.name:
                _title = self.name[: (self.columns - 4)]
                _title = ' ' + str(_title) + ' '
                #self.curses_pad.addstr(0,1, ' '+str(_title)+' ')
                if isinstance(_title, bytes):
                    _title = _title.decode('utf-8', 'replace')
                self.add_line(0, 1,
                    _title,
                    self.make_attributes_list(_title, curses.A_NORMAL),
                    self.columns - 4
                    )
        except Exception:
            pass

        if self.help and self.editing:
            try:
                help_advert = " Help: F1 or ^O "
                if isinstance(help_advert, bytes):
                    help_advert = help_advert.decode('utf-8', 'replace')
                self.add_line(
                 0, self.curses_pad.getmaxyx()[1] - len(help_advert) - 2,
                 help_advert,
                 self.make_attributes_list(help_advert, curses.A_NORMAL),
                 len(help_advert)
                 )
            except Exception:
                pass

    #@+node:ekr.20170428084207.205: *3* draw_form
    def draw_form(self):
        if self.framed:
            if curses.has_colors() and not GlobalOptions.DISABLE_ALL_COLORS:
                self.curses_pad.attrset(0)
                self.curses_pad.bkgdset(' ', curses.A_NORMAL | self.theme_manager.findPair(self, self.color))
            self.curses_pad.border()
            self.draw_title_and_help()


    #@+node:ekr.20170428084207.206: *3* add_widget
    def add_widget(self, widgetClass, w_id=None, max_height=None, rely=None, relx=None, *args, **keywords):
        """Add a widget to the form.  The form will do its best to decide on placing, unless you override it.
        The form of this function is add_widget(WidgetClass, ....) with any arguments or keywords supplied to
        the widget. The widget will be added to self._widgets__

        It is safe to use the return value of this function to keep hold of the widget, since that is a weak
        reference proxy, but it is not safe to keep hold of self._widgets__"""

        if rely is None:
            rely = self.nextrely
        if relx is None:
            relx = self.nextrelx

        if max_height is False:
            max_height = self.curses_pad.getmaxyx()[0] - rely - 1

        _w = widgetClass(self,
                rely=rely,
                relx=relx,
                max_height=max_height,
                * args, **keywords)

        self.nextrely = _w.height + _w.rely
        self._widgets__.append(_w)
        w_proxy = weakref.proxy(_w)
        if not w_id:
            w_id = self._next_w_id
            self._next_w_id += 1
        self._widgets_by_id[w_id] = w_proxy

        return w_proxy

    #@+node:ekr.20170428084207.207: *3* get_widget
    def get_widget(self, w_id):
        return self._widgets_by_id[w_id]

    add = add_widget

    #@-others
#@+node:ekr.20170428084207.208: ** class FormBaseNew
class FormBaseNew(form_edit_loop.FormNewEditLoop, _FormBase):
    # use the new-style edit loop.
    pass

#@+node:ekr.20170428084207.209: ** class Form
class Form(form_edit_loop.FormDefaultEditLoop, _FormBase,):
    #use the old-style edit loop

    def resize(self):
        super(Form, self).resize()
        self.move_ok_button()
#@+node:ekr.20170428084207.211: ** class FormBaseNewExpanded
class FormBaseNewExpanded(form_edit_loop.FormNewEditLoop, _FormBase):
    BLANK_LINES_BASE = 1
    OK_BUTTON_BR_OFFSET = (1, 6)
    # use the new-style edit loop.

#@+node:ekr.20170428084207.212: ** class FormExpanded
class FormExpanded(form_edit_loop.FormDefaultEditLoop, _FormBase,):
    BLANK_LINES_BASE = 1
    OK_BUTTON_BR_OFFSET = (1, 6)
    #use the old-style edit loop





#@+node:ekr.20170428084207.213: ** class TitleForm
class TitleForm(Form):
    """A form without a box, just a title line"""
    BLANK_LINES_BASE = 1
    DEFAULT_X_OFFSET = 1
    DEFAULT_NEXTRELY = 1
    BLANK_COLUMNS_RIGHT = 0
    OK_BUTTON_BR_OFFSET = (1, 6)
    #OKBUTTON_TYPE = button.MiniButton
    #DEFAULT_X_OFFSET = 1
    #@+others
    #@+node:ekr.20170428084207.214: *3* draw_form
    def draw_form(self):
        MAXY, MAXX = self.curses_pad.getmaxyx()
        self.curses_pad.hline(0, 0, curses.ACS_HLINE, MAXX)
        self.draw_title_and_help()

    #@-others
#@+node:ekr.20170428084207.215: ** class TitleFooterForm
class TitleFooterForm(TitleForm):
    BLANK_LINES_BASE = 1
    #@+others
    #@+node:ekr.20170428084207.216: *3* draw_form
    def draw_form(self):
        MAXY, MAXX = self.curses_pad.getmaxyx()

        if self.editing:
            self.curses_pad.hline(MAXY - 1, 0, curses.ACS_HLINE,
                    MAXX - self.__class__.OK_BUTTON_BR_OFFSET[1] - 1)
        else:
            self.curses_pad.hline(MAXY - 1, 0, curses.ACS_HLINE, MAXX - 1)

        super(TitleFooterForm, self).draw_form()

    #@-others
#@+node:ekr.20170428084207.217: ** class SplitForm
class SplitForm(Form):
    MOVE_LINE_ON_RESIZE = False
    """Just the same as the Title Form, but with a horizontal line"""
    #@+others
    #@+node:ekr.20170428084207.218: *3* __init__
    def __init__(self, draw_line_at=None, *args, **keywords):
        super(SplitForm, self).__init__(*args, **keywords)
        if not hasattr(self, 'draw_line_at'):
            if draw_line_at != None:
                self.draw_line_at = draw_line_at
            else:
                self.draw_line_at = self.get_half_way()

    #@+node:ekr.20170428084207.219: *3* draw_form
    def draw_form(self,):
        MAXY, MAXX = self.curses_pad.getmaxyx()
        super(SplitForm, self).draw_form()
        self.curses_pad.hline(self.draw_line_at, 1, curses.ACS_HLINE, MAXX - 2)

    #@+node:ekr.20170428084207.220: *3* get_half_way
    def get_half_way(self):
        return self.curses_pad.getmaxyx()[0] // 2

    #@+node:ekr.20170428084207.221: *3* resize
    def resize(self):
        super(SplitForm, self).resize()
        if self.MOVE_LINE_ON_RESIZE:
            self.draw_line_at = self.get_half_way()


    #@-others
#@+node:ekr.20170428084207.222: ** blank_terminal
def blank_terminal():
    F = _FormBase(framed=False)
    F.erase()
    F.display()


#@-others
#@@language python
#@@tabwidth -4
#@-leo
