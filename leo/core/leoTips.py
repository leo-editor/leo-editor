# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20180121041003.1: * @file leoTips.py
#@@first
'''Save and show tips to the user.'''
import random
import leo.core.leoGlobals as g
assert g
#@+others
#@+node:ekr.20180121041252.1: ** class TipManager
class TipManager(object):
    '''A class to manage user tips.'''
    
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
            # g.trace('===== reinit tips')
            db [self.key] = []
            unseen = list(range(len(tips)))
            seen = []
        # Choose a tip at random from the unseen tips.
        i = random.choice(unseen)
        assert i not in seen, (i, seen)
        seen.append(i)
        db [self.key] = seen
        return tips[i]
    #@-others
#@+node:ekr.20180121041301.1: ** class UserTip
class UserTip(object):
    '''A User Tip.'''
    
    def __init__(self, n=0, tags=None, text='', title=''):
        self.n = n # Not used.
        self.tags = tags or [] # Not used.
        self.title = title.strip()
        self.text = text.strip()
        
    def __repr__(self):
        return '%s\n\n%s\n' % (self.title, self.text)

    __str__ = __repr__
#@+node:ekr.20180121045646.1: ** make_tips (leoTips.py)
def make_tips(c):
    '''
    A script to make entries in the global tips array.
    
    Each printed entry has the form:
        
        UserTip(
            n=anInt
            tags=[list of tags],
            title=aString,
            text="""
            
            aString
            
            """)
        
    After running this script, copy the result from the console to the
    <define tips> section of leoTips.py.
    '''
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
                    lines = lines[:i] + lines[i+1:]
                    text = ''.join(lines).strip()
                    s = s.strip().rstrip('.').strip()
                    s = s[len('tags:'):].strip()
                    tags = [z.strip() for z in s.split(',')]
                    break
            else:
                tags = []
                text = body.strip()
            tips.append(
                UserTip(
                    n=n,
                    tags=tags,
                    text=text.strip(),
                    title=title.strip(),
                ))
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
    for kind in ('open',): # 'closed':
        data = requests.get(url+kind).json()
        for tip in get_tips(data):
            tags = ["%s" % (z) for z in tip.tags or []]
            title = tip.title.lstrip('Tip:').lstrip('tip:').strip()
            print(template % (tip.n, tags, title, tip.text))
#@+node:ekr.20180126052528.1: ** make_tip_nodes (leoTips.py)
def make_tip_nodes(c):
    '''Create a list of all tips as the last top-level node.'''
    global tips
    root = c.lastTopLevel().insertAfter()
    root.h = 'User Tips'
    root.b = '@language rest\n@wrap\nFrom leo.core.leoTips.py'
    for tip in tips:
        p = root.insertAsLastChild()
        p.h = tip.title
        p.b = tip.text
    if root.hasChildren():
        root.h = '%s User Tips' % root.numberOfChildren()
        c.sortSiblings(p=root.firstChild())
    root.expand()
    c.selectPosition(root)
    c.redraw()
