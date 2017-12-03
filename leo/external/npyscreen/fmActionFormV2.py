#@+leo-ver=5-thin
#@+node:ekr.20170428084207.131: * @file ../external/npyscreen/fmActionFormV2.py
#@+others
#@+node:ekr.20170428084207.132: ** Declarations
import operator
# import weakref
from . import wgwidget as widget
from . import wgbutton
from . import fmForm

#@+node:ekr.20170428084207.133: ** class ActionFormV2
class ActionFormV2(fmForm.FormBaseNew):
    #@+others
    #@+node:ekr.20170428084207.134: *3* class OK_Button
    class OK_Button(wgbutton.MiniButtonPress):
        #@+others
        #@+node:ekr.20170428084207.135: *4* whenPressed
        def whenPressed(self):
            return self.parent._on_ok()

        #@-others
    #@+node:ekr.20170428084207.136: *3* class Cancel_Button
    class Cancel_Button(wgbutton.MiniButtonPress):
        #@+others
        #@+node:ekr.20170428084207.137: *4* whenPressed
        def whenPressed(self):
            return self.parent._on_cancel()

        #@-others
    OKBUTTON_TYPE = OK_Button
    CANCELBUTTON_TYPE = Cancel_Button
    CANCEL_BUTTON_BR_OFFSET = (2, 12)
    OK_BUTTON_TEXT          = "OK"
    CANCEL_BUTTON_TEXT      = "Cancel"
    #@+node:ekr.20170428084207.138: *3* __init__
    def __init__(self, *args, **keywords):
        super(ActionFormV2, self).__init__(*args, **keywords)
        self._added_buttons = {}
        self.create_control_buttons()


    #@+node:ekr.20170428084207.139: *3* create_control_buttons
    def create_control_buttons(self):
        self._add_button('ok_button',
                        self.__class__.OKBUTTON_TYPE,
                        self.__class__.OK_BUTTON_TEXT,
                        0 - self.__class__.OK_BUTTON_BR_OFFSET[0],
                        0 - self.__class__.OK_BUTTON_BR_OFFSET[1] - len(self.__class__.OK_BUTTON_TEXT),
                        None
                        )

        self._add_button('cancel_button',
                        self.__class__.CANCELBUTTON_TYPE,
                        self.__class__.CANCEL_BUTTON_TEXT,
                        0 - self.__class__.CANCEL_BUTTON_BR_OFFSET[0],
                        0 - self.__class__.CANCEL_BUTTON_BR_OFFSET[1] - len(self.__class__.CANCEL_BUTTON_TEXT),
                        None
                        )

    #@+node:ekr.20170428084207.140: *3* on_cancel
    def on_cancel(self):
        pass

    #@+node:ekr.20170428084207.141: *3* on_ok
    def on_ok(self):
        pass

    #@+node:ekr.20170428084207.142: *3* ActionFormV2._on_ok
    def _on_ok(self):
        self.editing = self.on_ok()

    #@+node:ekr.20170428084207.143: *3* ActionFormV2._on_cancel
    def _on_cancel(self):
        self.editing = self.on_cancel()

    #@+node:ekr.20170428084207.144: *3* ActionFormV2.set_up_exit_condition_handlers
    def set_up_exit_condition_handlers(self):
        super(ActionFormV2, self).set_up_exit_condition_handlers()
        self.how_exited_handers.update({
            widget.EXITED_ESCAPE:   self.find_cancel_button
        })

    #@+node:ekr.20170428084207.145: *3* ActionFormV2.find_cancel_button
    def find_cancel_button(self):
        self.editw = len(self._widgets__)-2

    #@+node:ekr.20170428084207.146: *3* _add_button
    def _add_button(self, button_name, button_type, button_text, button_rely, button_relx, button_function):
        tmp_rely, tmp_relx = self.nextrely, self.nextrelx
        this_button = self.add_widget(
                        button_type,
                        name=button_text,
                        rely=button_rely,
                        relx=button_relx,
                        when_pressed_function = button_function,
                        use_max_space=True,
                        )
        self._added_buttons[button_name] = this_button
        self.nextrely, self.nextrelx = tmp_rely, tmp_relx


    #@+node:ekr.20170428084207.147: *3* ActionFormV2.pre_edit_loop
    def pre_edit_loop(self):
        self._widgets__.sort(key=operator.attrgetter('relx'))
        self._widgets__.sort(key=operator.attrgetter('rely'))
        if not self.preserve_selected_widget:
            self.editw = 0
        if not self._widgets__[self.editw].editable:
            self.find_next_editable()

    #@+node:ekr.20170428084207.148: *3* ActionFormV2.post_edit_loop
    def post_edit_loop(self):
        pass

    #@+node:ekr.20170428084207.149: *3* ActionFormV2._during_edit_loop
    def _during_edit_loop(self):
        pass

    #@-others
#@+node:ekr.20170428084207.150: ** class ActionFormExpandedV2
class ActionFormExpandedV2(ActionFormV2):
    BLANK_LINES_BASE   = 1
    OK_BUTTON_BR_OFFSET = (1,6)
    CANCEL_BUTTON_BR_OFFSET = (1, 12)

#@+node:ekr.20170428084207.151: ** class ActionFormMinimal
class ActionFormMinimal(ActionFormV2):
        #@+others
        #@+node:ekr.20170428084207.152: *3* create_control_buttons
        def create_control_buttons(self):
            self._add_button('ok_button',
                        self.__class__.OKBUTTON_TYPE,
                        self.__class__.OK_BUTTON_TEXT,
                        0 - self.__class__.OK_BUTTON_BR_OFFSET[0],
                        0 - self.__class__.OK_BUTTON_BR_OFFSET[1] - len(self.__class__.OK_BUTTON_TEXT),
                        None
                        )

        #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
