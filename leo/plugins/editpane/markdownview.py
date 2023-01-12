#@+leo-ver=5-thin
#@+node:tbrown.20171028115144.4: * @file ../plugins/editpane/markdownview.py
#@+<< markdownview imports >>
#@+node:tbrown.20171028115507.1: ** << markdownview imports >>
import markdown
from leo.core import leoGlobals as g
assert g

# FIXME: for now, prefer the older WebKit over WebEngine.  WebEngine is
# probably superior, but needs --disable-web-security passed to the
# QApplication to load local images without a server.
try:
    from leo.plugins.editpane.webkitview import LEP_WebKitView as HtmlView
except ImportError:
    from leo.plugins.editpane.webengineview import LEP_WebEngineView as HtmlView

from leo.plugins.editpane.plaintextview import LEP_PlainTextView as TextView
#@-<< markdownview imports >>
#@+others
#@+node:tbrown.20171028115507.2: ** to_html
def to_html(text):
    """to_html - convert to HTML

    Args:
        text (str): markdown text to convert

    Returns:
        str: html
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
        super().__init__(c=c, lep=lep, *args, **kwargs)
        self.c = c
        self.lep = lep
    #@+node:tbrown.20171028115507.5: *3* new_text
    def new_text(self, text):
        """new_text - update for new text

        Args:
            text (str): new text
        """
        self.setHtml(to_html(text))
    #@+node:tbrown.20171028115507.6: *3* update_text
    def update_text(self, text):
        """update_text - update for current text

        Args:
            text (str): current position
        """
        # h = self.horizontalScrollBar().value()
        # v = self.verticalScrollBar().value()
        self.new_text(text)
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
        super().__init__(c=c, lep=lep, *args, **kwargs)
        self.c = c
        self.lep = lep
    #@+node:tbrown.20171028115507.9: *3* new_text
    def new_text(self, text):
        """new_text - update for new text

        Args:
            text (str): new text
        """
        self.setPlainText(to_html(text))
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
