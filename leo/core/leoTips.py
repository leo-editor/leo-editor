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
    #@+others
    #@+node:ekr.20180121041822.1: *3* tipm.__init__
    def __init__(self, c):
        '''ctor for TipManager class.'''
        self.key = 'shown-tips'
        # Testing only.
        # self.tips = [UserTip(i) for i in range(4)]
    #@+node:ekr.20180121041748.1: *3* tipm.get_next_tip
    def get_next_tip(self):
        trace = False
        global tips
        db = g.app.db
        # Compute list of unseen tips.
        seen = db.get(self.key, [])
        unseen = [i for i in range(len(tips)) if i not in seen]
        if not unseen:
            if trace: g.trace('===== reinit tips')
            db [self.key] = []
            unseen = list(range(len(tips)))
            seen = []
        # Choose a tip at random from the unseen tips.
        i = random.choice(unseen)
        assert i not in seen, (i, seen)
        seen.append(i)
        db [self.key] = seen
        if trace: g.trace('returns', i)
        return tips[i]
    #@-others
#@+node:ekr.20180121041301.1: ** class UserTip
class UserTip(object):
    '''A User Tip.'''
    
    def __init__(self, n, tags=None, text='', title=''):
        self.n = n
        self.tags = tags or []
        self.title = title
        self.text = text.strip()
        
    def __repr__(self):
        # return 'User tip %s...\n\n%s\n\n' % (self.n, self.text.strip())
        return self.text.strip() + '\n'
    __str__ = __repr__
