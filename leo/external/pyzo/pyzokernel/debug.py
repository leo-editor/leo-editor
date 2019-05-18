# -*- coding: utf-8 -*-
# Copyright (C) 2016, the Pyzo development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import os
import sys
import time
import bdb
import traceback


class Debugger(bdb.Bdb):
    """ Debugger for the pyzo kernel, based on bdb.
    """
    
    def __init__(self):
        self._wait_for_mainpyfile = False  # from pdb, do we need this?
        bdb.Bdb.__init__(self)
        self._debugmode = 0  # 0: no debug,  1: postmortem,  2: full debug
        self._files_with_offset = []
    
    def clear_all_breaks(self):
        bdb.Bdb.clear_all_breaks(self)
        self._files_with_offset = []
    
    def trace_dispatch(self, frame, event, arg):
        # Overload to deal with offset in filenames
        # (cells or lines being executed)
        ori_filename = frame.f_code.co_filename
        
        if '+' in ori_filename and ori_filename not in self._files_with_offset:
            clean_filename, offset = ori_filename.rsplit('+', 1)
            try:
                offset = int(offset)
            except Exception:
                offset = None
            if offset is not None:
                # This is a cell or selected lines being executed
                self._files_with_offset.append(ori_filename)
                if clean_filename.startswith('<'):
                    self.fncache[ori_filename] = ori_filename
                for i in self.breaks.get(clean_filename, []):
                    self.set_break(ori_filename, i-offset)
        
        return bdb.Bdb.trace_dispatch(self, frame, event, arg)
    
    def interaction(self, frame, traceback=None, pm=False):
        """ Enter an interaction-loop for debugging. No GUI events are
        processed here. We leave this event loop at some point, after
        which the conrol flow will proceed.
        
        This is called to enter debug-mode at a breakpoint, or to enter
        post-mortem debugging.
        """
        interpreter = sys._pyzoInterpreter
        
        # Collect frames
        frames = []
        while frame:
            if frame is self.botframe: break
            co_filename = frame.f_code.co_filename
            if 'pyzokernel' in co_filename: break  # pyzo kernel
            if 'interactiveshell.py' in co_filename: break  # IPython kernel
            frames.insert(0, frame)
            frame = frame.f_back
        
        # Tell interpreter our stack
        if frames:
            interpreter._dbFrames = frames
            interpreter._dbFrameIndex = len(interpreter._dbFrames)
            frame = interpreter._dbFrames[interpreter._dbFrameIndex-1]
            interpreter._dbFrameName = frame.f_code.co_name
            interpreter.locals = frame.f_locals
            interpreter.globals = frame.f_globals
        
        # Let the IDE know (
        # "self._debugmode = 1 if pm else 2" does not work not on py2.4)
        if pm:
            self._debugmode = 1
        else:
            self._debugmode = 2
        self.writestatus()
        
        # Enter interact loop. We may hang in here for a while ...
        self._interacting = True
        while self._interacting:
            time.sleep(0.05)
            interpreter.process_commands()
            pe = os.getenv('PYZO_PROCESS_EVENTS_WHILE_DEBUGGING', '').lower()
            if pe in ('1', 'true', 'yes'):
                interpreter.guiApp.process_events()
        
        # Reset
        self._debugmode = 0
        interpreter.locals = interpreter._main_locals
        interpreter.globals = None
        interpreter._dbFrames = []
        self.writestatus()
        
    
    def stopinteraction(self):
        """ Stop the interaction loop.
        """
        self._interacting = False
    
    
    def set_on(self):
        """ To turn debugging on right before executing code.
        """
        # Reset and set bottom frame
        self.reset()
        self.botframe = sys._getframe().f_back
        # Don't stop except at breakpoints or when finished
        # We do: self._set_stopinfo(self.botframe, None, -1) from set_continue
        # But write it all out because py2.4 does not have _set_stopinfo
        self.stopframe = self.botframe
        self.returnframe = None
        self.quitting = False
        self.stoplineno = -1
        # Set tracing or not
        if self.breaks:
            sys.settrace(self.trace_dispatch)
        else:
            sys.settrace(None)
    
    
    def message(self, msg):
        """ Alias for interpreter.write(), but appends a newline.
        Writes to stderr.
        """
        sys._pyzoInterpreter.write(msg+'\n')
    
    
    def error(self, msg):
        """ method used in some code that we copied from pdb.
        """
        raise self.message('*** '+msg)
    
    
    def writestatus(self):
        """ Write the debug status so the IDE can take action.
        """
        
        interpreter = sys._pyzoInterpreter
        
        # Collect frames info
        frames = []
        for f in interpreter._dbFrames:
            # Get fname and lineno, and correct if required
            fname, lineno = f.f_code.co_filename, f.f_lineno
            fname, lineno = interpreter.correctfilenameandlineno(fname, lineno)
            if not fname.startswith('<'):
                fname2 = os.path.abspath(fname)
                if os.path.isfile(fname2):
                    fname = fname2
            frames.append((fname, lineno, f.f_code.co_name))
            # Build string
            #text = 'File "%s", line %i, in %s' % (
            #                        fname, lineno, f.f_code.co_name)
            #frames.append(text)
        
        # Send info object
        state = {   'index': interpreter._dbFrameIndex,
                    'frames': frames,
                    'debugmode': self._debugmode}
        interpreter.context._stat_debug.send(state)
    
    
    ## Stuff that we need to overload
    
    
    # Overload set_break to also allow non-existing filenames like "<tmp 1"
    def set_break(self, filename, lineno, temporary=False, cond=None,
                  funcname=None):
        filename = self.canonic(filename)
        list = self.breaks.setdefault(filename, [])
        if lineno not in list:
            list.append(lineno)
        bdb.Breakpoint(filename, lineno, temporary, cond, funcname)
    
    
    # Prevent stopping in bdb code or pyzokernel code
    def stop_here(self, frame):
        result = bdb.Bdb.stop_here(self, frame)
        if result:
            return (    ('bdb.py' not in frame.f_code.co_filename) and
                        ('pyzokernel' not in frame.f_code.co_filename) )
    
    
    def do_clear(self, arg):
        """"""
        # Clear breakpoints, we need to overload from Bdb,
        # but do not expose this command to the user.
        """cl(ear) filename:lineno\ncl(ear) [bpnumber [bpnumber...]]
        With a space separated list of breakpoint numbers, clear
        those breakpoints.  Without argument, clear all breaks (but
        first ask confirmation).  With a filename:lineno argument,
        clear all breaks at that line in that file.
        """
        if not arg:
            bplist = [bp for bp in bdb.Breakpoint.bpbynumber if bp]
            self.clear_all_breaks()
            for bp in bplist:
                self.message('Deleted %s' % bp)
            return
        if ':' in arg:
            # Make sure it works for "clear C:\foo\bar.py:12"
            i = arg.rfind(':')
            filename = arg[:i]
            arg = arg[i+1:]
            try:
                lineno = int(arg)
            except ValueError:
                err = "Invalid line number (%s)" % arg
            else:
                bplist = self.get_breaks(filename, lineno)
                err = self.clear_break(filename, lineno)
            if err:
                self.error(err)
            else:
                for bp in bplist:
                    self.message('Deleted %s' % bp)
            return
        numberlist = arg.split()
        for i in numberlist:
            try:
                bp = self.get_bpbynumber(i)
            except ValueError:
                self.error("Cannot get breakpoint by number.")
            else:
                self.clear_bpbynumber(i)
                self.message('Deleted %s' % bp)
    
    
    def user_call(self, frame, argument_list):
        """This method is called when there is the remote possibility
        that we ever need to stop in this function."""
        if self._wait_for_mainpyfile:
            return
        if self.stop_here(frame):
            self.message('--Call--')
            self.interaction(frame, None)
            
    
    
    def user_line(self, frame):
        """This function is called when we stop or break at this line."""
        if self._wait_for_mainpyfile:
            if (self.mainpyfile != self.canonic(frame.f_code.co_filename) or frame.f_lineno <= 0):
                return
            self._wait_for_mainpyfile = False
        if True: #self.bp_commands(frame):  from pdb
            self.interaction(frame, None)
    
    
    def user_return(self, frame, return_value):
        """This function is called when a return trap is set here."""
        if self._wait_for_mainpyfile:
            return
        frame.f_locals['__return__'] = return_value
        self.message('--Return--')
        self.interaction(frame, None)
    
    
    def user_exception(self, frame, exc_info):
        """This function is called if an exception occurs,
        but only if we are to stop at or just below this level."""
        if self._wait_for_mainpyfile:
            return
        exc_type, exc_value, exc_traceback = exc_info
        frame.f_locals['__exception__'] = exc_type, exc_value
        self.message(traceback.format_exception_only(exc_type,
                                                     exc_value)[-1].strip())
        self.interaction(frame, exc_traceback)
    
    
    ## Commands
    
    def do_help(self, arg):
        """ Get help on debug commands.
        """
        # Collect docstrings
        docs = {}
        for name in dir(self):
            if name.startswith('do_'):
                doc = getattr(self, name).__doc__
                if doc:
                    docs[name[3:]] = doc.strip()
        
        if not arg:
            print('All debug commands:')
            # Show docs in  order
            for name in [   'start', 'stop', 'frame', 'up', 'down',
                            'next', 'step','return', 'continue',
                            'where', 'events']:
                doc = docs.pop(name)
                name= name.rjust(10)
                print(' %s - %s' % (name, doc))
            # Show rest
            for name in docs:
                doc = docs[name]
                name= name.rjust(10)
                print(' %s - %s' % (name, doc))
        
        else:
            # Show specific doc
            name = arg.lower()
            doc = docs.get(name, None)
            if doc is not None:
                print('%s - %s' % (name, doc))
            else:
                print('Unknown debug command: %s' % name)
    
        
    def do_start(self, arg):
        """ Start postmortem debugging from the last uncaught exception.
        """
        
        # Get traceback
        try:
            tb = sys.last_traceback
        except AttributeError:
            tb = None
        
        # Get top frame
        frame = None
        while tb:
            frame = tb.tb_frame
            tb = tb.tb_next
        
        # Interact, or not
        if self._debugmode:
            self.message("Already in debug mode.")
        elif frame:
            self.interaction(frame, None, pm=True)
        else:
            self.message("No debug information available.")
    
    
    def do_frame(self, arg):
        """ Go to the i'th frame in the stack.
        """
        interpreter = sys._pyzoInterpreter
        
        if not self._debugmode:
            self.message("Not in debug mode.")
        else:
            # Set frame index
            interpreter._dbFrameIndex = int(arg)
            if interpreter._dbFrameIndex < 1:
                interpreter._dbFrameIndex = 1
            elif interpreter._dbFrameIndex > len(interpreter._dbFrames):
                interpreter._dbFrameIndex = len(interpreter._dbFrames)
            # Set name and locals
            frame = interpreter._dbFrames[interpreter._dbFrameIndex-1]
            interpreter._dbFrameName = frame.f_code.co_name
            interpreter.locals = frame.f_locals
            interpreter.globals = frame.f_globals
            self.writestatus()
    
    
    def do_up(self, arg):
        """ Go one frame up the stack.
        """
        interpreter = sys._pyzoInterpreter
        
        if not self._debugmode:
            self.message("Not in debug mode.")
        else:
            # Decrease frame index
            interpreter._dbFrameIndex -= 1
            if interpreter._dbFrameIndex < 1:
                interpreter._dbFrameIndex = 1
            # Set name and locals
            frame = interpreter._dbFrames[interpreter._dbFrameIndex-1]
            interpreter._dbFrameName = frame.f_code.co_name
            interpreter.locals = frame.f_locals
            interpreter.globals = frame.f_globals
            self.writestatus()
    
    
    def do_down(self, arg):
        """ Go one frame down the stack.
        """
        interpreter = sys._pyzoInterpreter
        
        if not self._debugmode:
            self.message("Not in debug mode.")
        else:
            # Increase frame index
            interpreter._dbFrameIndex += 1
            if interpreter._dbFrameIndex > len(interpreter._dbFrames):
                interpreter._dbFrameIndex = len(interpreter._dbFrames)
            # Set name and locals
            frame = interpreter._dbFrames[interpreter._dbFrameIndex-1]
            interpreter._dbFrameName = frame.f_code.co_name
            interpreter.locals = frame.f_locals
            interpreter.globals = frame.f_globals
            self.writestatus()
    
    
    def do_stop(self, arg):
        """ Stop debugging, terminate process execution.
        """
        # Can be done both in postmortem and normal debugging
        if not self._debugmode:
            self.message("Not in debug mode.")
        else:
            self.set_quit()
            self.stopinteraction()
    
    
    def do_where(self, arg):
        """ Print the stack trace and indicate the current frame.
        """
        interpreter = sys._pyzoInterpreter
        
        if not self._debugmode:
            self.message("Not in debug mode.")
        else:
            lines = []
            for i in range(len(interpreter._dbFrames)):
                frameIndex = i+1
                f = interpreter._dbFrames[i]
                # Get fname and lineno, and correct if required
                fname, lineno = f.f_code.co_filename, f.f_lineno
                fname, lineno = interpreter.correctfilenameandlineno(fname,
                                                                        lineno)
                # Build string
                text = 'File "%s", line %i, in %s' % (
                                        fname, lineno, f.f_code.co_name)
                if frameIndex == interpreter._dbFrameIndex:
                    lines.append('-> %i: %s'%(frameIndex, text))
                else:
                    lines.append('   %i: %s'%(frameIndex, text))
            lines.append('')
            sys.stdout.write('\n'.join(lines))
    
    
    def do_continue(self, arg):
        """ Continue the program execution.
        """
        if self._debugmode == 0:
            self.message("Not in debug mode.")
        elif self._debugmode == 1:
            self.message("Cannot use 'continue' in postmortem debug mode.")
        else:
            self.set_continue()
            self.stopinteraction()
    
    
    def do_step(self, arg):
        """ Execute the current line, stop ASAP (step into).
        """
        if self._debugmode == 0:
            self.message("Not in debug mode.")
        elif self._debugmode == 1:
            self.message("Cannot use 'step' in postmortem debug mode.")
        else:
            self.set_step()
            self.stopinteraction()
    
    
    def do_next(self, arg):
        """ Continue execution until the next line (step over).
        """
        interpreter = sys._pyzoInterpreter
        
        if self._debugmode == 0:
            self.message("Not in debug mode.")
        elif self._debugmode == 1:
            self.message("Cannot use 'next' in postmortem debug mode.")
        else:
            frame = interpreter._dbFrames[-1]
            self.set_next(frame)
            self.stopinteraction()
    
    
    def do_return(self, arg):
        """ Continue execution until the current function returns (step out).
        """
        interpreter = sys._pyzoInterpreter
        
        if self._debugmode == 0:
            self.message("Not in debug mode.")
        elif self._debugmode == 1:
            self.message("Cannot use 'return' in postmortem debug mode.")
        else:
            frame = interpreter._dbFrames[-1]
            self.set_return(frame)
            self.stopinteraction()
    
    
    def do_events(self, arg):
        """ Process GUI events for the integrated GUI toolkit.
        """
        interpreter = sys._pyzoInterpreter
        interpreter.guiApp.process_events()
