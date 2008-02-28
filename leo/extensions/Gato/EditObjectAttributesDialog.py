#!/usr/bin/env python
################################################################################
#
#       This file is part of Gato (Graph Algorithm Toolbox) 
#       You can find more information at 
#       http://gato.sf.net
#
#	file:   EditObjectAttributesDialog.py
#	author: Alexander Schliep (schliep@molgen.mpg.de)
#
#       Copyright (C) 1998-2005, Alexander Schliep, Winfried Hochstaettler and 
#       Copyright 1998-2001 ZAIK/ZPR, Universitaet zu Koeln
#                                   
#       Contact: schliep@molgen.mpg.de, wh@zpr.uni-koeln.de             
#
#       Information: http://gato.sf.net
#
#       This library is free software; you can redistribute it and/or
#       modify it under the terms of the GNU Library General Public
#       License as published by the Free Software Foundation; either
#       version 2 of the License, or (at your option) any later version.
#
#       This library is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#       Library General Public License for more details.
#
#       You should have received a copy of the GNU Library General Public
#       License along with this library; if not, write to the Free
#       Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#
#
#       This file is version $Revision: 1.1 $ 
#                       from $Date: 2007/10/04 14:36:39 $
#             last change by $Author: edream $.
#
################################################################################
from Tkinter import *
from ScrolledText import *
import tkSimpleDialog 
import tkMessageBox
from tkColorChooser import askcolor
import copy
import sys
import os
import types


def typed_assign(var, val):
    result = type(var)(val)
    result.__dict__ = copy.copy(var.__dict__)
    return result
    
    
    
    #-------------------------------------------------------------------------------
class TkStringEntry:
    """Tk entry field for editing strings"""
    
    def __init__(self, master, width):
        self.entryWidget = Entry(master, width=width, exportselection=FALSE)
        
    def tkWidget(self):
        return self.entryWidget
        
    def get(self):
        return self.entryWidget.get()
        
    def set(self, value):
        self.entryWidget.delete(0,END)
        self.entryWidget.insert(0,"%s" % value)
        
    def select(self):    
        self.entryWidget.selection_range(0,"end")
        self.entryWidget.focus_set()
        
        
class TkIntEntry(TkStringEntry):
    """Tk entry field for editing one integer"""
    
    def get(self):
        return int(self.entryWidget.get())
        
        
class TkFloatEntry(TkStringEntry):
    """Tk entry field for editing one float"""
    
    def get(self):
        return float(self.entryWidget.get())
        
        
class TkDefaultMixin:
    """Mixin for TkStringEntry, TkIntEntry, TkFloatEntry, ... to deal with
       values which have an externally defined default value. Combination
       of 'use default' checkbox and corresponding entry field """
    
    def __init__(self, master, useDefault, defaultValue):
        self.frame = Frame(master, relief=FLAT)
        self.useDefault = IntVar()
        self.useDefault.set(useDefault)
        self.defaultValue = defaultValue
        useDefaultButton = Checkbutton(self.frame, text="Use default",
                                       variable=self.useDefault,
                                       command=self.toggleDefault)
        useDefaultButton.grid(row=0, column=0, padx=4, pady=3, sticky=W)
        
    def finish(self):
        self.entryWidget.grid(row=0, column=1, padx=4, pady=3, sticky=W)
        self.switchDefault(self.useDefault.get())   
        
    def UseDefault(self):
        return self.useDefault.get()
        
    def switchDefault(self, value):
        if value == 0:
            self.entryWidget['state'] = NORMAL
            self.entryWidget.delete(0,END)
            self.set(self.defaultValue)
        else:
            self.entryWidget.delete(0,END)
            self.entryWidget['state'] = DISABLED
            
    def toggleDefault(self):
        self.switchDefault(self.useDefault.get())            
        
        
