#@+leo-ver=5-thin
#@+node:ekr.20170428084207.223: * @file ../external/npyscreen/fmFormMultiPage.py
## Very, very experimental. Do NOT USE.
from leo.core import leoGlobals as g
assert g
#@+others
#@+node:ekr.20170428084207.224: ** Declarations
import curses
from . import fmForm
from .wgwidget import NotEnoughSpaceForWidget
from . import wgNMenuDisplay


#@+node:ekr.20170428084207.225: ** class FormMultiPage
class FormMultiPage(fmForm.FormBaseNew):
    page_info_pre_pages_display = '[ '
    page_info_post_pages_display = ' ]'
    page_info_pages_name = 'Page'
    page_info_out_of = 'of'
    #@+others
    #@+node:ekr.20170428084207.226: *3* __init__
    def __init__(self, display_pages=True, pages_label_color='NORMAL', *args, **keywords):
        self.display_pages = display_pages
        self.pages_label_color = pages_label_color
        super(FormMultiPage, self).__init__(*args, **keywords)
        self.switch_page(0)

    #@+node:ekr.20170428084207.227: *3* draw_form
    def draw_form(self, *args, **keywords):
        super(FormMultiPage, self).draw_form(*args, **keywords)
        self.display_page_number()

    #@+node:ekr.20170428084207.228: *3* _resize
    def _resize(self, *args):
        if not self.ALLOW_RESIZE:
            return False

        if hasattr(self, 'parentApp'):
            self.parentApp.resize()

        self._create_screen()
        self.resize()
        for page in self._pages__:
            for w in page:
                w._resize()
        self.DISPLAY()


    #@+node:ekr.20170428084207.229: *3* display_page_number
    def display_page_number(self):
        if not self.display_pages:
            return False

        if len(self._pages__) > 1:
            display_text = "%s%s %s %s %s%s" % (
                self.page_info_pre_pages_display,
                self.page_info_pages_name,
                self._active_page + 1,
                self.page_info_out_of,
                len(self._pages__),
                self.page_info_post_pages_display,
            )
        # for python2
            if isinstance(display_text, bytes):
                display_text = display_text.decode('utf-8', 'replace')

            maxy, maxx = self.curses_pad.getmaxyx()

            if (maxx - 5) <= len(display_text):
                # then give up.
                return False

            self.add_line(
                maxy - 1,
                maxx - len(display_text) - 2,
                display_text,
                self.make_attributes_list(display_text,
                     curses.A_NORMAL | self.theme_manager.findPair(self,
                                                                  self.pages_label_color)),
                maxx - len(display_text) - 2,
            )


    #@+node:ekr.20170428084207.230: *3* add_widget_intelligent
    def add_widget_intelligent(self, *args, **keywords):
        try:
            return self.add_widget(*args, **keywords)
        except NotEnoughSpaceForWidget:
            self.add_page()
            return self.add_widget(*args, **keywords)


    #@+node:ekr.20170428084207.231: *3* _clear_all_widgets
    def _clear_all_widgets(self,):
        super(FormMultiPage, self)._clear_all_widgets()
        self._pages__ = [[],]
        self._active_page = 0
        self.switch_page(self._active_page, display=False)

    #@+node:ekr.20170428084207.232: *3* FormMultiPage.switch_page
    def switch_page(self, page, display=True):
        self._widgets__ = self._pages__[page]
        self._active_page = page
        self.editw = 0
        if display:
            self.display(clear=True)

    #@+node:ekr.20170428084207.233: *3* add_page
    def add_page(self):
        self._pages__.append([])
        page_number = len(self._pages__) - 1
        self.nextrely = self.DEFAULT_NEXTRELY
        self.nextrelx = self.DEFAULT_X_OFFSET
        self.switch_page(page_number, display=False)
        return page_number

    #@+node:ekr.20170428084207.234: *3* FormMultiPage.find_next_editable
    def find_next_editable(self, *args):

        # g.trace('===== (FormMultiPage)')
        if not self.editw == len(self._widgets__):
            value_changed = False
            if not self.cycle_widgets:
                r = list(range(self.editw + 1, len(self._widgets__)))
            else:
                r = list(range(self.editw + 1, len(self._widgets__))) + list(range(0, self.editw))
            for n in r:
                if self._widgets__[n].editable and not self._widgets__[n].hidden:
                    self.editw = n
                    value_changed = True
                    break
            if not value_changed:
                if self._active_page < len(self._pages__) - 1:
                    self.switch_page(self._active_page + 1)
        self.display()


    #@+node:ekr.20170428084207.235: *3* FormMultiPage.find_previous_editable
    def find_previous_editable(self, *args):
        if self.editw == 0:
            if self._active_page > 0:
                self.switch_page(self._active_page - 1)

        if not self.editw == 0:
            # remember that xrange does not return the 'last' value,
            # so go to -1, not 0! (fence post error in reverse)
            for n in range(self.editw - 1, -1, -1):
                if self._widgets__[n].editable and not self._widgets__[n].hidden:
                    self.editw = n
                    break


    #@-others