#@-others
#@+<< define tips >>
#@+node:ekr.20180121053422.1: ** << define tips >>
# The global tips array, created by the make_tips script.
tips = [

UserTip(
    n=629,
    tags=['Scripting'],
    title="Use a universal shortcut for your scripts",
    text="""\
    
You can have a personal shortcut to run script while developing it. For example: put `@key=Alt-4` in headline.

If your script grows to several subnodes, you won't have to select top node every time you wish to run script. It would be enough to just press your universal shortcut.

"""),

UserTip(
    n=628,
    tags=['Scripting'],
    title="Clearing the Log window",
    text="""\
    
When developing scripts that use Log window to display results, it is sometimes useful to clear Log window by inserting the following two lines at the beginning of your script:

    c.frame.log.selectTab('Log')
    c.frame.log.clearLog()

"""),

UserTip(
    n=626,
    tags=[],
    title="Use section references sparingly",
    text="""\

Within scripts, use section references only when code must be placed exactly. Here is a common pattern for @file nodes for python files:

    @first # -*- coding: utf-8 -*-
    %s
    %s

""" % (g.angleBrackets('imports'), '@others')),

UserTip(
    n=625,
    tags=['Markdown', 'Documentation'],
    title="The @button make-md-toc script in LeoDocs.leo",
    text="""\

The @button make-md-toc script in LeoDocs.leo writes a markdown table of contents to the console.

You can then copy the text from the console to your document.

The selected outline node should be an `@auto-md` node.

"""),

UserTip(
    n=624,
    tags=['Settings', 'Scripting'],
    title="The pyflakes command",
    text="""\
    
pyflakes is a superb programming tool. It checks python files almost instantly.

These settings cause Leo to run pyflakes whenever saving a .py file and to raise a dialog if any errors are found:

    @bool run-pyflakes-on-write = True
    @bool syntax-error-popup = True
    
See https://pypi.python.org/pypi/pyflakes.

"""),

UserTip(
    n=623,
    tags=['Commands', 'Scripting'],
    title="The beautify command & @nobeautify directive",
    text="""\

The @nobeautify directive suppresses beautification of the node in which it appears.

"""),

UserTip(
    n=622,
    tags=['Command', 'Testing'],
    title="The pylint command",
    text="""\
    
Leo's pylint command runs pylint on all `@<file>` nodes in the selected trees.

Pylint runs in the background, so you can continue to use Leo while pylint runs.

See: https://www.pylint.org/.

"""),

UserTip(
    n=621,
    tags=['Tutorial', 'Commands'],
    title="The rst3 command",
    text="""\
    
The rst3 command converts an @rst tree to a document file.

See http://leoeditor.com/tutorial-rst3.html.

"""),

UserTip(
    n=620,
    tags=['PIM', 'Tutorial'],
    title="Use abbreviations",
    text="""\
    
Leo's abbreviations can correct spelling mistakes, expand to multiple lines or even trees of nodes.

Abbreviations can execute scripts and can prompt for values to be substituted within the abbreviation.

See http://leoeditor.com/tutorial-pim.html#using-abbreviations-and-templates.

"""),

UserTip(
    n=619,
    tags=['Tutorial', 'Testing', 'Scripting'],
    title="Use @test nodes",
    text="""\
    
@test nodes create unit tests. They automatically convert the body to a subclass of unittest.TestCase.

Leo's run-* commands execute unit tests.

See http://leoeditor.com/tutorial-basics.html#test-nodes.

"""),

UserTip(
    n=618,
    tags=['Scripting', 'Tutorial'],
    title="Use @button nodes",
    text="""\
    
@button nodes create commands. For example, `@button my-command` creates the `my-command` button and the `my-command` command.

Within `@button` scripts, c.p is the presently selected outline node.

As a result, @button nodes bring scripts to data.

"""),

UserTip(
    n=617,
    tags=['Plugins'],
    title="Leo's most important plugins",
    text="""\
    
Become familiar with Leo's most important plugins:
    
- bookmarks.py manages bookmarks.
- contextmenu.py shows a menu when when righ-clicking.
- mod_scripting.py supports @button and @command nodes.
- quicksearch.py adds a Nav tab for searching.
- todo.py handles to-do lists and is a project manager.
- valuespace.py creates an outline-oriented spreadsheet.
- viewrendered.py renders content in the rendering pane.

"""),

UserTip(
    n=616,
    tags=['Settings',],
    title="Put personal settings myLeoSettings.leo",
    text="""\
    
Put your personal settings in myLeoSettings.leo, not leoSettings.leo.

- The leo-settings-leo command opens leoSettings.leo.
- The my-leo-settings-leo command opens myLeoSettings.leo.
- Copy the desired settings nodes from leoSettings.leo to myLeoSettings.leo.

"""),

UserTip(
    n=615,
    tags=['Tutorial',],
    title="Learn to use clones",
    text="""
    
Clones are "live" copies of the node itself and all its descendants.

See http://leoeditor.com/tutorial-pim.html#clones.

"""),

UserTip(
    n=614,
    tags=['Command', 'Tutorial'],
    title="You don't have to remember command names",
    text="""

To execute a command, type `Alt-X` followed by the first few characters of command name, followed by `Tab`. The list of commands matching what you have typed appears.

"""),

UserTip(
    n=612,
    tags=['Commands', 'Power user', 'Scripting', 'Study'],
    title="Use cff to gather nodes matching a pattern",
    text="""

The cff command (aka clone-find-flattened) prompts for a search pattern, then clones all matching nodes so they are the children of a new last top-level node.

This is a great way to study code.

"""),

UserTip(
    n=611,
    tags=['Command', 'Power-User'],
    title="Use cffm to gather outline nodes",
    text="""

The cff command (aka clone-find-flattened-marked) clones all marked nodes as a children of a new node, created as the last top-level node.

Use this to gather nodes throughout an outline.

"""),

UserTip(
    n=610,
    tags=['Scripting', 'Debugging', 'Beginner'],
    title="g.callers() returns a list of callers",
    text="""
    
g.callers() returns the last n callers (default 4) callers of a function or method. The verbose option shows each caller on a separate line.  For example:
    
    g.trace(g.callers())

You must [launch Leo from a console for this to work.
See http://leoeditor.com/running.html#running-leo-from-a-console-window.

"""),

UserTip(
    n=609,
    tags=['Scripting', 'Debugging', 'Beginner'],
    title="Use g.trace to debug scripts",
    text="""
    
The g.trace function prints all its arguments to the console.

It's great for seeing patterns in running code.

You must [launch Leo from a console for this to work.
See http://leoeditor.com/running.html#running-leo-from-a-console-window.

"""),

UserTip(
    n=608,
    tags=['Scripting', 'Debugging'],
    title="Use g.pdb from the console",
    text="""
    
g.pdb launches Python's pdb debugger, adapted for Leo.

See https://docs.python.org/3/library/pdb.html.

You must [launch Leo from a console for this to work.
See http://leoeditor.com/running.html#running-leo-from-a-console-window.

"""),

UserTip(
    n=607,
    tags=['Commands', 'Find'],
    title="The find-quick-selected command",
    text="""

The find-quick-selected (Ctrl-Shift-F) command finds all nodes containing the selected text.

"""),

UserTip(
    n=606,
    tags=['Commands', 'Scripting'],
    title="The parse-body command",
    text="""

The parse-body command parses p.b (the body text of the selected node) into separate nodes.

"""),

UserTip(
    n=605,
    tags=['Commands',],
    title="The sort-siblings command",
    text="""

The sort-siblings (Alt-A) command sorts all the child nodes of their parent, or all top-level nodes.

"""),

UserTip(
    n=0,
    tags=['Settings',],
    title="Search for settings in leoSettings.leo",
    text="""
    
leoSettings.leo contains the defaults for all of Leo's
settings, with documentation for each. Searching
leoSettings.leo is thus a good way to find settings.
    
"""),

UserTip(
    n=0,
    tags=['Commands', 'Power User',],
    title='Use Alt-N (goto-next-clone) to find "primary" clone',
    text="""
    
Use Alt-N to cycle through the clones of the present cloned node.

This is a fast way of finding the clone whose ancestor is an @<file> node.
    
"""),

UserTip(
    n=0,
    tags=['Power User',],
    title='Move clones to the last top-level node',
    text="""
    
Focus your attention of the task at hand by cloning nodes,
including @file nodes, then moving those clones so they are
the last top-level nodes in the outline.

This allows you to work on nodes scattered throughout an
outline without altering the structure of @file nodes.

"""),

UserTip(
    n=0,
    tags=['Beginner',],
    title='Search LeoDocs.leo',
    text="""
    
The easiest way to find information on a topic is to search LeoDocs.leo.

"""),

UserTip(
    n=0,
    tags=['Power User',],
    title='Use Ctrl-P (repeat-complex-command) to avoid key bindings',
    text="""
    
Ctrl-P re-executes the last command made from the minibuffer.
You can use this to avoid having to define key bindings.

For example, instead of pressing an @button button, execute
its command from the minibuffer. Now you can re-execute the
button using Ctrl-P.

"""),

UserTip(
    n=0,
    tags=['Commands',],
    title='Use leo-* commands to open common .leo files',
    text="""
    
You can open files such as CheatSheet.leo, quickstart.leo,
leoSettings.leo, myLeoSettings.leo and scripts.leo with
commands starting with 'leo-'.

<Alt-X>leo-<tab> shows the complete list.

"""),

]
#@-<< define tips >>
#@@language python
#@@tabwidth -4
#@@pagewidth 60
#@-leo
