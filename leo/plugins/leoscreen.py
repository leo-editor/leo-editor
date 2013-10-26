#@+leo-ver=5-thin
#@+node:tbrown.20100226095909.12777: * @file leoscreen.py
#@+<< docstring >>
#@+node:tbrown.20100226095909.12778: ** << docstring >>
''' Allows interaction with shell apps via screen.

Analysis environments like SQL, R, scipy, ipython, etc. can be
used by pasting sections of text from an editor (Leo) and a
shell window.  Results can be pasted back into the editor.

This plugin streamlines the process by communicating with ``screen``,
the shell multiplexer

**Commands**

leoscreen-run-text
  Send the text selected in Leo's body text to the shell app.
  Selects the next line for your convenience.

leoscreen-run-all-text
  Send all the text in Leo's body text to the shell app.
  Selects the next node for your convenience.

leoscreen-run-all-here
  Like leoscreen-run-all-text without the inconvenient selection
  of the next node.
  
leoscreen-get-line
  Insert a line of the last result from the shell into Leo's body text
  at the current insert point.  Lines are pulled one at a time starting
  from the end of the output.  Can be used repeatedly to get the
  output you want into Leo.

leoscreen-get-all
  Insert all of the last result from the shell into Leo's body text
  at the current insert point.

leoscreen-get-note
  Insert all of the last result from the shell into a new child node of
  the current node.

leoscreen-show-all
  Show the output from the last result from the shell in a temporary
  read only window. **Important**: The output is not stored.

leoscreen-show-note
  Insert all of the last result from the shell into a new child node of
  the current node and display that node a a stickynote (requires stickynote
  plugin).

leoscreen-next
  Switch screen session to next window.

leoscreen-prev
  Switch screen session to preceding window.

leoscreen-other
  Switch screen session to last window displayed.

leoscreen-get-prefix
  Interactively get prefix for inserting text into body (#, --, //, etc/)
  Can also set using::

      c.leo_screen.get_line_prefix = '#'

leoscreen-more-prompt
  Skip one less line at the end of output when fetching output into Leo.
  Adjusts lines skipped to avoid pulling in the applications prompt line.

leoscreen-less-prompt
  Skip one more line at the end of output when fetching output into Leo
  Adjusts lines skipped to avoid pulling in the applications prompt line.

leoscreen-jump-to-error
  Jump to the python error reported in the shell window, if the file's
  loaded in the current Leo session.  Just looks for a line::
      
      File "somefile.py", line NNN, in xxx

  and looks for a node starting with "@" and ending with "somefile.py", then
  jumps to line NNN in that file.

leoscreen-jump-to-error-up
  `leoscreen-jump-to-error` jumps to the inner most stack-frame in the last
  traceback, this goes up one stack-frame. Note it will go through stack frames
  in previous tracebacks, so you need to pay attention to what's in the shell
  window. `leoscreen-jump-to-error` always resets to the inner most stack-frame
  in the last traceback.


**Settings**

leoscreen_prefix
  Prepended to output pulled in to Leo. The substring SPACE in this
  setting will be replaced with a space character, to allow for trailing
  spaces.

leoscreen_time_fmt
  time.strftime format for note type output headings.

**Theory of operation**

leoscreen creates a instance at c.leo_screen which has some methods which might
be useful in ``@button`` and other Leo contexts.

**Example SQL setup**

In a Leo file full of interactive SQL analysis, I have::

    @settings
        @string leoscreen_prefix = --SPACE
    @button rollback
        import time
        c.leo_screen.run_text('ROLLBACK;  -- %s\n' % time.asctime())
    @button commit
        import time
        cmd = 'COMMIT;  -- %s' % time.asctime()
        c.leo_screen.run_text(cmd)
        c.leo_screen.insert_line(cmd)

which creates a button to rollback messed up queries, another to commit
(requiring additional action to supply the newline as a safeguard) and
sets the prefix to "-- " for text pulled back from the SQL session into
Leo.

**Implementation note**: screen behave's differently if screen -X is executed
with the same stdout as the target screen, vs. a different stdout. Although
stdout is ignored, Popen() needs to ensure it's not just inherited.

'''
#@-<< docstring >>

#@@language python
#@@tabwidth -4

#@+<< imports >>
#@+node:tbrown.20100226095909.12779: ** << imports >>
import leo.core.leoGlobals as g

import subprocess
import os
import time
import tempfile
import difflib

try:
    import stickynotes
except ImportError:
    stickynotes = None
#@-<< imports >>
__version__ = "0.1"
#@+<< version history >>
#@+node:tbrown.20100226095909.12780: ** << version history >>
#@@killcolor

#@+at Use and distribute under the same terms as leo itself.
# 
# 0.1 TNB
#   - initial version
#@-<< version history >>

