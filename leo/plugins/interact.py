#@+leo-ver=4-thin
#@+node:tbrown.20090513125417.5244:@thin interact.py
#@@language python
#@@tabwidth -4
#@+others
#@+node:tbrown.20090603104805.4937:interact declarations
"""Add buttons so leo can interact with command line environments.

:20100226: see also leoscreen.py for a simpler approach.

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

Currently the `psql` button just connects to the default database.  ";"
is required at the end of SQL statements.

Requires `pexpect` module.
"""
# 0.1 by Terry Brown, 2009-05-12
import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins
from mod_scripting import scriptingController
import pexpect
import time
import os
#@-node:tbrown.20090603104805.4937:interact declarations
#@+node:tbrown.20090603104805.4938:init
def init():
    leoPlugins.registerHandler('after-create-leo-frame', onCreate)
    g.plugin_signon(__name__)
    return True

#@-node:tbrown.20090603104805.4938:init
#@+node:tbrown.20090603104805.4939:onCreate
def onCreate(tag, keywords):
    InteractController(keywords['c'])
#@-node:tbrown.20090603104805.4939:onCreate
#@+node:tbrown.20090603104805.4940:class Interact
class Interact(object):
    #@    @+others
    #@+node:tbrown.20090603104805.4941:__init__
    def __init__(self, c):
        self.c = c
    #@-node:tbrown.20090603104805.4941:__init__
    #@+node:tbrown.20090603104805.4942:available
    def available(self):
        raise NotImplementedError
    #@-node:tbrown.20090603104805.4942:available
    #@+node:tbrown.20090603104805.4943:run
    def run(self, p):
        raise NotImplementedError
    #@-node:tbrown.20090603104805.4943:run
    #@+node:tbrown.20090603104805.4944:buttonText
    def buttonText(self):
        raise NotImplementedError
    #@-node:tbrown.20090603104805.4944:buttonText
    #@+node:tbrown.20090603104805.4945:statusText
    def statusText(self):
        raise NotImplementedError
    #@-node:tbrown.20090603104805.4945:statusText
    #@-others
#@-node:tbrown.20090603104805.4940:class Interact
#@+node:tbrown.20090603104805.4946:class InteractPSQL
class InteractPSQL(Interact):

    prompt = '__psql-leo__'

    #@    @+others
    #@+node:tbrown.20090603104805.4947:__init__
    def __init__(self, c):
        Interact.__init__(self, c)
        prompts = ' '.join(['--set PROMPT%d=%s'%(i,self.prompt) for i in range(1,4)])
        prompts += ' --pset pager=off'
        self._available = True
        try:
            self.psqlLink = pexpect.spawn('psql %s'%prompts)
            self.leftover = ''
            for i in self.psqlReader(self.psqlLink):
                pass  # eat the initial output as it isn't interesting
        except pexpect.ExceptionPexpect:
            self._available = False

    #@-node:tbrown.20090603104805.4947:__init__
    #@+node:tbrown.20090603104805.4948:available
    def available(self):
        return self._available

    #@-node:tbrown.20090603104805.4948:available
    #@+node:tbrown.20090603104805.4949:buttonText
    def buttonText(self):
        return "psql"
    #@-node:tbrown.20090603104805.4949:buttonText
    #@+node:tbrown.20090603104805.4950:statusText
    def statusText(self):
        return "send headline or body to psql session"

    #@-node:tbrown.20090603104805.4950:statusText
    #@+node:tbrown.20090603104805.4951:run
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
            self.psqlLink.send(q.strip()+'\n')
            ans = []
            maxlen=100
            for d in self.psqlReader(self.psqlLink):
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

    #@-node:tbrown.20090603104805.4951:run
    #@+node:tbrown.20090603104805.4952:psqlReader
    def psqlReader(self, proc):
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
    #@-node:tbrown.20090603104805.4952:psqlReader
    #@-others
