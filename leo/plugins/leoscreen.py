#@+leo-ver=4-thin
#@+node:tbrown.20100226095909.12777:@thin leoscreen.py
#@<< docstring >>
#@+node:tbrown.20100226095909.12778:<< docstring >>
'''
leoscreen.py - interact with shell apps. via screen
===================================================

(an simpler alternative to interact.py)

Analysis environments like SQL, R, scipy, ipython, etc. can be
used by pasting sections of text from an editor (Leo) and a
shell window.  Results can be pasted back into the editor.

This plugin streamlines the process by communicating with ``screen``,
the shell multiplexer

Commands created
----------------

leoscreen-run-text
  Send the text selected in Leo's body text to the shell app.
leoscreen-get-line
  Insert a line of the last result from the shell into Leo's body text
  at the current insert point.  Lines are pulled one at a time starting
  from the end of the output.
leoscreen-next
  Switch screen session to next window.
leoscreen-prev
  Switch screen session to preceeding window.
leoscreen-other
  Switch screen session to last window displayed.

**IMPORTANT IMPLEMENTATION NOTE**: screen behave's differently
if screen -X is executed with the same stdout as the target
screen, vs. a different stdout.  Although stdout is ignored,
Popen() needs to ensure it's not just inherited.

'''
#@-node:tbrown.20100226095909.12778:<< docstring >>
#@nl

#@@language python
#@@tabwidth -4

#@<< imports >>
#@+node:tbrown.20100226095909.12779:<< imports >>
import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

import subprocess
import os
import tempfile
#@nonl
#@-node:tbrown.20100226095909.12779:<< imports >>
#@nl
__version__ = "0.1"
#@<< version history >>
#@+node:tbrown.20100226095909.12780:<< version history >>
#@@killcolor

#@+at 
#@nonl
# Use and distribute under the same terms as leo itself.
# 
# 0.1 TNB
#   - initial version
#@-at
#@nonl
#@-node:tbrown.20100226095909.12780:<< version history >>
#@nl

#@+others
#@+node:tbrown.20100226095909.12781:init
def init():
    """Leo plugin init. function"""
    leoPlugins.registerHandler('after-create-leo-frame',onCreate)

    g.plugin_signon(__name__)

    return True
#@-node:tbrown.20100226095909.12781:init
#@+node:tbrown.20100226095909.12782:onCreate
def onCreate (tag,key):
    """Bind an instance of leoscreen_Controller to c"""
    c = key.get('c')

    leoscreen_Controller(c)
#@-node:tbrown.20100226095909.12782:onCreate
#@+node:tbrown.20100226095909.12783:class leoscreen_Controller
class leoscreen_Controller:

    '''A per-commander class that manages screen interaction.'''

    #@    @+others
    #@+node:tbrown.20100226095909.12784:__init__
    def __init__ (self, c):
        """set up vars., prepare temporary file"""

        self.c = c
        c.leo_screen = self

        # skip line -1, which is
        # usually a prompt and not interesting
        self.first_line = -2

        # pulling in lines from output, this is the next one to get
        self.next_unread_line = self.first_line

        # output from last command
        self.output = []

        # file name for hardcopy and paste commands
        fd, self.tmpfile = tempfile.mkstemp()
        os.close(fd)
    #@-node:tbrown.20100226095909.12784:__init__
    #@+node:tbrown.20100226095909.12785:__del__
    def __del__(self):
        """remove temporary file"""
        try:
            os.unlink(self.tmpfile)
        except IOError:
            pass
    #@nonl
    #@-node:tbrown.20100226095909.12785:__del__
    #@+node:tbrown.20100226095909.12786:screen_cmd
    def screen_cmd(self, cmds):
        """Execute a screen command via screen -X"""
        cmd = [
            'screen', '-X', 'eval',
            'msgwait 0',    # avoid waiting for message display
        ]
        cmd.extend(cmds)

        cmd.extend([
            'msgwait 5',
        ])

        proc = subprocess.Popen(cmd,
            stdout=subprocess.PIPE,  # don't just inherit, which alters
            stderr=subprocess.PIPE)  # screen's behavior
        proc.communicate()
    #@-node:tbrown.20100226095909.12786:screen_cmd
    #@+node:tbrown.20100226095909.12787:run_text
    def run_text(self, txt, c=None):
        """Send txt to screen"""

        if c and c != self.c:
            return

        if not c:
            c = self.c

        self.output = []  # forget previous output

        open(self.tmpfile,'w').write(txt)

        self.screen_cmd([
            'readbuf "%s"'%self.tmpfile,
            'paste .',
        ])
    #@-node:tbrown.20100226095909.12787:run_text
    #@+node:tbrown.20100226095909.12788:get_line
    def get_line(self, c=None):
        """Get the next line of output from the last command"""

        if c and c != self.c:
            return

        if not c:
            c = self.c

        editor = c.frame.body

        if not self.output:

            self.screen_cmd(['hardcopy -h "%s"'%self.tmpfile])

            # seems new output file isn't visible to the process
            # without this call
            cmd = ['ls', self.tmpfile]
            proc = subprocess.Popen(cmd,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            proc.communicate()

            f = open(self.tmpfile)

            self.output = f.read().strip().split('\n')
            self.next_unread_line = self.first_line

        if not self.output:
            g.es('No output retreived')
            return

        line = self.output[self.next_unread_line]

        self.next_unread_line -= 1

        insert_point = editor.getInsertPoint()
        editor.insert(insert_point, line+'\n')
        editor.setInsertPoint(insert_point)
        c.setChanged(True)
    #@-node:tbrown.20100226095909.12788:get_line
    #@-others
#@-node:tbrown.20100226095909.12783:class leoscreen_Controller
#@+node:tbrown.20100226095909.12789:cmd_get_line
def cmd_get_line(c):
    """get next line of results"""
    c.leo_screen.get_line(c)
#@-node:tbrown.20100226095909.12789:cmd_get_line
#@+node:tbrown.20100226095909.12790:cmd_run_text
def cmd_run_text(c):
    """pass selected text to shell app. via screen"""
    txt = c.frame.body.getSelectedText()

    c.leo_screen.run_text(txt,c)
#@-node:tbrown.20100226095909.12790:cmd_run_text
#@+node:tbrown.20100226095909.12791:cmd_next,prev,other
def cmd_next(c):
    """execute screen command next"""
    c.leo_screen.screen_cmd(['next'])

def cmd_prev(c):
    """execute screen command prev"""
    c.leo_screen.screen_cmd(['prev'])

def cmd_other(c):
    """execute screen command other"""
    c.leo_screen.screen_cmd(['other'])
#@-node:tbrown.20100226095909.12791:cmd_next,prev,other
#@-others
#@nonl
#@-node:tbrown.20100226095909.12777:@thin leoscreen.py
#@-leo
