#!/usr/bin/env python3
"""
asciidoc3api - AsciiDoc3 API wrapper class.

The AsciiDoc3API class provides an API for executing asciidoc. Minimal example
compiles `mydoc.txt` to `mydoc.html`:

  import asciidoc3api
  asciidoc3 = asciidoc3api.AsciiDoc3API()
  asciidoc3.execute('mydoc.txt')

- Full documentation in asciidoc3api.txt.
- See the doctests below for more examples.

Doctests: ...

1. Check execution:

   >>> import io
   >>> infile = io.StringIO('Hello *{author}*')
   >>> outfile = io.StringIO()
   >>> asciidoc3 = AsciiDoc3API()
   >>> asciidoc3.options('--no-header-footer')
   >>> asciidoc3.attributes['author'] = 'Joe Bloggs'
   >>> asciidoc3.execute(infile, outfile, backend='html4')
   >>> print(outfile.getvalue())
   <p>Hello <strong>Joe Bloggs</strong></p>

   >>> asciidoc3.attributes['author'] = 'Bill Smith'
   >>> infile = io.StringIO('Hello _{author}_')
   >>> outfile = io.StringIO()
   >>> asciidoc3.execute(infile, outfile, backend='docbook')
   >>> print(outfile.getvalue())
   <simpara>Hello <emphasis>Bill Smith</emphasis></simpara>

2. Check error handling:

   >>> import io
   >>> asciidoc3 = AsciiDoc3API()
   >>> infile = io.StringIO('---------')
   >>> outfile = io.StringIO()
   >>> asciidoc3.execute(infile, outfile)
   Traceback (most recent call last):
     File "<stdin>", line 1, in <module>
     File "asciidoc3api.py", line 189, in execute
       raise AsciiDoc3Error(self.messages[-1])
   AsciiDoc3Error: ERROR: <stdin>: line 1: [blockdef-listing] missing closing delimiter

Copyright (C) 2009 Stuart Rackham.
Copyright (C) 2018-2019 Berthold Gehrke <berthold.gehrke@gmail.com>.
Free use of this software is granted under the terms of the
GNU General Public License v2 or higher (GPLv2+).
"""

import os
#import re # not used in AsciiDoc3
import sys
import importlib

# next two lines are momentarily unused placeholders
# since we have no doctests yet
API_VERSION = '0.1.2'
MIN_ASCIIDOC3_VERSION = '3.1.0'

def find_in_path(fname, path=None):
    """
    Find file fname in paths. Return None if not found.
    """
    if path is None:
        path = os.environ.get('PATH', '')
    for _dir in path.split(os.pathsep):
        fpath = os.path.join(_dir, fname)
        if os.path.isfile(fpath):
            return fpath
    else:
        return None


class AsciiDoc3Error(Exception):
    """
    Helps to distinguish API-Errors from remaining Python-Errors.
    """
    pass


class Options(object):
    """
    Stores asciidoc3 command options.
    """
    def __init__(self, values=[]):
        self.values = values[:]
    def __call__(self, name, value=None):
        """Shortcut for append method."""
        self.append(name, value)
    def append(self, name, value=None):
        """append(optname, 4.56) appends tuple
           (optname, '4.56') to list 'values'"""
        if type(value) in (int, float):
            value = str(value)
        self.values.append((name, value))

# 'class Version' not yet implemented in AsciiDoc3
# used in Ascidoc v2 for doctests
##class Version(object):
##    """
##    Parse and compare AsciiDoc version numbers. Instance attributes:
##    ...
##    """
##    def __init__(self, version):
##        self.string = version
##        ...
##        return result


class AsciiDoc3API(object):
    """
    AsciiDoc3 API class.
    """
    def __init__(self, asciidoc3_py=None):
        """
        Locate and import asciidoc3.py.
        Initialize instance attributes.
        """
        self.options = Options()
        self.attributes = {}
        self.messages = []
        # Search for the asciidoc3 command file.
        # Try ASCIIDOC3_PY environment variable first.
        cmd = os.environ.get('ASCIIDOC3_PY')
        if cmd:
            if not os.path.isfile(cmd):
                raise AsciiDoc3Error('missing ASCIIDOC3_PY file: %s' % cmd)
        elif asciidoc3_py:
            # Next try path specified by caller.
            cmd = asciidoc3_py
            if not os.path.isfile(cmd):
                raise AsciiDoc3Error('missing file: %s' % cmd)
        else:
            # Try shell search paths.
            for fname in ['asciidoc3.py', 'asciidoc3.pyc', 'asciidoc3']:
                cmd = find_in_path(fname)
                if cmd:
                    break
            else:
                # Finally try current working directory.
                for cmd in ['asciidoc3.py', 'asciidoc3.pyc', 'asciidoc3']:
                    if os.path.isfile(cmd):
                        break
                else:
                    raise AsciiDoc3Error('failed to locate asciidoc3')
        self.cmd = os.path.realpath(cmd)
        self.__import_asciidoc3()

    def __import_asciidoc3(self, reload=False):
        '''
        Import asciidoc3 module (script or compiled .pyc). See
        http://groups.google.com/group/asciidoc/browse_frm/thread/66e7b59d12cd2f91
        for an explanation of why a seemingly straight-forward job turned out
        quite complicated.
        '''
        if os.path.splitext(self.cmd)[1] in ['.py', '.pyc']:
            sys.path.insert(0, os.path.dirname(self.cmd))
            try:
                try:
                    if reload:
                        import builtins  # Because reload() is shadowed.
                        importlib.reload(self.asciidoc3)
                    else:
                        import asciidoc3
                        self.asciidoc3 = asciidoc3
                except ImportError:
                    raise AsciiDoc3Error('failed to import ' + self.cmd)
            finally:
                del sys.path[0]
        else:
            # 'else'-branch perhaps not neccessary any more in Python3
            # The import statement can only handle .py or .pyc files, have to
            # use imp.load_source() for scripts with other names.
            try:
                importlib.import_module('asciidoc3')
                self.asciidoc3 = asciidoc3
            except ImportError:
                raise AsciiDoc3Error('failed to import ' + self.cmd)
#        (doctest) Not yet implemented in AsciiDoc3
#        if Version(self.asciidoc3.VERSION) < Version(MIN_ASCIIDOC3_VERSION):
#            raise AsciiDoc3Error(
#                'asciidoc3api %s requires asciidoc3 %s or better'
#                % (API_VERSION, MIN_ASCIIDOC3_VERSION))

    def execute(self, infile, outfile=None, backend=None):
        """
        Compile infile to outfile using backend format.
        infile and outfile can be file path strings or file like objects.
        """
        self.messages = []
        opts = Options(self.options.values)
        if outfile is not None:
            opts('--out-file', outfile)
        if backend is not None:
            opts('--backend', backend)
        for k, v in list(self.attributes.items()):
            if v == '' or k[-1] in '!@':
                s = k
            elif v is None: # A None value undefines the attribute.
                s = k + '!'
            else:
                s = '%s=%s' % (k, v)
            opts('--attribute', s)
        args = [infile]
        # The AsciiDoc3 command was designed to process source text then
        # exit, there are globals and statics in asciidoc3.py that have
        # to be reinitialized before each run -- hence the reload.
        self.__import_asciidoc3(reload=True)
        try:
            try:
                self.asciidoc3.execute(self.cmd, opts.values, args)
            finally:
                self.messages = self.asciidoc3.messages[:]
        except SystemExit as e:
            if e.code:
                raise AsciiDoc3Error(self.messages[-1])


if __name__ == "__main__":
    # Run module doctests.
    import doctest
    options = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS
    doctest.testmod(optionflags=options)
