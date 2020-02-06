#@+leo-ver=5-thin
#@+node:ekr.20170428084207.332: * @file ../external/npyscreen/muNewMenu.py
#!/usr/bin/env python
# encoding: utf-8
#@+others
#@+node:ekr.20170428084207.333: ** Declarations
import weakref


#@+node:ekr.20170428084207.334: ** class NewMenu
class NewMenu:
    """docstring for NewMenu"""
    #@+others
    #@+node:ekr.20170428084207.335: *3* __init__
    def __init__(self, name=None, shortcut=None, preDisplayFunction=None, pdfuncArguments=None, pdfuncKeywords=None):
        self.name      = name
        self._menuList = []
        self.enabled   = True
        self.shortcut  = shortcut
        self.pre_display_function = preDisplayFunction
        self.pdfunc_arguments= pdfuncArguments or ()
        self.pdfunc_keywords = pdfuncKeywords  or {}

    #@+node:ekr.20170428084207.336: *3* addItemsFromList
    def addItemsFromList(self, item_list):
        for l in item_list:
            if isinstance(l, MenuItem):
                self.addNewSubmenu(*l)
            else:
                self.addItem(*l)

    #@+node:ekr.20170428084207.337: *3* addItem
    def addItem(self, *args, **keywords):
        _itm = MenuItem(*args, **keywords)
        self._menuList.append(_itm)

    #@+node:ekr.20170428084207.338: *3* addSubmenu
    def addSubmenu(self, submenu):
        "Not recommended. Use addNewSubmenu instead"
        # _itm = submenu
        self._menuList.append(submenu)

    #@+node:ekr.20170428084207.339: *3* addNewSubmenu
    def addNewSubmenu(self, *args, **keywords):
        _mnu = NewMenu(*args, **keywords)
        self._menuList.append(_mnu)
        return weakref.proxy(_mnu)

    #@+node:ekr.20170428084207.340: *3* getItemObjects
    def getItemObjects(self):
        return [itm for itm in self._menuList if itm.enabled]

    #@+node:ekr.20170428084207.341: *3* do_pre_display_function
    def do_pre_display_function(self):
        if self.pre_display_function:
            return self.pre_display_function(*self.pdfunc_arguments, **self.pdfunc_keywords)

    #@-others
#@+node:ekr.20170428084207.342: ** class MenuItem
class MenuItem:
    """docstring for MenuItem"""
    #@+others
    #@+node:ekr.20170428084207.343: *3* __init__
    def __init__(self, text='', onSelect=None, shortcut=None, document=None, arguments=None, keywords=None):
        self.setText(text)
        self.setOnSelect(onSelect)
        self.setDocumentation(document)
        self.shortcut = shortcut
        self.enabled = True
        self.arguments = arguments or ()
        self.keywords = keywords or {}

    #@+node:ekr.20170428084207.344: *3* setText
    def setText(self, text):
        self._text = text

    #@+node:ekr.20170428084207.345: *3* getText
    def getText(self):
        return self._text

    #@+node:ekr.20170428084207.346: *3* setOnSelect
    def setOnSelect(self, onSelect):
        self.onSelectFunction = onSelect

    #@+node:ekr.20170428084207.347: *3* setDocumentation
    def setDocumentation(self, document):
        self._help = document

    #@+node:ekr.20170428084207.348: *3* getDocumentation
    def getDocumentation(self):
        return self._help

    #@+node:ekr.20170428084207.349: *3* getHelp
    def getHelp(self):
        return self._help

    #@+node:ekr.20170428084207.350: *3* do
    def do(self):
        if self.onSelectFunction:
            return self.onSelectFunction(*self.arguments, **self.keywords)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
