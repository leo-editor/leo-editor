# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20180121041003.1: * @file leoTips.py
#@@first
"""Save and show tips to the user."""
import random
import leo.core.leoGlobals as g
assert g

# Define constant strings for use in f-strings.
at_s = "@"
ref1_s = "<<"
ref2_s = ">>"

#@+others
#@+node:ekr.20180121041252.1: ** class TipManager
#@@beautify


class TipManager:
    """A class to manage user tips."""

    key = 'shown-tips'
    #@+others
    #@+node:ekr.20180121041748.1: *3* tipm.get_next_tip
    def get_next_tip(self):
        global tips
        db = g.app.db
        # Compute list of unseen tips.
        seen = db.get(self.key, [])
        unseen = [i for i in range(len(tips)) if i not in seen]
        if not unseen:
            db[self.key] = []
            unseen = list(range(len(tips)))
            seen = []
        # Choose a tip at random from the unseen tips.
        i = random.choice(unseen)
        assert i not in seen, (i, seen)
        seen.append(i)
        db[self.key] = seen
        return tips[i]
    #@-others
#@+node:ekr.20180121041301.1: ** class UserTip
#@@beautify


class UserTip:
    """A User Tip."""

    def __init__(self, n=0, tags=None, text='', title=''):
        self.n = n  # Not used.
        self.tags = tags or []  # Not used.
        self.title = title.strip()
        self.text = text.strip()

    def __repr__(self):
        return f"{self.title}\n\n{self.text}\n"

    __str__ = __repr__
#@+node:ekr.20180121045646.1: ** make_tips (leoTips.py)
#@@beautify

def make_tips(c):
    """
    A script to make entries in the global tips array.
    
    Each printed entry has the form:
        
        UserTip(
            n=anInt
            tags=[list of tags],
            title=aString,
            text='''
            
            aString
            
            ''')
        
    After running this script, copy the result from the console to the
    <define tips> section of leoTips.py.
    """
    import requests
    url = 'https://api.github.com/repos/leo-editor/leo-editor/issues?labels=Tip&state='

    def get_tips(data):
        """get_tips - get tips from GitHub issues
        :param dict data: GitHub API issues list
        :return: list of Tips
        """
        tips = []
        for issue in data:
            body, n, title = issue['body'], issue['number'], issue['title']
            lines = g.splitLines(body)
            for i, s in enumerate(lines):
                if s.strip().lower().startswith('tags:'):
                    lines = lines[:i] + lines[i + 1 :]
                    text = ''.join(lines).strip()
                    s = s.strip().rstrip('.').strip()
                    s = s[len('tags:') :].strip()
                    tags = [z.strip() for z in s.split(',')]
                    break
            else:
                tags = []
                text = body.strip()
            tips.append(UserTip(n=n, tags=tags, text=text.strip(), title=title.strip(),))
        return tips

    g.cls()
    template = '''\
UserTip(
    n=%s,
    tags=%s,
    title="%s",
    text="""\
    
%s

"""),
'''
    template = g.adjustTripleString(template, c.tab_width)
    for kind in ('open',):  # 'closed':
        data = requests.get(url + kind).json()
        for tip in get_tips(data):
            tags = [f"{z}" for z in tip.tags or []]
            title = tip.title.lstrip('Tip:').lstrip('tip:').strip()
            print(template % (tip.n, tags, title, tip.text))
#@+node:ekr.20180126052528.1: ** make_tip_nodes (leoTips.py)
#@@beautify

def make_tip_nodes(c):
    """Create a list of all tips as the last top-level node."""
    global tips
    root = c.lastTopLevel().insertAfter()
    root.h = 'User Tips'
    root.b = '@language rest\n@wrap\nFrom leo.core.leoTips.py'
    for tip in tips:
        p = root.insertAsLastChild()
        p.h = tip.title
        p.b = tip.text
    if root.hasChildren():
        root.h = f"{root.numberOfChildren()} User Tips"
        c.sortSiblings(p=root.firstChild())
    root.expand()
    c.selectPosition(root)
    c.redraw()
#@-others

# The global tips array.
tips = [
#@+<< define tips >>
#@+node:ekr.20180121053422.1: ** << define tips >>
#@@wrap
#@+others
#@+node:ekr.20180324065145.1: *4* How to assign shortcuts to scripts
UserTip(
    n=629,
    tags=['Scripting'],
    title="How to live",
    text="""
    
Eat a taco.

"""),
#@-others
#@@beautify
#@-<< define tips >>
]
#@@language python
#@@tabwidth -4
#@@pagewidth 60
#@-leo