class TkDefaultStringEntry(TkStringEntry, TkDefaultMixin):

    def __init__(self, master, width, useDefault, defaultValue):
        TkDefaultMixin.__init__(self, master, useDefault, defaultValue)
        TkStringEntry.__init__(self, self.frame, width)
        self.finish()        
        
    def tkWidget(self): # To avoid ambiguity
        return self.frame
        
        
class TkDefaultIntEntry(TkIntEntry, TkDefaultMixin):

    def __init__(self, master, width, useDefault, defaultValue):
        TkDefaultMixin.__init__(self, master, useDefault, defaultValue)
        TkIntEntry.__init__(self, self.frame, width)
        self.finish()        
        
    def tkWidget(self): # To avoid ambiguity
        return self.frame
        
    def get(self):
        if self.UseDefault():
            return self.defaultValue
        else:
            return TkIntEntry.get(self)
            
class TkDefaultFloatEntry(TkFloatEntry, TkDefaultMixin):

    def __init__(self, master, width, useDefault, defaultValue):
        TkDefaultMixin.__init__(self, master, useDefault, defaultValue)
        TkFloatEntry.__init__(self, self.frame, width)
        self.finish()        
        
    def tkWidget(self): # To avoid ambiguity
        return self.frame
        
    def get(self):
        if self.UseDefault():
            return self.defaultValue
        else:
            return TkFloatEntry.get(self)
            
            
            
class TkPopupSelector:
    def __init__(self, master, value2pop, pop2value, width):
    
        self.value2pop = value2pop
        self.pop2value = pop2value
        self.popupvalue = StringVar()
        self.popupvalue.set(self.pop2value.keys()[0]) # XXX first value as default 
        
        # XXX Uuughhh
        keys = self.value2pop.keys()
        keys.sort()
        pops = map(lambda x: value2pop[x], keys)
        #log.debug("pops = %s" % pops)
        args = (master, self.popupvalue) + tuple(pops)
        
        self.tkwidget = apply(OptionMenu, args)
        self.tkwidget.config(height=1, width=width)
        
    def tkWidget(self):
        return self.tkwidget
        
    def get(self):
        return self.pop2value[self.popupvalue.get()]
        
    def set(self, value):
        try:
            self.popupvalue.set(self.value2pop[value])
        except:
            self.popupvalue.set(self.pop2value.keys()[0]) # XXX first value as default       
            
    def select(self):    
        # Cant choose invalid value with popup
        pass
        
class TkStringPopupSelector:
    def __init__(self, master, strings):
    
        self.strings = strings
        self.popupvalue = StringVar()
        if len(self.strings) > 0:
            self.popupvalue.set(self.strings[0]) # XXX first value as default 
            
        width = max(map(len, self.strings))
        args = (master, self.popupvalue) + tuple(self.strings)
        self.tkwidget = apply(OptionMenu, args)
        self.tkwidget.config(height=1, width=width)
        
    def tkWidget(self):
        return self.tkwidget
        
    def get(self):
        return self.popupvalue.get()
        
    def set(self, value):
        try:
            self.popupvalue.set(value)
        except:
            self.popupvalue.set(self.strings[0]) # XXX first value as default       
            
    def select(self):    
        # Cant choose invalid value with popup
        pass
        
        
class TkColorSelector:
    def __init__(self, master, color='black'):
        #self.tkwidget = Button(master, width=8, command=self.editColor)
        self.tkwidget = Frame(master, height=18, width=60, relief=RIDGE, borderwidth=1)
        self.tkwidget.bind("<ButtonRelease-1>", self.editColor)
        self.set(color)
        
    def editColor(self, event):
        color = askcolor(self.color)[1]
        if color is not None:
            self.set(color)
            
    def tkWidget(self):
        return self.tkwidget
        
    def get(self):
        return self.color
        
    def set(self, value):
        self.color = value
        self.tkwidget.config(bg=self.color)
        
    def select(self):    
        # Cant choose invalid value with popup
        pass
        
        
        
