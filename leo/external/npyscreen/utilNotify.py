#@+leo-ver=5-thin
#@+node:ekr.20170428084207.464: * @file ../external/npyscreen/utilNotify.py
# pylint: disable=no-member
# type: ignore
#@+others
#@+node:ekr.20170428084207.465: ** Declarations
from . import fmPopup
from . import wgmultiline
# from . import fmPopup
import curses
import textwrap

#@+node:ekr.20170428084207.466: ** class ConfirmCancelPopup (fmPopup.ActionPopup)
class ConfirmCancelPopup(fmPopup.ActionPopup):
    #@+others
    #@+node:ekr.20170428084207.467: *3* on_ok
    def on_ok(self):
        self.value = True
    #@+node:ekr.20170428084207.468: *3* on_cancel
    def on_cancel(self):
        self.value = False

    #@-others
#@+node:ekr.20170428084207.469: ** class YesNoPopup (ConfirmCancelPopup)
class YesNoPopup(ConfirmCancelPopup):
    OK_BUTTON_TEXT = "Yes"
    CANCEL_BUTTON_TEXT = "No"

#@+node:ekr.20170428084207.470: ** _prepare_message
def _prepare_message(message):
    if isinstance(message, (list, tuple)):
        return "\n".join([ s.rstrip() for s in message])
        #return "\n".join(message)
    else:
        return message

#@+node:ekr.20170428084207.471: ** _wrap_message_lines
def _wrap_message_lines(message, line_length):
    lines = []
    for line in message.split('\n'):
        lines.extend(textwrap.wrap(line.rstrip(), line_length))
    return lines

#@+node:ekr.20170428084207.472: ** notify
def notify(message, title="Message", form_color='STANDOUT',
            wrap=True, wide=False,
            ):
    message = _prepare_message(message)
    if wide:
        F = fmPopup.PopupWide(name=title, color=form_color)
    else:
        F   = fmPopup.Popup(name=title, color=form_color)
    F.preserve_selected_widget = True
    mlw = F.add(wgmultiline.Pager,)
    mlw_width = mlw.width-1
    if wrap:
        message = _wrap_message_lines(message, mlw_width)
    mlw.values = message
    F.display()

#@+node:ekr.20170428084207.473: ** notify_confirm (utilNotify.py)
def notify_confirm(message, title="Message", form_color='STANDOUT', wrap=True, wide=False,
                    editw = 0,):
    message = _prepare_message(message)
    if wide:
        F = fmPopup.PopupWide(name=title, color=form_color)
    else:
        F   = fmPopup.Popup(name=title, color=form_color)
    F.preserve_selected_widget = True
    mlw = F.add(wgmultiline.Pager,)
    mlw_width = mlw.width-1
    if wrap:
        message = _wrap_message_lines(message, mlw_width)
    else:
        message = message.split("\n")
    mlw.values = message
    F.editw = editw
    F.edit()

#@+node:ekr.20170428084207.474: ** notify_wait
def notify_wait(*args, **keywords):
    notify(*args, **keywords)
    curses.napms(3000)
    curses.flushinp()


#@+node:ekr.20170428084207.475: ** notify_ok_cancel (utilNotify.py)
def notify_ok_cancel(message, title="Message", form_color='STANDOUT', wrap=True, editw = 0,):
    message = _prepare_message(message)
    F   = ConfirmCancelPopup(name=title, color=form_color)
    F.preserve_selected_widget = True
    mlw = F.add(wgmultiline.Pager,)
    mlw_width = mlw.width-1
    if wrap:
        message = _wrap_message_lines(message, mlw_width)
    mlw.values = message
    F.editw = editw
    F.edit()
    return F.value

#@+node:ekr.20170428084207.476: ** notify_yes_no (utilNotify.py)
def notify_yes_no(message, title="Message", form_color='STANDOUT', wrap=True, editw = 0,):
    message = _prepare_message(message)
    F   = YesNoPopup(name=title, color=form_color)
    F.preserve_selected_widget = True
    mlw = F.add(wgmultiline.Pager,)
    mlw_width = mlw.width-1
    if wrap:
        message = _wrap_message_lines(message, mlw_width)
    mlw.values = message
    F.editw = editw
    F.edit()
    return F.value


#@-others
#@@language python
#@@tabwidth -4
#@-leo
