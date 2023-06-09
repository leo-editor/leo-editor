#@+leo-ver=5-thin
#@+node:ekr.20180121041003.1: * @file leoTips.py
"""Save and show tips to the user."""
#@+<< leoTips imports & annotations >>
#@+node:ekr.20220901094023.1: ** << leoTips imports & annotations >>
from __future__ import annotations
import random
import textwrap
from typing import Any, TYPE_CHECKING
from leo.core import leoGlobals as g

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
#@-<< leoTips imports & annotations >>
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
    def get_next_tip(self) -> "UserTip":
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

    def __init__(self, n: int = 0, tags: list[str] = None, text: str = '', title: str = '') -> None:
        self.n = n  # Not used.
        self.tags: list[str] = tags or []  # Not used.
        self.title = title.strip()
        self.text = text.strip()

    def __repr__(self) -> str:
        return f"{self.title}\n\n{self.text}\n"

    __str__ = __repr__
#@+node:ekr.20180121045646.1: ** make_tips (leoTips.py)
#@@beautify

def make_tips(c: Cmdr) -> None:
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

    def get_tips(data: Any) -> list[UserTip]:
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
    template = textwrap.dedent(template)
    for kind in ('open',):  # 'closed':
        data = requests.get(url + kind).json()
        for tip in get_tips(data):
            tags = [f"{z}" for z in tip.tags or []]
            title = tip.title.lstrip('Tip:').lstrip('tip:').strip()
            print(template % (tip.n, tags, title, tip.text))
#@+node:ekr.20180126052528.1: ** make_tip_nodes (leoTips.py)
#@@beautify