class EditObjectAttributesDialog(tkSimpleDialog.Dialog):
    """ Creates an editable (pseudo-)inspector for a selected set of
        attributes of a given object
    
         - master : tk master widget
         - object : the object, whose attributes we want to edit
         - attr_names : a list of attr_names
    
        By making use of Python 2.2's capability of subclassing built-in
        types such as ints, information about editing etc. is conveyed.
        An attr must have:
         - validate(value) method [return 1, if value is a valid new value for attr]
    
        The class of an attr can have the following mix-ins:
         - Popubable 
         - WithDefault 
    """
    
    def __init__(self, master, object, attr_names):
        self.object = object
        self.attr_names = attr_names
        self.edit = {}
        tkSimpleDialog.Dialog.__init__(self, master, "Edit: %s" % self.object.desc)
        
        
    def editWidget(self, master, object, attr_name):
        """ Create a widget capable of editing attr and insert attr's current value"""
        
        attr = object.__dict__[attr_name]
        attr_type = type(attr)
        widget = None
        default = isinstance(attr, WithDefault) # has a WithDefault mixin
        
        if isinstance(attr, Popupable):            
            widget = TkPopupSelector(master, attr.val2pop, attr.pop2val, attr.width)
            
        elif isinstance(attr, str):
        
            if default:
                widget = TkDefaultStringEntry(master, max(32, len(attr)), attr.useDefault, attr)
            else:
                widget = TkStringEntry(master, max(32, len(attr)))
                
        elif isinstance(attr, int):
        
            if default:
                widget = TkDefaultIntEntry(master, 6, attr.useDefault, attr)
            else:
                widget = TkIntEntry(master, 6)
                
        elif isinstance(attr, float):
        
            if default:
                widget = TkDefaultFloatEntry(master, 8, attr.useDefault, attr)
            else:
                widget = TkFloatEntry(master, 8)
                
        widget.set(attr)
        return widget
        
        
    def body(self, master):
        self.resizable(0,0)	
        
        # Header Zeile
        label = Label(master, text="Name", anchor=E)
        label.grid(row=0, column=0, padx=4, pady=3, sticky=E)
        label = Label(master, text="Value", anchor=W)
        label.grid(row=0, column=1, padx=4, pady=3, sticky=W)
        
        cur_row = 1
        
        for attr in self.attr_names:
            label = Label(master, text="%s" % attr, anchor=E)
            label.grid(row=cur_row, column=0, padx=4, pady=3, sticky=E)
            
            self.edit[attr] = self.editWidget(master, self.object, attr)
            if self.edit[attr] != None:
                self.edit[attr].tkWidget().grid(row=cur_row, column=1, padx=2, pady=1, sticky=W)
                
            cur_row = cur_row + 1
            
    def validate(self):
        for attr_name in self.edit.keys():
            try:
            
                # In python 2.2 we can subclass attributes and add a validate method
                # to attributes
            
                value = self.edit[attr_name].get()
                
                if self.object.__dict__[attr_name].validate(value) == 0:
                    raise ValueError
                    
            except ValueError:
                msg = "Please enter a valid value for %s" % attr_name
                tkMessageBox.showwarning("Invalid Value", msg, parent=self)
                self.edit[attr_name].select()
                return 0
                
                # Everything is valid => set values
        for attr_name in self.edit.keys():            
            self.object.__dict__[attr_name] = typed_assign(self.object.__dict__[attr_name], self.edit[attr_name].get())
            
            if isinstance(self.object.__dict__[attr_name], WithDefault):
                self.object.__dict__[attr_name].useDefault = self.edit[attr_name].useDefault.get()
                
                
        return 1
        
        
        #-------------------------------------------------------------------------------
