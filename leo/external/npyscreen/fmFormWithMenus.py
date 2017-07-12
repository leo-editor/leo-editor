#@+leo-ver=5-thin
#@+node:ekr.20170428084207.285: * @file ../external/npyscreen/fmFormWithMenus.py
#!/usr/bin/env python
# encoding: utf-8
#@+others
#@+node:ekr.20170428084207.286: ** Declarations
import curses
from . import fmForm
from . import fmActionForm
from . import fmActionFormV2
from . import wgNMenuDisplay

#@+node:ekr.20170428084207.287: ** class FormBaseNewWithMenus
class FormBaseNewWithMenus(fmForm.FormBaseNew, wgNMenuDisplay.HasMenus):
    """The FormBaseNew class, but with a handling system for menus as well.  See the HasMenus class for details."""
    #@+others
    #@+node:ekr.20170428084207.288: *3* __init__
    def __init__(self, *args, **keywords):
        super(FormBaseNewWithMenus, self).__init__(*args, **keywords)
        self.initialize_menus()

    #@+node:ekr.20170428084207.289: *3* display_menu_advert_at
    def display_menu_advert_at(self):
        return self.lines-1, 1

    #@+node:ekr.20170428084207.290: *3* draw_form
    def draw_form(self):
        super(FormBaseNewWithMenus, self).draw_form()
        menu_advert = " " + self.__class__.MENU_KEY + ": Menu "
        if isinstance(menu_advert, bytes):
            menu_advert = menu_advert.decode('utf-8', 'replace')
        y, x = self.display_menu_advert_at()
        self.add_line(y, x,
            menu_advert,
            self.make_attributes_list(menu_advert, curses.A_NORMAL),
            self.columns - x - 1
            )


    #@-others
#@+node:ekr.20170428084207.291: ** class FormWithMenus
class FormWithMenus(fmForm.Form, wgNMenuDisplay.HasMenus):
    """The Form class, but with a handling system for menus as well.  See the HasMenus class for details."""
    #@+others
    #@+node:ekr.20170428084207.292: *3* __init__
    def __init__(self, *args, **keywords):
        super(FormWithMenus, self).__init__(*args, **keywords)
        self.initialize_menus()

    #@+node:ekr.20170428084207.293: *3* display_menu_advert_at
    def display_menu_advert_at(self):
        return self.lines-1, 1

    #@+node:ekr.20170428084207.294: *3* draw_form
    def draw_form(self):
        super(FormWithMenus, self).draw_form()
        menu_advert = " " + self.__class__.MENU_KEY + ": Menu "
        y, x = self.display_menu_advert_at()
        if isinstance(menu_advert, bytes):
            menu_advert = menu_advert.decode('utf-8', 'replace')
        self.add_line(y, x,
            menu_advert,
            self.make_attributes_list(menu_advert, curses.A_NORMAL),
            self.columns - x - 1
            )

    #@-others
# The following class does not inherit from FormWithMenus and so some code is duplicated.
# The pig is getting to inherit edit() from ActionForm, but draw_form from FormWithMenus
#@+node:ekr.20170428084207.295: ** class ActionFormWithMenus
class ActionFormWithMenus(fmActionForm.ActionForm, wgNMenuDisplay.HasMenus):
    #@+others
    #@+node:ekr.20170428084207.296: *3* __init__
    def __init__(self, *args, **keywords):
        super(ActionFormWithMenus, self).__init__(*args, **keywords)
        self.initialize_menus()

    #@+node:ekr.20170428084207.297: *3* display_menu_advert_at
    def display_menu_advert_at(self):
        return self.lines-1, 1

    #@+node:ekr.20170428084207.298: *3* draw_form
    def draw_form(self):
        super(ActionFormWithMenus, self).draw_form()
        menu_advert = " " + self.__class__.MENU_KEY + ": Menu "
        y, x = self.display_menu_advert_at()

        if isinstance(menu_advert, bytes):
            menu_advert = menu_advert.decode('utf-8', 'replace')
        self.add_line(y, x,
            menu_advert,
            self.make_attributes_list(menu_advert, curses.A_NORMAL),
            self.columns - x - 1
            )

    #@-others
#@+node:ekr.20170428084207.299: ** class ActionFormV2WithMenus
class ActionFormV2WithMenus(fmActionFormV2.ActionFormV2, wgNMenuDisplay.HasMenus):
    #@+others
    #@+node:ekr.20170428084207.300: *3* __init__
    def __init__(self, *args, **keywords):
        super(ActionFormV2WithMenus, self).__init__(*args, **keywords)
        self.initialize_menus()



    #@-others
#@+node:ekr.20170428084207.301: ** class SplitFormWithMenus
class SplitFormWithMenus(fmForm.SplitForm, FormWithMenus):
    """Just the same as the Title Form, but with a horizontal line"""
    #@+others
    #@+node:ekr.20170428084207.302: *3* draw_form
    def draw_form(self):
        super(SplitFormWithMenus, self).draw_form()

    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