def make_tip_nodes(c: Cmdr) -> None:
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
tips: list[UserTip] = [
#@+<< define tips >>
#@+node:ekr.20180121053422.1: ** << define tips >>
#@@wrap
#@+others
#@+node:ekr.20180324073355.1: *3* Misc. tips
#@+node:ekr.20180324065653.2: *4* Most important plugins
UserTip(
    n=617,
    tags=['Plugins'],
    title="Leo's most important plugins",
    text="""\

Become familiar with Leo's most important plugins:

- bookmarks.py manages bookmarks.
- contextmenu.py shows a menu when when right-clicking.
- mod_scripting.py supports @button and @command nodes.
  The eval* command support persistent evaluation.
- quicksearch.py adds a Nav tab for searching.
- todo.py handles to-do lists and is a project manager.
- viewrendered.py renders content in the rendering pane.

"""),
#@+node:ekr.20180324072923.1: *4* Move clones to last top-level node
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
#@+node:ekr.20180324065653.3: *4* myLeoSettings.leo
UserTip(
    n=616,
    tags=['Settings',],
    title="Put personal settings myLeoSettings.leo",
    text="""\

Put your personal settings in myLeoSettings.leo, not leoSettings.leo.

- The leo-settings command opens leoSettings.leo.
- The my-leo-settings command opens myLeoSettings.leo.
- Copy the desired settings nodes from leoSettings.leo to myLeoSettings.leo.

"""),
#@+node:ekr.20180324065152.3: *4* Re @button make-md-toc
UserTip(
    n=625,
    tags=['Markdown', 'Documentation'],
    title="The @button make-md-toc script in LeoDocs.leo",
    text="""

The @button make-md-toc script in LeoDocs.leo writes a markdown table of contents to the console.

You can then copy the text from the console to your document.

The selected outline node should be an `@auto-md` node.

"""),
#@+node:ekr.20180324073053.1: *3* Tips re Commands
#@+node:ekr.20180324072156.1: *4* cff command
UserTip(
    n=612,
    tags=['Commands', 'Power user', 'Scripting', 'Study'],
    title="The clone-find commands gather nodes matching a pattern",
    text="""

The cff command (aka clone-find-flattened) prompts for a
search pattern, then clones all matching nodes so they are
the children of a new last top-level node.

This is a great way to study code.

"""),
#@+node:ekr.20180324065153.1: *4* beautify command & @nobeautify
UserTip(
    n=623,
    tags=['Commands', 'Scripting'],
    title="The beautify command & @nobeautify directive",
    text="""

The @nobeautify directive suppresses beautification of the node in which it appears.

"""),
#@+node:ekr.20180324072433.1: *4* cffm command
UserTip(
    n=611,
    tags=['Command', 'Power-User'],
    title="The cffm command gathers marked outline nodes",
    text="""

The cffm command (aka clone-find-flattened-marked) clones
all marked nodes as a children of a new node, created as the
last top-level node.

Use this to gather nodes throughout an outline.

"""),
#@+node:ekr.20180324072541.1: *4* find-quick-selected command
UserTip(
    n=607,
    tags=['Commands', 'Find'],
    title="The find-quick-selected command",
    text="""

The find-quick-selected (Ctrl-Shift-F) command finds all nodes containing the selected text.

"""),
#@+node:ekr.20180324072904.1: *4* goto-next-clone command
UserTip(
    n=0,
    tags=['Commands', 'Power User',],
    title='Alt-N (goto-next-clone) finds "primary" clones',
    text="""

Use Alt-N to cycle through the clones of the present cloned node.

This is a fast way of finding the clone whose ancestor is an @<file> node.

"""),
#@+node:ekr.20180527052858.1: *4* help-*
UserTip(
    n=0,
    tags=['Commands',],
    title="Leo's help system",
    text="""

F11, help-for-command, shows the docstring for any Leo command.

F12, help-for-python, shows Python's help classes, modules, etc.

Leo's help-for commands discuss important topics.

<Alt-X>leo-help<tab> shows all these commands.

"""),
#@+node:ekr.20180324065153.6: *4* leo-* commands
UserTip(
    n=0,
    tags=['Commands',],
    title='leo-* commands open common .leo files',
    text="""

You can open files such as CheatSheet.leo, quickstart.leo,
leoSettings.leo, myLeoSettings.leo and scripts.leo with
commands starting with 'leo-'.

<Alt-X>leo-<tab> shows the complete list.

"""),
#@+node:ekr.20180324072609.1: *4* parse-body command
UserTip(
    n=606,
    tags=['Commands', 'Scripting'],
    title="The parse-body command",
    text="""

The parse-body command parses p.b (the body text of the selected node) into separate nodes.

"""),
#@+node:ekr.20180324065153.2: *4* pylint command
UserTip(
    n=622,
    tags=['Command', 'Testing'],
    title="<html>The pylint command",
    text="""
<p>Leo's pylint command runs
<a href="https://www.pylint.org/">pylint</a>
on all `@<file>` nodes in the selected trees.</p>

<p>Pylint runs in the background. It doesn't interfere with Leo.</p>

</html>"""),
#@+node:ekr.20180324073008.1: *4* repeat-complex-command
UserTip(
    n=0,
    tags=['Power User',],
    title='Ctrl-P (repeat-complex-command)',
    text="""

Ctrl-P re-executes the last command made from the minibuffer.

You can use this to avoid having to define key bindings.

For example, instead of pressing an @button button, execute its command from the minibuffer.

Now you can re-execute the button using Ctrl-P.

"""),
#@+node:ekr.20180324065153.3: *4* rst3 command
UserTip(
    n=621,
    tags=['Tutorial', 'Commands'],
    title="<html>The rst3 command",
    text="""\
<p>The rst3 command converts an @rst tree to a document file.</p>

<p>See <a href="https://leo-editor.github.io/leo-editor/tutorial-rst3.html">Leo's rst3 tutorial.</a></p>

</html>"""),
#@+node:ekr.20180324072625.1: *4* sort-siblings command
UserTip(
    n=605,
    tags=['Commands',],
    title="The sort-siblings command",
    text="""

The sort-siblings (Alt-A) command sorts all the child nodes of their parent, or all top-level nodes.

"""),
#@+node:ekr.20180324073210.1: *3* Tips re Scripting
#@+node:ekr.20180324065152.1: *4* Clearing the log window
UserTip(
    n=628,
    tags=['Scripting'],
    title="Clearing the Log window",
    text="""\

When developing scripts that use Log window to display
results, it is sometimes useful to clear Log window by
inserting the following two lines at the beginning of your
script:

    c.frame.log.selectTab('Log')
    c.frame.log.clearLog()

"""),
#@+node:ekr.20180324072452.1: *4* g.callers()
UserTip(
    n=610,
    tags=['Scripting', 'Debugging', 'Beginner'],
    title="<html>The g.callers() function",
    text="""
<p>g.callers() returns the last n callers (default 4) callers of a function or method.
The verbose option shows each caller on a separate line.
For example:</p>

<p><pre>    g.trace(g.callers())</pre></p>

<p>You must
<a href="https://leo-editor.github.io/leo-editor/running.html#running-leo-from-a-console-window">
run Leo from a console</a> for this to work.</p>

</html>"""),
#@+node:ekr.20180324072527.1: *4* g.pdb
UserTip(
    n=608,
    tags=['Scripting', 'Debugging'],
    title="<html>The g.pdb function",
    text="""
<p>g.pdb launches
<a href="https://docs.python.org/3/library/pdb.html">Python's pdb debugger</a>
adapted for Leo.</p>

<p>You must
<a href="https://leo-editor.github.io/leo-editor/running.html#running-leo-from-a-console-window">
run Leo from a console</a> for this to work.</p>

</html>"""),
#@+node:ekr.20180324072513.1: *4* g.trace
UserTip(
    n=609,
    tags=['Scripting', 'Debugging', 'Beginner'],
    title="<html>The g.trace function",
    text="""
<p>The g.trace function prints all its arguments to the console.</p>

<p>It's great for seeing patterns in running code.</p>

<p>You must
<a href="https://leo-editor.github.io/leo-editor/running.html#running-leo-from-a-console-window">
run Leo from a console</a> for this to work.</p>

</html>"""),
#@+node:ekr.20180324065152.4: *4* Pyflakes
UserTip(
    n=624,
    tags=['Settings', 'Scripting'],
    title="<html>The pyflakes command",
    text="""\
<p><a href="https://pypi.python.org/pypi/pyflakes">pyflakes</a>
checks python files almost instantly.</p>

<p>Enable pyflakes with these settings:
<pre>
@bool run-pyflakes-on-write = True
@bool syntax-error-popup = True
</pre>
</p>

</html>"""),
#@+node:ekr.20180324065653.1: *4* Re @button
UserTip(
    n=618,
    tags=['Scripting', 'Tutorial'],
    title="@button nodes create commands",
    text="""

For example, `@button my-command` creates the `my-command` button and the `my-command` command.

Within `@button` scripts, c.p is the presently selected outline node.

As a result, @button nodes bring scripts to data.

"""),
#@+node:ekr.20180324065152.2: *4* Section refs vs @others
UserTip(
    n=626,
    tags=[],
    title="Use section references sparingly",
    text=f"""

Within scripts, use section references only when code must
be placed exactly. Here is a common pattern for @file nodes
for python files:

    {g.angleBrackets('imports')}
    {'@others'}

"""),
#@+node:ekr.20180324085629.1: *4* Use section refs to avoid "one @others per node" rule
UserTip(
    n=0,
    tags=['Scripting',],
    title='Use section refs to avoid one @others per node rule',
    text=f"""

Nodes can have at most one {at_s}others directive. You can work around this restriction as follows:

    {at_s}file myFile.py
    {at_s}others
    {ref1_s} organizer {ref2_s}

where the body of the {ref1_s} organizer {ref2_s} node contains just {at_s}others.

"""),
#@+node:ekr.20180324073458.1: *3* Tips re Work flow
#@+node:ekr.20180324065153.4: *4* Abbreviations
UserTip(
    n=620,
    tags=['PIM', 'Tutorial'],
    title="<html>Abbreviations",
    text="""

<p>Leo's
<a href="https://leo-editor.github.io/leo-editor/tutorial-pim.html#using-abbreviations-and-templates">
abbreviations</a>
can correct spelling mistakes, expand to multiple lines or even trees of nodes.
</p>

<p>Abbreviations can execute scripts and
can prompt for values to be substituted within the abbreviation.</p>

</html>"""),
#@+node:ekr.20180324072110.1: *4* Clones
UserTip(
    n=615,
    tags=['Tutorial',],
    title="<html>Clones",
    text="""
<p>
<a href="https://leo-editor.github.io/leo-editor/tutorial-pim.html#clones">Clones</a>
are "live" copies of the node itself and all its descendants.</p>

<p>Clones are a unique feature of Leo.</p>

</html>"""),
#@+node:ekr.20180324072128.1: *4* Don't remember command names
UserTip(
    n=614,
    tags=['Command', 'Tutorial'],
    title="Don't remember command names!",
    text="""

To execute a command, type `Alt-X` followed by the first few characters of command name, followed by `Tab`.

The list of commands matching what you have typed appears.

"""),
#@+node:ekr.20180324065145.1: *4* How to assign shortcuts to scripts
UserTip(
    n=629,
    tags=['Scripting'],
    title="How to assign shortcuts to scripts",
    text="""

You can have a personal shortcut to run script while developing it.

For example: put `@key=Alt-4` in headline.

If your script grows to several subnodes, you won't have to
select top node every time you wish to run script. It would
be enough to just press your universal shortcut.

"""),
#@+node:ekr.20180324072951.1: *4* How to find documenation
UserTip(
    n=0,
    tags=['Beginner',],
    title='How to find documentation',
    text="""

Just search LeoDocs.leo.

"""),
#@+node:ekr.20180324072812.1: *4* How to find settings
UserTip(
    n=0,
    tags=['Settings',],
    title="How to find settings",
    text="""

Just search leoSettings.leo.

leoSettings.leo contains the defaults for all of Leo's settings, with documentation for each.

"""),
#@+node:ekr.20180312101254.1: *4* How to find your @command nodes
UserTip(
    n=0,
    tags=['Settings',],
    title="How to find all your @command nodes",
    text="""

<alt-x>@c<tab> shows all the @command nodes in effect for the present outline, no matter where defined.

myLeoSettings.leo can define *common* @command nodes that apply to all outlines.

Such nodes reside in the @commands subtree of the @settings tree in myLeoSettings.leo.

"""),
#@+node:ekr.20180509070202.1: *4* How to minimize panes
UserTip(
    n=0,
    tags=['Tutorial',],
    title="How to minimize panes",
    text="""

Middle mouse click on the window divider (splitter) to
minimize all windows to the left of vertical splitters and
below horizontal splitters.

Using this with "Toggle Split Direction" allows a maximized
body, tree or even log window.

"""),
#@+node:ekr.20180503082333.1: *4* How to see all @command commands
UserTip(
    n=0,
    tags=['Command', 'Tutorial'],
    title="How to see all @command commands",
    text="""

Type <alt-x>@c<tab> shows all the @command nodes in effect for the present outline, no matter where defined.

Note: myLeoSettings.leo can define common @command nodes that apply to all outlines.

"""),
#@-others
#@@beautify
#@-<< define tips >>
]
#@@language python
#@@tabwidth -4
#@@pagewidth 60
#@-leo
