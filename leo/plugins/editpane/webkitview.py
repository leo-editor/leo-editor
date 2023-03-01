#@+leo-ver=5-thin
#@+node:tbrown.20171028115143.1: * @file ../plugins/editpane/webkitview.py
#@+<< webkitview imports >>
#@+node:tbrown.20171028115457.1: ** << webkitview imports >>
import os
from leo.core import leoGlobals as g
assert g
from leo.core.leoQt import QtWebKit, QtWebKitWidgets
if not QtWebKitWidgets or 'engine' in g.os_path_basename(
    QtWebKitWidgets.__file__).lower():
    # not loading webkit view, webengine masquerading as webkit
    raise ImportError
#@-<< webkitview imports >>
#@+others
#@+node:tbrown.20171028115457.2: ** _path_from_pos
def _path_from_pos(c, p):
    """_path_from_pos - get folder for position

    FIXME: should be in Leo core somewhere.

    Args:
        p (position): position

    Returns:
        str: path
    """
    p = p.copy()

    def atfile(p):
        word0 = p.h.split()[0]
        return (
            word0 in g.app.atFileNames | set(['@auto']) or
            word0.startswith('@auto-')
        )

    aList = g.get_directives_dict_list(p)
    path = c.scanAtPathDirectives(aList)
    while c.positionExists(p):
        if atfile(p):  # see if it's a @<file> node of some sort
            nodepath = p.h.split(None, 1)[-1]
            nodepath = g.os_path_join(path, nodepath)
            if not g.os_path_isdir(nodepath):  # remove filename
                nodepath = g.os_path_dirname(nodepath)
            if g.os_path_isdir(nodepath):  # append if it's a directory
                path = nodepath
            break
        p.moveToParent()

    return path
#@+node:tbrown.20171028115457.3: ** class LEP_WebKitView
class LEP_WebKitView(QtWebKitWidgets.QWebView):
    """LEP_WebKitView - Web Kit View
    """
    lep_type = "HTML"
    lep_name = "Web Kit View"
    #@+others
    #@+node:tbrown.20171028115457.4: *3* __init__
    def __init__(self, c=None, lep=None, *args, **kwargs):
        """set up"""
        super().__init__(*args, **kwargs)
        self.c = c
        self.lep = lep

        # enable inspector
        try:
            QtWebKit.QWebSettings.globalSettings().setAttribute(
              QtWebKit.QWebSettings.DeveloperExtrasEnabled, True)
        except AttributeError:
            # leoQt substitutes QtWebEngine for QtWebKit
            # if QtWebKit isn't available, causing this to fail
            pass
    #@+node:tbrown.20171028115457.5: *3* new_text
    def new_text(self, text):
        """new_text - update for new text

        Args:
            text (str): new text
        """
        owd = os.getcwd()
        path = _path_from_pos(self.c, self.c.p)
        g.es("FIXME: _path_from_pos() in WebKitView - not self.c.p")
        os.chdir(path)
        g.es(path)
        self.setHtml(text)
        os.chdir(owd)
    #@+node:tbrown.20171028115457.6: *3* update_text
    def update_text(self, text):
        """update_text - update for current text

        Args:
            text (str): current text
        """
        self.new_text(text)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
