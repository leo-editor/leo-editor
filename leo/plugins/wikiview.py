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

@bool wikiview-active
    True / False - should wikiview be on by default (if the plugin is enabled)

@data wikiview-link-patterns
    This node contains regex patterns for text to be hidden by the plugin.

    Blank lines and lines starting with '#' are comment lines.
    Each non-comment line represents a pattern.
    Use \b# for patterns starting with '#'
    Only `groups` parts of the pattern in parentheses will be shown.
    The first character of the pattern (not counting \b) is the **leadin character**.
    The pattern will be applied only for strings starting with the leadin character.
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
    '''Return True if this plugin should be enabled.'''
    if g.unitTesting:
        return False
    else:
        g.registerHandler('after-create-leo-frame', onCreate)
        g.plugin_signon(__name__)
        return True
#@+node:tbrown.20141101114322.5: ** onCreate
def onCreate(tag, keys):

    c = keys.get('c')
    WikiView(c)
#@+node:tbrown.20141101114322.6: ** wikiview-toggle
@g.command('wikiview-toggle')
def cmd_toggle(event):
    '''wikiview: toggle active flag'''
    c = event.get('c')
    c._wikiview.active = not c._wikiview.active
    if  c._wikiview.active:
        g.es("WikiView active")
        cmd_hide_all(event)
    else:
        g.es("WikiView inactive")
        cmd_show_all(event)
#@+node:tbrown.20141101114322.7: ** wikiview-hide-all
@g.command('wikiview-hide-all')
def cmd_hide_all(event):
    '''wikiview: re-apply hiding.'''
    c = event.get('c')
    c._wikiview.hide(c._wikiview.select, {'c': c}, force=True)
#@+node:tbrown.20141101114322.8: ** wikiview-show-all
@g.command('wikiview-show-all')
def cmd_show_all(event):
    '''wikiview: undo hiding'''
    c = event.get('c')
    c._wikiview.unhide(all=True)
#@+node:tbrown.20141101114322.9: ** class WikiView
class WikiView(object):
    """Manage wikiview for an outline"""

    #@+others
    #@+node:tbrown.20141101114322.10: *3* __init__ & reloadSettings (WikiView)
    def __init__(self, c):
        '''Ctor for WikiView class.'''
        self.c = c
        c._wikiview = self
        leadins, self.urlpats = self.parse_options()
        assert len(leadins) == len(self.urlpats), (leadins, self.urlpats)
        self.colorizer = c.frame.body.colorizer
        if hasattr(self.colorizer, 'set_wikiview_patterns'):
            self.colorizer.set_wikiview_patterns(leadins, self.urlpats)
        self.select = 'select3'  # Leo hook to hide text
        self.pts=1  # hidden text size (0.1 does not work!)
        self.pct=1  # hidden text letter spacing
        self.reloadSettings()
        w = c.frame.body.widget
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
        
    def reloadSettings(self):
        c = self.c
        c.registerReloadSettings(self)
        self.active = c.config.getBool('wikiview-active')
            # This setting is True by default, so the redundancy is harmless.
    #@+node:ekr.20170205071315.1: *3* parse_options & helper
    def parse_options(self):
        '''Return leadins, patterns from @data wikiview-link-patterns'''
        c = self.c
        # unl://leoSettings.leo#@settings-->Plugins-->wikiview plugin
        data = c.config.getData('wikiview-link-patterns')
        leadins, patterns = [], []
        for s in data:
            leadin = self.get_leadin(s)
            if leadin:
                # g.trace(repr(leadin), repr(s))
                leadins.append(leadin)
                patterns.append(re.compile(s, re.IGNORECASE))
            else:
                g.trace('bad leadin:', repr(s))
        return leadins, patterns
    #@+node:ekr.20170205160357.1: *4* get_leadin
    leadin_pattern = re.compile(r'(\\b)?(\()*(.)')

    def get_leadin(self, s):
        '''Return the leadin of the given pattern s, or None if there is an error.'''
        m = self.leadin_pattern.match(s)
        return m and m.group(3)
    #@+node:tbrown.20141101114322.11: *3* hide
    def hide(self, tag, kwargs, force=False):
        '''Hide all wikiview tags. Now done in the colorizer.'''
        trace = False and not g.unitTesting
        trace_parts = True
        trace_pats = False
        c = self.c
        if not (self.active or force) or kwargs['c'] != c:
            return
        w = c.frame.body.widget
        cursor = w.textCursor()
        s = w.toPlainText()
        if trace:
            g.trace('=====', g.callers())
            g.printList(g.splitLines(s))
        for urlpat in self.urlpats:
            if trace and trace_pats: g.trace(repr(urlpat))
            for m in urlpat.finditer(s):
                if trace: g.trace('FOUND', urlpat.pattern, m.start(0), repr(m.group(0)))
                for group_n, group in enumerate(m.groups()):
                    if group is None:
                        continue
                    if trace and trace_parts: g.trace(
                            m.start(group_n+1),
                            m.end(group_n+1),
                            repr(m.group(group_n+1)))
                    cursor.setPosition(m.start(group_n+1))
                    cursor.setPosition(m.end(group_n+1), cursor.KeepAnchor)
                    cfmt = cursor.charFormat()
                    cfmt.setFontPointSize(self.pts)
                    cfmt.setFontLetterSpacing(self.pct)
                    # cfmt._is_hidden = True  # gets lost
                    cursor.setCharFormat(cfmt)
                        # Triggers a recolor.
    #@+node:tbrown.20141101114322.12: *3* unhide
    def unhide(self, all=False):
        trace = False and not g.unitTesting
        c = self.c
        w = c.frame.body.widget
        cursor = w.textCursor()
        cfmt = cursor.charFormat()
        if cfmt.fontPointSize() == self.pts or all:
            if trace: g.trace()
            if all:
                cursor.setPosition(0)
                cursor.setPosition(len(w.toPlainText()), cursor.KeepAnchor)
            else:
                end = cursor.position()
                # move left to find left end of range
                while (
                    cursor.movePosition(cursor.PreviousCharacter) and
                    cursor.charFormat().fontPointSize() == self.pts
                ):
                    pass
                start = cursor.position()
                # move right to find left end of range
                cursor.setPosition(end)
                while (
                    cursor.movePosition(cursor.NextCharacter) and
                    cursor.charFormat().fontPointSize() == self.pts
                ):
                    pass
                # select range and restore normal size
                cursor.setPosition(start, cursor.KeepAnchor)
            # Common code.
            cfmt.setFontPointSize(self.size)
            cfmt.setFontLetterSpacing(100)
            cursor.setCharFormat(cfmt)
                # Triggers a recolor.
    #@-others
#@-others
#@-leo