#@+node:ekr.20170428084207.236: ** class FormMultiPageAction
class FormMultiPageAction(FormMultiPage):
    CANCEL_BUTTON_BR_OFFSET = (2, 12)
    OK_BUTTON_TEXT = "OK"
    CANCEL_BUTTON_TEXT = "Cancel"

    #@+others
    #@+node:ekr.20170428084207.237: *3* FormMultiPageAction.on_ok
    def on_ok(self):
        pass

    #@+node:ekr.20170428084207.238: *3* FormMultiPageAction.on_cancel
    def on_cancel(self):
        pass

    #@+node:ekr.20170428084207.239: *3* FormMultiPageAction.pre_edit_loop
    def pre_edit_loop(self):
        self._page_for_buttons = len(self._pages__) - 1
        self.switch_page(self._page_for_buttons)

        # Add ok and cancel buttons. Will remove later
        tmp_rely, tmp_relx = self.nextrely, self.nextrelx

        c_button_text = self.CANCEL_BUTTON_TEXT
        cmy, cmx = self.curses_pad.getmaxyx()
        cmy -= self.__class__.CANCEL_BUTTON_BR_OFFSET[0]
        cmx -= len(c_button_text) + self.__class__.CANCEL_BUTTON_BR_OFFSET[1]
        self.c_button = self.add_widget(self.__class__.OKBUTTON_TYPE, name=c_button_text, rely=cmy, relx=cmx, use_max_space=True)
        self._c_button_postion = len(self._widgets__) - 1
        self.c_button.update()

        my, mx = self.curses_pad.getmaxyx()
        ok_button_text = self.OK_BUTTON_TEXT
        my -= self.__class__.OK_BUTTON_BR_OFFSET[0]
        mx -= len(ok_button_text) + self.__class__.OK_BUTTON_BR_OFFSET[1]
        self.ok_button = self.add_widget(self.__class__.OKBUTTON_TYPE, name=ok_button_text, rely=my, relx=mx, use_max_space=True)
        self._ok_button_postion = len(self._widgets__) - 1
        # End add buttons
        self.nextrely, self.nextrelx = tmp_rely, tmp_relx
        self.switch_page(0)

    #@+node:ekr.20170428084207.240: *3* FormMultiPageAction._during_edit_loop
    def _during_edit_loop(self):
        if self.ok_button.value or self.c_button.value:
            self.editing = False

        if self.ok_button.value:
            self.ok_button.value = False
            self.edit_return_value = self.on_ok()
        elif self.c_button.value:
            self.c_button.value = False
            self.edit_return_value = self.on_cancel()

    #@+node:ekr.20170428084207.241: *3* FormMultiPageAction.resize
    def resize(self):
        super(FormMultiPageAction, self).resize()
        self.move_ok_button()

    #@+node:ekr.20170428084207.242: *3* FormMultiPageAction.move_ok_button
    def move_ok_button(self):
        if hasattr(self, 'ok_button'):
            my, mx = self.curses_pad.getmaxyx()
            my -= self.__class__.OK_BUTTON_BR_OFFSET[0]
            mx -= len(self.__class__.OK_BUTTON_TEXT) + self.__class__.OK_BUTTON_BR_OFFSET[1]
            self.ok_button.relx = mx
            self.ok_button.rely = my
        if hasattr(self, 'c_button'):
            c_button_text = self.CANCEL_BUTTON_TEXT
            cmy, cmx = self.curses_pad.getmaxyx()
            cmy -= self.__class__.CANCEL_BUTTON_BR_OFFSET[0]
            cmx -= len(c_button_text) + self.__class__.CANCEL_BUTTON_BR_OFFSET[1]
            self.c_button.rely = cmy
            self.c_button.relx = cmx


    #@+node:ekr.20170428084207.243: *3* FormMultiPageAction.post_edit_loop
    def post_edit_loop(self):
        self.switch_page(self._page_for_buttons)
        self.ok_button.destroy()
        self.c_button.destroy()
        del self._widgets__[self._ok_button_postion]
        del self.ok_button
        del self._widgets__[self._c_button_postion]
        del self.c_button
        #self.nextrely, self.nextrelx = tmp_rely, tmp_relx
        self.display()
        self.editing = False

        return self.edit_return_value


    #@-others
#@+node:ekr.20170428084207.244: ** class FormMultiPageWithMenus
class FormMultiPageWithMenus(FormMultiPage, wgNMenuDisplay.HasMenus):
    #@+others
    #@+node:ekr.20170428084207.245: *3* __init__
    def __init__(self, *args, **keywords):
        super(FormMultiPageWithMenus, self).__init__(*args, **keywords)
        self.initialize_menus()

    #@-others
#@+node:ekr.20170428084207.246: ** class FormMultiPageActionWithMenus
class FormMultiPageActionWithMenus(FormMultiPageAction, wgNMenuDisplay.HasMenus):
    #@+others
    #@+node:ekr.20170428084207.247: *3* __init__
    def __init__(self, *args, **keywords):
        super(FormMultiPageActionWithMenus, self).__init__(*args, **keywords)
        self.initialize_menus()
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@nobeautify
#@-leo