class WithDefault:
    """Mix-in for variables which have a default value"""
    
    def setDefault(self, useDefault, defaultValue):
        self.useDefault = useDefault
        self.defaultValue = defaultValue
        
    def validate(self, value):
    ##        if self.useDefault:
    ##            return 1
    ##        else:
    ##            return 1 # XXX How can I call a method of the class I am mixed too
        return 1
        
        
class Popupable:
    """Mix-in for variables which can be edited via a pop-up menu
       - val2pop : dict mapping value to string for pop up menu
       - pop2val: dict mapping pop up menu string to value
       - width: maximal string length in pop up
    """
    def setPopup(self, val2pop, pop2val = None, width = None):
        self.val2pop = val2pop
        self.pop2val = None
        self.width = None
        
        if pop2val == None:
            self.pop2val = {} # Private copy
            self.width = 0
            
            for val in val2pop.keys():
                pop = val2pop[val]
                self.width = max(len(pop), self.width)
                self.pop2val[pop] = val
        else:
            self.pop2val = pop2val
            self.width = width
            
    def validate(self, value):
        return 1
        
        ##class PopupableStr(str):
        ##    """Class for variables which can be edited via a pop-up menu
        ##       - values: array of values 
        ##       - width: maximal string length in pop up
        ##    """
        ##    def setPopup(self, values, width = None):
        
        ##        self.values = values
        ##        self.width = width
        
        ##        if width == None:
        ##            self.width = 0
        
        ##            for s in values:
        ##                self.width = max(len(s), self.width)
        
        ##    def validate(self, value):
        ##        return 1
        
        
class AlwaysValidate:
    """Mix-in for variables which always are valid"""
    def validate(self, value):
        return 1
        
        #-------------------------------------------------------------------------------
class ValidatingInt(int, AlwaysValidate):
    """Editable replacement for ints"""
    pass
    
class  ValidatingFloat(float, AlwaysValidate):
    """Editable replacement for floats"""
    pass
    
class  ValidatingString(str, AlwaysValidate):
    """Editable replacement for strings"""
    pass
    
class PopupableInt(int, Popupable):
    """A replacement for ints editable via a pop-up"""
    pass
    
class Probability(float):
    """An editable float taking values from [0,1]"""
    def validate(self, value):
        if 0.0 <= value and value <= 1.0:
            return 1
        else:
            return 0
            
class DefaultedInt(int, WithDefault):
    """An editable int with a default value"""    
    pass
    
class DefaultedFloat(float, WithDefault):
    """An editable float with a default value"""    
    pass
    
class DefaultedString(str, WithDefault):
    """An editable strinf with a default value"""    
    pass
    
    
    #======================================================================
    #
    # Demo:
    #
class TkTestFrame(Frame):

    def __init__(self, parent=None):
        Frame.__init__(self,parent)
        Pack.config(self)
        self.createWidgets()
        
        self.desc = ValidatingString("The TkTestFrame")
        self.x = DefaultedInt(1)
        self.x.setDefault(1, 122)
        self.y = ValidatingFloat(2.33)
        self.choose = PopupableInt(3)
        self.pop2val = {"aaa":1, "xxx":2, "sss":3}
        self.val2pop = {1:"aaa", 2:"xxx", 3:"sss"}
        self.choose.setPopup(self.val2pop, self.pop2val, 5)
        
    def createWidgets(self):
        self.QUIT = Button(self, text='QUIT', foreground='red', 
                           command=self.quit)
        self.QUIT.pack(side=LEFT)
        self.About = Button(self, text='Preferences', foreground='red', 
                           command=self.About)
        self.About.pack(side=LEFT)
        
        
    def About(self):
        aboutBox = EditObjectAttributesDialog(self.master, self, ['desc', 'x', 'y', 'choose'])
        del self.pop2val["aaa"]
        del self.val2pop[1]
        aboutBox = EditObjectAttributesDialog(self.master, self, ['desc', 'x', 'y', 'choose'])
        
if __name__ == '__main__':
    app = TkTestFrame()
    app.mainloop()
    
    
