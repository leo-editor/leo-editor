#@+leo-ver=5-thin
#@+node:tbrown.20171028115144.3: * @file ../plugins/editpane/pandownview.py
#@+<< pandownview imports >>
#@+node:tbrown.20171028115505.1: ** << pandownview imports >>
"""Markdown view using Pandoc.

There could also be a more generic Pandoc view that handles more input
languages, but this just does markdown.
"""
from subprocess import Popen, PIPE

from leo.core import leoGlobals as g
assert g
# from leo.core.leoQt import QtCore, QtGui, QtWidgets, QtConst

# FIXME: for now, prefer the older WebKit over WebEngine.  WebEngine is
# probably superior, but needs --disable-web-security passed to the
# QApplication to load local images without a server.
try:
    from leo.plugins.editpane.webkitview import LEP_WebKitView as HtmlView
except ImportError:
    from leo.plugins.editpane.webengineview import LEP_WebEngineView as HtmlView

from leo.plugins.editpane.plaintextview import LEP_PlainTextView as TextView

#@-<< pandownview imports >>
#@+others
#@+node:tbrown.20171028115505.2: ** to_html
def to_html(text, from_='markdown'):
    """to_html - convert to HTML

    Args:
        text (str): markdown text to convert

    Returns:
        str: html
    """

    cmd = f"pandoc --smart --standalone --mathjax --from {from_} --to html"
    cmd = cmd.split()
    proc = Popen(cmd, stdin=PIPE, stdout=PIPE)
    out, err = proc.communicate(text)
    return out

# see if Pandoc's installed

try:
    to_html("test")
except:  # pylint: disable=raise-missing-from
    raise ImportError
#@+node:tbrown.20171028115505.3: ** class LEP_PanDownView
class LEP_PanDownView(HtmlView):
    """LEP_MarkdownView -
    """
    lep_type = "MARKDOWN"
    lep_name = "PanDoc Markdown View"
    from_fmt = 'markdown'
    #@+others
    #@+node:tbrown.20171028115505.4: *3* __init__
    def __init__(self, c=None, lep=None, *args, **kwargs):
        """set up"""
        super().__init__(c=c, lep=lep, *args, **kwargs)
        self.c = c
        self.lep = lep
    #@+node:tbrown.20171028115505.5: *3* new_text
    def new_text(self, text):
        """new_text - update for new text

        Args:
            text (str): new text
        """
        self.setHtml(to_html(text, from_=self.from_fmt))
    #@+node:tbrown.20171028115505.6: *3* update_text
    def update_text(self, text):
        """update_text - update for current text

        Args:
            text (str): current text
        """
        # h = self.horizontalScrollBar().value()
        # v = self.verticalScrollBar().value()
        self.new_text(text)
        # self.horizontalScrollBar().setValue(h)
        # self.verticalScrollBar().setValue(v)
    #@-others
#@+node:tbrown.20171028115505.7: ** class LEP_PanDownHtmlView
class LEP_PanDownHtmlView(TextView):
    """LEP_PanDownHtmlView - view the HTML for markdown from PanDoc
    """
    lep_type = "MARKDOWN-HTML"
    lep_name = "PanDoc Markdown Html View"
    from_fmt = 'markdown'
    #@+others
    #@+node:tbrown.20171028115505.8: *3* __init__
    def __init__(self, c=None, lep=None, *args, **kwargs):
        """set up"""
        super().__init__(c=c, lep=lep, *args, **kwargs)
        self.c = c
        self.lep = lep
    #@+node:tbrown.20171028115505.9: *3* new_text
    def new_text(self, text):
        """new_text - update for new text

        Args:
            text (str): new text
        """
        self.setPlainText(to_html(text, from_=self.from_fmt))
    #@-others
#@+node:tbrown.20171128074654.1: ** class LEP_PanRstView
class LEP_PanRstView(LEP_PanDownView):
    """LEP_PanDownView -
    """
    lep_type = "RST"
    lep_name = "PanDoc rst View"
    from_fmt = 'rst'
#@+node:tbrown.20171128074707.1: ** class LEP_PanRstHtmlView
class LEP_PanRstHtmlView(LEP_PanDownHtmlView):
    """LEP_PanDownHtmlView -
    """
    lep_type = "RST-HTML"
    lep_name = "PanDoc rst Html View"
    from_fmt = 'rst'
#@-others
#@@language python
#@@tabwidth -4
#@-leo
