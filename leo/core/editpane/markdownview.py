#@+leo-ver=5-thin
#@+node:tbrown.20171028115144.4: * @file editpane/markdownview.py
#@+others
#@+node:tbrown.20171028115507.1: ** Declarations
import leo.core.leoGlobals as g
from leo.core.leoQt import QtCore, QtGui, QtWidgets, QtConst

import markdown

# FIXME: for now, prefer the older WebKit over WebEngine.  WebEngine is
# probably superior, but needs --disable-web-security passed to the
# QApplication to load local images without a server.
try:
    from leo.core.editpane.webkitview import LEP_WebKitView as HtmlView
except ImportError:
    from leo.core.editpane.webengineview import LEP_WebEngineView as HtmlView

from leo.core.editpane.plaintextview import LEP_PlainTextView as TextView
#@+node:tbrown.20171028115507.2: ** to_html
def to_html(text):
    """to_html - convert to HTML

    :param str text: markdown text to convert
    :return: html
    :rtype: str
    """

    return markdown.markdown(
        text,
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
        ]
    )

#@+node:tbrown.20171028115507.3: ** class LEP_MarkdownView
class LEP_MarkdownView(HtmlView):
    """LEP_MarkdownView -
    """
    lep_type = "MARKDOWN"
    lep_name = "Markdown(.py) View"
    #@+others
    #@+node:tbrown.20171028115507.4: *3* __init__
    def __init__(self, c=None, lep=None, *args, **kwargs):
        """set up"""
        super(LEP_MarkdownView, self).__init__(c=c, lep=lep, *args, **kwargs)
        self.c = c
        self.lep = lep

    #@+node:tbrown.20171028115507.5: *3* new_position
    def new_position(self, p):
        """new_position - update for new position

        :param Leo position p: new position
        """
        if self.lep.recurse:
            self.setHtml(to_html(g.getScript(self.c, p, useSelectedText=False, useSentinels=False)))
        else:
            self.setHtml(to_html(p.b))

    #@+node:tbrown.20171028115507.6: *3* update_position
    def update_position(self, p):
        """update_position - update for current position

        :param Leo position p: current position
        """
        # h = self.horizontalScrollBar().value()
        # v = self.verticalScrollBar().value()
        self.new_position(p)
        # self.horizontalScrollBar().setValue(h)
        # self.verticalScrollBar().setValue(v)


    #@-others
#@+node:tbrown.20171028115507.7: ** class LEP_MarkdownHtmlView
class LEP_MarkdownHtmlView(TextView):
    """LEP_MarkdownHtmlView - view the HTML for markdown
    """
    lep_type = "MARKDOWN-HTML"
    lep_name = "Markdown(.py) Html View"
    #@+others
    #@+node:tbrown.20171028115507.8: *3* __init__
    def __init__(self, c=None, lep=None, *args, **kwargs):
        """set up"""
        super(LEP_MarkdownHtmlView, self).__init__(c=c, lep=lep, *args, **kwargs)
        self.c = c
        self.lep = lep

    #@+node:tbrown.20171028115507.9: *3* new_position
    def new_position(self, p):
        """new_position - update for new position

        :param Leo position p: new position
        """
        if self.lep.recurse:
            self.setPlainText(to_html(g.getScript(self.c, p, useSelectedText=False, useSentinels=False)))
        else:
            self.setPlainText(to_html(p.b))



    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
