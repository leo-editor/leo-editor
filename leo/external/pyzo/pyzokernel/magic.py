# -*- coding: utf-8 -*-
# Copyright (C) 2016, the Pyzo development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

"""
Magic commands for the Pyzo kernel.
No need to use printDirect here, magic commands are just like normal Python
commands, in the sense that they print something etc.
"""

import sys
import os
import re
import time
import inspect
import tokenize, token, keyword
try:
    import io
except ImportError:  # Not on Python 2.4
    pass

# Set Python version and get some names
PYTHON_VERSION = sys.version_info[0]
if PYTHON_VERSION < 3:
    input = raw_input  # noqa

MESSAGE = """List of *magic* commands:
    ?               - show this message
    ?X or X?        - show docstring of X
    ??X or X??      - help(X)
    cd              - show current directory
    cd X            - change directory
    ls              - list current directory
    who             - list variables in current workspace
    whos            - list variables plus their class and representation
    timeit X        - times execution of command X
    open X          - open file X or the Python module that defines object X
    run X           - run file X
    install         - install a new package
    update          - update an installed package
    remove          - remove (i.e. uninstall) an installed package
    uninstall       - alias for remove
    conda           - manage packages using conda
    pip             - manage packages using pip
    db X            - debug commands
    cls             - clear screen
    notebook        - launch the Jupyter notebook
"""


TIMEIT_MESSAGE = """Time execution duration. Usage:
    timeit fun  # where fun is a callable
    timeit 'expression'
    timeit expression
    timeit 20 fun/expression  # tests 20 passes
"""

def _should_not_interpret_as_magic(line):
    interpreter = sys._pyzoInterpreter
    
    # Check that line is not some valid python input
    try:
        # gets a list of 5-tuples, of which [0] is the type of token and [1] is the token string
        ltok = list(tokenize.tokenize(io.BytesIO(line.encode('utf-8')).readline))
    except tokenize.TokenError:  # typically this means an unmatched parenthesis
                                 # (which should not happen because these are detected before)
        return True
    
    # ignore garbage and indentation at the beginning
    pos = 0
    while pos < len(ltok) and ltok[pos][0] in [59, token.INDENT, tokenize.ENCODING]:
        # 59 is BACKQUOTE but there is no token.BACKQUOTE...
        pos = pos + 1
    # when line is only garbage or does not begin with a name
    if pos >= len(ltok) or ltok[pos][0] != token.NAME:
        return True
    command = ltok[pos][1]
    if keyword.iskeyword(command):
        return True
    pos = pos + 1
    # command is alone on the line
    if pos >= len(ltok) or ltok[pos][0] in [token.ENDMARKER, tokenize.COMMENT]:
        if command in interpreter.locals:
            return True
        if interpreter.globals and command in interpreter.globals:
            return True
    else: # command is not alone ; next token should not be an operator (this includes parentheses)
        if ltok[pos][0] == token.OP and not line.endswith('?'):
            return True
    
    return False