#@+node:ekr.20180121045646.1: ** make_tips
def make_tips():
    '''
    A script to make entries in the global tips array.
    
    Each entry will have the form:
        
        UserTip(
            n=anInt
            tags=[list of tags],
            text=aString,
            title=aString,
        )
        
    Run this script, then copy the result from the console to leoTips.py.
    '''
    import requests
    base_url = 'https://api.github.com/repos/leo-editor/leo-editor/issues?labels=Tip&state='
    
    def get_tips(data):
        """get_tips - get tips from GitHub issues
        :param dict data: GitHub API issues list
        :return: list of Tips
        """
        tips = []
        for issue in data:
            if '\n' in issue['body']:
                tip, tags = issue['body'].strip().rsplit('\n', 1)
            else:
                tip, tags = issue['body'].strip(), ''
            if tags.lower().startswith('tags:'):
                tags = [i.strip().strip('.') for i in tags[5:].split(',')]
            else:
                tags = []
                tip = "%s\n%s" % (tip, tags)
            if isinstance(tip, (tuple, list)):
                tip = (z for z in tip if z and z.strip())
            tips.append(
                UserTip(
                    n=issue['number'],
                    tags=tags,
                    text=tip.strip(), ### tip.strip().strip('[]').strip(),
                    title=issue['title'],
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
    for kind in ('open',): ### 'open', 'closed':
        URL = base_url+kind
        data = requests.get(URL).json()
        for tip in get_tips(data):
            tags = ["%s" % (z) for z in tip.tags or []]
            text = tip.text.replace('\n', '\\n')
            title = tip.title.rstrip('Tip: ')
            print(template % (tip.n, tags, title, text))
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
    
You can have a personal shortcut to run script while
developing it. For example: put `@key=Alt-4` in headline.

If your script grows to several subnodes, you won't have to
select top node every time you wish to run script. It would
be enough to just press your universal shortcut.

"""),

UserTip(
    n=628,
    tags=['Scripting'],
    title="Tip: Clearing the Log window",
    text="""\
    
When developing scripts that use Log window to display
results, it is sometimes useful to clear Log window by
inserting the following two lines at the beginning of your
script:

    c.frame.log.selectTab('Log')
    c.frame.log.clearLog()

"""),

UserTip(
    n=626,
    tags=[],
    title="Use section references sparingly",
    text="""\

Within scripts, use section references only when code must
be placed exactly. Here is a common pattern for @file nodes
for python files:

    @first # -*- coding: utf-8 -*-
    %s
    %s

""" % (g.angleBrackets('imports'), '@others')),

UserTip(
    n=625,
    tags=['Markdown', 'Documentation'],
    title="The @button make-md-toc script in LeoDocs.leo",
    text="""\

The @button make-md-toc script in LeoDocs.leo writes a markdown table of
contents to the console.

You can then copy the text from the console to your document.

The selected outline node should be an `@auto-md` node.

"""),

UserTip(
    n=624,
    tags=['Settings', 'Scripting'],
    title="Run pyflakes automatically",
    text="""\
    
pyflakes is a superb programming tool. It checks python files almost
instantly.

These settings cause Leo to run pyflakes whenever saving a
.py file and to raise a dialog if any errors are found:

    @bool run-pyflakes-on-write = True
    @bool syntax-error-popup = True
    
See https://pypi.python.org/pypi/pyflakes.

"""),

UserTip(
    n=623,
    tags=['Commands', 'Scripting'],
    title="The beautify command and @nobeautify",
    text="""\

The @nobeautify directive suppresses beautification of the node in which it appears.

"""),

UserTip(
    n=622,
    tags=['Command', 'Testing'],
    title="Use Leo's pylint command",
    text="""\
    
Leo's pylint command runs pylint on all `@<file>` nodes in the selected trees.

Pylint runs in the background, so you can continue to use
Leo while pylint runs.

See: https://www.pylint.org/.

"""),

UserTip(
    n=621,
    tags=['Tutorial', 'Commands'],
    title="Leo's rst3 command converts outlines to documents",
    text="""\
    
Leo's rst3 command converts an @rst tree to a document
file.

See http://leoeditor.com/tutorial-rst3.html.

"""),

UserTip(
    n=620,
    tags=['PIM', 'Tutorial'],
    title="Use abbreviations",
    text="""\
    
Leo's abbreviations can correct spelling mistakes, expand to
multiple lines or even trees of nodes.

Abbreviations can execute scripts and can prompt for values
to be substituted within the abbreviation.

See http://leoeditor.com/tutorial-pim.html#using-abbreviations-and-templates.

"""),

UserTip(
    n=619,
    tags=['Tutorial', 'Testing', 'Scripting'],
    title="Use @test nodes",
    text="""\
    
@test nodes create unit tests. They automatically convert
the body to a subclass of unittest.TestCase.

Leo's run-* commands execute unit tests.

See http://leoeditor.com/tutorial-basics.html#test-nodes.

"""),

UserTip(
    n=618,
    tags=['Scripting', 'Tutorial'],
    title="Use @button nodes",
    text="""\
    
@button nodes create commands. For example,
`@button my-command` creates the `my-command` button and the `my-command` command.

Within `@button` scripts, c.p is the presently selected outline node.

As a result, @button nodes bring scripts to data.

"""),

UserTip(
    n=617,
    tags=['Plugins'],
    title="Learn Leo's most important plugins",
    text="""\
    
Become familiar with Leo's most important plugins:
    
- bookmarks.py manages bookmarks.
- contextmenu.py shows a context menu when you right-click a headline.
- mod_scripting.py supports @button and @command nodes.
- quicksearch.py adds a Nav tab for searching.
- todo.py provides to-do list and simple project-management capabilities.
- valuespace.py adds outline-oriented spreadsheet capabilities.
- viewrendered.py creates the rendering pane and renders content in it.

"""),

UserTip(
    n=616,
    tags=['Settigns',],
    title="Put personal settings myLeoSettings.leo",
    text="""\
    
Put your personal settings in myLeoSettings.leo, not leoSettings.leo.

- The leo-settings-leo command opens leoSettings.leo.
- The my-leo-settings-leo command opens myLeoSettings.leo.
- Copy the desired settings nodes from leoSettings.leo to myLeoSettings.leo.

"""),

]
#@-<< define tips >>
#@@language python
#@@tabwidth -4
#@@pagewidth 60
#@-leo