#@+others
#@+node:tbrown.20100226095909.12781: ** init
def init():
    """Leo plugin init. function"""
    g.registerHandler('after-create-leo-frame',onCreate)

    g.plugin_signon(__name__)

    return True
#@+node:tbrown.20100226095909.12782: ** onCreate
def onCreate (tag,key):
    """Bind an instance of leoscreen_Controller to c"""
    c = key.get('c')

    leoscreen_Controller(c)
#@+node:tbrown.20100226095909.12783: ** class leoscreen_Controller
class leoscreen_Controller:

    '''A per-commander class that manages screen interaction.'''

    #@+others
    #@+node:tbrown.20100226095909.12784: *3* __init__
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
        self.old_output = []

        # file name for hardcopy and paste commands
        fd, self.tmpfile = tempfile.mkstemp()
        os.close(fd)

        # line prefix for pasting results into leo (#, --, //, C, etc.)
        x = self.c.config.getString('leoscreen_prefix')
        if x:
            self.get_line_prefix = x.replace('SPACE', ' ')
        else:
            self.get_line_prefix = ''

        self.time_fmt = self.c.config.getString('leoscreen_time_fmt') or '%Y-%m-%d %H:%M:%S' 

        self._get_output()  # prime output diffing system

        self.popups = []  # store references to popup windows
        
        self.stack_frame = 0
        # used by jump to error commands, 0 = innermost frame
    #@+node:tbrown.20100226095909.12785: *3* __del__
    def __del__(self):
        """remove temporary file"""
        try:
            os.unlink(self.tmpfile)
        except IOError:
            pass
    #@+node:tbrown.20100226095909.12786: *3* screen_cmd
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
    #@+node:tbrown.20100226095909.12787: *3* run_text
    def run_text(self, txt, c=None):
        """Send txt to screen"""

        if c and c != self.c:
            return

        if not c:
            c = self.c

        if not txt:
            return  
            # otherwise there's an annoying delay for "Slurped zero chars" msg.

        if self.output:
            self.old_output = self.output
        self.output = []  # forget previous output (mostly)

        open(self.tmpfile,'w').write(txt)

        self.screen_cmd([
            'readbuf "%s"'%self.tmpfile,
            'paste .',
        ])
    #@+node:tbrown.20100421115534.21602: *3* insert_line
    def insert_line(self, line, c=None):
        """insert a line of text into the current body"""

        if not c:
            c = self.c

        editor = c.frame.body

        insert_point = editor.getInsertPoint()
        editor.insert(insert_point, self.get_line_prefix+line+'\n')
        editor.setInsertPoint(insert_point)
        c.setChanged(True)
    #@+node:tbrown.20100528205637.5725: *3* _get_output
    def _get_output(self):
        """grab some output"""
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
    #@+node:tbrown.20100226095909.12788: *3* get_line
    def get_line(self, c=None):
        """Get the next line of output from the last command"""

        if c and c != self.c:
            return

        if not c:
            c = self.c

        if not self.output:
            self._get_output()

        if not self.output:
            g.es('No output retreived')
            return

        line = self.output[self.next_unread_line]

        self.next_unread_line -= 1

        return line
    #@+node:tbrown.20100422203442.5579: *3* get_all
    def get_all(self, c=None):
        """Get all output from the last command"""

        if c and c != self.c:
            return

        if not c:
            c = self.c

        self.output = None  # trick get_line into getting output
        self.get_line()     # updates self.output, ignore returned line

        sm = difflib.SequenceMatcher(None, self.old_output, self.output)
        x = sm.find_longest_match(0, len(self.old_output)-1, 0, len(self.output)-1)
        # print x, len(self.old_output), len(self.output)

        ans = self.output[:]
        del ans[x.b:x.b+x.size]

        return '\n'.join(ans[:self.first_line])

    #@+node:tbrown.20100502155649.5599: *3* get_note
    def get_note(self, c=None):
        """Get all output from the last command"""

        if c and c != self.c:
            return

        if not c:
            c = self.c

        dat = self.get_all(c)

        p = c.currentPosition()
        n = p.insertAsLastChild()
        n.h = time.strftime(self.time_fmt)
        n.b = dat
        c.setChanged(True)
        c.selectPosition(n)
        c.redraw()
    #@+node:tbrown.20100424115939.5735: *3* show
    def show(self, what, title=None, plain=False):

        try:
            from PyQt4.QtGui import QTextEdit, QTextCursor
        except ImportError:
            g.es("Need Qt for show command")
            return

        if not title:
            title = what.split('\n', 1)[0].strip()

        te = QTextEdit()
        te.setReadOnly(True)
        if plain:
            te.setText(what)
        else:
            te.setHtml("<pre>%s</pre>" % what)
        te.setLineWrapMode(QTextEdit.NoWrap)
        te.resize(800, 600)
        te.setWindowTitle(title)
        te.moveCursor(QTextCursor.End)
        te.show()
        self.popups.append(te)
    #@+node:tbrown.20100502155649.5605: *3* show_note
    def show_note(self):
        if stickynotes:
            stickynotes.stickynote_f({'c':self.c})
        else:
            g.es('stickynotes not available')

    #@+node:tbrown.20100421115534.14949: *3* get_prefix
    def get_prefix(self):
        """get the prefix for insertions from get_line"""

        x = g.app.gui.runAskOkCancelStringDialog(
            self.c,'Prefix for text loading' ,'Prefix for text loading')

        if x is not None:
            self.get_line_prefix = x
    #@-others
