#@+leo-ver=5-thin
#@+node:ekr.20170428084207.477: * @file ../external/npyscreen/util_viewhelp.py
#@+others
#@+node:ekr.20170428084207.478: ** Declarations
import textwrap


#@+node:ekr.20170428084207.479: ** view_help
def view_help(message, title="Message", form_color="STANDOUT", scroll_exit=False, autowrap=False):
    from . import fmForm
    from . import wgmultiline
    F = fmForm.Form(name=title, color=form_color)
    mlw = F.add(wgmultiline.Pager, scroll_exit=True, autowrap=autowrap)
    mlw_width = mlw.width-1

    message_lines = []
    for line in message.splitlines():
        line = textwrap.wrap(line, mlw_width)
        if line == []:
            message_lines.append('')
        else:
            message_lines.extend(line)
    mlw.values = message_lines
    F.edit()
    del mlw
    del F

#@-others
#@@language python
#@@tabwidth -4
#@-leo
