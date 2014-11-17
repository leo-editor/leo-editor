#@+leo-ver=5-thin
#@+node:tbrown.20141101114322.1: * @file wikiview.py
#@+<< docstring >>
#@+node:tbrown.20141101114322.2: ** << docstring >>
r"""
Hide text in the body editor, each time a new node is selected.  Makes::
    
  file;//#some-->headlines-->mynode appear as mynode,
  http;//www.google.com/search as search, and
  `Python <https;//www.python.org/>`_ as Python

(the ';' that should be ':' above prevent wikiview from hiding
the examples :-)

Commands
--------

  wikiview-toggle
      Turn wikiview on or off
  wikiview-hide-all
      Hide all links
  wikiview-show-all
      Show all links

Settings
--------

  wikiview-active
      True / False - should wikiview be on by default (if the plugin is enabled)
  wikiview-link-patterns
      Regular expressions defining text to hide.  Examples and details::

        # regex patterns for text to be hidden by the wikiview plugin
        # each non-blank link not starting with '#' is treated as a
        # separate pattern, use [#] for patterns starting with '#'
        
        # only `groups` within the pattern, i.e. parts of the pattern
        # in (parentheses), will be hidden, e.g. the first \S+ in the
        # restructuredText pattern is not hidden
        
        # restructuredText `Visible text <http://invisible.url/here>`
        (`)\S+(\s*<(https?|file)://\S+>`_)
        
        # regular urls
        ((https?|file)://(\S+)?(-->|[/#])(?=[.%/a-zA-Z0-9_]))
"""
#@-<< docstring >>

#@@language python
#@@tabwidth -4

__version__ = "0.1"
#@+<< imports >>
#@+node:tbrown.20141101114322.3: ** << imports >>
import re

import leo.core.leoGlobals as g

from leo.core.leoQt import QtGui # ,QtWidgets
#@-<< imports >>

#@+others
#@+node:tbrown.20141101114322.4: ** init
def init():
    
    if g.unitTesting:
        return False

    g.registerHandler('after-create-leo-frame', onCreate)
    g.plugin_signon(__name__)

    return True
#@+node:tbrown.20141101114322.5: ** onCreate
def onCreate(tag, keys):
    
    c = keys.get('c')
    
    WikiView(c)
#@+node:tbrown.20141101114322.6: ** cmd_toggle
def cmd_toggle(c):
    """cmd_toggle - toggle active flag

    :param outline c: outline
    """

    c._wikiview.active = not c._wikiview.active
    if  c._wikiview.active:
        g.es("WikiView active")
        cmd_hide_all(c)
    else:
        g.es("WikiView inactive")
        cmd_show_all(c)
#@+node:tbrown.20141101114322.7: ** cmd_hide_all
def cmd_hide_all(c):
    """cmd_hide_all - re-apply hiding

    :param outline c: outline
    """

    c._wikiview.hide(c._wikiview.select, {'c': c}, force=True)
#@+node:tbrown.20141101114322.8: ** cmd_show_all
def cmd_show_all(c):
    """cmd_show_all - undo hiding

    :param outline c: outline
    """
    c._wikiview.unhide(all=True)
#@+node:tbrown.20141101114322.9: ** class WikiView
class WikiView:
    """Manage wikiview for an outline"""

    #@+others
    #@+node:tbrown.20141101114322.10: *3* __init__
    def __init__(self, c):
        '''Ctor for WikiView class.'''
        self.c = c
        c._wikiview = self
        url_patterns = c.config.getData('wikiview-link-patterns')
        self.urlpats = [re.compile(i, re.IGNORECASE) for i in url_patterns]
        self.select = 'select3'  # Leo hook to hide text
        self.pts=0.1  # hidden text size
        self.pct=1  # hidden text letter spacing
        self.active = c.config.getBool('wikiview-active')
        w = c.frame.body.wrapper.widget
        if not w:
            return # w may not exist during unit testing.
        g.registerHandler(self.select,self.hide)
        w.cursorPositionChanged.connect(self.unhide)
        # size to restore text to when unhiding,
        # w.currentFont().pointSize() is -1 which doesn't work, hence QFontInfo
        self.size = QtGui.QFontInfo(w.currentFont()).pointSize()
        # apply hiding for initial load (`after-create-leo-frame` from module level
        # init() / onCreate())
        self.hide(self.select, {'c': c})
    #@+node:tbrown.20141101114322.11: *3* hide
    def hide(self, tag, kwargs, force=False):

        c = self.c
        if not (self.active or force) or kwargs['c'] != c:
            return

        w = c.frame.body.wrapper.widget
        curse = w.textCursor()
             
        s = w.toPlainText()
        for urlpat in self.urlpats:
            for match in urlpat.finditer(s):   
                for group_n, group in enumerate(match.groups()):
                    # print group_n, group, match.start(group_n+1), match.end(group_n+1)
                    if group is None:
                        continue
                    curse.setPosition(match.start(group_n+1))
                    curse.setPosition(match.end(group_n+1), curse.KeepAnchor)
                    cfmt = curse.charFormat()
                    cfmt.setFontPointSize(self.pts)
                    cfmt.setFontLetterSpacing(self.pct)
                    # cfmt._is_hidden = True  # gets lost
                    curse.setCharFormat(cfmt)
    #@+node:tbrown.20141101114322.12: *3* unhide
    def unhide(self, all=False):
        c = self.c
        w = c.frame.body.wrapper.widget
        curse = w.textCursor()
        cfmt = curse.charFormat()
        if cfmt.fontPointSize() == self.pts or all:
            if not all:
                end = curse.position()
                # move left to find left end of range
                while curse.movePosition(curse.PreviousCharacter) and \
                      curse.charFormat().fontPointSize() == self.pts:
                    pass
                start = curse.position()
                # move right to find left end of range
                curse.setPosition(end)
                while curse.movePosition(curse.NextCharacter) and \
                      curse.charFormat().fontPointSize() == self.pts:
                    pass
                # select range and restore normal size
                curse.setPosition(start, curse.KeepAnchor)
            else:
                curse.setPosition(0)
                curse.setPosition(len(w.toPlainText()), curse.KeepAnchor)
            cfmt.setFontPointSize(self.size)
            cfmt.setFontLetterSpacing(100)
            curse.setCharFormat(cfmt)
    #@-others
#@-others
#@-leo
