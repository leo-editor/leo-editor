"""Add buttons so leo can interact with command line environments.

Currently implements `bash` shell and `psql` (postresql SQL db shell).

Single-line commands can be entered in the headline with a blank body,
multi-line commands can be entered in the body with a descriptive
title in the headline.  Press the `bash` or `psql` button to send
the command to the appropriate interpreter.

The output from the command is **always** stored in a new node added
as the first child of the command node.  For multi-line commands
this new node is selected.  For single-line command this new node
is not shown, instead the body text of the command node is updated
to reflect the most recent output.  Comment delimiter magic is used
to allow single-line and multi-line commands to maintain their
single-line and multi-line flavors.

Both the new child nodes and the updated body text of single-line
commands are timestamped.

For the `bash` button the execution directory is either the directory
containing the `.leo` file, or any other path as specified by ancestor
`@path` nodes.

Currently the `psql` button just connects to the default database.
"""
# 0.1 by Terry Brown, 2009-05-12
import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins
from mod_scripting import scriptingController
import pexpect
import time
import os
def init():
    leoPlugins.registerHandler('after-create-leo-frame', onCreate)
    g.plugin_signon(__name__)
    return True

def onCreate(tag, keywords):
    InteractController(keywords['c'])
class Interact(object):
    def __init__(self, c):
        self.c = c
    def run(self, p):
        raise NotImplementedError
    def buttonText(self):
        raise NotImplementedError
    def statusText(self):
        raise NotImplementedError
class InteractPSQL(Interact):

    prompt = '__psql-leo__'

    def __init__(self, c):
        Interact.__init__(self, c)
        prompts = ' '.join(['--set PROMPT%d=%s'%(i,self.prompt) for i in range(1,4)])
        prompts += ' --pset pager=off'
        c.psqlLink = pexpect.spawn('psql %s'%prompts)
        c.psqlLink.leftover = ''

    def buttonText(self):
        return "psql"
    def statusText(self):
        return "send headline or body to psql session"

    def run(self, p):
        c = self.c
        q = p.b
        if not q.strip() or p.b.strip().startswith('--- '):
            q = p.h
        if p.h.strip().startswith('--'):
            q = None

        if q is None:
            g.es('No valid / uncommented query')
        else:
            c.psqlLink.send(q.strip()+'\n')
            ans = []
            maxlen=100
            for d in self.psqlReader(c.psqlLink):
                if d.strip():
                    ans.append(d)
                    if len(ans) > maxlen:
                        del ans[maxlen-10]
                        ans[maxlen-10] = '   ... skipping ...'
            n = p.insertAsNthChild(0)
            n.h = '-- ' + time.asctime()
            n.b = '\n'.join(ans)
            if p.b.strip().startswith('--- ') or not p.b.strip():
                p.b = '-'+n.h+'\n\n'+n.b
                p.contract()
            else:
                c.selectPosition(n)
            c.redraw()

    def psqlReader(self, proc):
        cnt = 0
        timeout = False
        while not timeout:
            dat = []
            try:
                dat = proc.leftover + proc.read_nonblocking(size=10240,timeout=1)
                proc.leftover = ''
                #X print dat
                if not(dat.endswith('\n')):
                    if '\n' in dat:
                        dat, proc.leftover = dat.rsplit('\n',1)
                    else:
                        time.sleep(0.5)
                        proc.leftover = dat
                        dat = None
                if dat:
                    dat = dat.split("\n")
            except pexpect.TIMEOUT:
                timeout = True

            #X if proc.leftover == self.prompt:
            #X     timeout = True

            if dat:
                for d in dat:
                    cnt += 1
                    #X if d == self.prompt:
                    #X     timeout = True
                    #X else:
                    yield d.replace(self.prompt,'# ') # '%4d: %s' % (cnt,d)
