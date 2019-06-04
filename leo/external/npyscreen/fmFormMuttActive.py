#@+leo-ver=5-thin
#@+node:ekr.20170428084207.258: * @file ../external/npyscreen/fmFormMuttActive.py
#@+others
#@+node:ekr.20170428084207.259: ** Declarations
import weakref
import re
import curses
import collections
from . import fmFormMutt
from . import fmFormWithMenus
from . import npysNPSFilteredData
from . import wgtextbox

# This file defines Action Controllers
# and Widgets
# and Forms


##########################################################################################
# Action Controllers
##########################################################################################

#@+node:ekr.20170428084207.260: ** class ActionControllerSimple
class ActionControllerSimple:
    #@+others
    #@+node:ekr.20170428084207.261: *3* __init__
    def __init__(self, parent=None):
        try:
            self.parent = weakref.proxy(parent)
        except Exception:
            self.parent = parent
        self._action_list = []
        self.create()

    #@+node:ekr.20170428084207.262: *3* create
    def create(self):
        pass

    #@+node:ekr.20170428084207.263: *3* add_action
    def add_action(self, ident, function, live):
        ident = re.compile(ident)
        self._action_list.append({'identifier': ident,
                                  'function': function,
                                  'live': live
                                  })

    #@+node:ekr.20170428084207.264: *3* process_command_live
    def process_command_live(self, command_line, control_widget_proxy):
        for a in self._action_list:
            if a['identifier'].match(command_line) and a['live']==True:
                a['function'](command_line, control_widget_proxy, live=True)

    #@+node:ekr.20170428084207.265: *3* process_command_complete
    def process_command_complete(self, command_line, control_widget_proxy):
        for a in self._action_list:
            if a['identifier'].match(command_line):
                a['function'](command_line, control_widget_proxy, live=False)


    #@-others
##########################################################################################
# Widgets
##########################################################################################

#@+node:ekr.20170428084207.266: ** class TextCommandBox
class TextCommandBox(wgtextbox.Textfield):
    #@+others
    #@+node:ekr.20170428084207.267: *3* __init__
    def __init__(self, screen,
                    history=False,
                    history_max=100,
                    set_up_history_keys=False,
                    *args, **keywords):
        super(TextCommandBox, self).__init__(screen, *args, **keywords)
        self.history = history
        self._history_store = collections.deque(maxlen=history_max)
        self._current_history_index = False
        self._current_command = None
        if set_up_history_keys:
            self.set_up_history_keys()

        # History functions currently not complete.

    #@+node:ekr.20170428084207.268: *3* set_up_handlers
    def set_up_handlers(self):
        '''TextCommandBox.set_up_handlers.'''
        super(TextCommandBox, self).set_up_handlers()
        self.handlers.update({
           curses.ascii.NL:     self.h_execute_command,
           curses.ascii.CR:     self.h_execute_command,
        })

    #@+node:ekr.20170428084207.269: *3* set_up_history_keys
    def set_up_history_keys(self):
        '''ActionControllerSimple.set_up_history_keys'''
        self.handlers.update({
            "^P":   self.h_get_previous_history,
            "^N":   self.h_get_next_history,
            curses.KEY_UP: self.h_get_previous_history,
            curses.KEY_DOWN: self.h_get_next_history,
        })

    #@+node:ekr.20170428084207.270: *3* h_get_previous_history
    def h_get_previous_history(self, ch):
        if self._current_history_index is False:
            self._current_command = self.value
            _current_history_index = -1
        else:
            _current_history_index = self._current_history_index - 1
        try:
            self.value = self._history_store[_current_history_index]
        except IndexError:
            return True
        self.cursor_position = len(self.value)
        self._current_history_index = _current_history_index
        self.display()

    #@+node:ekr.20170428084207.271: *3* h_get_next_history
    def h_get_next_history(self, ch):
        if self._current_history_index is False:
            return True
        elif self._current_history_index == -1:
            self.value = self._current_command
            self._current_history_index = False
            self.cursor_position = len(self.value)
            self.display()
            return True
        else:
            _current_history_index = self._current_history_index + 1
        try:
            self.value = self._history_store[_current_history_index]
        except IndexError:
            return True
        self.cursor_position = len(self.value)
        self._current_history_index = _current_history_index
        self.display()

    #@+node:ekr.20170428084207.272: *3* h_execute_command
    def h_execute_command(self, *args, **keywords):
        if self.history:
            self._history_store.append(self.value)
            self._current_history_index = False
        self.parent.action_controller.process_command_complete(self.value, weakref.proxy(self))
        self.value = ''

    #@+node:ekr.20170428084207.273: *3* TextCommandBox.when_value_edited
    def when_value_edited(self):
        super(TextCommandBox, self).when_value_edited()
        if self.editing:
            self.parent.action_controller.process_command_live(self.value, weakref.proxy(self))
        else:
            self.parent.action_controller.process_command_complete(self.value, weakref.proxy(self))

    #@-others