class Magician:
    
    def _eval(self, command):
        
        # Get namespace
        NS1 = sys._pyzoInterpreter.locals
        NS2 = sys._pyzoInterpreter.globals
        if not NS2:
            NS = NS1
        else:
            NS = NS2.copy()
            NS.update(NS1)
        
        # Evaluate in namespace
        return eval(command, {}, NS)
    
    
    def convert_command(self, line):
        """ convert_command(line)
        
        Convert a given command from a magic command to Python code.
        Returns the converted command if it was a magic command, or
        the original otherwise.
        
        """
        # Get converted command, catch and report errors
        try:
            res = self._convert_command(line)
        except Exception:
            # Try informing about line number
            type, value, tb = sys.exc_info()
            msg = 'Error in handling magic function:\n'
            msg += '  %s\n' % str(value)
            if tb.tb_next: tb = tb.tb_next.tb_next
            while tb:
                msg += '  line %i in %s\n' % (tb.tb_lineno, tb.tb_frame.f_code.co_filename)
                tb = tb.tb_next
            # Clear
            del tb
            # Write
            print(msg)
            return None
        
        # Process
        if res is None:
            return line
        else:
            return res
    
    
    def _convert_command(self, line):
        
        # Get interpreter
        interpreter = sys._pyzoInterpreter
        command = line.rstrip()
        
        have_hard_chars = 'cd ', '?'
        if PYTHON_VERSION >= 3 and not command.lower().startswith(have_hard_chars):
            try:
                if _should_not_interpret_as_magic(line):
                    return
            except Exception:
                pass  # dont break interpreter if above func has a bug ...
                
        else:
            # Old, not as good check for outdated Python version
            # Check if it is a variable
            if ' ' not in command:
                if command in interpreter.locals:
                    return
                if interpreter.globals and command in interpreter.globals:
                    return
            
        # Clean and make case insensitive
        command = line.upper().rstrip()
        
        # Commands to always support (also with IPython)
        
        if not command:
            return
        
        elif command.startswith('DB'):
            return self.debug(line, command)
        
        elif command.startswith('NOTEBOOK'):
            return self.notebook(line, command)
        
        elif command.startswith('INSTALL'):
            return self.install(line, command)
        
        elif command.startswith('UPDATE') or command.startswith('UPGRADE'):
            line = line.replace('upgrade', 'update')
            command = command.replace('UPGRADE', 'UPDATE')
            return self.update(line, command)
        
        elif command.startswith('REMOVE') or command.startswith('UNINSTALL'):
            line = line.replace('uninstall', 'remove')
            return self.remove(line, command)
        
        elif command.startswith('CONDA'):
            return self.conda(line, command)
        
        elif command.startswith('PIP'):
            return self.pip(line, command)
        
        elif command == 'CLS':
            return self.cls(line, command)
        
        elif command.startswith('OPEN '):
            return self.open(line, command)
        
        elif interpreter._ipython:
            # Patch IPython magic
            
            # EDIT do not run code after editing
            if command.startswith('EDIT ') and not ' -X ' in command:
                return 'edit -x ' + line[5:]
            
            # In all cases stop processing magic commands
            return
        
        # Commands that we only support in the absense of IPtython
        
        elif command == '?':
            return 'print(%s)' % repr(MESSAGE)
        
        elif command.startswith("??"):
            return 'help(%s)' % line[2:].rstrip()
        elif command.endswith("??"):
            return 'help(%s)' % line.rstrip()[:-2]
        
        elif command.startswith("?"):
            return 'print(%s.__doc__)' % line[1:].rstrip()
            
        elif command.endswith("?"):
            return 'print(%s.__doc__)' % line.rstrip()[:-1]
        
        elif command.startswith('CD'):
            return self.cd(line, command)
        
        elif command.startswith('LS'):
            return self.ls(line, command)
        
        elif command.startswith('TIMEIT'):
            return self.timeit(line, command)
        
        elif command == 'WHO':
            return self.who(line, command)
        
        elif command == 'WHOS':
            return self.whos(line, command)
        
        elif command.startswith('RUN '):
            return self.run(line, command)
    
    
    def debug(self, line, command):
        if command == 'DB':
            line = 'db help'
        elif not command.startswith('DB '):
            return
        
        # Get interpreter
        interpreter = sys._pyzoInterpreter
        # Get command and arg
        line += ' '
        _, cmd, arg = line.split(' ', 2)
        cmd = cmd.lower()
        # Get func
        func = getattr(interpreter.debugger, 'do_'+cmd, None)
        # Call or show warning
        if func is not None:
            func(arg.strip())
        else:
            interpreter.write("Unknown debug command: %s.\n" % cmd)
        # Done (no code to execute)
        return ''
    
    
    def cd(self, line, command):
        if command == 'CD' or command.startswith("CD ") and '=' not in command:
            path = line[3:].strip()
            if path:
                try:
                    os.chdir(path)
                except Exception:
                    print('Could not change to directory "%s".' % path)
                    return ''
                newPath = os.getcwd()
            else:
                newPath = os.getcwd()
            # Done
            print(repr(newPath))
            return ''
    
    def ls(self, line, command):
        if command == 'LS' or command.startswith("LS ") and '=' not in command:
            path = line[3:].strip()
            if not path:
                path = os.getcwd()
            L = [p for p in os.listdir(path) if not p.startswith('.')]
            text = '\n'.join(sorted(L))
            # Done
            print(text)
            return ''
    
    
    def timeit(self, line, command):
        if command == "TIMEIT":
            return 'print(%s)' % repr(TIMEIT_MESSAGE)
        elif command.startswith("TIMEIT "):
            expression = line[7:]
            # Get number of iterations
            N = 1
            tmp = expression.split(' ',1)
            if len(tmp)==2:
                try:
                    N = int(tmp[0])
                    expression = tmp[1]
                except Exception:
                    N = 1
            if expression[0] not in '\'\"':
                isidentifier = lambda x: bool(re.match(r'[a-z_]\w*$', x, re.I))
                if not isidentifier(expression):
                    expression = "'%s'" % expression
            # Compile expression
            line2 = 'import timeit; t=timeit.Timer(%s);' % expression
            line2 += 'print(str( t.timeit(%i)/%i ) ' % (N, N)
            line2 += '+" seconds on average for %i iterations." )' % N
            #
            return line2
    
    
    def who(self, line, command):
        L = self._eval('dir()\n')
        L = [k for k in L if not k.startswith('__')]
        if L:
            print(', '.join(L))
        else:
            print("There are no variables defined in this scope.")
        return ''
    
    
    def _justify(self, line, width, offset):
        realWidth = width - offset
        if len(line) > realWidth:
            line = line[:realWidth-3] + '...'
        return line.ljust(width)
    
    
    def whos(self, line, command):
        # Get list of variables
        L = self._eval('dir()\n')
        L = [k for k in L if not k.startswith('__')]
        # Anny variables?
        if not L:
            print("There are no variables defined in this scope.")
            return ''
        else:
            text = "VARIABLE: ".ljust(20,' ') + "TYPE: ".ljust(20,' ')
            text += "REPRESENTATION: ".ljust(20,' ') + '\n'
        # Create list item for each variablee
        for name in L:
            ob = self._eval(name)
            cls = ''
            if hasattr(ob, '__class__'):
                cls = ob.__class__.__name__
            rep = repr(ob)
            text += self._justify(name,20,2) + self._justify(cls,20,2)
            text += self._justify(rep,40,2) + '\n'
        # Done
        print(text)
        return ''
    
    def cls(self, line, command):
        sys._pyzoInterpreter.context._strm_action.send('cls')
        return ''
    
    def open(self, line, command):
        
        # Get what to open
        name = line.split(' ',1)[1].strip()
        fname = ''
        linenr = None
        
        # Is it a file name?
        tmp = os.path.join(os.getcwd(), name)
        #
        if name[0] in '"\'' and name[-1] in '"\'': # Explicitly given
            fname = name[1:-1]
        elif os.path.isfile(tmp):
            fname = tmp
        elif os.path.isfile(name):
            fname = name
        
        else:
            # Then it maybe is an object
            
            # Get the object
            try:
                ob = self._eval(name)
            except NameError:
                print('There is no object known as "%s"' % name)
                return ''
            
            # Try get filename
            for iter in range(3):
                # Try successive steps
                if iter == 0:
                    ob = ob
                elif iter == 1 and not isinstance(ob, type):
                    ob = ob.__class__
                elif iter == 2 and hasattr(ob, '__module__'):
                    ob = sys.modules[ob.__module__]
                # Try get fname
                fname = ''
                try:
                    fname = inspect.getsourcefile(ob)
                except Exception:
                    pass
                # Returned fname may simply be x.replace('.pyc', '.py')
                if os.path.isfile(fname):
                    break
            
            # Try get line number
            if fname:
                try:
                    lines, linenr = inspect.getsourcelines(ob)
                except Exception:
                    pass
        
        # Almost done
        # IPython's edit now support this via our hook in interpreter.py
        if not fname:
            print('Could not determine file name for object "%s".' % name)
        elif linenr is not None:
            action = 'open %i %s' % (linenr, os.path.abspath(fname))
            sys._pyzoInterpreter.context._strm_action.send(action)
        else:
            action = 'open %s' % os.path.abspath(fname)
            sys._pyzoInterpreter.context._strm_action.send(action)
        #
        return ''
    
    
    def run(self, line, command):
        
        # Get what to open
        name = line.split(' ',1)[1].strip()
        fname = ''
        
        # Enable dealing with qoutes
        if name[0] in '"\'' and name[-1] in '"\'':
            name = name[1:-1]
        
        # Is it a file name?
        tmp = os.path.join(os.getcwd(), name)
        #
        if os.path.isfile(tmp):
            fname = tmp
        elif os.path.isfile(name):
            fname = name
        
        # Go run!
        if not fname:
            print('Could not find file to run "%s".' % name)
        else:
            sys._pyzoInterpreter.runfile(fname)
        #
        return ''
    
    
    def _hasconda(self):
        try:
            from conda import __version__
        except ImportError:
            return False
        return True
    
    def install(self, line, command):
        if not command.startswith('INSTALL '):
            return
        
        hasconda = self._hasconda()
        
        if hasconda:
            text = "Trying installation with conda. If this does not work, try:\n"
            text += "   pip " + line + "\n"
        else:
            text = "Trying installation with pip\n"
            
        print("\x1b[34m\x1b[1m" + text + "\x1b[0m")
        time.sleep(0.2)
        
        if hasconda:
            self.conda('conda ' + line, 'CONDA')
        else:
            self.pip('pip ' + line, 'PIP')
        return ''
    
    def update(self, line, command):
        if not command.startswith('UPDATE '):
            return
        
        hasconda = self._hasconda()
        
        if hasconda:
            text = "Trying update with conda. If this does not work, try:\n"
            text += "   pip " + line.replace('update', 'install') + " --upgrade\n"
        else:
            text = "Trying pip install --upgrade\n"
        
        print("\x1b[34m\x1b[1m" + text + "\x1b[0m")
        time.sleep(0.2)
        
        if hasconda:
            self.conda('conda ' + line, 'CONDA')
        else:
            self.pip('pip ' + line.replace('update', 'install') + " --upgrade", 'PIP')
        return ''
    
    def remove(self, line, command):
        if not command.startswith(('REMOVE ', 'UNINSTALL')):
            return
        
        hasconda = self._hasconda()
        
        if hasconda:
            text = "Trying remove/uninstall with conda. If this does not work, try:\n"
            text += "   pip " + line.replace('remove', 'uninstall') + "\n"
        else:
            text = "Trying remove/uninstall with pip\n"
        
        if hasconda:
            self.conda('conda ' + line, 'CONDA')
        else:
            self.pip('pip ' + line.replace('remove', 'uninstall'), 'PIP')
        return ''
    
    def conda(self, line, command):
        
        if not (command == 'CONDA' or command.startswith('CONDA ')):
            return
        
        # Get command args
        args = line.split(' ')
        args = [w for w in args if w]
        args.pop(0) # remove 'conda'
        
        # Stop if user does "conda = ..."
        if args and '=' in args[0]:
            return
        
        # Add channels when using install, this gets added last, so
        # that user-specified channels take preference
        channel_list = []
        if args and args[0] == 'install':
            channel_list = ['-c', 'conda-forge', '-c', 'pyzo']
        
        def write_no_dots(x):
            if x.strip() == '.':  # note, no "x if y else z" in Python 2.4
                return 0
            return stderr_write(x)
        
        # Go!
        # Weird double-try, to make work on Python 2.4
        oldargs = sys.argv
        stderr_write = sys.stderr.write
        try:
            try:
                # older version of conda would spew dots to stderr during downloading
                sys.stderr.write = write_no_dots
                import conda  # noqa
                from conda.cli import main
                sys.argv = ['conda'] + list(args) + channel_list
                main()
            except SystemExit:  # as err:
                type, err, tb = sys.exc_info(); del tb
                err = str(err)
                if len(err) > 4:  # Only print if looks like a message
                    print(err)
            except Exception:  # as err:
                type, err, tb = sys.exc_info(); del tb
                print('Error in conda command:')
                print(err)
        finally:
            sys.argv = oldargs
            sys.stderr.write = stderr_write
        
        return ''
    
    # todo: I think we can deprecate this
    def _check_imported_modules(self):
        KNOWN_PURE_PYHON = ('conda', 'yaml', 'IPython', 'requests',
                            'readline', 'pyreadline')
        if not sys.platform.startswith('win'):
            return  # Only a problem on Windows
        # Check what modules are currently imported
        loaded_modules = set()
        for name, mod in sys.modules.items():
            if 'site-packages' in getattr(mod, '__file__', ''):
                name = name.split('.')[0]
                if name.startswith('_') or name in KNOWN_PURE_PYHON:
                    continue
                loaded_modules.add(name)
        # Add PySide PyQt4 from IEP if prefix is the same
        if os.getenv('IEP_PREFIX', '') == sys.prefix:
            loaded_modules.add(os.getenv('IEP_QTLIB', 'qt'))
        # Warn if we have any such modules
        loaded_modules = [m.lower() for m in loaded_modules if m]
        if loaded_modules:
            print('WARNING! The following modules are currently loaded:\n')
            print('  ' + ', '.join(sorted(loaded_modules)))
            print('\nUpdating or removing them may fail if they are not '
                  'pure Python.\nIf none of the listed packages is updated or '
                  'removed, it is safe\nto proceed (use "f" if necessary).\n')
            print('-'*80)
            time.sleep(2.0)  # Give user time to realize there is a warning
    
    def pip(self, line, command):
        
        if not (command == 'PIP' or command.startswith('PIP ')):
            return
        
        # Get command args
        args = line.split(' ')
        args = [w for w in args if w]
        args.pop(0) # remove 'pip'
        
        # Stop if user does "pip = ..."
        if args and '=' in args[0]:
            return
        
        # Tweak the args
        if args and args[0] == 'uninstall':
            args.insert(1, '--yes')
        
        # Go!
        try:
            from pyzokernel.pipper import pip_command
            pip_command(*args)
        except SystemExit:  # as err:
            type, err, tb = sys.exc_info(); del tb
            err = str(err)
            if len(err) > 4:  # Only print if looks like a message
                print(err)
        except Exception:# as err:
            type, err, tb = sys.exc_info(); del tb
            print('Error in pip command:')
            print(err)
        
        return ''
    
    def notebook(self, line, command):
        
        if not (command == 'NOTEBOOK' or command.startswith('NOTEBOOK ')):
            return
        
        # Get command args
        args = line.split(' ')
        args = [w.replace('%20', ' ') for w in args if w]
        args.pop(0) # remove 'notebook'
        
        # Stop if user does "conda = ..."
        if args and '=' in args[0]:
            return
        
        # Go!
        # Weird double-try, to make work on Python 2.4
        oldargs = sys.argv
        try:
            try:
                import notebook.notebookapp
                sys.argv = ['jupyter_notebook'] + list(args)
                notebook.notebookapp.main()
            except SystemExit:  # as err:
                type, err, tb = sys.exc_info(); del tb
                err = str(err)
                if len(err) > 4:  # Only print if looks like a message
                    print(err)
            except Exception:  # as err:
                type, err, tb = sys.exc_info(); del tb
                print('Error in notebook command:')
                print(err)
        finally:
            sys.argv = oldargs
        
        return ''