#@-node:tbrown.20090603104805.4946:class InteractPSQL
#@+node:tbrown.20090603104805.4953:class InteractBASH
class InteractBASH(Interact):

    prompt = '__bash-leo__'

    #@    @+others
    #@+node:tbrown.20090603104805.4954:__init__
    def __init__(self, c):
        Interact.__init__(self, c)
        self._available = True
        try:
            self.bashLink = pexpect.spawn('bash -i')
            self.bashLink.setwinsize(30,256)
            # stop bash emitting chars for long lines
            self.bashLink.send("PS1='> '\n")
            self.bashLink.send("unalias ls\n")
            self.leftover = ''
            for i in self.bashReader(self.bashLink):
                pass  # eat the initial output as it isn't interesting
                      # and in includes chrs leo can't encode currently
        except pexpect.ExceptionPexpect:
            self._available = False

    #@-node:tbrown.20090603104805.4954:__init__
    #@+node:tbrown.20090603104805.4955:buttonText
    def buttonText(self):
        return "bash"
    #@-node:tbrown.20090603104805.4955:buttonText
    #@+node:tbrown.20090603104805.4956:statusText
    def statusText(self):
        return "send headline or body to bash session"

    #@-node:tbrown.20090603104805.4956:statusText
    #@+node:tbrown.20090603104805.4957:available
    def available(self):
        return self._available

    #@-node:tbrown.20090603104805.4957:available
    #@+node:tbrown.20090603104805.4958:run
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

    #@-node:tbrown.20090603104805.4958:run
    #@+node:tbrown.20090603104805.4959:bashReader
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

    #@-node:tbrown.20090603104805.4959:bashReader
    #@+node:tbrown.20090603104805.4960:getPath
    def getPath(self, c, p):
        for n in p.self_and_parents():
            if n.h.startswith('@path'):
                break
        else:
            return None  # must have a full fledged @path in parents

        aList = g.get_directives_dict_list(p)
        path = c.scanAtPathDirectives(aList)
        return path
    #@-node:tbrown.20090603104805.4960:getPath
    #@-others
#@-node:tbrown.20090603104805.4953:class InteractBASH
#@+node:tbrown.20090603104805.4961:class InteractController
class InteractController:

    """quickMove binds to a controller, adds menu entries for
       creating buttons, and creates buttons as needed
    """
    #@    @+others
    #@+node:tbrown.20090603104805.4962:__init__

    def __init__(self, c):

        self.c = c

        #X table = (
        #X     ("Add To First Child Button",None,self.addToFirstChildButton),
        #X     ("Add To Last Child Button",None,self.addToLastChildButton),
        #X )

        #X  c.frame.menu.createMenuItemsFromTable('Outline', table)

        self.addButton(InteractPSQL)
        self.addButton(InteractBASH)
    #@-node:tbrown.20090603104805.4962:__init__
    #@+node:tbrown.20090603104805.4963:addToFirstChildButton
    def addToFirstChildButton (self,event=None):
        self.addButton(first=True)

    #@-node:tbrown.20090603104805.4963:addToFirstChildButton
    #@+node:tbrown.20090603104805.4964:addToLastChildButton
    def addToLastChildButton (self,event=None):
        self.addButton(first=False)
    #@-node:tbrown.20090603104805.4964:addToLastChildButton
    #@+node:tbrown.20090603104805.4965:addButton
    def addButton(self, class_):

        '''Add a button for an interact class.'''

        c = self.c ; p = c.p
        sc = scriptingController(c)

        mb = InteractButton(c, class_)

        if mb.available():
            b = sc.createIconButton(
                text = mb.interactor.buttonText(),
                command = mb.run,
                shortcut = None,
                statusLine = mb.interactor.statusText(),
                bg = "LightBlue",
            )
    #@-node:tbrown.20090603104805.4965:addButton
    #@-others
#@-node:tbrown.20090603104805.4961:class InteractController
#@+node:tbrown.20090603104805.4966:class InteractButton
class InteractButton:

    """contains target data and function for moving node"""
    #@    @+others
    #@+node:tbrown.20090603104805.4967:__init__

    def __init__(self, c, class_):

        self.c = c
        self.interactor = class_(c)
    #@-node:tbrown.20090603104805.4967:__init__
    #@+node:tbrown.20090603104805.4968:run
    def run(self):

        '''Move the current position to the last child of self.target.'''

        c = self.c
        p = c.p
        self.interactor.run(p)
        c.redraw()
    #@-node:tbrown.20090603104805.4968:run
    #@+node:tbrown.20090603104805.4969:available
    def available(self):
        return self.interactor.available()
    #@-node:tbrown.20090603104805.4969:available
    #@-others
#@-node:tbrown.20090603104805.4966:class InteractButton
#@-others
#@-node:tbrown.20090513125417.5244:@thin interact.py
#@-leo
