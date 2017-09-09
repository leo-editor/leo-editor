#@+leo-ver=5-thin
#@+node:ekr.20170428084208.359: * @file ../external/npyscreen/wgtextbox_controlchrs.py
#@+others
#@+node:ekr.20170428084208.360: ** Declarations
# import curses
from . import wgtextbox as textbox

#@+node:ekr.20170428084208.361: ** class TextfieldCtrlChars
class TextfieldCtrlChars(textbox.Textfield):
    "Implements a textfield, but which can be prefixed with special curses graphics.  Currently unfinished. Not for use."
    #@+others
    #@+node:ekr.20170428084208.362: *3* __init__
    def __init__(self, *args, **keywords):
        self.ctr_chars = []
        super(TextfieldCtrlChars, self).__init__(*args, **keywords)

    #@+node:ekr.20170428084208.363: *3* _get_maximum_string_length
    def _get_maximum_string_length(self):
        if self.on_last_line:
            _maximum_string_length = self.width - 1
        else:
            _maximum_string_length = self.width

        _maximum_string_length -= (len(self.ctr_chars) + 1)

        return _maximum_string_length

    #@+node:ekr.20170428084208.364: *3* _set_maxiumum_string_length
    def _set_maxiumum_string_length(self, *args):
        pass

    #@+node:ekr.20170428084208.365: *3* _del_maxiumum_string_length
    def _del_maxiumum_string_length(self):
        pass

    maximum_string_length = property(_get_maximum_string_length, _set_maxiumum_string_length, _del_maxiumum_string_length)


    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