class InteractBASH(Interact):

    prompt = '__bash-leo__'

    def __init__(self, c):
        Interact.__init__(self, c)
        self.bashLink = pexpect.spawn('bash -i')
        self.bashLink.send("PS1='> '\n")
        self.bashLink.send("unalias ls\n")
        self.leftover = ''

    def buttonText(self):
        return "bash"
    def statusText(self):
        return "send headline or body to bash session"

    def run(self, p):
        c = self.c
        q = p.b
        if not q.strip() or p.b.strip().startswith('### '):
            q = p.h
        if p.h.strip().startswith('#'):
            q = None

        if q is None:
            g.es('No valid / uncommented statement')
        else:
            path = self.getPath(c, p)
            if not path:
                path = os.path.dirname(c.fileName())
            if path:
                self.bashLink.send('cd %s\n' % path)
            self.bashLink.send(q.strip()+'\n')
            ans = []
            maxlen=100
            for d in self.bashReader(self.bashLink):
                if d.strip():
                    ans.append(d)
                    if len(ans) > maxlen:
                        del ans[maxlen-10]
                        ans[maxlen-10] = '   ... skipping ...'
            n = p.insertAsNthChild(0)
            n.h = '## ' + time.asctime()
            n.b = '\n'.join(ans)
            if p.b.strip().startswith('### ') or not p.b.strip():
                p.b = '#'+n.h+'\n\n'+n.b
                p.contract()
            else:
                c.selectPosition(n)
            c.redraw()

    def bashReader(self, proc):
        cnt = 0
        timeout = False
        while not timeout:
            dat = []
            try:
                dat = self.leftover + proc.read_nonblocking(size=10240,timeout=1)
                self.leftover = ''
                #X print dat
                if not(dat.endswith('\n')):
                    if '\n' in dat:
                        dat, self.leftover = dat.rsplit('\n',1)
                    else:
                        time.sleep(0.5)
                        self.leftover = dat
                        dat = None
                if dat:
                    dat = dat.split("\n")
            except pexpect.TIMEOUT:
                timeout = True

            #X if self.leftover == self.prompt:
            #X     timeout = True

            if dat:
                for d in dat:
                    cnt += 1
                    #X if d == self.prompt:
                    #X     timeout = True
                    #X else:
                    yield d.replace(self.prompt,'# ') # '%4d: %s' % (cnt,d)

    def getPath(self, c, p):
        for n in p.self_and_parents_iter():
            if n.h.startswith('@path'):
                break
        else:
            return None  # must have a full fledged @path in parents

        aList = g.get_directives_dict_list(p)
        path = c.scanAtPathDirectives(aList)
        return path
class InteractController:

    """quickMove binds to a controller, adds menu entries for
       creating buttons, and creates buttons as needed
    """

    def __init__(self, c):

        self.c = c

        #X table = (
        #X     ("Add To First Child Button",None,self.addToFirstChildButton),
        #X     ("Add To Last Child Button",None,self.addToLastChildButton),
        #X )

        #X  c.frame.menu.createMenuItemsFromTable('Outline', table)

        self.addButton(InteractPSQL)
        self.addButton(InteractBASH)
    def addToFirstChildButton (self,event=None):
        self.addButton(first=True)

    def addToLastChildButton (self,event=None):
        self.addButton(first=False)
    def addButton(self, class_):

        '''Add a button for an interact class.'''

        c = self.c ; p = c.p
        sc = scriptingController(c)

        mb = InteractButton(c, class_)

        b = sc.createIconButton(
            text = mb.interactor.buttonText(),
            command = mb.run,
            shortcut = None,
            statusLine = mb.interactor.statusText(),
            bg = "LightBlue",
        )
class InteractButton:

    """contains target data and function for moving node"""

    def __init__(self, c, class_):

        self.c = c
        self.interactor = class_(c)
    def run(self):

        '''Move the current position to the last child of self.target.'''

        c = self.c
        p = c.p
        self.interactor.run(p)
        c.redraw()