#@+node:tbrown.20100226095909.12789: ** cmd_get_line
def cmd_get_line(c):
    """get next line of results"""
    line = c.leo_screen.get_line(c)
    c.leo_screen.insert_line(line)
#@+node:tbrown.20100423084809.19285: ** cmd_get_all
def cmd_get_all(c):
    """get all of results"""
    line = c.leo_screen.get_all(c)
    c.leo_screen.insert_line(line)
#@+node:tbrown.20100502155649.5597: ** cmd_get_note
def cmd_get_note(c):
    """get all of results"""
    c.leo_screen.get_note()
#@+node:tbrown.20100502155649.5603: ** cmd_show_note
def cmd_show_note(c):
    """get all of results"""
    c.leo_screen.get_note()
    c.leo_screen.show_note()
#@+node:tbrown.20100502155649.5595: ** cmd_show_all
def cmd_show_all(c):
    """get all of results"""
    line = c.leo_screen.get_all(c)
    c.leo_screen.show(line)
#@+node:tbrown.20100226095909.12790: ** cmd_run_text
def cmd_run_text(c):
    """pass selected text to shell app. via screen"""
    txt = c.frame.body.getSelectedText()

    # select next line ready for next select/send cycle
    b = c.frame.body.getAllText()
    i = c.frame.body.getInsertPoint()
    try:
        j = b[i:].index('\n')+i+1
        c.frame.body.setSelectionRange(i,j)
    except ValueError:  # no more \n in text
        c.frame.body.setSelectionRange(i,i)
        pass

    c.leo_screen.run_text(txt,c)
#@+node:tbrown.20120905091352.20333: ** cmd_run_all_text
def cmd_run_all_text(c, move=True):
    """pass whole body text to shell app. via screen and move to next body"""
    txt = c.p.b
    if txt[-1] != '\n':
        txt += '\n'
    c.leo_screen.run_text(txt,c)
    if move:
        c.selectThreadNext()
    c.redraw()
#@+node:tbrown.20121108162853.20118: ** cmd_run_all_here
def cmd_run_all_here(c):
    """non-advancing variant of cmd_run_all_text()"""
    cmd_run_all_text(c, move=False)
#@+node:tbrown.20100226095909.12791: ** cmd_next,prev,other
def cmd_next(c):
    """execute screen command next"""
    c.leo_screen.screen_cmd(['next'])

def cmd_prev(c):
    """execute screen command prev"""
    c.leo_screen.screen_cmd(['prev'])

def cmd_other(c):
    """execute screen command other"""
    c.leo_screen.screen_cmd(['other'])
#@+node:tbrown.20100421115534.14948: ** cmd_get_prefix
def cmd_get_prefix(c):
    """call get_prefix"""
    c.leo_screen.get_prefix()
#@+node:tbrown.20100424115939.5581: ** cmd_more/less prompt
def cmd_more_prompt(c):
    """call get_prefix"""
    c.leo_screen.first_line += 1

def cmd_less_prompt(c):
    """call get_prefix"""
    c.leo_screen.first_line -= 1
#@+node:tbrown.20120516075804.26095: ** cmd_jump_to_error
def cmd_jump_to_error(c):
    
    c.leo_screen.stack_frame = 0
    
    jump_to_error_internal(c)

def cmd_jump_to_error_up(c):
    
    c.leo_screen.stack_frame += 1
    
    jump_to_error_internal(c)

def jump_to_error_internal(c):
    
    import re
    regex = re.compile(r'  File "(.*)", line (\d+), in')
    
    lines = c.leo_screen.get_all(c)
    lines = lines.split('\n')
    
    skipped = 0
    for i in reversed(lines):
        match = regex.match(i)
        if match:
            if skipped == c.leo_screen.stack_frame:
                g.es("Line %s in %s"%(match.group(2), match.group(1)))
                filename = g.os_path_basename(match.group(1))
                for p in c.all_unique_positions():
                    if p.h.startswith('@') and p.h.endswith(filename):
                        c.selectPosition(p)
                        c.goToLineNumber(c).go(n=int(match.group(2)))
                        c.bodyWantsFocusNow()
                        break
                break
            skipped += 1
    else:
        g.es("%d error frames found in console content"%skipped)
#@-others
#@-leo