#@+node:ekr.20170428084207.274: ** class TextCommandBoxTraditional
class TextCommandBoxTraditional(TextCommandBox):
    # EXPERIMENTAL
    # WILL PASS INPUT TO A LINKED WIDGET - THE LINKED WIDGET
    # UNLESS PUT IN TO COMMAND LINE MODE BY THE ENTRY OF BEGINNING_OF_COMMAND_LINE_CHARS
    # WILL NEED TO BE ALTERED TO LOOK AS IF IT IS BEING EDITED TOO.
    BEGINNING_OF_COMMAND_LINE_CHARS = (":", "/")
    #@+others
    #@+node:ekr.20170428084207.275: *3* __init__
    def __init__(self, screen,
                    history=True,
                    history_max=100,
                    set_up_history_keys=True,
                    *args, **keywords):
        super(TextCommandBoxTraditional, self).__init__(screen,
         history=history,
         history_max=history_max,
         set_up_history_keys=set_up_history_keys,
         *args, **keywords
        )
        self.linked_widget = None
        self.always_pass_to_linked_widget = []

    #@+node:ekr.20170428084207.276: *3* ActionControllerSimple.handle_input
    def handle_input(self, inputch):
        try:
            inputchstr = chr(inputch)
        except Exception:
            inputchstr = False

        try:
            input_unctrl = curses.ascii.unctrl(inputch)
        except TypeError:
            input_unctrl = False

        if not self.linked_widget:
            return super(TextCommandBoxTraditional, self).handle_input(inputch)

        if (inputch in self.always_pass_to_linked_widget) or \
            (inputchstr in self.always_pass_to_linked_widget) or \
            (input_unctrl in self.always_pass_to_linked_widget):
            rtn = self.linked_widget.handle_input(inputch)
            self.linked_widget.update()
            return rtn

        if inputchstr and (self.value == '' or self.value == None):
            if inputchstr in self.BEGINNING_OF_COMMAND_LINE_CHARS or \
                inputch in self.BEGINNING_OF_COMMAND_LINE_CHARS:
                return super(TextCommandBoxTraditional, self).handle_input(inputch)

        if self.value:
            return super(TextCommandBoxTraditional, self).handle_input(inputch)

        rtn = self.linked_widget.handle_input(inputch)
        self.linked_widget.update()
        return rtn


    #@-others
##########################################################################################
# Form Classes
##########################################################################################

#@+node:ekr.20170428084207.277: ** class FormMuttActive
class FormMuttActive(fmFormMutt.FormMutt):
    DATA_CONTROLER    = npysNPSFilteredData.NPSFilteredDataList
    ACTION_CONTROLLER  = ActionControllerSimple
    COMMAND_WIDGET_CLASS = TextCommandBox
    #@+others
    #@+node:ekr.20170428084207.278: *3* __init__
    def __init__(self, *args, **keywords):
        # first create action_controller, so that the create methods
        # of forms can use it.
        self.action_controller = self.ACTION_CONTROLLER(parent=self)
        # then call the superclass init method.
        super(FormMuttActive, self).__init__(*args, **keywords)
        self.set_value(self.DATA_CONTROLER())


    #@-others
#@+node:ekr.20170428084207.279: ** class FormMuttActiveWithMenus
class FormMuttActiveWithMenus(FormMuttActive, fmFormWithMenus.FormBaseNewWithMenus):
    #@+others
    #@+node:ekr.20170428084207.280: *3* __init__
    def __init__(self, *args, **keywords):
        super(FormMuttActiveWithMenus, self).__init__(*args, **keywords)
        self.initialize_menus()

    #@-others
#@+node:ekr.20170428084207.281: ** class FormMuttActiveTraditional
class FormMuttActiveTraditional(fmFormMutt.FormMutt):
    DATA_CONTROLER    = npysNPSFilteredData.NPSFilteredDataList
    ACTION_CONTROLLER  = ActionControllerSimple
    COMMAND_WIDGET_CLASS = TextCommandBoxTraditional
    #@+others
    #@+node:ekr.20170428084207.282: *3* __init__
    def __init__(self, *args, **keywords):
        # First create action_controller so that create methods of forms
        # can use it.
        self.action_controller        = self.ACTION_CONTROLLER(parent=self)
        super(FormMuttActiveTraditional, self).__init__(*args, **keywords)
        self.set_value(self.DATA_CONTROLER())
        self.wCommand.linked_widget   = self.wMain
        self.wMain.editable           = False
        self.wMain.always_show_cursor = True

        # special mouse handling
        self.wMain.interested_in_mouse_even_when_not_editable = True

    #@-others
#@+node:ekr.20170428084207.283: ** class FormMuttActiveTraditionalWithMenus
class FormMuttActiveTraditionalWithMenus(FormMuttActiveTraditional,
 fmFormWithMenus.FormBaseNewWithMenus):
    #@+others
    #@+node:ekr.20170428084207.284: *3* __init__
    def __init__(self, *args, **keywords):
        super(FormMuttActiveTraditionalWithMenus, self).__init__(*args, **keywords)
        self.initialize_menus()
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
