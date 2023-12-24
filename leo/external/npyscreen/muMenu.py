#@+leo-ver=5-thin
#@+node:ekr.20170428084207.324: * @file ../external/npyscreen/muMenu.py
#!/usr/bin/python
# encoding: utf-8

#@+others
#@+node:ekr.20170428084207.325: ** Declarations
# import sys
# import os
from . import wgmultiline
from . import fmForm
# import weakref


#@+node:ekr.20170428084207.326: ** class Menu
class Menu:
    "This class is obsolete and Deprecated.  Use NewMenu instead."

    #@+others
    #@+node:ekr.20170428084207.327: *3* __init__
    def __init__(self, name=None, show_atx=None, show_aty=None):
        self.__menu_items = []
        self.name = name
        self.__show_atx = show_atx
        self.__show_aty = show_aty

    #@+node:ekr.20170428084207.328: *3* before_item_select
    def before_item_select(self):
        pass

    #@+node:ekr.20170428084207.329: *3* add_item
    def add_item(self, text, func):
        self.__menu_items.append((text, func))

    #@+node:ekr.20170428084207.330: *3* set_menu
    def set_menu(self, pairs):
        """Pass in a list of pairs of text labels and functions"""
        self.__menu_items = []
        for pair in pairs:
            self.add_item(pair[0], pair[1])

    #@+node:ekr.20170428084207.331: *3* Menu.edit
    def edit(self, *args, **keywords):
        """Display choice to user, execute function associated"""

        menu_text = [x[0] for x in self.__menu_items]

        longest_text = 0
        #Slightly different layout if we are showing a title
        if self.name: longest_text = len(self.name) + 2
        for item in menu_text:
            if len(item) > longest_text:
                longest_text = len(item)

        height = len(menu_text)
        if self.name:
            height += 3
        else:
            height += 2

        if height > 14:
            height = 13

        atx = self.__show_atx or 20
        aty = self.__show_aty or 2

        popup = fmForm.Form(name=self.name,
            lines=height, columns=longest_text + 4,
                show_aty=aty, show_atx=atx,)
        if not self.name: popup.nextrely = 1
        l = popup.add(wgmultiline.MultiLine,
                        values=menu_text,
                        #exit_left=True,
                        return_exit=True)

        popup.display()
        l.edit()
        if l.value is not None:
            self.before_item_select()
            self.__menu_items[l.value][1]()

    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
