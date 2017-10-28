"""Markdown view using Pandoc.

There could also be a more generic Pandoc view that handles more input
languages, but this just does markdown.
"""
from subprocess import Popen, PIPE

import leo.core.leoGlobals as g
from leo.core.leoQt import QtCore, QtGui, QtWidgets, QtConst

# FIXME: for now, prefer the older WebKit over WebEngine.  WebEngine is
# probably superior, but needs --disable-web-security passed to the
# QApplication to load local images without a server.
try:
    from leo.core.editpane.webkitview import LEP_WebKitView as HtmlView
except ImportError:
    from leo.core.editpane.webengineview import LEP_WebEngineView as HtmlView

from leo.core.editpane.plaintextview import LEP_PlainTextView as TextView

def to_html(text):
    """to_html - convert to HTML

    :param str text: markdown text to convert
    :return: html
    :rtype: str
    """

    cmd = "pandoc --smart --standalone --mathjax --from markdown --to html".split()
    proc = Popen(cmd, stdin=PIPE, stdout=PIPE)
    out, err = proc.communicate(text)
    return out

# see if Pandoc's installed
try:
    to_html("test")
except:
    raise ImportError

class LEP_PanDownView(HtmlView):
    """LEP_MarkdownView -
    """
    lep_type = "MARKDOWN"
    lep_name = "PanDoc Markdown View"
    def __init__(self, c=None, lep=None, *args, **kwargs):
        """set up"""
        super(LEP_PanDownView, self).__init__(c=c, lep=lep, *args, **kwargs)
        self.c = c
        self.lep = lep

    def new_position(self, p):
        """new_position - update for new position

        :param Leo position p: new position
        """
        if self.lep.recurse:
            self.setHtml(to_html(g.getScript(self.c, p, useSelectedText=False, useSentinels=False)))
        else:
            self.setHtml(to_html(p.b))

    def update_position(self, p):
        """update_position - update for current position

        :param Leo position p: current position
        """
        # h = self.horizontalScrollBar().value()
        # v = self.verticalScrollBar().value()
        self.new_position(p)
        # self.horizontalScrollBar().setValue(h)
        # self.verticalScrollBar().setValue(v)


class LEP_PanDownHtmlView(TextView):
    """LEP_PanDownHtmlView - view the HTML for markdown from PanDoc
    """
    lep_type = "MARKDOWN-HTML"
    lep_name = "PanDoc Markdown Html View"
    def __init__(self, c=None, lep=None, *args, **kwargs):
        """set up"""
        super(LEP_PanDownHtmlView, self).__init__(c=c, lep=lep, *args, **kwargs)
        self.c = c
        self.lep = lep

    def new_position(self, p):
        """new_position - update for new position

        :param Leo position p: new position
        """
        if self.lep.recurse:
            self.setPlainText(to_html(g.getScript(self.c, p, useSelectedText=False, useSentinels=False)))
        else:
            self.setPlainText(to_html(p.b))



