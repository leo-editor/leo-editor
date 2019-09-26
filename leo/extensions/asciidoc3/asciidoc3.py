#!/usr/bin/env python3

"""
asciidoc3.py converts an AsciiDoc text file to HTML or DocBook or
Manpage using Python3.x - asciidoc3.py is also used by a2x3.py
Copyright (C) 2002-2010 Stuart Rackham
Copyright (C) 2018-2019 by Berthold Gehrke <berthold.gehrke@gmail.com>
          for Python3 version and 2to3 work.
Free use of this software is granted under the terms of the
GNU General Public License Version 2 or higher (GNU GPLv2+).
"""

import ast
from ast import literal_eval
from codecs import lookup
import collections
from copy import copy as ccopy
from csv import reader as csv_reader
from decimal import Decimal, ROUND_HALF_UP
from functools import lru_cache
import getopt
from io import StringIO as io_StringIO
from itertools import repeat as itertools_repeat
from locale import getdefaultlocale
import os
import re
import shutil
import subprocess
import sys
from tempfile import mkstemp
import time
import traceback
from unicodedata import east_asian_width, normalize
import zipfile

### Used by asciidoc3api.py ###
VERSION = '3.1.0'           # See CHANGELOG file for version history.
MIN_PYTHON_VERSION = '3.4'  # Require this version of Python or better.
                            # Note: Python3.4 has reached EOL, so consider
                            # updating your Python!
#---------------------------------------------------------------------------
# Program constants.
#---------------------------------------------------------------------------
DEFAULT_BACKEND = 'html'
DEFAULT_DOCTYPE = 'article'
# Allowed substitution options for List, Paragraph and DelimitedBlock
# definition subs entry.
SUBS_OPTIONS = ('specialcharacters', 'quotes', 'specialwords',
                'replacements', 'attributes', 'macros', 'callouts', 'normal',
                'verbatim', 'none', 'replacements2', 'replacements3')
# Default value for unspecified subs and presubs configuration file entries.
SUBS_NORMAL = ('specialcharacters', 'quotes', 'attributes', 'specialwords',
               'replacements', 'macros', 'replacements2')
SUBS_VERBATIM = ('specialcharacters', 'callouts')

NAME_RE = r'[^\W\d][-\w]*'    # Valid section or attribute name.
OR, AND = ',', '+'            # Attribute list separators.

#---------------------------------------------------------------------------
# Utility functions and classes.
#---------------------------------------------------------------------------

class EAsciiDoc(Exception):
    """
    Subclass of 'Exception' to make a difference between
    builtin Python Errors and AsciiDoc3-Errors.
    """


class AttrDict(dict):
    """
    Like a dictionary except values can be accessed as attributes
    i.e. obj.foo can be used in addition to obj['foo'].
    If an item is not present None is returned.
    """
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            return None

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError as k:
            raise AttributeError(k)

    def __repr__(self):
        return '<AttrDict ' + dict.__repr__(self) + '>'

    def __getstate__(self):
        return dict(self)

    def __setstate__(self, value):
        for k, v in list(value.items()):
            self[k] = v


class InsensitiveDict(dict):
    """
    Like a dictionary except key access is case insensitive.
    Keys are stored in lower case.
    """
    def __getitem__(self, key):
        return dict.__getitem__(self, key.lower())

    def __setitem__(self, key, value):
        dict.__setitem__(self, key.lower(), value)

    # 'has_key()' is never called in asciidoc3.py
    # and not existent in Python3 anyway!
    #def has_key(self, key):
    #    return dict.has_key(self, key.lower())

    def get(self, key, default=None):
        return dict.get(self, key.lower(), default)

    def update(self, dict):
        for k, v in list(dict.items()):
            self[k] = v

    def setdefault(self, key, default=None):
        return dict.setdefault(self, key.lower(), default)


class Trace():
    """
    Used in conjunction with the 'trace' attribute to generate diagnostic
    output. There is a single global instance of this class named trace.
    """
    SUBS_NAMES = ('specialcharacters', 'quotes', 'specialwords',
                  'replacements', 'attributes', 'macros', 'callouts',
                  'replacements2', 'replacements3')

    def __init__(self):
        self.name_re = ''        # Regexp pattern to match trace names.
        self.linenos = True
        self.offset = 0

    def __call__(self, name, before, after=None):
        """
        Print trace message if tracing is on and the trace 'name' matches
        the document 'trace' attribute (treated as a regexp).
        'before' is the source text before substitution; 'after' text is
        the source text after substitution.
        The 'before' and 'after' messages are only printed if they differ.
        """
        name_re = document.attributes.get('trace')
        if name_re == 'subs':    # Alias for all the inline substitutions.
            name_re = '|'.join(self.SUBS_NAMES)
        self.name_re = name_re
        if self.name_re is not None:
            msg = message.format(name, 'TRACE: ', \
                                 self.linenos, offset=self.offset)
            if before != after and re.match(self.name_re, name):
                if is_array(before):
                    before = '\n'.join(before)
                if after is None:
                    msg += '\n%s\n' % before
                else:
                    if is_array(after):
                        after = '\n'.join(after)
                    msg += '\n<<<\n%s\n>>>\n%s\n' % (before, after)
                message.stderr(msg)

class Message:
    """
    Message functions.
    """
    PROG = os.path.basename(os.path.splitext(__file__)[0])

    def __init__(self):
        # Set to True or False to globally override line numbers method
        # argument. Has no effect when set to None.
        self.linenos = None
        self.messages = []
        self.prev_msg = ''

    def stdout(self, msg):
        print(msg)

    def stderr(self, msg=''):
        if msg == self.prev_msg:  # Suppress repeated messages.
            return
        self.messages.append(msg)
        # __name__ == 'asciidoc3.asciidoc3' if installed via pip3
        if __name__ in ('__main__', 'asciidoc3.asciidoc3'):
            sys.stderr.write('%s: %s%s' % (self.PROG, msg, os.linesep))
        self.prev_msg = msg

    def verbose(self, msg, linenos=True):
        if config.verbose:
            msg = self.format(msg, linenos=linenos)
            self.stderr(msg)

    def warning(self, msg, linenos=True, offset=0):
        msg = self.format(msg, 'WARNING: ', linenos, offset=offset)
        document.has_warnings = True
        self.stderr(msg)

    def deprecated(self, msg, linenos=True):
        msg = self.format(msg, 'DEPRECATED: ', linenos)
        self.stderr(msg)

    def format(self, msg, prefix='', linenos=True, cursor=None, offset=0):
        """Return formatted message string."""
        if self.linenos is not False and ((linenos or self.linenos) and reader.cursor):
            if cursor is None:
                cursor = reader.cursor
            prefix += '%s: line %d: ' % (os.path.basename(cursor[0]), cursor[1]+offset)
        return prefix + msg

    def error(self, msg, cursor=None, halt=False):
        """
        Report fatal error.
        If halt=True raise EAsciiDoc exception.
        If halt=False don't exit application, continue in the hope of reporting
        all fatal errors finishing with a non-zero exit code.
        """
        if halt:
            raise EAsciiDoc(self.format(msg, linenos=False, cursor=cursor))
        else:
            msg = self.format(msg, 'ERROR: ', cursor=cursor)
            self.stderr(msg)
            document.has_errors = True

    def unsafe(self, msg):
        self.error('unsafe: '+msg)

def userdir():
    """
    Return user's home directory or None if it is not defined.
    """
    result = os.path.expanduser('~')
    if result == '~':
        result = None
    return result

def localapp():
    """
    Return True if we are not executing the system wide version
    i.e. the configuration is in the executable's directory.
    """
    return os.path.isfile(os.path.join(APP_DIR, 'asciidoc3.conf'))

def file_in(fname, directory):
    """Return True if file fname resides inside directory."""
    assert os.path.isfile(fname)
    # Empty directory (not to be confused with None) is the current directory.
    if directory == '':
        directory = os.getcwd()
    else:
        assert os.path.isdir(directory)
        directory = os.path.realpath(directory)
    fname = os.path.realpath(fname)
    return os.path.commonprefix((directory, fname)) == directory

def safe():
    return document.safe

def is_safe_file(fname, directory=None):
    # A safe file must reside in 'directory' (defaults to the source
    # file directory).
    if directory is None:
        if document.infile == '<stdin>':
            return not safe()
        directory = os.path.dirname(document.infile)
    elif directory == '':
        directory = '.'
    return (
        not safe()
        or file_in(fname, directory)
        or file_in(fname, APP_DIR)
        or file_in(fname, CONF_DIR)
    )

def safe_filename(fname, parentdir):
    """
    Return file name which must reside in the parent file directory.
    Return None if file is not safe.
    """
    if not os.path.isabs(fname):
        # Include files are relative to parent document
        # directory.
        fname = os.path.normpath(os.path.join(parentdir, fname))
    if not is_safe_file(fname, parentdir):
        message.unsafe('include file: %s' % fname)
        return None
    return fname

def assign(dst, src):
    """Assign all attributes from 'src' object to 'dst' object."""
    for a, v in list(src.__dict__.items()):
        setattr(dst, a, v)

def strip_quotes(s):
    """Trim white space and, if necessary, quote characters from s."""
    s = s.strip()
    # Strip quotation mark characters from quoted strings.
    if len(s) >= 3 and s[0] == '"' and s[-1] == '"':
        s = s[1:-1]
    return s

def is_re(s):
    """Return True if s is a valid regular expression else return False."""
    try:
        re.compile(s)
    except TypeError:  # was bare 'except' in v2
        return False
    else:
        return True

def re_join(relist):
    """Join list of regular expressions re1,re2,... to single regular
    expression (re1)|(re2)|..."""
    if not relist:
        return None
    result = []
    # Delete named groups to avoid ambiguity.
    for s in relist:
        result.append(re.sub(r'\?P<\S+?>', '', s))
    result = ')|('.join(result)
    result = '('+result+')'
    return result

def lstrip_list(s):
    """
    Return list with empty items from start of list removed.
    """
    for i in range(len(s)):
        if s[i]:
            break
    else:
        return []
    return s[i:]

def rstrip_list(s):
    """
    Return list with empty items from end of list removed.
    """
    for i in range(len(s)-1, -1, -1):
        if s[i]:
            break
    else:
        return []
    return s[:i+1]

def strip_list(s):
    """
    Return list with empty items from start and end of list removed.
    """
    s = lstrip_list(s)
    s = rstrip_list(s)
    return s

def is_array(obj):
    """
    Return True if object is list or tuple type.
    """
    return isinstance(obj, (list, tuple))

def dovetail(lines1, lines2):
    """
    Append list or tuple of strings 'lines2' to list 'lines1'.  Join the last
    non-blank item in 'lines1' with the first non-blank item in 'lines2' into a
    single string.
    """
    assert is_array(lines1)
    assert is_array(lines2)
    lines1 = strip_list(lines1)
    lines2 = strip_list(lines2)
    if not lines1 or not lines2:
        return list(lines1) + list(lines2)
    result = list(lines1[:-1])
    result.append(lines1[-1] + lines2[0])
    result += list(lines2[1:])
    return result

def dovetail_tags(stag, content, etag):
    """Merge the end tag with the first content line and the last
    content line with the end tag. This ensures verbatim elements don't
    include extraneous opening and closing line breaks."""
    return dovetail(dovetail(stag, content), etag)

def get_args(val):
    d = {}
    args = ast.parse("d(" + val + ")", mode='eval').body.args
    i = 1
    for arg in args:
        if isinstance(arg, ast.Name):
            d[str(i)] = literal_eval(arg.id)
        else:
            d[str(i)] = literal_eval(arg)
        i += 1
    return d

def get_kwargs(val):
    d = {}
    args = ast.parse("d(" + val + ")", mode='eval').body.keywords
    for arg in args:
        d[arg.arg] = literal_eval(arg.value)
    return d

def parse_to_list(val):
    values = ast.parse("[" + val + "]", mode='eval').body.elts
    return [literal_eval(v) for v in values]

def parse_attributes(attrs, dict):
    """Update a dictionary with name/value attributes from the attrs string.
    The attrs string is a comma separated list of values and keyword name=value
    pairs. Values must precede keywords and are named '1','2'... The entire
    attributes list is named '0'. If keywords are specified string values must
    be quoted. Examples:

    attrs: ''
    dict: {}

    attrs: 'hello,world'
    dict: {'2': 'world', '0': 'hello,world', '1': 'hello'}

    attrs: '"hello", planet="earth"'
    dict: {'planet': 'earth', '0': '"hello",planet="earth"', '1': 'hello'}
    """
    def f(*args, **keywords):
        # Name and add arguments '1','2'... to keywords.
        for i in range(len(args)):
            if str(i+1) not in keywords:
                keywords[str(i+1)] = args[i]
        return keywords

    if not attrs:
        return
    dict['0'] = attrs
    # Replace line separators with spaces so line spanning works.
    s = re.sub(r'\s', ' ', attrs)
    d = {}
    try:
        d.update(get_args(s))
        d.update(get_kwargs(s))
        for v in list(d.values()):
            if not (isinstance(v, str) or isinstance(v, int) \
                    or isinstance(v, float) or v is None):
                raise Exception
    except Exception:
        s = s.replace('"', '\\"')
        s = s.split(',')
        s = ['"' + x.strip() + '"' for x in s]
        s = ','.join(s)
        try:
            d = {}
            d.update(get_args(s))
            d.update(get_kwargs(s))
        except Exception:
            return  # If there's a syntax error leave with {0}=attrs.
        for k in list(d.keys()):  # Drop any empty positional arguments.
            if d[k] == '':
                del d[k]
    dict.update(d)
    assert len(d)

def parse_named_attributes(s, attrs):
    """Update a attrs dictionary with name="value" attributes from the s string.
    Returns False if invalid syntax.
    Example:
    attrs: 'star="sun",planet="earth"'
    dict: {'planet':'earth', 'star':'sun'}
    """
    def f(**keywords):
        return keywords

    try:
        d = {}
        d = get_kwargs(s)
        attrs.update(d)
        return True
    except Exception:
        return False

def parse_list(s):
    """Parse comma separated string of Python literals. Return a tuple of of
    parsed values."""
    try:
        result = tuple(parse_to_list(s))
    except Exception:
        raise EAsciiDoc('malformed list: '+s)
    return result

def parse_options(options, allowed, errmsg):
    """Parse comma separated string of unquoted option names and return as a
    tuple of valid options. 'allowed' is a list of allowed option values.
    If allowed=() then all legitimate names are allowed.
    'errmsg' is an error message prefix if an illegal option error is thrown."""
    result = []
    if options:
        for s in re.split(r'\s*,\s*', options):
            if (allowed and s not in allowed) or not is_name(s):
                raise EAsciiDoc('%s: %s' % (errmsg, s))
            result.append(s)
    return tuple(result)

def symbolize(s):
    """Drop non-symbol characters and convert to lowercase."""
    return re.sub(r'[^\w\-_]', '', s).lower()

def is_name(s):
    """Return True if s is valid attribute, macro or tag name
    (starts with alpha containing alphanumeric and dashes only)."""
    return re.match(r'^'+NAME_RE+r'$', s) is not None

def subs_quotes(text):
    """Quoted text is marked up and the resulting text is
    returned."""
    keys = list(config.quotes.keys())
    for q in keys:
        i = q.find('|')
        if i != -1 and q != '|' and q != '||':
            lq = q[:i]      # Left quote.
            rq = q[i+1:]    # Right quote.
        else:
            lq = rq = q
        tag = config.quotes[q]
        if not tag:
            continue
        # Unconstrained quotes prefix the tag name with a hash.
        if tag[0] == '#':
            tag = tag[1:]
            # Unconstrained quotes can appear anywhere.
            reo = re.compile(r'(?ms)(^|.)(\[(?P<attrlist>[^[\]]+?)\])?' \
                    + r'(?:' + re.escape(lq) + r')' \
                    + r'(?P<content>.+?)(?:'+re.escape(rq)+r')')
        else:
            # The text within constrained quotes must be bounded by white space.
            # Non-word (\W) characters are allowed at boundaries to accommodate
            # enveloping quotes and punctuation e.g. a='x', ('x'), 'x', ['x'].
            reo = re.compile(r'(?ms)(^|[^\w;:}])(\[(?P<attrlist>[^[\]]+?)\])?' \
                + r'(?:' + re.escape(lq) + r')' \
                + r'(?P<content>\S|\S.*?\S)(?:'+re.escape(rq)+r')(?=\W|$)')
        pos = 0
        while True:
            mo = reo.search(text, pos)
            if not mo:
                break
            if text[mo.start()] == '\\':
                # Delete leading backslash.
                text = text[:mo.start()] + text[mo.start()+1:]
                # Skip past start of match.
                pos = mo.start() + 1
            else:
                attrlist = {}
                parse_attributes(mo.group('attrlist'), attrlist)
                stag, etag = config.tag(tag, attrlist)
                s = mo.group(1) + stag + mo.group('content') + etag
                text = text[:mo.start()] + s + text[mo.end():]
                pos = mo.start() + len(s)
    return text

def subs_tag(tag, dict={}):
    """Perform attribute substitution and split tag string returning start, end
    tag tuple (c.f. Config.tag())."""
    if not tag:
        return [None, None]
    s = subs_attrs(tag, dict)
    if not s:
        message.warning('tag \'%s\' dropped: contains undefined attribute' % tag)
        return [None, None]
    result = s.split('|')
    if len(result) == 1:
        return result+[None]
    elif len(result) == 2:
        return result
    else:
        raise EAsciiDoc('malformed tag: %s' % tag)

def parse_entry(entry, dict=None, unquote=False, unique_values=False,
                allow_name_only=False, escape_delimiter=True):
    """Parse name=value entry to dictionary 'dict'. Return tuple (name,value)
    or None if illegal entry.
    If name= then value is set to ''.
    If name and allow_name_only=True then value is set to ''.
    If name! and allow_name_only=True then value is set to None.
    Leading and trailing white space is striped from 'name' and 'value'.
    'name' can contain any printable characters.
    If the '=' delimiter character is allowed in  the 'name' then
    it must be escaped with a backslash and escape_delimiter must be True.
    If 'unquote' is True leading and trailing double-quotes are stripped from
    'name' and 'value'.
    If unique_values' is True then dictionary entries with the same value are
    removed before the parsed entry is added."""
    if escape_delimiter:
        mo = re.search(r'(?:[^\\](=))', entry)
    else:
        mo = re.search(r'(=)', entry)
    if mo:  # name=value entry.
        if mo.group(1):
            name = entry[:mo.start(1)]
            if escape_delimiter:
                name = name.replace(r'\=', '=')  # Unescape \= in name.
            value = entry[mo.end(1):]
    elif allow_name_only and entry:         # name or name! entry.
        name = entry
        if name[-1] == '!':
            name = name[:-1]
            value = None
        else:
            value = ''
    else:
        return None
    if unquote:
        name = strip_quotes(name)
        if value is not None:
            value = strip_quotes(value)
    else:
        name = name.strip()
        if value is not None:
            value = value.strip()
    if not name:
        return None
    if dict is not None:
        if unique_values:
            for k, v in list(dict.items()):
                if v == value:
                    del dict[k]
        dict[name] = value
    return name, value

def parse_entries(entries, dict, unquote=False, unique_values=False,
                  allow_name_only=False, escape_delimiter=True):
    """Parse name=value entries from  from lines of text in 'entries' into
    dictionary 'dict'. Blank lines are skipped."""
    entries = config.expand_templates(entries)
    for entry in entries:
        if entry and not parse_entry(entry, dict, unquote, unique_values,
                                     allow_name_only, escape_delimiter):
            raise EAsciiDoc('malformed section entry: %s' % entry)

def dump_section(name, dict, f=sys.stdout):
    """Write parameters in 'dict' as in configuration file section format
       with section 'name'."""
    f.write('[%s]%s' % (name, writer.newline))
    for k, v in list(dict.items()):
        k = str(k)
        k = k.replace('=', r'\=')    # Escape = in name.
        # Quote if necessary.
        if len(k) != len(k.strip()):
            k = '"'+k+'"'
        if v and len(v) != len(v.strip()):
            v = '"'+v+'"'
        if v is None:
            # Don't dump undefined attributes.
            continue
        else:
            s = k+'='+v
        if s[0] == '#':
            s = '\\' + s    # Escape so not treated as comment lines.
        f.write('%s%s' % (s, writer.newline))
    f.write(writer.newline)


def update_attrs(attrs, dict):
    """Update 'attrs' dictionary with parsed attributes in dictionary 'dict'."""
    for k, v in list(dict.items()):
        if not is_name(k):
            raise EAsciiDoc('illegal attribute name: %s' % k)
        attrs[k] = v

def is_attr_defined(attrs, dic):
    """
    Check if the sequence of attributes is defined in dictionary 'dic'.
    Valid 'attrs' sequence syntax:
    <attr> Return True if single attribute is defined.
    <attr1>,<attr2>,... Return True if one or more attributes are defined.
    <attr1>+<attr2>+... Return True if all the attributes are defined.
    """
    if OR in attrs:
        for a in attrs.split(OR):
            if dic.get(a.strip()) is not None:
                return True
        else:
            return False
    elif AND in attrs:
        for a in attrs.split(AND):
            if dic.get(a.strip()) is None:
                return False
        else:
            return True
    else:
        return dic.get(attrs.strip()) is not None

def filter_lines(filter_cmd, lines, attrs={}):
    """
    Run 'lines' through the 'filter_cmd' shell command and return the result.
    The 'attrs' dictionary contains additional filter attributes.
    """
    def findfilter(name, dir, filter):
        """Find filter file 'fname' with style name 'name' in directory
        'dir'. Return found file path or None if not found."""
        if name:
            result = os.path.join(dir, 'filters', name, filter)
            if os.path.isfile(result):
                return result
        result = os.path.join(dir, 'filters', filter)
        if os.path.isfile(result):
            return result
        return None

    # Return input lines if there's not filter.
    if not filter_cmd or not filter_cmd.strip():
        return lines
    # Perform attributes substitution on the filter command.
    s = subs_attrs(filter_cmd, attrs)
    if not s:
        message.error('undefined filter attribute in command: %s' % filter_cmd)
        return []
    filter_cmd = s.strip()
    # Parse for quoted and unquoted command and command tail.
    # Double quoted.
    mo = re.match(r'^"(?P<cmd>[^"]+)"(?P<tail>.*)$', filter_cmd)
    if not mo:
        # Single quoted.
        mo = re.match(r"^'(?P<cmd>[^']+)'(?P<tail>.*)$", filter_cmd)
        if not mo:
            # Unquoted catch all.
            mo = re.match(r'^(?P<cmd>\S+)(?P<tail>.*)$', filter_cmd)
    cmd = mo.group('cmd').strip()
    found = None
    if not os.path.dirname(cmd):
        # Filter command has no directory path so search filter directories.
        filtername = attrs.get('style')
        d = document.attributes.get('docdir')
        if d:
            found = findfilter(filtername, d, cmd)
        if not found:
            if USER_DIR:
                found = findfilter(filtername, USER_DIR, cmd)
            if not found:
                if localapp():
                    found = findfilter(filtername, APP_DIR, cmd)
                else:
                    found = findfilter(filtername, CONF_DIR, cmd)
    else:
        if os.path.isfile(cmd):
            found = cmd
        else:
            message.warning('filter not found: %s' % cmd)
    if found:
        filter_cmd = '"' + found + '"' + mo.group('tail')
    if found:
        if cmd.endswith('.py'):
            filter_cmd = '"%s" %s' % (document.attributes['python3'],
                                      filter_cmd)
        elif cmd.endswith('.rb'):
            filter_cmd = 'ruby ' + filter_cmd

    message.verbose('filtering: ' + filter_cmd)
    if os.name == 'nt':
        # Remove redundant quoting -- this is not just
        # cosmetic, unnecessary quoting appears to cause
        # command line truncation.
        filter_cmd = re.sub(r'"([^ ]+?)"', r'\1', filter_cmd)
    try:
        p = subprocess.Popen(filter_cmd, shell=True, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, universal_newlines=True, bufsize=-1)
        output = p.communicate(os.linesep.join(lines))[0]
    except Exception:
        raise EAsciiDoc('filter error: %s: %s' % (filter_cmd, sys.exc_info()[1]))
    if output:
        result = [s.rstrip() for s in output.split(os.linesep)]
    else:
        result = []
    filter_status = p.returncode
    if filter_status:
        message.warning('filter non-zero exit code: %s: returned %d' %
                        (filter_cmd, filter_status))
    if lines and not result:
        message.warning('no output from filter: %s' % filter_cmd)
    return result

def system(name, args, is_macro=False, attrs=None):
    """
    Evaluate a system attribute ({name:args}) or system block macro
    (name::[args]).
    If is_macro is True then we are processing a system block macro otherwise
    it's a system attribute.
    The attrs dictionary is updated by the counter and set system attributes.
    NOTE: The include1 attribute is used internally by the include1::[] macro
    and is not for public use.
    """
    if is_macro:
        syntax = '%s::[%s]' % (name, args)
        separator = '\n'
    else:
        syntax = '{%s:%s}' % (name, args)
        separator = writer.newline
    if name not in ('eval', 'eval3', 'sys', 'sys2', 'sys3', 'include', 'include1', \
                    'counter', 'counter2', 'set', 'set2', 'template'):
        if is_macro:
            msg = 'illegal system macro name: %s' % name
        else:
            msg = 'illegal system attribute name: %s' % name
        message.warning(msg)
        return None
    if is_macro:
        s = subs_attrs(args)
        if s is None:
            message.warning('skipped %s: undefined attribute in: %s' % (name, args))
            return None
        args = s
    if name != 'include1':
        message.verbose('evaluating: %s' % syntax)
    if safe() and name not in ('include', 'include1'):
        message.unsafe(syntax)
        return None
    result = None
    if name in ('eval', 'eval3'):
        try:
            result = eval(args)
            if result is True:
                result = ''
            elif result is False:
                result = None
            elif result is not None:
                result = str(result)
        except Exception:
            message.warning('%s: evaluation error' % syntax)
    elif name in ('sys', 'sys2', 'sys3'):
        result = ''
        fd, tmp = mkstemp()
        os.close(fd)
        try:
            cmd = args
            cmd = cmd + (' > "%s"' % tmp)
            if name == 'sys2':
                cmd = cmd + ' 2>&1'
            # We need some 'tuning' to handle 'sys' on Windows ...
            # Shelling does'nt like spaces in path (but Windows does)
            # and we have to adjust quoting, too.
            # Perhaps modules shlex and/or subprocess may help,
            # but until then we do it the hard way.
            if os.name == 'nt':
                # Begin discard space in 'path to executable'.
                path_to_executable = re.match(r'"(.*)python3?', cmd)
                if path_to_executable.group(0) and r" " in path_to_executable.group(0):
                    cmd = re.sub(r'".*python3?\.exe', r'"python3', cmd, 1, re.IGNORECASE)
                # End discard space in 'path to executable'.
                # Adjust quoting for 'sys' in 'image-inlinemacro' and 'image-blockmacro'.
                if 'ad3mtype' in cmd:
                    cmd = re.sub(r'ad3data\)" <', r'ad3data)" "<', cmd, 1, re.IGNORECASE)
                # Remove redundant quoting -- this is not just
                # cosmetic, unnecessary quoting appears to cause
                # command line truncation.
                cmd = re.sub(r'"([^ ]+?)"', r'\1', cmd)
                # End of 'tuning'.
            message.verbose('shelling: %s' % cmd)
            if os.system(cmd):
                message.warning('%s: non-zero exit status' % syntax)
            try:
                if os.path.isfile(tmp):
                    with open(tmp, encoding='utf-8') as f:
                        lines = [s.rstrip() for s in f]
                else:
                    lines = []
            except Exception:
                raise EAsciiDoc('%s: temp file read error' % syntax)
            result = separator.join(lines)
        finally:
            if os.path.isfile(tmp):
                os.remove(tmp)
    elif name in ('counter', 'counter2'):
        mo = re.match(r'^(?P<attr>[^:]*?)(:(?P<seed>.*))?$', args)
        attr = mo.group('attr')
        seed = mo.group('seed')
        if seed and (not re.match(r'^\d+$', seed) and len(seed) > 1):
            message.warning('%s: illegal counter seed: %s' % (syntax, seed))
            return None
        if not is_name(attr):
            message.warning('%s: illegal attribute name' % syntax)
            return None
        value = document.attributes.get(attr)
        if value:
            if not re.match(r'^\d+$', value) and len(value) > 1:
                message.warning('%s: illegal counter value: %s'
                                % (syntax, value))
                return None
            if re.match(r'^\d+$', value):
                expr = value + '+1'
            else:
                expr = 'chr(ord("%s")+1)' % value
            try:
                result = str(eval(expr))
            except Exception:
                message.warning('%s: evaluation error: %s' % (syntax, expr))
        else:
            if seed:
                result = seed
            else:
                result = '1'
        document.attributes[attr] = result
        if attrs is not None:
            attrs[attr] = result
        if name == 'counter2':
            result = ''
    elif name in ('set', 'set2'):
        mo = re.match(r'^(?P<attr>[^:]*?)(:(?P<value>.*))?$', args)
        attr = mo.group('attr')
        value = mo.group('value')
        if value is None:
            value = ''
        if attr.endswith('!'):
            attr = attr[:-1]
            value = None
        if not is_name(attr):
            message.warning('%s: illegal attribute name' % syntax)
        else:
            if attrs is not None:
                attrs[attr] = value
            if name != 'set2':  # set2 only updates local attributes.
                document.attributes[attr] = value
        if value is None:
            result = None
        else:
            result = ''
    elif name == 'include':
        if not os.path.exists(args):
            message.warning('%s: file does not exist' % syntax)
        elif not is_safe_file(args):
            message.unsafe(syntax)
        else:
            with open(args, encoding='utf-8') as f:
                result = [s.rstrip() for s in f]
            if result:
                result = subs_attrs(result)
                result = separator.join(result)
                result = result.expandtabs(reader.tabsize)
            else:
                result = ''
    elif name == 'include1':
        result = separator.join(config.include1[args])
    elif name == 'template':
        if args not in config.sections:
            message.warning('%s: template does not exist' % syntax)
        else:
            result = []
            for line in  config.sections[args]:
                line = subs_attrs(line)
                if line is not None:
                    result.append(line)
            result = '\n'.join(result)
    else:
        assert False
    if result and name in ('eval3', 'sys3'):
        macros.passthroughs.append(result)
        result = '\x07' + str(len(macros.passthroughs)-1) + '\x07'
    return result

def subs_attrs(lines, dictionary=None):
    """Substitute 'lines' of text with attributes from the global
    document.attributes dictionary and from 'dictionary' ('dictionary'
    entries take precedence). Return a tuple of the substituted lines.
    'lines' containing undefined attributes are deleted. If 'lines'
    is a string then return a string.

    - Attribute references are substituted in the following order: simple,
      conditional, system.
    - Attribute references inside 'dictionary' entry values are substituted.
    """

    def end_brace(text, start):
        """Return index following end brace that matches brace
           at start in text."""
        assert text[start] == '{'
        n = 0
        result = start
        for c in text[start:]:
            # Skip braces that are followed by a backslash.
            if result == len(text)-1 or text[result+1] != '\\':
                if c == '{':
                    n = n + 1
                elif c == '}':
                    n = n - 1
            result = result + 1
            if not n:
                break
        return result

    if isinstance(lines, str):
        string_result = True
        lines = [lines]
    else:
        string_result = False
    if dictionary is None:
        attrs = document.attributes
    else:
        # Remove numbered document attributes so they don't clash with
        # attribute list positional attributes.
        attrs = {}
        for k, v in list(document.attributes.items()):
            if not re.match(r'^\d+$', k):
                attrs[k] = v
        # Substitute attribute references inside dictionary values.
        for k, v in list(dictionary.items()):
            if v is None:
                del dictionary[k]
            else:
                v = subs_attrs(str(v))
                if v is None:
                    del dictionary[k]
                else:
                    dictionary[k] = v
        attrs.update(dictionary)
    # Substitute all attributes in all lines.
    result = []
    for line in lines:
        # Make it easier for regular expressions.
        line = line.replace('\\{', '{\\')
        line = line.replace('\\}', '}\\')
        # Expand simple attributes ({name}).
        # Nested attributes not allowed.
        reo = re.compile(r'(?s)\{(?P<name>[^\\\W][-\w]*?)\}(?!\\)')
        pos = 0
        while True:
            mo = reo.search(line, pos)
            if not mo:
                break
            s = attrs.get(mo.group('name'))
            if s is None:
                pos = mo.end()
            else:
                s = str(s)
                line = line[:mo.start()] + s + line[mo.end():]
                pos = mo.start() + len(s)
        # Expand conditional attributes.
        # Single name -- higher precedence.
        reo1 = re.compile(r'(?s)\{(?P<name>[^\\\W][-\w]*?)' \
                          r'(?P<op>\=|\?|!|#|%|@|\$)' \
                          r'(?P<value>.*?)\}(?!\\)')
        # Multiple names (n1,n2,... or n1+n2+...) -- lower precedence.
        reo2 = re.compile(r'(?s)\{(?P<name>[^\\\W][-\w'+OR+AND+r']*?)' \
                          r'(?P<op>\=|\?|!|#|%|@|\$)' \
                          r'(?P<value>.*?)\}(?!\\)')
        for reo in [reo1, reo2]:
            pos = 0
            while True:
                mo = reo.search(line, pos)
                if not mo:
                    break
                attr = mo.group()
                name = mo.group('name')
                if reo == reo2:
                    if OR in name:
                        sep = OR
                    else:
                        sep = AND
                    names = [s.strip() for s in name.split(sep) if s.strip()]
                    for n in names:
                        if not re.match(r'^[^\\\W][-\w]*$', n):
                            message.error('illegal attribute syntax: %s' % attr)
                    if sep == OR:
                        # Process OR name expression: n1,n2,...
                        for n in names:
                            if attrs.get(n) is not None:
                                lval = ''
                                break
                        else:
                            lval = None
                    else:
                        # Process AND name expression: n1+n2+...
                        for n in names:
                            if attrs.get(n) is None:
                                lval = None
                                break
                        else:
                            lval = ''
                else:
                    lval = attrs.get(name)
                op = mo.group('op')
                # mo.end() not good enough because '{x={y}}' matches '{x={y}'.
                end = end_brace(line, mo.start())
                rval = line[mo.start('value'):end-1]
                UNDEFINED = '{zzzzz}'
                if lval is None:
                    if op == '=':
                        s = rval
                    elif op == '?':
                        s = ''
                    elif op == '!':
                        s = rval
                    elif op == '#':
                        s = UNDEFINED   # So the line is dropped.
                    elif op == '%':
                        s = rval
                    elif op in ('@', '$'):
                        s = UNDEFINED               # So the line is dropped.
                    else:
                        assert False, 'illegal attribute: %s' % attr
                else:
                    if op == '=':
                        s = lval
                    elif op == '?':
                        s = rval
                    elif op == '!':
                        s = ''
                    elif op == '#':
                        s = rval
                    elif op == '%':
                        s = UNDEFINED   # So the line is dropped.
                    elif op in ('@', '$'):
                        v = re.split(r'(?<!\\):', rval)
                        if len(v) not in (2, 3):
                            message.error('illegal attribute syntax: %s' % attr)
                            s = ''
                        elif not is_re('^'+v[0]+'$'):
                            message.error('illegal attribute regexp: %s' % attr)
                            s = ''
                        else:
                            v = [s.replace('\\:', ':') for s in v]
                            re_mo = re.match('^'+v[0]+'$', lval)
                            if op == '@':
                                if re_mo:
                                    s = v[1]         # {<name>@<re>:<v1>[:<v2>]}
                                else:
                                    if len(v) == 3:   # {<name>@<re>:<v1>:<v2>}
                                        s = v[2]
                                    else:             # {<name>@<re>:<v1>}
                                        s = ''
                            else:
                                if re_mo:
                                    if len(v) == 2:   # {<name>$<re>:<v1>}
                                        s = v[1]
                                    elif v[1] == '':  # {<name>$<re>::<v2>}
                                        s = UNDEFINED # So the line is dropped.
                                    else:             # {<name>$<re>:<v1>:<v2>}
                                        s = v[1]
                                else:
                                    if len(v) == 2:   # {<name>$<re>:<v1>}
                                        s = UNDEFINED # So the line is dropped.
                                    else:             # {<name>$<re>:<v1>:<v2>}
                                        s = v[2]
                    else:
                        assert False, 'illegal attribute: %s' % attr
                s = str(s)
                line = line[:mo.start()] + s + line[end:]
                pos = mo.start() + len(s)
        # Drop line if it contains  unsubstituted {name} references.
        skipped = re.search(r'(?s)\{[^\\\W][-\w]*?\}(?!\\)', line)
        if skipped:
            trace('dropped line', line)
            continue
        # Expand system attributes (eval has precedence).
        reos = [
            re.compile(r'(?s)\{(?P<action>eval):(?P<expr>.*?)\}(?!\\)'),
            re.compile(r'(?s)\{(?P<action>[^\\\W][-\w]*?):(?P<expr>.*?)\}(?!\\)'),
        ]
        skipped = False
        for reo in reos:
            pos = 0
            while True:
                mo = reo.search(line, pos)
                if not mo:
                    break
                expr = mo.group('expr')
                action = mo.group('action')
                expr = expr.replace('{\\', '{')
                expr = expr.replace('}\\', '}')
                s = system(action, expr, attrs=dictionary)
                if dictionary is not None and action in ('counter', 'counter2', 'set', 'set2'):
                    # These actions create and update attributes.
                    attrs.update(dictionary)
                if s is None:
                    # Drop line if the action returns None.
                    skipped = True
                    break
                line = line[:mo.start()] + s + line[mo.end():]
                pos = mo.start() + len(s)
            if skipped:
                break
        if not skipped:
            # Remove backslash from escaped entries.
            line = line.replace('{\\', '{')
            line = line.replace('}\\', '}')
            result.append(line)
    if string_result:
        if result:
            return '\n'.join(result)
        else:
            return None
    else:
        return tuple(result)

# def char_len(s): return len(s)            # no longer needed in AsciiDoc3
# def char_decode(s): return s              # no longer needed in AsciiDoc3
# def char_encode(s) ...                    # no longer needed in AsciiDoc3

class Ad3Codec():
    """New in AsciiDoc3. Class Ad3Codec is not used directly, but provides
       static methods and serves as a base class to Ad3In/Ad3Out.
       Python3's muddle concerning encoding regarding the users input, stdin/out,
       output, and command line options happens here."""

    ad3codec_counter = 0
    fixed_encoding = False      # overriding of encoding-attributes is not allowed

    def __init__(self):
        Ad3Codec.ad3codec_counter += 1
        if Ad3Codec.ad3codec_counter > 2:
            raise EAsciiDoc('Class Ad3Codec(): too many instances')

    def check_encoding(self, encoding_name):
        """Checks if 'encoding_name' is a valid Python codec.
        If not, an exception is thrown and the program exits.
        Replaces 'char_encoding()' in AsciiDoc2."""
        try:
            lookup(encoding_name.lower())
            return
        except LookupError as e:
            raise EAsciiDoc(str(e))

    def check_errors(self, error_name):
        """Checks if 'error_name' is valid. If not, an exception is thrown
           and the program exits."""
        if error_name.rstrip().lower() not in ('strict', 'ignore', 'replace'):
            raise EAsciiDoc('errors has to be "strict" or "ignore" or "replace!"')
        return

    def block_updating(self):
        """blocks immediately any further altering of
        _ie/_oe/_ierr/_oerr, respectively."""
        raise NotImplementedError

    @staticmethod
    def update_encoding(fname, attrs, cmd_attrs):
        """bundles the updating functions for _ie/_oe/_ierr/_oerr."""
        if ad3in and ad3out:
            ad3in.update_input_encoding(fname, attrs, cmd_attrs)
            ad3in.update_input_errors(fname, attrs, cmd_attrs)
            ad3out.update_output_encoding(fname, attrs, cmd_attrs)
            ad3out.update_output_errors(fname, attrs, cmd_attrs)
        else:
            raise NotImplementedError

    @staticmethod
    def add_encoding_for_compatibility():
        """Ensures that encoding is not edited by user"""
        if Ad3Codec.fixed_encoding:
            document.attributes['input-encoding'] = ad3in._ie
            document.attributes['input-errors'] = ad3in._ierr
            document.attributes['output-errors'] = ad3out._oerr
            document.attributes['encoding'] = ad3out._oe
            document.attributes['output-encoding'] = ad3out._oe
            if ad3out._oe.lower() == 'utf-8' or 'utf8' or 'utf_8' \
               or 'u8' or 'utf' or 'utf8':
                document.attributes['encoding'] = 'UTF-8'
                document.attributes['output-encoding'] = 'UTF-8'

class Ad3In(Ad3Codec):
    """Exactly one instance in AsciiDoc3, handles the attributes 'input-encoding'
       and 'input-errors' and their corresponding 'private' variables
       '_ie' and '_ierr'."""

    ad3in_counter = 0

    def __init__(self):
        super().__init__()
        Ad3In.ad3in_counter += 1
        if Ad3In.ad3in_counter != 1:
            raise EAsciiDoc('Class Ad3In: Only one instance allowed')
        self._ie = 'utf-8'
        self._ierr = 'strict'
        self.update_ie_allowed = True
        self.update_ierr_allowed = True

    def update_input_encoding(self, fname, conf_attrs, cmd_attrs):
        """Input-encoding '_ie' is updated and then fixed, find this point in time at approx.
           line 4860 of the source code. (Search for "update_attrs(self.conf_attrs, d)" and
           add three lines downwards). The user can not set _ie directly: she (or he) sets the
           attribute "input-encoding" in command line (ranks first) or conf-files. Just before
           the output file is opened, '_ie' is fixed and inalterable later on. This implies,
           _ie is not affected by ':input-encoding: xyz' somewhere in the input-file, such a
           statement is ignored. "input-encoding" has to be set in the command-line or *.conf,
           '_ie' is initialized as 'utf-8'."""
        if self.update_ie_allowed:
            message.verbose('Entering "update_input-encoding()" ' \
                            'with file: {filename}'.format(filename=fname))
            # 'stdin' here seems quite impossible - if-branch added for 'security reasons'.
            if fname == 'stdin'.lower():
                """Stdin found, no more encoding updates any more! No change is made to _ie."""
                self.block_updating()
                message.verbose('stdin as input-file found, encodings are fixed:' \
                                '{filename}'.format(filename=fname))
            elif fname.rstrip().endswith(".conf"):                # is this neccessary? TODO
                # _ie as set in command-line, overrides conf-files
                if cmd_attrs and ('input-encoding' in cmd_attrs):
                    self._ie = cmd_attrs['input-encoding']
                    self.update_ie_allowed = False
                    message.verbose('input-encoding is fixed as found in ' \
                                    'command-line: {iencoding}'.format(iencoding=self._ie))
                # _ie as set in conf-files by user
                elif conf_attrs and ('input-encoding' in conf_attrs):
                    self._ie = conf_attrs['input-encoding']       # may be 'None' or missing
                    message.verbose('input-encoding updated as in {filename}: ' \
                                    '{iencoding}'.format(filename=fname, iencoding=self._ie))
                else: pass
            else:
                """fname is not == stdin and does not end with '.conf':
                   there is nothing to do."""
        else:
            # self.update_ie_allowed == False
            message.verbose('altering input-encoding is no longer allowed')

        # End of updating/fixing. Validate the current input-encoding:
        self.check_encoding(self._ie)

    def get_input_encoding(self, fname):
        """get the input-encoding: conf/css/py are utf-8, 'stdin' is possibly 'special',
        asciidoc3-input-file is opened with _ie. 'stdin' and 'input-file' block any
        further altering of '_ie'."""
        if fname.rstrip().lower().endswith('.conf'):
            return 'utf-8'
        elif fname.rstrip().lower().endswith('.css'):
            return 'utf-8'
        elif fname.rstrip().lower().endswith('.py'):
            return 'utf-8'
        elif fname.lower() == 'stdin':
            if 'stdin'.lower() == document.attributes['infile']:
                return self._ie
            else:
                try:
                    return getdefaultlocale()[1]
                except:     # except OSError:
                    return 'utf-8'
            self.block_updating()
        # AsciiDoc3 opens 'infile' and/or a file not ending with conf/css/py
        elif fname == document.attributes['infile'] or  \
                not (fname.rstrip().lower().endswith('.conf') or \
                     fname.rstrip().lower().endswith('.css')  or \
                     fname.rstrip().lower().endswith('.py')):
            self.block_updating()
            return self._ie
        else:
            raise EAsciiDoc("""AsciiDoc3 cannot open a file that is not ending
                               with conf/css/py or "stdin" or infile""")

    def update_input_errors(self, fname, conf_attrs, cmd_attrs):
        """Input-errors is updated and fixed undergoing the same procedures as input-encoding.
           _ierr has to be set in *.conf or command-line, _ierr is initialized as 'strict'."""
        if self.update_ierr_allowed:
            message.verbose('Entering "update/fix input-errors" with input-file: ' \
                            '{filename}'.format(filename=fname))
            # 'stdin' here seems quite impossible - this if-branch is added for 'security reasons'.
            if fname == 'stdin'.lower():
                """stdin found, no more encoding updates any more! No change is made to _ierr."""
                self.block_updating()
                message.verbose('stdin found, encodings are fixed: ' \
                                '{filename}'.format(filename=fname))
            elif fname.rstrip().endswith(".conf"):
                if cmd_attrs and 'input-errors' in cmd_attrs:
                    self._ierr = cmd_attrs['input-errors']
                    self.update_ierr_allowed = False
                    message.verbose('input-errors updated as in command-line: ' \
                                    '{iencodingerrors}'.format(iencodingerrors=self._ierr))
                elif conf_attrs and 'input-errors' in conf_attrs:
                    self._ierr = conf_attrs['input-errors']
                    message.verbose('input-errors updated as in {filename}: '\
                                    '{iencodingerrors}'.format(filename=fname, \
                                                               iencodingerrors=self._ierr))
            else:
                """fname is not == stdin and does not end with '.conf': there is nothing to do."""
        else:
            # self.update_ierr_allowed == False
            message.verbose('altering input-errors is no longer allowed')

        # End of updating/fixing. Validate the current errors:
        self.check_errors(self._ierr)

    def get_input_errors(self, fname):
        if fname.lower().endswith('.conf'):
            return 'strict'
        elif fname.lower().endswith('.css'):
            return 'strict'
        elif fname.lower().endswith('.py'):
            return 'strict'
        # AsciiDoc3 opens 'infile' and/or a file not ending with conf/css/py
        elif fname == ('stdin' or document.attributes['infile']) or  \
                    not (fname.rstrip().lower().endswith('.conf') or \
                    fname.rstrip().lower().endswith('.css')  or \
                    fname.rstrip().lower().endswith('.py')):
            self.block_updating()
            return self._ierr
        else:
            raise EAsciiDoc("""AsciiDoc3 cannot open a file that is not
                               ending with conf/css/py or "stdin" or infile!""")

    def block_updating(self):
        """no more updating _ie/_ierr"""
        self.update_ie_allowed = False
        self.update_ierr_allowed = False

    east_asian_widths = {'W' : 2,   # Wide
                         'F' : 2,   # Full-width (wide)
                         'Na': 1,   # Narrow
                         'H' : 1,   # Half-width (narrow)
                         'N' : 1,   # Neutral (not East Asian, treated as narrow)
                         'A' : 1}   # Ambiguous (s/b wide in East Asian context,
                                    # narrow otherwise, but that doesn't work)
    """Mapping of result codes from 'unicodedata.east_asian_width()' to character
    column widths."""

    def column_width(self, s):
        """Computes the 'widths' of utf-8-words, especially east-asian."""

        width = 0
        for c in s:
            width += self.east_asian_widths[east_asian_width(c)]
        return width


class Ad3Out(Ad3Codec):
    """Exactly one instance in AsciiDoc3, handles the attributes 'output-encoding'
       and 'output-errors' and their corresponding 'private' variables
       '_oe' and '_oerr'."""

    ad3out_counter = 0

    def __init__(self):
        super().__init__()
        Ad3Out.ad3out_counter += 1
        if Ad3Out.ad3out_counter != 1:
            raise EAsciiDoc('class Ad3Out: Only one instance allowed')
        self._oe = 'utf-8'                        # this is the default
        self._oerr = 'strict'                     # this is the default
        self.update_oe_allowed = True
        self.update_oerr_allowed = True

    def update_output_encoding(self, fname, conf_attrs, cmd_attrs):
        """Output-encoding '_oe' is updated and then fixed, find this point in time at
           approx. line 4860 of the source code. (Search for "update_attrs(self.conf_attrs, d)"
           and add three lines downwards). The user can not set _oe directly: she (or he) sets
           the attribute "output-encoding" in command line (ranks first) or conf-files. Just
           before the output file is opened, '_oe' is fixed and inalterable later on.
           This implies, _oe is not affected by ':output-encoding: xyz' somewhere in the
           input-file, such a statement is ignored. "output-encoding" has to be set in the
           command-line or *.conf, '_oe' is initialized as 'utf-8'."""

        if self.update_oe_allowed:
            message.verbose('Entering "update/fix output-encoding" with input-file: ' \
                            '{filename}'.format(filename=fname))
            # 'stdin' here seems quite impossible - if-branch added for 'security reasons'.
            if fname == 'stdin'.lower():
                """Stdin found, no more encoding updates any more! No change is made to _oe."""
                self.block_updating()
                message.verbose('stdin found, encodings are fixed: ' \
                                '{filename}'.format(filename=fname))
            elif fname.rstrip().endswith(".conf"):
                # as set in command-line, overrides conf-files
                if cmd_attrs and 'output-encoding' in cmd_attrs:
                    self._oe = cmd_attrs['output-encoding']
                    self.update_oe_allowed = False
                    message.verbose('output-encoding is fixed as found in command-line: ' \
                                    '{oencoding}'.format(oencoding=self._oe))
                # as set in conf-files from user
                elif conf_attrs and ('output-encoding' in conf_attrs):
                    self._oe = conf_attrs['output-encoding']       # may be None or missing
                    message.verbose('output-encoding updated as in {filename}: ' \
                                    '{oencoding}'.format(filename=fname, oencoding=self._oe))
                else: pass
            else:
                """fname is not == stdin and does not end with '.conf':
                   there is nothing to do."""
        else:
            # self.update_oe_allowed == False
            message.verbose('altering output-encoding is no longer allowed')

        # End of updating/fixing. Validate the current output-encoding:
        self.check_encoding(self._oe)

    def get_output_encoding(self, fname):
        if fname:
            ad3in.block_updating()
            self.block_updating()
            return self._oe
        else:
            raise EAsciiDoc("AsciiDoc3 tries to open an unproper file")

    def update_output_errors(self, fname, conf_attrs, cmd_attrs):
        """Output-errors (_oerr) is fixed; _oerr has to be set in *.conf or command-line."""
        if self.update_oerr_allowed:
            message.verbose('Entering "update/fix output-errors" with input-file: ' \
                            '{filename}'.format(filename=fname))
            # 'stdin' here seems quite impossible - if-branch added for 'security reasons'.
            if fname == 'stdin'.lower():
                """Stdin found, no more encoding updates any more!
                   No change is made to _oerr."""
                self.update_oerr_allowed = False
                message.verbose('stdin found, encodings are fixed: ' \
                                '{filename}'.format(filename=fname))
            elif fname.rstrip().endswith(".conf"):
                if cmd_attrs and ('output-errors' in cmd_attrs):
                    self._oerr = cmd_attrs['output-errors']
                    self.update_oerr_allowed = False
                    message.verbose('output-errors updated as in command-line: ' \
                                    '{oencoding}'.format(oencoding=self._oerr))
                elif conf_attrs and ('output-errors' in conf_attrs):
                    self._oerr = conf_attrs['output-errors']
                    message.verbose('output-errors updated as in {filename}: ' \
                                    '{oencoding}'.format(filename=fname, oencoding=self._oerr))
                else: pass
            else: pass

        # End of updating/fixing. Validate the current output-errors:
        self.check_errors(self._oerr)

    def get_output_errors(self, fname):
        if fname:
            ad3in.block_updating()
            self.block_updating()
            return self._oerr

    def block_updating(self):
        """no more updating _oe/_oerr"""
        self.update_oe_allowed = False
        self.update_oerr_allowed = False

def time_str(t):
    """Convert seconds since the Epoch to formatted local time string."""
    t = time.localtime(t)
    s = time.strftime('%H:%M:%S', t)
    if time.daylight and t.tm_isdst == 1:
        result = s + ' ' + time.tzname[1]
    else:
        result = s + ' ' + time.tzname[0]
    # Attempt to convert the localtime to the output encoding.
    # but only if OS != Windows, see
    # https://asciidoc3.org/blog/minor-bug-already-fixed-asciidoc3-303.html
    if not sys.platform.lower().startswith('win'):
        try:
            result = bytes(result, 'utf8')
            result = result.decode(getdefaultlocale()[1])
        except Exception:
            pass # ... hoping that it will go anywhere
    return result

def date_str(t):
    """Convert seconds since the Epoch to formatted local date string."""
    t = time.localtime(t)
    return time.strftime('%Y-%m-%d', t)


class Lex:
    """Lexical analysis routines. Static methods and attributes only."""
    prev_element = None
    prev_cursor = None
    def __init__(self):
        raise AssertionError('no class instances allowed')

    @staticmethod
    def nxt():
        """Returns class of next element on the input (None if EOF).  The
        reader is assumed to be at the first line following a previous element,
        end of file or line one.  Exits with the reader pointing to the first
        line of the next element or EOF (leading blank lines are skipped)."""
        reader.skip_blank_lines()
        if reader.eof():
            return None
        # Optimization: If we've already checked for an element at this
        # position return the element.
        if Lex.prev_element and Lex.prev_cursor == reader.cursor:
            return Lex.prev_element
        if AttributeEntry.isnext():
            result = AttributeEntry
        elif AttributeList.isnext():
            result = AttributeList
        elif BlockTitle.isnext() and not tables_OLD.isnext():
            result = BlockTitle
        elif Title.isnext():
            if AttributeList.style() == 'float':
                result = FloatingTitle
            else:
                result = Title
        elif macros.isnext():
            result = macros.current
        elif lists.isnext():
            result = lists.current
        elif blocks.isnext():
            result = blocks.current
        elif tables_OLD.isnext():
            result = tables_OLD.current
        elif tables.isnext():
            result = tables.current
        else:
            if not paragraphs.isnext():
                raise EAsciiDoc('paragraph expected')
            result = paragraphs.current
        # Optimization: Cache answer.
        Lex.prev_cursor = reader.cursor
        Lex.prev_element = result
        return result

    @staticmethod
    def canonical_subs(options):
        """Translate composite subs values."""
        if len(options) == 1:
            if options[0] == 'none':
                options = ()
            elif options[0] == 'normal':
                options = config.subsnormal
            elif options[0] == 'verbatim':
                options = config.subsverbatim
        return options

    @staticmethod
    def subs_1(s, options):
        """Perform substitution specified in 'options' (in 'options' order)."""
        if not s:
            return s
        if document.attributes.get('plaintext') is not None:
            options = ('specialcharacters',)
        result = s
        options = Lex.canonical_subs(options)
        for o in options:
            if o == 'specialcharacters':
                result = config.subs_specialchars(result)
            elif o == 'attributes':
                result = subs_attrs(result)
            elif o == 'quotes':
                result = subs_quotes(result)
            elif o == 'specialwords':
                result = config.subs_specialwords(result)
            elif o in ('replacements', 'replacements2', 'replacements3'):
                result = config.subs_replacements(result, o)
            elif o == 'macros':
                result = macros.subs(result)
            elif o == 'callouts':
                result = macros.subs(result, callouts=True)
            else:
                raise EAsciiDoc('illegal substitution option: %s' % o)
            trace(o, s, result)
            if not result:
                break
        return result

    @staticmethod
    def subs(lines, options):
        """Perform inline processing specified by 'options' (in 'options'
        order) on sequence of 'lines'."""
        if not lines or not options:
            return lines
        options = Lex.canonical_subs(options)
        # Join lines so quoting can span multiple lines.
        para = '\n'.join(lines)
        if 'macros' in options:
            para = macros.extract_passthroughs(para)
        for o in options:
            if o == 'attributes':
                # If we don't substitute attributes line-by-line then a single
                # undefined attribute will drop the entire paragraph.
                lines = subs_attrs(para.split('\n'))
                para = '\n'.join(lines)
            else:
                para = Lex.subs_1(para, (o,))
        if 'macros' in options:
            para = macros.restore_passthroughs(para)
        return para.splitlines()

    @staticmethod
    def set_margin(lines, margin=0):
        """Utility routine that sets the left margin to 'margin' space in a
        block of non-blank lines."""
        # Calculate width of block margin.
        lines = list(lines)
        width = len(lines[0])
        for s in lines:
            i = re.search(r'\S', s).start()
            if i < width:
                width = i
        # Strip margin width from all lines.
        for i in range(len(lines)):
            lines[i] = ' '*margin + lines[i][width:]
        return lines

#---------------------------------------------------------------------------
# Document element classes parse AsciiDoc3 reader input and write DocBook
# writer output.
#---------------------------------------------------------------------------

class Document():

    # doctype property.
    def getdoctype(self):
        return self.attributes.get('doctype')
    def setdoctype(self, doctype):
        self.attributes['doctype'] = doctype
    doctype = property(getdoctype, setdoctype)

    # backend property.
    def getbackend(self):
        return self.attributes.get('backend')
    def setbackend(self, backend):
        if backend:
            backend = self.attributes.get('backend-alias-' + backend, backend)
        self.attributes['backend'] = backend
    backend = property(getbackend, setbackend)

    def __init__(self):
        self.infile = None        # Source file name.
        self.outfile = None       # Output file name.
        self.attributes = InsensitiveDict()
        self.level = 0            # 0 => front matter. 1,2,3 => sect1,2,3.
        self.has_errors = False   # Set true if processing errors were flagged.
        self.has_warnings = False # Set true if warnings were flagged.
        self.safe = False         # Default safe mode.

    def update_attributes(self, attrs=None):
        """
        Set implicit attributes and attributes in 'attrs'.
        """
        t = time.time()
        self.attributes['localtime'] = time_str(t)
        self.attributes['localdate'] = date_str(t)
        self.attributes['asciidoc3-version'] = VERSION
        self.attributes['asciidoc3-file'] = APP_FILE
        self.attributes['asciidoc3-dir'] = APP_DIR
        if localapp():
            self.attributes['asciidoc3-confdir'] = APP_DIR
        else:
            self.attributes['asciidoc3-confdir'] = CONF_DIR
        self.attributes['user-dir'] = USER_DIR
        if config.verbose:
            self.attributes['verbose'] = ''
        # Update with configuration file attributes.
        if attrs:
            self.attributes.update(attrs)
        # Update with command-line attributes.
        self.attributes.update(config.cmd_attrs)
        # Extract miscellaneous configuration section entries from attributes.
        if attrs:
            config.load_miscellaneous(attrs)
        config.load_miscellaneous(config.cmd_attrs)
        self.attributes['newline'] = config.newline
        # File name related attributes can't be overridden.
        if self.infile is not None:
            if self.infile and os.path.exists(self.infile):
                t = os.path.getmtime(self.infile)
            elif self.infile == '<stdin>':
                t = time.time()
            else:
                t = None
            if t:
                self.attributes['doctime'] = time_str(t)
                self.attributes['docdate'] = date_str(t)
            if self.infile != '<stdin>':
                self.attributes['infile'] = self.infile
                self.attributes['indir'] = os.path.dirname(self.infile)
                self.attributes['docfile'] = self.infile
                self.attributes['docdir'] = os.path.dirname(self.infile)
                self.attributes['docname'] = os.path.splitext(
                    os.path.basename(self.infile))[0]
        if self.outfile:
            if self.outfile != '<stdout>':
                self.attributes['outfile'] = self.outfile
                self.attributes['outdir'] = os.path.dirname(self.outfile)
                if self.infile == '<stdin>':
                    self.attributes['docname'] = os.path.splitext(
                        os.path.basename(self.outfile))[0]
                ext = os.path.splitext(self.outfile)[1][1:]
            elif config.outfilesuffix:
                ext = config.outfilesuffix[1:]
            else:
                ext = ''
            if ext:
                self.attributes['filetype'] = ext
                self.attributes['filetype-'+ext] = ''

    def load_lang(self):
        """
        Load language configuration file.
        """
        lang = self.attributes.get('lang')
        if lang is None:
            filename = 'lang-en.conf'   # Default language file.
        else:
            filename = 'lang-' + lang + '.conf'
        if config.load_from_dirs(filename):
            self.attributes['lang'] = lang  # Reinstate new lang attribute.
        else:
            if lang is None:
                # The default language file must exist.
                message.error('missing conf file: %s' % filename, halt=True)
            else:
                message.warning('missing language conf file: %s' % filename)

    def set_deprecated_attribute(self, old, new):
        """
        Ensures the 'old' name of an attribute that was renamed to 'new' is
        still honored.
        """
        if self.attributes.get(new) is None:
            if self.attributes.get(old) is not None:
                self.attributes[new] = self.attributes[old]
        else:
            self.attributes[old] = self.attributes[new]

    def consume_attributes_and_comments(self, comments_only=False, noblanks=False):
        """
        Returns True if one or more attributes or comments were consumed.
        If 'noblanks' is True then consummation halts if a blank line is
        encountered.
        """
        result = False
        finished = False
        while not finished:
            finished = True
            if noblanks and not reader.read_next():
                return result
            if blocks.isnext() and 'skip' in blocks.current.options:
                result = True
                finished = False
                blocks.current.translate()
            if noblanks and not reader.read_next():
                return result
            if macros.isnext() and macros.current.name == 'comment':
                result = True
                finished = False
                macros.current.translate()
            if not comments_only:
                if AttributeEntry.isnext():
                    result = True
                    finished = False
                    AttributeEntry.translate()
                if AttributeList.isnext():
                    result = True
                    finished = False
                    AttributeList.translate()
        return result

    def parse_header(self, doctype, backend):
        """
        Parses header, sets corresponding document attributes and finalizes
        document doctype and backend properties.
        Returns False if the document does not have a header.
        'doctype' and 'backend' are the doctype and backend option values
        passed on the command-line, None if no command-line option was not
        specified.
        """
        assert not self.level
        # Skip comments and attribute entries that precede the header.
        self.consume_attributes_and_comments()
        if doctype is not None:
            # Command-line overrides header.
            self.doctype = doctype
        elif self.doctype is None:
            # Was not set on command-line or in document header.
            self.doctype = DEFAULT_DOCTYPE
        # Process document header.
        has_header = (Title.isnext() and not Title.level
                      and AttributeList.style() != 'float')
        if self.doctype == 'manpage' and not has_header:
            message.error('manpage document title is mandatory', halt=True)
        if has_header:
            Header.parse()
        # Command-line entries override header derived entries.
        self.attributes.update(config.cmd_attrs)
        # DEPRECATED: revision renamed to revnumber.
        self.set_deprecated_attribute('revision', 'revnumber')
        # DEPRECATED: date renamed to revdate.
        self.set_deprecated_attribute('date', 'revdate')
        if doctype is not None:
            # Command-line overrides header.
            self.doctype = doctype
        if backend is not None:
            # Command-line overrides header.
            self.backend = backend
        elif self.backend is None:
            # Was not set on command-line or in document header.
            self.backend = DEFAULT_BACKEND
        else:
            # Has been set in document header.
            self.backend = self.backend # Translate alias in header.
        assert self.doctype in ('article', 'manpage', 'book'), 'illegal document type'
        return has_header

    def translate(self, has_header):
        if self.doctype == 'manpage':
            # Translate mandatory NAME section.
            if Lex.nxt() is not Title:
                message.error('name section expected')
            else:
                Title.translate()
                if Title.level != 1:
                    message.error('name section title must be at level 1')
                if not isinstance(Lex.nxt(), Paragraph):
                    message.error('malformed name section body')
                lines = reader.read_until(r'^$')
                s = ' '.join(lines)
                mo = re.match(r'^(?P<manname>.*?)\s+-\s+(?P<manpurpose>.*)$', s)
                if not mo:
                    message.error('malformed name section body')
                self.attributes['manname'] = mo.group('manname').strip()
                self.attributes['manpurpose'] = mo.group('manpurpose').strip()
                names = [s.strip() for s in self.attributes['manname'].split(',')]
                if len(names) > 9:
                    message.warning('too many manpage names')
                for i, name in enumerate(names):
                    self.attributes['manname%d' % (i+1)] = name
        if has_header:
            # Do postponed substitutions (backend confs have been loaded).
            self.attributes['doctitle'] = Title.dosubs(self.attributes['doctitle'])
            if config.header_footer:
                hdr = config.subs_section('header', {})
                writer.write(hdr, trace='header')
            if 'title' in self.attributes:
                del self.attributes['title']
            self.consume_attributes_and_comments()
            if self.doctype in ('article', 'book'):
                # Translate 'preamble' (untitled elements between header
                # and first section title).
                if Lex.nxt() is not Title:
                    stag, etag = config.section2tags('preamble')
                    writer.write(stag, trace='preamble open')
                    Section.translate_body()
                    writer.write(etag, trace='preamble close')
            elif self.doctype == 'manpage' and 'name' in config.sections:
                writer.write(config.subs_section('name', {}), trace='name')
        else:
            self.process_author_names()
            if config.header_footer:
                hdr = config.subs_section('header', {})
                writer.write(hdr, trace='header')
            if Lex.nxt() is not Title:
                Section.translate_body()
        # Process remaining sections.
        while not reader.eof():
            if Lex.nxt() is not Title:
                raise EAsciiDoc('section title expected')
            Section.translate()
        Section.setlevel(0) # Write remaining unwritten section close tags.
        # Substitute document parameters and write document footer.
        if config.header_footer:
            ftr = config.subs_section('footer', {})
            writer.write(ftr, trace='footer')

    def parse_author(self, s):
        """ Return False if the author is malformed."""
        attrs = self.attributes # Alias for readability.
        s = s.strip()
        mo = re.match(r'^(?P<name1>[^<>\s]+)'
                      r'(\s+(?P<name2>[^<>\s]+))?'
                      r'(\s+(?P<name3>[^<>\s]+))?'
                      r'(\s+<(?P<email>\S+)>)?$', s)
        if not mo:
            # Names that don't match the formal specification.
            if s:
                attrs['firstname'] = s
            return
        firstname = mo.group('name1')
        if mo.group('name3'):
            middlename = mo.group('name2')
            lastname = mo.group('name3')
        else:
            middlename = None
            lastname = mo.group('name2')
        firstname = firstname.replace('_', ' ')
        if middlename:
            middlename = middlename.replace('_', ' ')
        if lastname:
            lastname = lastname.replace('_', ' ')
        email = mo.group('email')
        if firstname:
            attrs['firstname'] = firstname
        if middlename:
            attrs['middlename'] = middlename
        if lastname:
            attrs['lastname'] = lastname
        if email:
            attrs['email'] = email
        return

    def process_author_names(self):
        """ Calculate any missing author related attributes."""
        attrs = self.attributes # Alias for readability.
        firstname = attrs.get('firstname', '')
        middlename = attrs.get('middlename', '')
        lastname = attrs.get('lastname', '')
        author = attrs.get('author')
        initials = attrs.get('authorinitials')
        if author and not (firstname or middlename or lastname):
            self.parse_author(author)
            attrs['author'] = author.replace('_', ' ')
            self.process_author_names()
            return
        if not author:
            author = '%s %s %s' % (firstname, middlename, lastname)
            author = author.strip()
            author = re.sub(r'\s+', ' ', author)
        if not initials:
            initials = (firstname[:1] + middlename[:1] + lastname[:1])
            initials = initials.upper()
        names = [firstname, middlename, lastname, author, initials]
        for i, v in enumerate(names):
            v = config.subs_specialchars(v)
            v = subs_attrs(v)
            names[i] = v
        firstname, middlename, lastname, author, initials = names
        if firstname:
            attrs['firstname'] = firstname
        if middlename:
            attrs['middlename'] = middlename
        if lastname:
            attrs['lastname'] = lastname
        if author:
            attrs['author'] = author
        if initials:
            attrs['authorinitials'] = initials
        if author:
            attrs['authored'] = ''


class Header:
    """Static methods and attributes only."""

    REV_LINE_RE = r'^(\D*(?P<revnumber>.*?),)?(?P<revdate>.*?)(:\s*(?P<revremark>.*))?$'
    RCS_ID_RE = r'^\$Id: \S+ (?P<revnumber>\S+) (?P<revdate>\S+) \S+ (?P<author>\S+) (\S+ )?\$$'

    def __init__(self):
        raise AssertionError('no class instances allowed')

    @staticmethod
    def parse():
        assert Lex.nxt() is Title and not Title.level
        attrs = document.attributes # Alias for readability.
        # Postpone title subs until backend conf files have been loaded.
        Title.translate(skipsubs=True)
        attrs['doctitle'] = Title.attributes['title']
        document.consume_attributes_and_comments(noblanks=True)
        s = reader.read_next()
        mo = None
        if s:
            # Process first header line after the title that is not a comment
            # or an attribute entry.
            s = reader.read()
            mo = re.match(Header.RCS_ID_RE, s)
            if not mo:
                document.parse_author(s)
                document.consume_attributes_and_comments(noblanks=True)
                if reader.read_next():
                    # Process second header line after the title that is not a
                    # comment or an attribute entry.
                    s = reader.read()
                    s = subs_attrs(s)
                    if s:
                        mo = re.match(Header.RCS_ID_RE, s)
                        if not mo:
                            mo = re.match(Header.REV_LINE_RE, s)
            document.consume_attributes_and_comments(noblanks=True)
        s = attrs.get('revnumber')
        if s:
            mo = re.match(Header.RCS_ID_RE, s)
        if mo:
            revnumber = mo.group('revnumber')
            if revnumber:
                attrs['revnumber'] = revnumber.strip()
            author = mo.groupdict().get('author')
            if author and 'firstname' not in attrs:
                document.parse_author(author)
            revremark = mo.groupdict().get('revremark')
            if revremark is not None:
                revremark = [revremark]
                # Revision remarks can continue on following lines.
                while reader.read_next():
                    if document.consume_attributes_and_comments(noblanks=True):
                        break
                    revremark.append(reader.read())
                revremark = Lex.subs(revremark, ['normal'])
                revremark = '\n'.join(revremark).strip()
                attrs['revremark'] = revremark
            revdate = mo.group('revdate')
            if revdate:
                attrs['revdate'] = revdate.strip()
            elif revnumber or revremark:
                # Set revision date to ensure valid DocBook revision.
                attrs['revdate'] = attrs['docdate']
        document.process_author_names()
        if document.doctype == 'manpage':
            # manpage title formatted like mantitle(manvolnum).
            mo = re.match(r'^(?P<mantitle>.*)\((?P<manvolnum>.*)\)$',
                          attrs['doctitle'])
            if not mo:
                message.error('malformed manpage title')
            else:
                mantitle = mo.group('mantitle').strip()
                mantitle = subs_attrs(mantitle)
                if mantitle is None:
                    message.error('undefined attribute in manpage title')
                # mantitle is lowered only if in ALL CAPS
                if mantitle == mantitle.upper():
                    mantitle = mantitle.lower()
                attrs['mantitle'] = mantitle
                attrs['manvolnum'] = mo.group('manvolnum').strip()

class AttributeEntry:
    """Static methods and attributes only."""
    pattern = None
    subs = None
    name = None
    name2 = None
    value = None
    attributes = {}     # Accumulates all the parsed attribute entries.

    def __init__(self):
        raise AssertionError('no class instances allowed')

    @staticmethod
    def isnext():
        result = False  # Assume not next.
        if not AttributeEntry.pattern:
            pat = document.attributes.get('attributeentry-pattern')
            if not pat:
                message.error("[attributes] missing 'attributeentry-pattern' entry")
            AttributeEntry.pattern = pat
        line = reader.read_next()
        if line:
            # Attribute entry formatted like :<name>[.<name2>]:[ <value>]
            mo = re.match(AttributeEntry.pattern, line)
            if mo:
                AttributeEntry.name = mo.group('attrname')
                AttributeEntry.name2 = mo.group('attrname2')
                AttributeEntry.value = mo.group('attrvalue') or ''
                AttributeEntry.value = AttributeEntry.value.strip()
                result = True
        return result

    @staticmethod
    def translate():
        assert Lex.nxt() is AttributeEntry
        attr = AttributeEntry    # Alias for brevity.
        reader.read()            # Discard attribute entry from reader.
        while attr.value.endswith(' +'):
            if not reader.read_next():
                break
            attr.value = attr.value[:-1] + reader.read().strip()
        if attr.name2 is not None:
            # Configuration file attribute.
            if attr.name2 != '':
                # Section entry attribute.
                section = {}
                # Some sections can have name! syntax.
                if attr.name in ('attributes', 'miscellaneous') and attr.name2[-1] == '!':
                    section[attr.name] = [attr.name2]
                else:
                    section[attr.name] = ['%s=%s' % (attr.name2, attr.value)]
                config.load_sections(section)
                config.load_miscellaneous(config.conf_attrs)
            else:
                # Markup template section attribute.
                config.sections[attr.name] = [attr.value]
        else:
            # Normal attribute.
            if attr.name[-1] == '!':
                # Names like name! undefine the attribute.
                attr.name = attr.name[:-1]
                attr.value = None
            # Strip white space and illegal name chars.
            attr.name = re.sub(r'[^\w\-_]', '', attr.name).lower()
            # Don't override most command-line attributes.
            if attr.name in config.cmd_attrs \
                    and attr.name not in ('trace', 'numbered'):
                return
            # Update document attributes with attribute value.
            if attr.value is not None:
                mo = re.match(r'^pass:(?P<attrs>.*)\[(?P<value>.*)\]$', attr.value)
                if mo:
                    # Inline passthrough syntax.
                    attr.subs = mo.group('attrs')
                    attr.value = mo.group('value')  # Passthrough.
                else:
                    # Default substitution.
                    # DEPRECATED: attributeentry-subs
                    attr.subs = document.attributes.get('attributeentry-subs',
                                                        'specialcharacters,attributes')
                attr.subs = parse_options(attr.subs, SUBS_OPTIONS,
                                          'illegal substitution option')
                attr.value = Lex.subs((attr.value,), attr.subs)
                attr.value = writer.newline.join(attr.value)
                document.attributes[attr.name] = attr.value
            elif attr.name in document.attributes:
                del document.attributes[attr.name]
            attr.attributes[attr.name] = attr.value
        Ad3Codec.add_encoding_for_compatibility()


class AttributeList:
    """Static methods and attributes only."""
    pattern = None
    match = None
    attrs = {}

    def __init__(self):
        raise AssertionError('no class instances allowed')

    @staticmethod
    def initialize():
        if 'attributelist-pattern' not in document.attributes:
            message.error("[attributes] missing 'attributelist-pattern' entry")
        AttributeList.pattern = document.attributes['attributelist-pattern']

    @staticmethod
    def isnext():
        result = False  # Assume not next.
        line = reader.read_next()
        if line:
            mo = re.match(AttributeList.pattern, line)
            if mo:
                AttributeList.match = mo
                result = True
        return result

    @staticmethod
    def translate():
        assert Lex.nxt() is AttributeList
        reader.read()   # Discard attribute list from reader.
        attrs = {}
        d = AttributeList.match.groupdict()
        for k, v in list(d.items()):
            if v is not None:
                if k == 'attrlist':
                    v = subs_attrs(v)
                    if v:
                        parse_attributes(v, attrs)
                else:
                    AttributeList.attrs[k] = v
        AttributeList.subs(attrs)
        AttributeList.attrs.update(attrs)
        Ad3Codec.add_encoding_for_compatibility()

    @staticmethod
    def subs(attrs):
        '''Substitute single quoted attribute values normally.'''
        reo = re.compile(r"^'.*'$")
        for k, v in list(attrs.items()):
            if reo.match(str(v)):
                attrs[k] = Lex.subs_1(v[1:-1], config.subsnormal)

    @staticmethod
    def style():
        return AttributeList.attrs.get('style') or AttributeList.attrs.get('1')

    @staticmethod
    def consume(d={}):
        """Add attribute list to the dictionary 'd' and reset the list."""
        if AttributeList.attrs:
            d.update(AttributeList.attrs)
            AttributeList.attrs = {}
            # Generate option attributes.
            if 'options' in d:
                options = parse_options(d['options'], (), 'illegal option name')
                for option in options:
                    d[option+'-option'] = ''


class BlockTitle:
    """Static methods and attributes only."""
    title = None
    pattern = None

    def __init__(self):
        raise AssertionError('no class instances allowed')

    @staticmethod
    def isnext():
        result = False  # Assume not next.
        line = reader.read_next()
        if line:
            mo = re.match(BlockTitle.pattern, line)
            if mo:
                BlockTitle.title = mo.group('title')
                result = True
        return result

    @staticmethod
    def translate():
        assert Lex.nxt() is BlockTitle
        reader.read()   # Discard title from reader.
        # Perform title substitutions.
        if not Title.subs:
            Title.subs = config.subsnormal
        s = Lex.subs((BlockTitle.title,), Title.subs)
        s = writer.newline.join(s)
        if not s:
            message.warning('blank block title')
        BlockTitle.title = s

    @staticmethod
    def consume(d={}):
        """If there is a title add it to dictionary 'd' then reset title."""
        if BlockTitle.title:
            d['title'] = BlockTitle.title
            BlockTitle.title = None


class Title:
    """Processes Header and Section titles. Static methods and attributes
    only."""
    # Class variables
    underlines = ('==', '--', '~~', '^^', '++') # Levels 0,1,2,3,4.
    subs = ()
    pattern = None
    level = 0
    attributes = {}
    sectname = None
    section_numbers = [0]*len(underlines)
    dump_dict = {}
    linecount = None    # Number of lines in title (1 or 2).

    def __init__(self):
        raise AssertionError('no class instances allowed')

    @staticmethod
    def translate(skipsubs=False):
        """Parse the Title.attributes and Title.level from the reader. The
        real work has already been done by parse()."""
        assert Lex.nxt() in (Title, FloatingTitle)
        # Discard title from reader.
        for __ in itertools_repeat(None, Title.linecount):
            reader.read()
        Title.setsectname()
        if not skipsubs:
            Title.attributes['title'] = Title.dosubs(Title.attributes['title'])

    @staticmethod
    def dosubs(title):
        """
        Perform title substitutions.
        """
        if not Title.subs:
            Title.subs = config.subsnormal
        title = Lex.subs((title,), Title.subs)
        title = writer.newline.join(title)
        if not title:
            message.warning('blank section title')
        return title

    @staticmethod
    def isnext():
        lines = reader.read_ahead(2)
        return Title.parse(lines)

    @staticmethod
    def parse(lines):
        """Parse title at start of lines tuple."""
        if not lines:
            return False
        if not lines[0]:
            return False # Title can't be blank.
        # Check for single-line titles.
        result = False
        for level in range(len(Title.underlines)):
            k = 'sect%s' % level
            if k in Title.dump_dict:
                mo = re.match(Title.dump_dict[k], lines[0])
                if mo:
                    Title.attributes = mo.groupdict()
                    Title.level = level
                    Title.linecount = 1
                    result = True
                    break
        if not result:
            # Check for double-line titles.
            if not Title.pattern:
                return False  # Single-line titles only.
            if len(lines) < 2:
                return False
            title, ul = lines[:2]
            title_len = ad3in.column_width(title)
            ul_len = len(ul)
            if ul_len < 2:
                return False
            # Fast elimination check.
            if ul[:2] not in Title.underlines:
                return False
            # Length of underline must be within +-3 of title.
            if not ((ul_len-3 < title_len < ul_len+3)
                    # Next test for backward compatibility.
                    or (ul_len-3 < len(title) < ul_len+3)):
                return False
            # Check for valid repetition of underline character pairs.
            s = ul[:2]*((ul_len+1)//2)
            if ul != s[:ul_len]:
                return False
            # Don't be fooled by back-to-back delimited blocks, require at
            # least one alphanumeric character in title.
            if not re.search(r'\w', title):
                return False
            mo = re.match(Title.pattern, title)
            if mo:
                Title.attributes = mo.groupdict()
                Title.level = list(Title.underlines).index(ul[:2])
                Title.linecount = 2
                result = True
        # Check for expected pattern match groups.
        if result:
            if 'title' not in Title.attributes:
                message.warning('[titles] entry has no <title> group')
                Title.attributes['title'] = lines[0]
            for k, v in list(Title.attributes.items()):
                if v is None:
                    del Title.attributes[k]
        try:
            Title.level += int(document.attributes.get('leveloffset', '0'))
        except:
            pass
        Title.attributes['level'] = str(Title.level)
        return result

    @staticmethod
    def load(entries):
        """Load and validate [titles] section entries dictionary."""
        if 'underlines' in entries:
            errmsg = 'malformed [titles] underlines entry'
            try:
                underlines = parse_list(entries['underlines'])
            except Exception:
                raise EAsciiDoc(errmsg)
            if len(underlines) != len(Title.underlines):
                raise EAsciiDoc(errmsg)
            for s in underlines:
                if len(s) != 2:
                    raise EAsciiDoc(errmsg)
            Title.underlines = tuple(underlines)
            Title.dump_dict['underlines'] = entries['underlines']
        if 'subs' in entries:
            Title.subs = parse_options(entries['subs'], SUBS_OPTIONS,
                                       'illegal [titles] subs entry')
            Title.dump_dict['subs'] = entries['subs']
        if 'sectiontitle' in entries:
            pat = entries['sectiontitle']
            if not pat or not is_re(pat):
                raise EAsciiDoc('malformed [titles] sectiontitle entry')
            Title.pattern = pat
            Title.dump_dict['sectiontitle'] = pat
        if 'blocktitle' in entries:
            pat = entries['blocktitle']
            if not pat or not is_re(pat):
                raise EAsciiDoc('malformed [titles] blocktitle entry')
            BlockTitle.pattern = pat
            Title.dump_dict['blocktitle'] = pat
        # Load single-line title patterns.
        for k in ('sect0', 'sect1', 'sect2', 'sect3', 'sect4'):
            if k in entries:
                pat = entries[k]
                if not pat or not is_re(pat):
                    raise EAsciiDoc('malformed [titles] %s entry' % k)
                Title.dump_dict[k] = pat
        # TODO: Check we have either a Title.pattern or at least one
        # single-line title pattern -- can this be done here or do we need
        # check routine like the other block checkers?

    @staticmethod
    def dump():
        dump_section('titles', Title.dump_dict)

    @staticmethod
    def setsectname():
        """
        Set Title section name:
        If the first positional or 'template' attribute is set use it,
        next search for section title in [specialsections],
        if not found use default 'sect<level>' name.
        """
        sectname = AttributeList.attrs.get('1')
        if sectname and sectname != 'float':
            Title.sectname = sectname
        elif 'template' in AttributeList.attrs:
            Title.sectname = AttributeList.attrs['template']
        else:
            for pat, sect in list(config.specialsections.items()):
                mo = re.match(pat, Title.attributes['title'])
                if mo:
                    title = mo.groupdict().get('title')
                    if title is not None:
                        Title.attributes['title'] = title.strip()
                    else:
                        Title.attributes['title'] = mo.group().strip()
                    Title.sectname = sect
                    break
            else:
                Title.sectname = 'sect%d' % Title.level

    @staticmethod
    def getnumber(level):
        """Return next section number at section 'level'
           formatted like 1.2.3.4."""
        number = ''
        for l in range(len(Title.section_numbers)):
            n = Title.section_numbers[l]
            if not l:
                continue
            elif l < level:
                number = '%s%d.' % (number, n)
            elif l == level:
                number = '%s%d.' % (number, n + 1)
                Title.section_numbers[l] = n + 1
            elif l > level:
                # Reset unprocessed section levels.
                Title.section_numbers[l] = 0
        return number


class FloatingTitle(Title):
    """Floated titles are translated differently."""

    @staticmethod
    def isnext():
        return Title.isnext() and AttributeList.style() == 'float'

    @staticmethod
    def translate():
        assert Lex.nxt() is FloatingTitle
        Title.translate()
        Section.set_id()
        AttributeList.consume(Title.attributes)
        template = 'floatingtitle'
        if template in config.sections:
            stag, __ = config.section2tags(template, Title.attributes)
            writer.write(stag, trace='floating title')
        else:
            message.warning('missing template section: [%s]' % template)


class Section:
    """Static methods and attributes only."""
    endtags = []  # Stack of currently open section (level,endtag) tuples.
    ids = []      # List of already used ids.

    def __init__(self):
        raise AssertionError('no class instances allowed')

    @staticmethod
    def savetag(level, etag):
        """Save section end."""
        Section.endtags.append((level, etag))

    @staticmethod
    def setlevel(level):
        """Set document level and write open section close tags up to level."""
        while Section.endtags and Section.endtags[-1][0] >= level:
            writer.write(Section.endtags.pop()[1], trace='section close')
        document.level = level

    @staticmethod
    def gen_id(title):
        """
        The normalized value of the id attribute is an NCName according to
        the 'Namespaces in XML' Recommendation:
        NCName          ::=     NCNameStartChar NCNameChar*
        NCNameChar      ::=     NameChar - ':'
        NCNameStartChar ::=     Letter | '_'
        NameChar        ::=     Letter | Digit | '.' | '-' | '_' | ':'
        """
        # Replace non-alpha numeric characters in title with underscores and
        # convert to lower case.
        base_id = re.sub(r'\W+', '_', title).strip('_').lower()
        if 'ascii-ids' in document.attributes:
            # Replace non-ASCII characters with ASCII equivalents.
            base_id = normalize('NFKD', base_id).encode('ascii', 'ignore')
            base_id = str(base_id, encoding='ascii')
        # Prefix the ID name with idprefix attribute or underscore if not
        # defined. Prefix ensures the ID does not clash with existing IDs.
        idprefix = document.attributes.get('idprefix', '_')
        base_id = idprefix + base_id
        i = 1
        while True:
            if i == 1:
                id = base_id
            else:
                id = '%s_%d' % (base_id, i)
            if id not in Section.ids:
                Section.ids.append(id)
                return id
            else:
                id = base_id
            i += 1

    @staticmethod
    def set_id():
        if document.attributes.get('sectids') is not None \
           and 'id' not in AttributeList.attrs:
            # Generate ids for sections.
            AttributeList.attrs['id'] = Section.gen_id(Title.attributes['title'])

    @staticmethod
    def translate():
        assert Lex.nxt() is Title
        prev_sectname = Title.sectname
        Title.translate()
        if not Title.level and document.doctype != 'book':
            message.error('only book doctypes can contain level 0 sections')
        if Title.level > document.level \
           and 'basebackend-docbook' in document.attributes \
           and prev_sectname in ('colophon', 'abstract', \
                                 'dedication', 'glossary', 'bibliography'):
            message.error('%s section cannot contain sub-sections' % prev_sectname)
        if Title.level > document.level+1:
            # Sub-sections of multi-part book level zero Preface and Appendices
            # are meant to be out of sequence.
            if document.doctype == 'book' \
               and not document.level \
               and Title.level == 2 \
               and prev_sectname in ('preface', 'appendix'):
                pass
            else:
                message.warning('section title out of sequence: '
                                'expected level %d, got level %d'
                                % (document.level+1, Title.level))
        Section.set_id()
        Section.setlevel(Title.level)
        if 'numbered' in document.attributes:
            Title.attributes['sectnum'] = Title.getnumber(document.level)
        else:
            Title.attributes['sectnum'] = ''
        AttributeList.consume(Title.attributes)
        stag, etag = config.section2tags(Title.sectname, Title.attributes)
        Section.savetag(Title.level, etag)
        writer.write(stag, trace='section open: level %d: %s' %
                     (Title.level, Title.attributes['title']))
        Section.translate_body()

    @staticmethod
    def translate_body(terminator=Title):
        isempty = True
        nxt = Lex.nxt()
        while nxt and nxt is not terminator:
            if isinstance(terminator, DelimitedBlock) and nxt is Title:
                message.error('section title not permitted in delimited block')
            nxt.translate()
            nxt = Lex.nxt()
            isempty = False
        # The section is not empty if contains a subsection.
        if nxt and isempty and Title.level > document.level:
            isempty = False
        # Report empty sections if invalid markup will result.
        if isempty:
            if document.backend == 'docbook' and Title.sectname != 'index':
                message.error('empty section is not valid')


class AbstractBlock:

    blocknames = [] # Global stack of names for push_blockname() and pop_blockname().

    def __init__(self):
        # Configuration parameter names common to all blocks.
        self.CONF_ENTRIES = ('delimiter', 'options', 'subs', 'presubs', 'postsubs',
                             'posattrs', 'style', '.*-style', 'template', 'filter')
        self.start = None     # File reader cursor at start delimiter.
        self.defname = None   # Configuration file block definition section name.
        # Configuration parameters.
        self.delimiter = None # Regular expression matching block delimiter.
        self.delimiter_reo = None # Compiled delimiter.
        self.template = None  # template section entry.
        self.options = ()     # options entry list.
        self.presubs = None   # presubs/subs entry list.
        self.postsubs = ()    # postsubs entry list.
        self.filter = None    # filter entry.
        self.posattrs = ()    # posattrs entry list.
        self.style = None     # Default style.
        self.styles = collections.OrderedDict() # Each entry is a styles dictionary.
        # Before a block is processed it's attributes (from it's
        # attributes list) are merged with the block configuration parameters
        # (by self.merge_attributes()) resulting in the template substitution
        # dictionary (self.attributes) and the block's processing parameters
        # (self.parameters).
        self.attributes = {}
        # The names of block parameters.
        self.PARAM_NAMES = ('template', 'options', 'presubs', 'postsubs', 'filter')
        self.parameters = None
        # Leading delimiter match object.
        self.mo = None

    def short_name(self):
        """ Return the text following the first dash in the section name."""
        i = self.defname.find('-')
        if i == -1:
            return self.defname
        else:
            return self.defname[i+1:]

    def error(self, msg, cursor=None, halt=False):
        message.error('[%s] %s' % (self.defname, msg), cursor, halt)

    def is_conf_entry(self, param):
        """Return True if param matches an allowed configuration file entry
        name."""
        for s in self.CONF_ENTRIES:
            if re.match('^'+s+'$', param):
                return True
        return False

    def load(self, defname, entries):
        """Update block definition from section 'entries' dictionary."""
        self.defname = defname
        self.update_parameters(entries, self, all=True)

    def update_parameters(self, src, dst=None, all=False):
        """
        Parse processing parameters from src dictionary to dst object.
        dst defaults to self.parameters.
        If all is True then copy src entries that aren't parameter names.
        """
        dst = dst or self.parameters
        msg = '[%s] malformed entry %%s: %%s' % self.defname

        def copy(obj, k, v):
            if isinstance(obj, dict):
                obj[k] = v
            else:
                setattr(obj, k, v)
        for k, v in list(src.items()):
            if not re.match(r'\d+', k) and not is_name(k):
                raise EAsciiDoc(msg % (k, v))
            if k == 'template':
                if not is_name(v):
                    raise EAsciiDoc(msg % (k, v))
                copy(dst, k, v)
            elif k == 'filter':
                copy(dst, k, v)
            elif k == 'options':
                if isinstance(v, str):
                    v = parse_options(v, (), msg % (k, v))
                    # Merge with existing options.
                    v = tuple(set(dst.options).union(set(v)))
                copy(dst, k, v)
            elif k in ('subs', 'presubs', 'postsubs'):
                # Subs is an alias for presubs.
                if k == 'subs':
                    k = 'presubs'
                if isinstance(v, str):
                    v = parse_options(v, SUBS_OPTIONS, msg % (k, v))
                copy(dst, k, v)
            elif k == 'delimiter':
                if v and is_re(v):
                    copy(dst, k, v)
                else:
                    raise EAsciiDoc(msg % (k, v))
            elif k == 'style':
                if is_name(v):
                    copy(dst, k, v)
                else:
                    raise EAsciiDoc(msg % (k, v))
            elif k == 'posattrs':
                v = parse_options(v, (), msg % (k, v))
                copy(dst, k, v)
            else:
                mo = re.match(r'^(?P<style>.*)-style$', k)
                if mo:
                    if not v:
                        raise EAsciiDoc(msg % (k, v))
                    style = mo.group('style')
                    if not is_name(style):
                        raise EAsciiDoc(msg % (k, v))
                    d = {}
                    if not parse_named_attributes(v, d):
                        raise EAsciiDoc(msg % (k, v))
                    if 'subs' in d:
                        # Subs is an alias for presubs.
                        d['presubs'] = d['subs']
                        del d['subs']
                    self.styles[style] = d
                elif all or k in self.PARAM_NAMES:
                    copy(dst, k, v) # Derived class specific entries.

    def get_param(self, name, params=None):
        """
        Return named processing parameter from params dictionary.
        If the parameter is not in params look in self.parameters.
        """
        if params and name in params:
            return params[name]
        elif name in self.parameters:
            return self.parameters[name]
        else:
            return None

    def get_subs(self, params=None):
        """
        Return (presubs,postsubs) tuple.
        """
        presubs = self.get_param('presubs', params)
        postsubs = self.get_param('postsubs', params)
        return (presubs, postsubs)

    def dump(self):
        """Write block definition to stdout."""
        write = lambda s: sys.stdout.write('%s%s' % (s, writer.newline))
        write('['+self.defname+']')
        if self.is_conf_entry('delimiter'):
            write('delimiter='+self.delimiter)
        if self.template:
            write('template='+self.template)
        if self.options:
            write('options='+','.join(self.options))
        if self.presubs:
            if self.postsubs:
                write('presubs='+','.join(self.presubs))
            else:
                write('subs='+','.join(self.presubs))
        if self.postsubs:
            write('postsubs='+','.join(self.postsubs))
        if self.filter:
            write('filter='+self.filter)
        if self.posattrs:
            write('posattrs='+','.join(self.posattrs))
        if self.style:
            write('style='+self.style)
        if self.styles:
            for style, d in list(self.styles.items()):
                s = ''
                for k, v in list(d.items()):
                    s += '%s=%r,' % (k, v)
                write('%s-style=%s' % (style, s[:-1]))

    def validate(self):
        """Validate block after the complete configuration has been loaded."""
        if self.is_conf_entry('delimiter') and not self.delimiter:
            raise EAsciiDoc('[%s] missing delimiter' % self.defname)
        if self.style:
            if not is_name(self.style):
                raise EAsciiDoc('illegal style name: %s' % self.style)
            if self.style not in self.styles:
                if not isinstance(self, List):   # Lists don't have templates.
                    message.warning('[%s] \'%s\' style not in %s' % (
                        self.defname, self.style, list(self.styles.keys())))
        # Check all styles for missing templates.
        all_styles_have_template = True
        for __, v in list(self.styles.items()):
            t = v.get('template')
            if t and t not in config.sections:
                # Defer check if template name contains attributes.
                if not re.search(r'{.+}', t):
                    message.warning('missing template section: [%s]' % t)
            if not t:
                all_styles_have_template = False
        # Check we have a valid template entry or alternatively that all the
        # styles have templates.
        if self.is_conf_entry('template') and 'skip' not in self.options:
            if self.template:
                if self.template not in config.sections:
                    # Defer check if template name contains attributes.
                    if not re.search(r'{.+}', self.template):
                        message.warning('missing template section: [%s]'
                                        % self.template)
            elif not all_styles_have_template:
                if not isinstance(self, List): # Lists don't have templates.
                    message.warning('missing styles templates: [%s]' % self.defname)

    def isnext(self):
        """Check if this block is next in document reader."""
        result = False
        reader.skip_blank_lines()
        if reader.read_next():
            if not self.delimiter_reo:
                # Cache compiled delimiter optimization.
                self.delimiter_reo = re.compile(self.delimiter)
            mo = self.delimiter_reo.match(reader.read_next())
            if mo:
                self.mo = mo
                result = True
        return result

    def translate(self):
        """Translate block from document reader."""
        if not self.presubs:
            self.presubs = config.subsnormal
        if reader.cursor:
            self.start = reader.cursor[:]

    def push_blockname(self, blockname=None):
        '''
        On block entry set the 'blockname' attribute.
        Only applies to delimited blocks, lists and tables.
        '''
        if blockname is None:
            blockname = self.attributes.get('style', self.short_name()).lower()
        trace('push blockname', blockname)
        self.blocknames.append(blockname)
        document.attributes['blockname'] = blockname

    def pop_blockname(self):
        '''
        On block exits restore previous (parent) 'blockname' attribute or
        undefine it if we're no longer inside a block.
        '''
        assert self.blocknames
        blockname = self.blocknames.pop()
        trace('pop blockname', blockname)
        if not self.blocknames:
            document.attributes['blockname'] = None
        else:
            document.attributes['blockname'] = self.blocknames[-1]

    def merge_attributes(self, attrs, params=[]):
        """
        Use the current block's attribute list (attrs dictionary) to build a
        dictionary of block processing parameters (self.parameters) and tag
        substitution attributes (self.attributes).

        1. Copy the default parameters (self.*) to self.parameters.
        self.parameters are used internally to render the current block.
        Optional params array of additional parameters.

        2. Copy attrs to self.attributes. self.attributes are used for template
        and tag substitution in the current block.

        3. If a style attribute was specified update self.parameters with the
        corresponding style parameters; if there are any style parameters
        remaining add them to self.attributes (existing attribute list entries
        take precedence).

        4. Set named positional attributes in self.attributes if self.posattrs
        was specified.

        5. Finally self.parameters is updated with any corresponding parameters
        specified in attrs.
        """

        def check_array_parameter(param):
            # Check the parameter is a sequence type.
            if not is_array(self.parameters[param]):
                message.error('malformed %s parameter: %s' %
                              (param, self.parameters[param]))
                # Revert to default value.
                self.parameters[param] = getattr(self, param)
        params = list(self.PARAM_NAMES) + params
        self.attributes = {}
        if self.style:
            # If a default style is defined make it available in the template.
            self.attributes['style'] = self.style
        self.attributes.update(attrs)
        # Calculate dynamic block parameters.
        # Start with configuration file defaults.
        self.parameters = AttrDict()
        for name in params:
            self.parameters[name] = getattr(self, name)
        # Load the selected style attributes.
        posattrs = self.posattrs
        if posattrs and posattrs[0] == 'style':
            # Positional attribute style has highest precedence.
            style = self.attributes.get('1')
        else:
            style = None
        if not style:
            # Use explicit style attribute, fall back to default style.
            style = self.attributes.get('style', self.style)
        if style:
            if not is_name(style):
                message.error('illegal style name: %s' % style)
                style = self.style
            # Lists have implicit styles and do their own style checks.
            elif style not in self.styles and not isinstance(self, List):
                message.warning('missing style: [%s]: %s' % (self.defname, style))
                style = self.style
            if style in self.styles:
                self.attributes['style'] = style
                for k, v in list(self.styles[style].items()):
                    if k == 'posattrs':
                        posattrs = v
                    elif k in params:
                        self.parameters[k] = v
                    elif k not in self.attributes:
                        # Style attributes don't take precedence over explicit.
                        self.attributes[k] = v
        # Set named positional attributes.
        for i, v in enumerate(posattrs):
            if str(i+1) in self.attributes:
                self.attributes[v] = self.attributes[str(i+1)]
        # Override config and style attributes with attribute list attributes.
        self.update_parameters(attrs)
        check_array_parameter('options')
        check_array_parameter('presubs')
        check_array_parameter('postsubs')


class AbstractBlocks:
    """List of block definitions."""
    PREFIX = ''         # Conf file section name prefix set in derived classes.
    BLOCK_TYPE = None   # Block type set in derived classes.

    def __init__(self):
        self.current = None
        self.blocks = []        # List of Block objects.
        self.default = None     # Default Block.
        self.delimiters = None  # Combined delimiters regular expression.

    def load(self, sections):
        """Load block definition from 'sections' dictionary."""
        for k in list(sections.keys()):
            if re.match(r'^'+ self.PREFIX + r'.+$', k):
                d = {}
                parse_entries(sections.get(k, ()), d)
                for b in self.blocks:
                    if b.defname == k:
                        break
                else:
                    b = self.BLOCK_TYPE()
                    self.blocks.append(b)
                try:
                    b.load(k, d)
                except EAsciiDoc as e:
                    raise EAsciiDoc('[%s] %s' % (k, str(e)))

    def dump(self):
        for b in self.blocks:
            b.dump()

    def isnext(self):
        for b in self.blocks:
            if b.isnext():
                self.current = b
                return True
        return False

    def validate(self):
        """Validate the block definitions."""
        # Validate delimiters and build combined lists delimiter pattern.
        delimiters = []
        for b in self.blocks:
            assert b.__class__ is self.BLOCK_TYPE
            b.validate()
            if b.delimiter:
                delimiters.append(b.delimiter)
        self.delimiters = re_join(delimiters)


class Paragraph(AbstractBlock):

    def __init__(self):
        AbstractBlock.__init__(self)
        self.text = None          # Text in first line of paragraph.

    def load(self, name, entries):
        AbstractBlock.load(self, name, entries)

    def dump(self):
        AbstractBlock.dump(self)
        write = lambda s: sys.stdout.write('%s%s' % (s, writer.newline))
        write('')

    def isnext(self):
        result = AbstractBlock.isnext(self)
        if result:
            self.text = self.mo.groupdict().get('text')
        return result

    def translate(self):
        AbstractBlock.translate(self)
        attrs = self.mo.groupdict().copy()
        if 'text' in attrs:
            del attrs['text']
        BlockTitle.consume(attrs)
        AttributeList.consume(attrs)
        self.merge_attributes(attrs)
        reader.read()   # Discard (already parsed item first line).
        body = reader.read_until(paragraphs.terminators)
        if 'skip' in self.parameters.options:
            return
        body = [self.text] + list(body)
        presubs = self.parameters.presubs
        postsubs = self.parameters.postsubs
        if document.attributes.get('plaintext') is None:
            body = Lex.set_margin(body) # Move body to left margin.
        body = Lex.subs(body, presubs)
        template = self.parameters.template
        template = subs_attrs(template, attrs)
        stag = config.section2tags(template, self.attributes, skipend=True)[0]
        if self.parameters.filter:
            body = filter_lines(self.parameters.filter, body, self.attributes)
        body = Lex.subs(body, postsubs)
        etag = config.section2tags(template, self.attributes, skipstart=True)[1]
        # Write start tag, content, end tag.
        writer.write(dovetail_tags(stag, body, etag), trace='paragraph')


class Paragraphs(AbstractBlocks):
    """List of paragraph definitions."""
    BLOCK_TYPE = Paragraph
    PREFIX = 'paradef-'

    def __init__(self):
        AbstractBlocks.__init__(self)
        self.terminators = None    # List of compiled re's.

    def initialize(self):
        self.terminators = [
            re.compile(r'^\+$|^$'),
            re.compile(AttributeList.pattern),
            re.compile(blocks.delimiters),
            re.compile(tables.delimiters),
            re.compile(tables_OLD.delimiters),
            ]

    def load(self, sections):
        AbstractBlocks.load(self, sections)

    def validate(self):
        AbstractBlocks.validate(self)
        # Check we have a default paragraph definition, put it last in list.
        for b in self.blocks:
            if b.defname == 'paradef-default':
                self.blocks.append(b)
                self.default = b
                self.blocks.remove(b)
                break
        else:
            raise EAsciiDoc('missing section: [paradef-default]')


class List(AbstractBlock):
    NUMBER_STYLES = ('arabic', 'loweralpha', 'upperalpha', 'lowerroman',
                     'upperroman')

    def __init__(self):
        AbstractBlock.__init__(self)
        self.CONF_ENTRIES += ('type', 'tags')
        self.PARAM_NAMES += ('tags',)
        # listdef conf file parameters.
        self.type = None
        self.tags = None      # Name of listtags-<tags> conf section.
        # Calculated parameters.
        self.tag = None       # Current tags AttrDict.
        self.label = None     # List item label (labeled lists).
        self.text = None      # Text in first line of list item.
        self.index = None     # Matched delimiter 'index' group (numbered lists).
        self.type = None      # List type ('numbered','bulleted','labeled').
        self.ordinal = None   # Current list item ordinal number (1..)
        self.number_style = None # Current numbered list style ('arabic'..)

    def load(self, name, entries):
        AbstractBlock.load(self, name, entries)

    def dump(self):
        AbstractBlock.dump(self)
        write = lambda s: sys.stdout.write('%s%s' % (s, writer.newline))
        write('type='+self.type)
        write('tags='+self.tags)
        write('')

    def validate(self):
        AbstractBlock.validate(self)
        tags = [self.tags]
        tags += [s['tags'] for s in list(self.styles.values()) if 'tags' in s]
        for t in tags:
            if t not in lists.tags:
                self.error('missing section: [listtags-%s]' % t, halt=True)

    def isnext(self):
        result = AbstractBlock.isnext(self)
        if result:
            self.label = self.mo.groupdict().get('label')
            self.text = self.mo.groupdict().get('text')
            self.index = self.mo.groupdict().get('index')
        return result

    def translate_entry(self):
        assert self.type == 'labeled'
        entrytag = subs_tag(self.tag.entry, self.attributes)
        labeltag = subs_tag(self.tag.label, self.attributes)
        writer.write(entrytag[0], trace='list entry open')
        writer.write(labeltag[0], trace='list label open')
        # Write labels.
        while Lex.nxt() is self:
            reader.read()   # Discard (already parsed item first line).
            writer.write_tag(self.tag.term, [self.label],
                             self.presubs, self.attributes, trace='list term')
            if self.text:
                break
        writer.write(labeltag[1], trace='list label close')
        # Write item text.
        self.translate_item()
        writer.write(entrytag[1], trace='list entry close')

    def translate_item(self):
        if self.type == 'callout':
            self.attributes['coids'] = calloutmap.calloutids(self.ordinal)
        itemtag = subs_tag(self.tag.item, self.attributes)
        writer.write(itemtag[0], trace='list item open')
        # Write ItemText.
        text = reader.read_until(lists.terminators)
        if self.text:
            text = [self.text] + list(text)
        if text:
            writer.write_tag(self.tag.text, text, self.presubs, self.attributes, trace='list text')
        # Process explicit and implicit list item continuations.
        while True:
            continuation = reader.read_next() == '+'
            if continuation: reader.read()  # Discard continuation line.
            while Lex.nxt() in (BlockTitle, AttributeList):
                # Consume continued element title and attributes.
                Lex.nxt().translate()
            if not continuation and BlockTitle.title:
                # Titled elements terminate the list.
                break
            nxt = Lex.nxt()
            if nxt in lists.open:
                break
            elif isinstance(nxt, List):
                nxt.translate()
            elif isinstance(nxt, Paragraph) and 'listelement' in nxt.options:
                nxt.translate()
            elif continuation:
                # This is where continued elements are processed.
                if nxt is Title:
                    message.error('section title not allowed in list item', halt=True)
                nxt.translate()
            else:
                break
        writer.write(itemtag[1], trace='list item close')

    @staticmethod
    def calc_style(index):
        """Return the numbered list style ('arabic'...) of the list item index.
        Return None if unrecognized style."""
        if re.match(r'^\d+[\.>]$', index):
            style = 'arabic'
        elif re.match(r'^[ivx]+\)$', index):
            style = 'lowerroman'
        elif re.match(r'^[IVX]+\)$', index):
            style = 'upperroman'
        elif re.match(r'^[a-z]\.$', index):
            style = 'loweralpha'
        elif re.match(r'^[A-Z]\.$', index):
            style = 'upperalpha'
        else:
            assert False
        return style

    @staticmethod
    def calc_index(index, style):
        """Return the ordinal number of (1...) of the list item index
        for the given list style."""
        def roman_to_int(roman):
            roman = roman.lower()
            digits = {'i':1, 'v':5, 'x':10}
            result = 0
            for i in range(len(roman)):
                digit = digits[roman[i]]
                # If next digit is larger this digit is negative.
                if i+1 < len(roman) and digits[roman[i+1]] > digit:
                    result -= digit
                else:
                    result += digit
            return result
        index = index[:-1]
        if style == 'arabic':
            ordinal = int(index)
        elif style == 'lowerroman':
            ordinal = roman_to_int(index)
        elif style == 'upperroman':
            ordinal = roman_to_int(index)
        elif style == 'loweralpha':
            ordinal = ord(index) - ord('a') + 1
        elif style == 'upperalpha':
            ordinal = ord(index) - ord('A') + 1
        else:
            assert False
        return ordinal

    def check_index(self):
        """Check calculated self.ordinal (1,2,...) against the item number
        in the document (self.index) and check the number style is the same as
        the first item (self.number_style)."""
        assert self.type in ('numbered', 'callout')
        if self.index:
            style = self.calc_style(self.index)
            if style != self.number_style:
                message.warning('list item style: expected %s got %s' %
                                (self.number_style, style), offset=1)
            ordinal = self.calc_index(self.index, style)
            if ordinal != self.ordinal:
                message.warning('list item index: expected %s got %s' %
                                (self.ordinal, ordinal), offset=1)

    def check_tags(self):
        """ Check that all necessary tags are present. """
        tags = set(Lists.TAGS)
        if self.type != 'labeled':
            tags = tags.difference(['entry', 'label', 'term'])
        missing = tags.difference(list(self.tag.keys()))
        if missing:
            self.error('missing tag(s): %s' % ','.join(missing), halt=True)

    def translate(self):
        AbstractBlock.translate(self)
        if self.short_name() in ('bibliography', 'glossary', 'qanda'):
            message.deprecated('old %s list syntax' % self.short_name())
        lists.open.append(self)
        attrs = self.mo.groupdict().copy()
        for k in ('label', 'text', 'index'):
            if k in attrs:
                del attrs[k]
        if self.index:
            # Set the numbering style from first list item.
            attrs['style'] = self.calc_style(self.index)
        BlockTitle.consume(attrs)
        AttributeList.consume(attrs)
        self.merge_attributes(attrs, ['tags'])
        self.push_blockname()
        if self.type in ('numbered', 'callout'):
            self.number_style = self.attributes.get('style')
            if self.number_style not in self.NUMBER_STYLES:
                message.error('illegal numbered list style: %s' % self.number_style)
                # Fall back to default style.
                self.attributes['style'] = self.number_style = self.style
        self.tag = lists.tags[self.parameters.tags]
        self.check_tags()
        if 'width' in self.attributes:
            # Set horizontal list 'labelwidth' and 'itemwidth' attributes.
            v = str(self.attributes['width'])
            mo = re.match(r'^(\d{1,2})%?$', v)
            if mo:
                labelwidth = int(mo.group(1))
                self.attributes['labelwidth'] = str(labelwidth)
                self.attributes['itemwidth'] = str(100-labelwidth)
            else:
                self.error('illegal attribute value: width="%s"' % v)
        stag, etag = subs_tag(self.tag.list, self.attributes)
        if stag:
            writer.write(stag, trace='list open')
        self.ordinal = 0
        # Process list till list syntax changes or there is a new title.
        while Lex.nxt() is self and not BlockTitle.title:
            self.ordinal += 1
            document.attributes['listindex'] = str(self.ordinal)
            if self.type in ('numbered', 'callout'):
                self.check_index()
            if self.type in ('bulleted', 'numbered', 'callout'):
                reader.read()   # Discard (already parsed item first line).
                self.translate_item()
            elif self.type == 'labeled':
                self.translate_entry()
            else:
                raise AssertionError('illegal [%s] list type' % self.defname)
        if etag:
            writer.write(etag, trace='list close')
        if self.type == 'callout':
            calloutmap.validate(self.ordinal)
            calloutmap.listclose()
        lists.open.pop()
        if lists.open:
            document.attributes['listindex'] = str(lists.open[-1].ordinal)
        self.pop_blockname()


class Lists(AbstractBlocks):
    """List of List objects."""
    BLOCK_TYPE = List
    PREFIX = 'listdef-'
    TYPES = ('bulleted', 'numbered', 'labeled', 'callout')
    TAGS = ('list', 'entry', 'item', 'text', 'label', 'term')

    def __init__(self):
        AbstractBlocks.__init__(self)
        self.open = []          # A stack of the current and parent lists.
        self.tags = {}          # List tags dictionary. Each entry is a tags AttrDict.
        self.terminators = None # List of compiled re's.

    def initialize(self):
        self.terminators = [
            re.compile(r'^\+$|^$'),
            re.compile(AttributeList.pattern),
            re.compile(lists.delimiters),
            re.compile(blocks.delimiters),
            re.compile(tables.delimiters),
            re.compile(tables_OLD.delimiters),
            ]

    def load(self, sections):
        AbstractBlocks.load(self, sections)
        self.load_tags(sections)

    def load_tags(self, sections):
        """
        Load listtags-* conf file sections to self.tags.
        """
        for section in list(sections.keys()):
            mo = re.match(r'^listtags-(?P<name>\w+)$', section)
            if mo:
                name = mo.group('name')
                if name in self.tags:
                    d = self.tags[name]
                else:
                    d = AttrDict()
                parse_entries(sections.get(section, ()), d)
                for k in list(d.keys()):
                    if k not in self.TAGS:
                        message.warning('[%s] contains illegal list tag: %s' %
                                        (section, k))
                self.tags[name] = d

    def validate(self):
        AbstractBlocks.validate(self)
        for b in self.blocks:
            # Check list has valid type.
            if b.type not in Lists.TYPES:
                raise EAsciiDoc('[%s] illegal type' % b.defname)
            b.validate()

    def dump(self):
        AbstractBlocks.dump(self)
        for k, v in list(self.tags.items()):
            dump_section('listtags-'+k, v)


class DelimitedBlock(AbstractBlock):

    def __init__(self):
        AbstractBlock.__init__(self)

    def load(self, name, entries):
        AbstractBlock.load(self, name, entries)

    def dump(self):
        AbstractBlock.dump(self)
        write = lambda s: sys.stdout.write('%s%s' % (s, writer.newline))
        write('')

    def isnext(self):
        return AbstractBlock.isnext(self)

    def translate(self):
        AbstractBlock.translate(self)
        reader.read()   # Discard delimiter.
        self.merge_attributes(AttributeList.attrs)
        if 'skip' not in self.parameters.options:
            BlockTitle.consume(self.attributes)
            AttributeList.consume()
        self.push_blockname()
        options = self.parameters.options
        if 'skip' in options:
            reader.read_until(self.delimiter, same_file=True)
        elif safe() and self.defname == 'blockdef-backend':
            message.unsafe('Backend Block')
            reader.read_until(self.delimiter, same_file=True)
        else:
            template = self.parameters.template
            template = subs_attrs(template, self.attributes)
            name = self.short_name()+' block'
            if 'sectionbody' in options:
                # The body is treated like a section body.
                stag, etag = config.section2tags(template, self.attributes)
                writer.write(stag, trace=name+' open')
                Section.translate_body(self)
                writer.write(etag, trace=name+' close')
            else:
                stag = config.section2tags(template, self.attributes, skipend=True)[0]
                body = reader.read_until(self.delimiter, same_file=True)
                presubs = self.parameters.presubs
                postsubs = self.parameters.postsubs
                body = Lex.subs(body, presubs)
                if self.parameters.filter:
                    body = filter_lines(self.parameters.filter, body, self.attributes)
                body = Lex.subs(body, postsubs)
                # Write start tag, content, end tag.
                etag = config.section2tags(template, self.attributes, skipstart=True)[1]
                writer.write(dovetail_tags(stag, body, etag), trace=name)
            trace(self.short_name()+' block close', etag)
        if reader.eof():
            self.error('missing closing delimiter', self.start)
        else:
            delimiter = reader.read()   # Discard delimiter line.
            assert re.match(self.delimiter, delimiter)
        self.pop_blockname()


class DelimitedBlocks(AbstractBlocks):
    """List of delimited blocks."""
    BLOCK_TYPE = DelimitedBlock
    PREFIX = 'blockdef-'

    def __init__(self):
        AbstractBlocks.__init__(self)

    def load(self, sections):
        """Update blocks defined in 'sections' dictionary."""
        AbstractBlocks.load(self, sections)

    def validate(self):
        AbstractBlocks.validate(self)


class Column:
    """Table column."""
    def __init__(self, width=None, align_spec=None, style=None):
        self.width = width or '1'
        self.halign, self.valign = Table.parse_align_spec(align_spec)
        self.style = style      # Style name or None.
        # Calculated attribute values.
        self.abswidth = None    # 1..   (page units).
        self.pcwidth = None     # 1..99 (percentage).


class Cell:
    """Table cell."""
    def __init__(self, data, span_spec=None, align_spec=None, style=None):
        self.data = data
        self.span, self.vspan = Table.parse_span_spec(span_spec)
        self.halign, self.valign = Table.parse_align_spec(align_spec)
        self.style = style
        self.reserved = False

    def __repr__(self):
        return '<Cell: %d.%d %s.%s %s "%s">' % (
            self.span, self.vspan,
            self.halign, self.valign,
            self.style or '',
            self.data)

    def clone_reserve(self):
        """Return a clone of self to reserve vertically spanned cell."""
        result = ccopy(self)
        result.vspan = 1
        result.reserved = True
        return result


class Table(AbstractBlock):
    ALIGN = {'<':'left', '>':'right', '^':'center'}
    VALIGN = {'<':'top', '>':'bottom', '^':'middle'}
    FORMATS = ('psv', 'csv', 'dsv')
    SEPARATORS = dict(
        csv=',',
        dsv=r':|\n',
        # The count and align group matches are not exact.
        psv=r'((?<!\S)((?P<span>[\d.]+)(?P<op>[*+]))?(?P<align>[<\^>.]{,3})?(?P<style>[a-z])?)?\|'
    )

    def __init__(self):
        AbstractBlock.__init__(self)
        self.CONF_ENTRIES += ('format', 'tags', 'separator')
        # tabledef conf file parameters.
        self.format = 'psv'
        self.separator = None
        self.tags = None        # Name of tabletags-<tags> conf section.
        # Calculated parameters.
        self.abswidth = None    # 1..   (page units).
        self.pcwidth = None     # 1..99 (percentage).
        self.rows = []          # Parsed rows, each row is a list of Cells.
        self.columns = []       # List of Columns.

    @staticmethod
    def parse_align_spec(align_spec):
        """
        Parse AsciiDoc3 cell alignment specifier and return 2-tuple with
        horizontal and vertical alignment names. Unspecified alignments
        set to None.
        """
        result = (None, None)
        if align_spec:
            mo = re.match(r'^([<\^>])?(\.([<\^>]))?$', align_spec)
            if mo:
                result = (Table.ALIGN.get(mo.group(1)),
                          Table.VALIGN.get(mo.group(3)))
        return result

    @staticmethod
    def parse_span_spec(span_spec):
        """
        Parse AsciiDoc3 cell span specifier and return 2-tuple with horizontal
        and vertical span counts. Set default values (1,1) if not
        specified.
        """
        result = (None, None)
        if span_spec:
            mo = re.match(r'^(\d+)?(\.(\d+))?$', span_spec)
            if mo:
                result = (mo.group(1) and int(mo.group(1)),
                          mo.group(3) and int(mo.group(3)))
        return (result[0] or 1, result[1] or 1)

    def load(self, name, entries):
        AbstractBlock.load(self, name, entries)

    def dump(self):
        AbstractBlock.dump(self)
        write = lambda s: sys.stdout.write('%s%s' % (s, writer.newline))
        write('format='+self.format)
        write('')

    def validate(self):
        AbstractBlock.validate(self)
        if self.format not in Table.FORMATS:
            self.error('illegal format=%s' % self.format, halt=True)
        self.tags = self.tags or 'default'
        tags = [self.tags]
        tags += [s['tags'] for s in list(self.styles.values()) if 'tags' in s]
        for t in tags:
            if t not in tables.tags:
                self.error('missing section: [tabletags-%s]' % t, halt=True)
        if self.separator:
            # Evaluate escape characters.
            self.separator = literal_eval('"'+self.separator+'"')
        #TODO: Move to class Tables
        # Check global table parameters.
        elif config.pagewidth is None:
            self.error('missing [miscellaneous] entry: pagewidth')
        elif config.pageunits is None:
            self.error('missing [miscellaneous] entry: pageunits')

    def validate_attributes(self):
        """Validate and parse table attributes."""
        # Set defaults.
        format = self.format
        tags = self.tags
        separator = self.separator
        abswidth = float(config.pagewidth)
        pcwidth = 100.0
        for k, v in list(self.attributes.items()):
            if k == 'format':
                if v not in self.FORMATS:
                    self.error('illegal %s=%s' % (k, v))
                else:
                    format = v
            elif k == 'tags':
                if v not in tables.tags:
                    self.error('illegal %s=%s' % (k, v))
                else:
                    tags = v
            elif k == 'separator':
                separator = v
            elif k == 'width':
                if not re.match(r'^\d{1,3}%$', v) or int(v[:-1]) > 100:
                    self.error('illegal %s=%s' % (k, v))
                else:
                    abswidth = float(v[:-1])/100 * config.pagewidth
                    pcwidth = float(v[:-1])
        # Calculate separator if it has not been specified.
        if not separator:
            separator = Table.SEPARATORS[format]
        if format == 'csv':
            if len(separator) > 1:
                self.error('illegal csv separator=%s' % separator)
                separator = ','
        else:
            if not is_re(separator):
                self.error('illegal regular expression: separator=%s' %
                           separator)
        self.parameters.format = format
        self.parameters.tags = tags
        self.parameters.separator = separator
        self.abswidth = abswidth
        self.pcwidth = pcwidth

    def get_tags(self, params):
        tags = self.get_param('tags', params)
        assert tags and tags in tables.tags
        return tables.tags[tags]

    def get_style(self, prefix):
        """
        Return the style dictionary whose name starts with 'prefix'.
        """
        if prefix is None:
            return None
        names = sorted(list(self.styles.keys()))
        for name in names:
            if name.startswith(prefix):
                return self.styles[name]
        else:
            self.error('missing style: %s*' % prefix)
            return None

    def parse_cols(self, cols, halign, valign):
        """
        Build list of column objects from table 'cols', 'halign' and 'valign'
        attributes.
        """
        # TODO: make use of 're.VERBOSE'
        # [<multiplier>*][<align>][<width>][<style>]
        COLS_RE1 = r'^((?P<count>\d+)\*)?(?P<align>[<\^>.]' \
                   r'{,3})?(?P<width>\d+%?)?(?P<style>[a-z]\w*)?$'
        # [<multiplier>*][<width>][<align>][<style>]
        COLS_RE2 = r'^((?P<count>\d+)\*)?(?P<width>\d+%?)?' \
                   r'(?P<align>[<\^>.]{,3})?(?P<style>[a-z]\w*)?$'
        reo1 = re.compile(COLS_RE1)
        reo2 = re.compile(COLS_RE2)
        cols = str(cols)
        if re.match(r'^\d+$', cols):
            for __ in itertools_repeat(None, int(cols)):
                self.columns.append(Column())
        else:
            for col in re.split(r'\s*,\s*', cols):
                mo = reo1.match(col)
                if not mo:
                    mo = reo2.match(col)
                if mo:
                    count = int(mo.groupdict().get('count') or 1)
                    for __ in itertools_repeat(None, count):
                        self.columns.append(
                            Column(mo.group('width'), mo.group('align'),
                                   self.get_style(mo.group('style')))
                        )
                else:
                    self.error('illegal column spec: %s' % col, self.start)
        # Set column (and indirectly cell) default alignments.
        for col in self.columns:
            col.halign = col.halign or halign or document.attributes.get('halign') or 'left'
            col.valign = col.valign or valign or document.attributes.get('valign') or 'top'
        # Validate widths and calculate missing widths.
        n = 0
        percents = 0
        props = 0
        for col in self.columns:
            if col.width:
                if col.width[-1] == '%':
                    percents += int(col.width[:-1])
                else:
                    props += int(col.width)
                n += 1
        if percents > 0 and props > 0:
            self.error('mixed percent and proportional widths: %s'
                       % cols, self.start)
        pcunits = percents > 0
        # Fill in missing widths.
        if n < len(self.columns) and percents < 100:
            if pcunits:
                width = float(100 - percents)/float(len(self.columns) - n)
            else:
                width = 1
            for col in self.columns:
                if not col.width:
                    if pcunits:
                        col.width = str(int(width))+'%'
                        percents += width
                    else:
                        col.width = str(width)
                        props += width
        # Calculate column alignment and absolute and percent width values.
        percents = 0
        for col in self.columns:
            if pcunits:
                col.pcwidth = float(col.width[:-1])
            else:
                col.pcwidth = (float(col.width)/props)*100
            col.abswidth = self.abswidth * (col.pcwidth/100)
            if config.pageunits in ('cm', 'mm', 'in', 'em'):
                col.abswidth = '%.2f' % round(col.abswidth, 2)
            else:
                col.abswidth = '%d' % Decimal(str(col.abswidth)).quantize(Decimal('1'), \
                                                                          rounding=ROUND_HALF_UP)
            percents += col.pcwidth
            col.pcwidth = int(col.pcwidth)
        if Decimal(str(percents)).quantize(Decimal('1'), \
                                           rounding=ROUND_HALF_UP) > 100:
            self.error('total width exceeds 100%%: %s' % cols, self.start)
        elif Decimal(str(percents)).quantize(Decimal('1'), \
                                             rounding=ROUND_HALF_UP) < 100:
            self.error('total width less than 100%%: %s' % cols, self.start)

    def build_colspecs(self):
        """
        Generate column related substitution attributes.
        """
        cols = []
        i = 1
        for col in self.columns:
            colspec = self.get_tags(col.style).colspec
            if colspec:
                self.attributes['halign'] = col.halign
                self.attributes['valign'] = col.valign
                self.attributes['colabswidth'] = col.abswidth
                self.attributes['colpcwidth'] = col.pcwidth
                self.attributes['colnumber'] = str(i)
                s = subs_attrs(colspec, self.attributes)
                if not s:
                    message.warning('colspec dropped: contains undefined attribute')
                else:
                    cols.append(s)
            i += 1
        if cols:
            self.attributes['colspecs'] = writer.newline.join(cols)

    def parse_rows(self, text):
        """
        Parse the table source text into self.rows (a list of rows, each row
        is a list of Cells.
        """
        reserved = {}  # Reserved cells generated by rowspans.
        if self.parameters.format in ('psv', 'dsv'):
            colcount = len(self.columns)
            parsed_cells = self.parse_psv_dsv(text)
            ri = 0  # Current row index 0..
            ci = 0  # Column counter 0..colcount
            row = []
            i = 0
            while True:
                resv = reserved.get(ri) and reserved[ri].get(ci)
                if resv:
                    # We have a cell generated by a previous row span so
                    # process it before continuing with the current parsed
                    # cell.
                    cell = resv
                else:
                    if i >= len(parsed_cells):
                        break   # No more parsed or reserved cells.
                    cell = parsed_cells[i]
                    i += 1
                    if cell.vspan > 1:
                        # Generate ensuing reserved cells spanned vertically by
                        # the current cell.
                        for j in range(1, cell.vspan):
                            if ri+j not in reserved:
                                reserved[ri+j] = {}
                            reserved[ri+j][ci] = cell.clone_reserve()
                ci += cell.span
                if ci <= colcount:
                    row.append(cell)
                if ci >= colcount:
                    self.rows.append(row)
                    ri += 1
                    row = []
                    ci = 0
        elif self.parameters.format == 'csv':
            self.rows = self.parse_csv(text)
        else:
            assert True, 'illegal table format'
        # Check for empty rows containing only reserved (spanned) cells.
        for ri, row in enumerate(self.rows):
            empty = True
            for cell in row:
                if not cell.reserved:
                    empty = False
                    break
            if empty:
                message.warning('table row %d: empty spanned row' % (ri+1))
        # Check that all row spans match.
        for ri, row in enumerate(self.rows):
            row_span = 0
            for cell in row:
                row_span += cell.span
            if not ri:
                header_span = row_span
            if row_span < header_span:
                message.warning('table row %d: does not span all columns' % (ri+1))
            if row_span > header_span:
                message.warning('table row %d: exceeds columns span' % (ri+1))

    def subs_rows(self, rows, rowtype='body'):
        """
        Return a string of output markup from a list of rows, each row
        is a list of raw data text.
        """
        tags = tables.tags[self.parameters.tags]
        if rowtype == 'header':
            rtag = tags.headrow
        elif rowtype == 'footer':
            rtag = tags.footrow
        else:
            rtag = tags.bodyrow
        result = []
        stag, etag = subs_tag(rtag, self.attributes)
        for row in rows:
            result.append(stag)
            result += self.subs_row(row, rowtype)
            result.append(etag)
        return writer.newline.join(result)

    def subs_row(self, row, rowtype):
        """
        Substitute the list of Cells using the data tag.
        Returns a list of marked up table cell elements.
        """
        result = []
        i = 0
        for cell in row:
            if cell.reserved:
                # Skip vertically spanned placeholders.
                i += cell.span
                continue
            if i >= len(self.columns):
                break   # Skip cells outside the header width.
            col = self.columns[i]
            self.attributes['halign'] = cell.halign or col.halign
            self.attributes['valign'] = cell.valign or  col.valign
            self.attributes['colabswidth'] = col.abswidth
            self.attributes['colpcwidth'] = col.pcwidth
            self.attributes['colnumber'] = str(i+1)
            self.attributes['colspan'] = str(cell.span)
            self.attributes['colstart'] = self.attributes['colnumber']
            self.attributes['colend'] = str(i+cell.span)
            self.attributes['rowspan'] = str(cell.vspan)
            self.attributes['morerows'] = str(cell.vspan-1)
            # Fill missing column data with blanks.
            if i > len(self.columns) - 1:
                data = ''
            else:
                data = cell.data
            if rowtype == 'header':
                # Use table style unless overridden by cell style.
                colstyle = cell.style
            else:
                # If the cell style is not defined use the column style.
                colstyle = cell.style or col.style
            tags = self.get_tags(colstyle)
            presubs, postsubs = self.get_subs(colstyle)
            data = [data]
            data = Lex.subs(data, presubs)
            data = filter_lines(self.get_param('filter', colstyle),
                                data, self.attributes)
            data = Lex.subs(data, postsubs)
            if rowtype != 'header':
                ptag = tags.paragraph
                if ptag:
                    stag, etag = subs_tag(ptag, self.attributes)
                    text = '\n'.join(data).strip()
                    data = []
                    for para in re.split(r'\n{2,}', text):
                        data += dovetail_tags([stag], para.split('\n'), [etag])
            if rowtype == 'header':
                dtag = tags.headdata
            elif rowtype == 'footer':
                dtag = tags.footdata
            else:
                dtag = tags.bodydata
            stag, etag = subs_tag(dtag, self.attributes)
            result = result + dovetail_tags([stag], data, [etag])
            i += cell.span
        return result

    def parse_csv(self, text):
        """
        Parse the table source text and return a list of rows, each row
        is a list of Cells.
        """
        rows = []
        rdr = csv_reader(io_StringIO('\r\n'.join(text)),
                         delimiter=self.parameters.separator,
                         skipinitialspace=True)
        try:
            for row in rdr:
                rows.append([Cell(data) for data in row])
        except Exception:
            self.error('csv parse error: %s' % row)
        return rows

    def parse_psv_dsv(self, text):
        """
        Parse list of PSV or DSV table source text lines and return a list of
        Cells.
        """
        def append_cell(data, span_spec, op, align_spec, style):
            op = op or '+'
            if op == '*':   # Cell multiplier.
                span = Table.parse_span_spec(span_spec)[0]
                for __ in itertools_repeat(None, span):
                    cells.append(Cell(data, '1', align_spec, style))
            elif op == '+': # Column spanner.
                cells.append(Cell(data, span_spec, align_spec, style))
            else:
                self.error('illegal table cell operator')
        text = '\n'.join(text)
        separator = '(?ms)'+self.parameters.separator
        format = self.parameters.format
        start = 0
        span = None
        op = None
        align = None
        style = None
        cells = []
        data = ''
        for mo in re.finditer(separator, text):
            data += text[start:mo.start()]
            if data.endswith('\\'):
                data = data[:-1]+mo.group() # Reinstate escaped separators.
            else:
                append_cell(data, span, op, align, style)
                span = mo.groupdict().get('span')
                op = mo.groupdict().get('op')
                align = mo.groupdict().get('align')
                style = mo.groupdict().get('style')
                if style:
                    style = self.get_style(style)
                data = ''
            start = mo.end()
        # Last cell follows final separator.
        data += text[start:]
        append_cell(data, span, op, align, style)
        # We expect a dummy blank item preceding first PSV cell.
        if format == 'psv':
            if cells[0].data.strip() != '':
                self.error('missing leading separator: %s' % separator,
                           self.start)
            else:
                cells.pop(0)
        return cells

    def translate(self):
        AbstractBlock.translate(self)
        reader.read()   # Discard delimiter.
        # Reset instance specific properties.
        self.columns = []
        self.rows = []
        attrs = {}
        BlockTitle.consume(attrs)
        # Mix in document attribute list.
        AttributeList.consume(attrs)
        self.merge_attributes(attrs)
        self.validate_attributes()
        # Add global and calculated configuration parameters.
        self.attributes['pagewidth'] = config.pagewidth
        self.attributes['pageunits'] = config.pageunits
        self.attributes['tableabswidth'] = int(self.abswidth)
        self.attributes['tablepcwidth'] = int(self.pcwidth)
        # Read the entire table.
        text = reader.read_until(self.delimiter)
        if reader.eof():
            self.error('missing closing delimiter', self.start)
        else:
            delimiter = reader.read()   # Discard closing delimiter.
            assert re.match(self.delimiter, delimiter)
        if not text:
            message.warning('[%s] table is empty' % self.defname)
            return
        self.push_blockname('table')
        cols = attrs.get('cols')
        if not cols:
            # Calculate column count from number of items in first line.
            if self.parameters.format == 'csv':
                cols = text[0].count(self.parameters.separator) + 1
            else:
                cols = 0
                for cell in self.parse_psv_dsv(text[:1]):
                    cols += cell.span
        self.parse_cols(cols, attrs.get('halign'), attrs.get('valign'))
        # Set calculated attributes.
        self.attributes['colcount'] = len(self.columns)
        self.build_colspecs()
        self.parse_rows(text)
        # The 'rowcount' attribute is used by the experimental LaTeX backend.
        self.attributes['rowcount'] = str(len(self.rows))
        # Generate headrows, footrows, bodyrows.
        # Headrow, footrow and bodyrow data replaces same named attributes in
        # the table markup template. In order to ensure this data does not get
        # a second attribute substitution (which would interfere with any
        # already substituted inline passthroughs) unique placeholders are used
        # (the tab character does not appear elsewhere since it is expanded on
        # input) which are replaced after template attribute substitution.
        headrows = footrows = bodyrows = None
        for option in self.parameters.options:
            self.attributes[option+'-option'] = ''
        if self.rows and 'header' in self.parameters.options:
            headrows = self.subs_rows(self.rows[0:1], 'header')
            self.attributes['headrows'] = '\x07headrows\x07'
            self.rows = self.rows[1:]
        if self.rows and 'footer' in self.parameters.options:
            footrows = self.subs_rows(self.rows[-1:], 'footer')
            self.attributes['footrows'] = '\x07footrows\x07'
            self.rows = self.rows[:-1]
        if self.rows:
            bodyrows = self.subs_rows(self.rows)
            self.attributes['bodyrows'] = '\x07bodyrows\x07'
        table = subs_attrs(config.sections[self.parameters.template],
                           self.attributes)
        table = writer.newline.join(table)
        # Before we finish replace the table head, foot and body place holders
        # with the real data.
        if headrows:
            table = table.replace('\x07headrows\x07', headrows, 1)
        if footrows:
            table = table.replace('\x07footrows\x07', footrows, 1)
        if bodyrows:
            table = table.replace('\x07bodyrows\x07', bodyrows, 1)
        writer.write(table, trace='table')
        self.pop_blockname()


class Tables(AbstractBlocks):
    """List of tables."""
    BLOCK_TYPE = Table
    PREFIX = 'tabledef-'
    TAGS = ('colspec', 'headrow', 'footrow', 'bodyrow',
            'headdata', 'footdata', 'bodydata', 'paragraph')

    def __init__(self):
        AbstractBlocks.__init__(self)
        # Table tags dictionary. Each entry is a tags dictionary.
        self.tags = {}

    def load(self, sections):
        AbstractBlocks.load(self, sections)
        self.load_tags(sections)
    def load_tags(self, sections):
        """
        Load tabletags-* conf file sections to self.tags.
        """
        for section in list(sections.keys()):
            mo = re.match(r'^tabletags-(?P<name>\w+)$', section)
            if mo:
                name = mo.group('name')
                if name in self.tags:
                    d = self.tags[name]
                else:
                    d = AttrDict()
                parse_entries(sections.get(section, ()), d)
                for k in list(d.keys()):
                    if k not in self.TAGS:
                        message.warning('[%s] contains illegal table tag: %s' %
                                        (section, k))
                self.tags[name] = d

    def validate(self):
        AbstractBlocks.validate(self)
        # Check we have a default table definition,
        for i in range(len(self.blocks)):
            if self.blocks[i].defname == 'tabledef-default':
                default = self.blocks[i]
                break
        else:
            raise EAsciiDoc('missing section: [tabledef-default]')
        # Propagate defaults to unspecified table parameters.
        for b in self.blocks:
            if b is not default:
                if b.format is None:
                    b.format = default.format
                if b.template is None:
                    b.template = default.template
        # Check tags and propagate default tags.
        if 'default' not in self.tags:
            raise EAsciiDoc('missing section: [tabletags-default]')
        default = self.tags['default']
        for tag in ('bodyrow', 'bodydata', 'paragraph'): # Mandatory default tags.
            if tag not in default:
                raise EAsciiDoc('missing [tabletags-default] entry: %s' % tag)
        for t in list(self.tags.values()):
            if t is not default:
                if t.colspec is None:
                    t.colspec = default.colspec
                if t.headrow is None:
                    t.headrow = default.headrow
                if t.footrow is None:
                    t.footrow = default.footrow
                if t.bodyrow is None:
                    t.bodyrow = default.bodyrow
                if t.headdata is None:
                    t.headdata = default.headdata
                if t.footdata is None:
                    t.footdata = default.footdata
                if t.bodydata is None:
                    t.bodydata = default.bodydata
                if t.paragraph is None:
                    t.paragraph = default.paragraph
        # Use body tags if header and footer tags are not specified.
        for t in list(self.tags.values()):
            if not t.headrow:
                t.headrow = t.bodyrow
            if not t.footrow:
                t.footrow = t.bodyrow
            if not t.headdata:
                t.headdata = t.bodydata
            if not t.footdata:
                t.footdata = t.bodydata
        # Check table definitions are valid.
        for b in self.blocks:
            b.validate()

    def dump(self):
        AbstractBlocks.dump(self)
        for k, v in list(self.tags.items()):
            dump_section('tabletags-'+k, v)


class Macros:
    # Default system macro syntax.
    SYS_RE = r'^(?P<name>[\\]?\w(\w|-)*?)::(?P<target>\S*?)' + \
             r'(\[(?P<attrlist>.*?)\])$'

    def __init__(self):
        self.macros = []        # List of Macros.
        self.current = None     # The last matched block macro.
        self.passthroughs = []
        # Initialize default system macro.
        m = Macro()
        m.pattern = self.SYS_RE
        m.prefix = '+'
        m.reo = re.compile(m.pattern)
        self.macros.append(m)

    def load(self, entries):
        for entry in entries:
            m = Macro()
            m.load(entry)
            if m.name is None:
                # Delete undefined macro.
                for i, m2 in enumerate(self.macros):
                    if m2.pattern == m.pattern:
                        del self.macros[i]
                        break
                else:
                    message.warning('unable to delete missing macro: %s' % m.pattern)
            else:
                # Check for duplicates.
                for m2 in self.macros:
                    if m2.pattern == m.pattern:
                        message.verbose('macro redefinition: %s%s' % (m.prefix, m.name))
                        break
                else:
                    self.macros.append(m)

    def dump(self):
        write = lambda s: sys.stdout.write('%s%s' % (s, writer.newline))
        write('[macros]')
        # Dump all macros except the first (built-in system) macro.
        for m in self.macros[1:]:
            # Escape = in pattern.
            macro = '%s=%s%s' % (m.pattern.replace('=', r'\='), m.prefix, m.name)
            if m.subslist is not None:
                macro += '[' + ','.join(m.subslist) + ']'
            write(macro)
        write('')

    def validate(self):
        # Check all named sections exist.
        if config.verbose:
            for m in self.macros:
                if m.name and m.prefix != '+':
                    m.section_name()

    def subs(self, text, prefix='', callouts=False):
        # If callouts is True then only callout macros are processed, if False
        # then all non-callout macros are processed.
        result = text
        for m in self.macros:
            if m.prefix == prefix:
                if callouts ^ (m.name != 'callout'):
                    result = m.subs(result)
        return result

    def isnext(self):
        """Return matching macro if block macro is next on reader."""
        reader.skip_blank_lines()
        line = reader.read_next()
        if line:
            for m in self.macros:
                if m.prefix == '#':
                    if m.reo.match(line):
                        self.current = m
                        return m
        return False

    @lru_cache(65536)
    def match(self, prefix, name, text):
        """Return re match object matching 'text' with macro type 'prefix',
        macro name 'name'."""
        for m in self.macros:
            if m.prefix == prefix:
                mo = m.reo.match(text)
                if mo:
                    if m.name == name:
                        return mo
                    if re.match(name, mo.group('name')):
                        return mo
        return None

    def extract_passthroughs(self, text, prefix=''):
        """ Extract the passthrough text and replace with temporary
        placeholders."""
        self.passthroughs = []
        for m in self.macros:
            if m.has_passthrough() and m.prefix == prefix:
                text = m.subs_passthroughs(text, self.passthroughs)
        return text

    def restore_passthroughs(self, text):
        """ Replace passthough placeholders with the original passthrough
        text."""
        for i, __ in enumerate(self.passthroughs):
            text = text.replace('\x07'+str(i)+'\x07', self.passthroughs[i])
        return text


class Macro:

    def __init__(self):
        self.pattern = None     # Matching regular expression.
        self.name = ''          # Conf file macro name (None if implicit).
        self.prefix = ''        # '' if inline, '+' if system, '#' if block.
        self.reo = None         # Compiled pattern re object.
        self.subslist = []      # Default subs for macros passtext group.

    def has_passthrough(self):
        return self.pattern.find(r'(?P<passtext>') >= 0

    def section_name(self, name=None):
        """Return macro markup template section name based on macro name and
        prefix.  Return None section not found."""
        assert self.prefix != '+'
        if not name:
            assert self.name
            name = self.name
        if self.prefix == '#':
            suffix = '-blockmacro'
        else:
            suffix = '-inlinemacro'
        if name+suffix in config.sections:
            return name+suffix
        else:
            message.warning('missing macro section: [%s]' % (name+suffix))
            return None

    def load(self, entry):
        e = parse_entry(entry)
        if e is None:
            # Only the macro pattern was specified, mark for deletion.
            self.name = None
            self.pattern = entry
            return
        if not is_re(e[0]):
            raise EAsciiDoc('illegal macro regular expression: %s' % e[0])
        pattern, name = e
        if name and name[0] in ('+', '#'):
            prefix, name = name[0], name[1:]
        else:
            prefix = ''
        # Parse passthrough subslist.
        mo = re.match(r'^(?P<name>[^[]*)(\[(?P<subslist>.*)\])?$', name)
        name = mo.group('name')
        if name and not is_name(name):
            raise EAsciiDoc('illegal section name in macro entry: %s' % entry)
        subslist = mo.group('subslist')
        if subslist is not None:
            # Parse and validate passthrough subs.
            subslist = parse_options(subslist, SUBS_OPTIONS,
                                     'illegal subs in macro entry: %s' % entry)
        self.pattern = pattern
        self.reo = re.compile(pattern)
        self.prefix = prefix
        self.name = name
        self.subslist = subslist or []

    def subs(self, text):
        def subs_func(mo):
            """Function called to perform macro substitution.
            Uses matched macro regular expression object and returns string
            containing the substituted macro body."""
            # Check if macro reference is escaped.
            if mo.group()[0] == '\\':
                return mo.group()[1:]   # Strip leading backslash.
            d = mo.groupdict()
            # Delete groups that didn't participate in match.
            for k, v in list(d.items()):
                if v is None:
                    del d[k]
            if self.name:
                name = self.name
            else:
                if 'name' not in d:
                    message.warning('missing macro name group: %s' % mo.re.pattern)
                    return ''
                name = d['name']
            section_name = self.section_name(name)
            if not section_name:
                return ''
            # If we're dealing with a block macro get optional block ID and
            # block title.
            if self.prefix == '#' and self.name != 'comment':
                AttributeList.consume(d)
                BlockTitle.consume(d)
            # Parse macro attributes.
            if 'attrlist' in d:
                if d['attrlist'] in (None, ''):
                    del d['attrlist']
                else:
                    if self.prefix == '':
                        # Unescape ] characters in inline macros.
                        d['attrlist'] = d['attrlist'].replace('\\]', ']')
                    parse_attributes(d['attrlist'], d)
                    # Generate option attributes.
                    if 'options' in d:
                        options = parse_options(d['options'], (),
                                                '%s: illegal option name' % name)
                        for option in options:
                            d[option+'-option'] = ''
                    # Substitute single quoted attribute values in block macros.
                    if self.prefix == '#':
                        AttributeList.subs(d)
            if name == 'callout':
                listindex = int(d['index'])
                d['coid'] = calloutmap.add(listindex)
            # The alt attribute is the first image macro positional attribute.
            if name == 'image' and '1' in d:
                d['alt'] = d['1']
            # Unescape special characters in LaTeX target file names.
            if document.backend == 'latex' and 'target' in d and d['target']:
                if '0' not in d:
                    d['0'] = d['target']
                d['target'] = config.subs_specialchars_reverse(d['target'])
            # BUG: We've already done attribute substitution on the macro which
            # means that any escaped attribute references are now unescaped and
            # will be substituted by config.subs_section() below. As a partial
            # fix have withheld {0} from substitution but this kludge doesn't
            # fix it for other attributes containing unescaped references.
            # Passthrough macros don't have this problem.
            a0 = d.get('0')
            if a0:
                d['0'] = chr(0)  # Replace temporarily with unused character.
            body = config.subs_section(section_name, d)
            if not body:
                result = ''
            elif len(body) == 1:
                result = body[0]
            else:
                if self.prefix == '#':
                    result = writer.newline.join(body)
                else:
                    # Internally processed inline macros use UNIX line
                    # separator.
                    result = '\n'.join(body)
            if a0:
                result = result.replace(chr(0), a0)
            return result
        return self.reo.sub(subs_func, text)

    def translate(self):
        """ Block macro translation."""
        assert self.prefix == '#'
        s = reader.read()
        before = s
        if self.has_passthrough():
            s = macros.extract_passthroughs(s, '#')
        s = subs_attrs(s)
        if s:
            s = self.subs(s)
            if self.has_passthrough():
                s = macros.restore_passthroughs(s)
            if s:
                trace('macro block', before, s)
                writer.write(s)

    def subs_passthroughs(self, text, passthroughs):
        """ Replace macro attribute lists in text with placeholders.
        Substitute and append the passthrough attribute lists to the
        passthroughs list."""
        def subs_func(mo):
            """Function called to perform inline macro substitution.
            Uses matched macro regular expression object and returns string
            containing the substituted macro body."""
            # Don't process escaped macro references.
            if mo.group()[0] == '\\':
                return mo.group()
            d = mo.groupdict()
            if 'passtext' not in d:
                message.warning('passthrough macro %s: missing passtext group' %
                                d.get('name', ''))
                return mo.group()
            passtext = d['passtext']
            if re.search('\x07\\d+\x07', passtext):
                message.warning('nested inline passthrough')
                return mo.group()
            if d.get('subslist'):
                if d['subslist'].startswith(':'):
                    message.error('block macro cannot occur here: %s' % mo.group(),
                                  halt=True)
                subslist = parse_options(d['subslist'], SUBS_OPTIONS,
                                         'illegal passthrough macro subs option')
            else:
                subslist = self.subslist
            passtext = Lex.subs_1(passtext, subslist)
            if passtext is None:
                passtext = ''
            if self.prefix == '':
                # Unescape ] characters in inline macros.
                passtext = passtext.replace('\\]', ']')
            passthroughs.append(passtext)
            # Tabs guarantee the placeholders are unambiguous.
            result = (
                text[mo.start():mo.start('passtext')] +
                '\x07' + str(len(passthroughs)-1) + '\x07' +
                text[mo.end('passtext'):mo.end()]
            )
            return result

        return self.reo.sub(subs_func, text)


class CalloutMap:
    def __init__(self):
        self.comap = {}         # key = list index, value = callouts list.
        self.calloutindex = 0   # Current callout index number.
        self.listnumber = 1     # Current callout list number.

    def listclose(self):
        # Called when callout list is closed.
        self.listnumber += 1
        self.calloutindex = 0
        self.comap = {}

    def add(self, listindex):
        # Add next callout index to listindex map entry. Return the callout id.
        self.calloutindex += 1
        # Append the coindex to a list in the comap dictionary.
        if listindex not in self.comap:
            self.comap[listindex] = [self.calloutindex]
        else:
            self.comap[listindex].append(self.calloutindex)
        return self.calloutid(self.listnumber, self.calloutindex)

    @staticmethod
    def calloutid(listnumber, calloutindex):
        return 'CO%d-%d' % (listnumber, calloutindex)

    def calloutids(self, listindex):
        # Retrieve list of callout indexes that refer to listindex.
        if listindex in self.comap:
            result = ''
            for coindex in self.comap[listindex]:
                result += ' ' + self.calloutid(self.listnumber, coindex)
            return result.strip()
        else:
            message.warning('no callouts refer to list item '+str(listindex))
            return ''

    def validate(self, maxlistindex):
        # Check that all list indexes referenced by callouts exist.
        for listindex in list(self.comap.keys()):
            if listindex > maxlistindex:
                message.warning('callout refers to non-existent list item '
                                + str(listindex))

#---------------------------------------------------------------------------
# Input stream Reader and output stream writer classes.
#---------------------------------------------------------------------------

UTF8_BOM = b'\xef\xbb\xbf'


class Reader1:
    """Line oriented AsciiDoc3 input file reader. Processes include and
    conditional inclusion system macros. Tabs are expanded and lines are right
    trimmed."""
    # This class is not used directly, use Reader class instead.
    READ_BUFFER_MIN = 10        # Read buffer low level.

    def __init__(self):
        self.f = None           # Input file object.
        self.fname = None       # Input file name.
        self.nxt = []           # Read ahead buffer containing
                                # [filename,linenumber,linetext] lists.
        self.cursor = None      # Last read() [filename,linenumber,linetext].
        self.tabsize = 8        # Tab expansion number of spaces.
        self.parent = None      # Included reader's parent reader.
        self._lineno = 0        # The last line read from file object f.
        self.current_depth = 0  # Current include depth.
        self.max_depth = 10     # Initial maxiumum allowed include depth.
        self.bom = None         # Byte order mark (BOM).
        self.infile = None      # Saved document 'infile' attribute.
        self.indir = None       # Saved document 'indir' attribute.

    def open(self, fname):
        """Depending on file is stdin or not: set proper encoding, check BOM (ignored in v3)."""
        self.fname = fname
        message.verbose('reading: '+fname)
        if fname == '<stdin>':
            self.f = sys.stdin
            assert ad3in and ad3out
            ad3in.block_updating()
            ad3out.block_updating()
            self.infile = None
            self.indir = None
        else:
            self.f = open(fname, 'r', encoding=ad3in.get_input_encoding(fname), \
                          errors=ad3in.get_input_errors(fname))

            self.infile = fname
            self.indir = os.path.dirname(fname)
        document.attributes['infile'] = self.infile
        document.attributes['indir'] = self.indir
        self._lineno = 0            # The last line read from file object f.
        self.nxt = []
        # Prefill buffer by reading the first line and then pushing it back.
        if Reader1.read(self):
            if self.cursor[2].startswith(str(UTF8_BOM, encoding='utf-8')):
                self.cursor[2] = self.cursor[2][len(str(UTF8_BOM, encoding='utf-8')):]
                message.verbose('BOM utf-8 was erased, no output with BOM')
                self.bom = None  # replaces "self.bom = UTF8_BOM" -> BOM is cut and BOM == False
            self.unread(self.cursor)
            self.cursor = None

    def closefile(self):
        """Used by class methods to close nested include files."""
        self.f.close()
        self.nxt = []

    def close(self):
        self.closefile()
        self.__init__()

    def read(self, skip=False):
        """Read next line. Return None if EOF. Expand tabs. Strip trailing
        white space. Maintain self.nxt read ahead buffer. If skip=True then
        conditional exclusion is active (ifdef and ifndef macros)."""
        # Top up buffer.
        if len(self.nxt) <= self.READ_BUFFER_MIN:
            s = self.f.readline()
            if s:
                self._lineno = self._lineno + 1
            while s:
                if self.tabsize != 0:
                    s = s.expandtabs(self.tabsize)
                s = s.rstrip()
                self.nxt.append([self.fname, self._lineno, s])
                if len(self.nxt) > self.READ_BUFFER_MIN:
                    break
                s = self.f.readline()
                if s:
                    self._lineno = self._lineno + 1
        # Return first (oldest) buffer entry.
        if self.nxt:
            self.cursor = self.nxt[0]
            del self.nxt[0]
            result = self.cursor[2]
            # Check for include macro.
            mo = macros.match('+', r'^include[1]?$', result)
            if mo and not skip:
                # Parse include macro attributes.
                attrs = {}
                parse_attributes(mo.group('attrlist'), attrs)
                warnings = attrs.get('warnings', True)
                # Don't process include macro once the maximum depth is reached.
                if self.current_depth >= self.max_depth:
                    message.warning('maximum include depth exceeded')
                    return result
                # Perform attribute substitution on include macro file name.
                fname = subs_attrs(mo.group('target'))
                if not fname:
                    return Reader1.read(self)   # Return next input line.
                if self.fname != '<stdin>':
                    fname = os.path.expandvars(os.path.expanduser(fname))
                    fname = safe_filename(fname, os.path.dirname(self.fname))
                    if not fname:
                        return Reader1.read(self)   # Return next input line.
                    if not os.path.isfile(fname):
                        if warnings:
                            message.warning('include file not found: %s' % fname)
                        return Reader1.read(self)   # Return next input line.
                    if mo.group('name') == 'include1':
                        if not config.dumping:
                            if fname not in config.include1:
                                message.verbose('include1: ' + fname, linenos=False)
                                # Store the include file in memory for later
                                # retrieval by the {include1:} system attribute.
                                f = open(fname)
                                try:
                                    config.include1[fname] = [
                                        s.rstrip() for s in f]
                                finally:
                                    f.close()
                            return '{include1:%s}' % fname
                        else:
                            # This is a configuration dump, just pass the macro
                            # call through.
                            return result
                # Clone self and set as parent (self assumes the role of child).
                parent = Reader1()
                assign(parent, self)
                self.parent = parent
                # Set attributes in child.
                if 'tabsize' in attrs:
                    try:
                        val = int(attrs['tabsize'])
                        #if not val >= 0:
                        if val < 0:
                            raise ValueError('not >= 0')
                        self.tabsize = val
                    except ValueError:
                        raise EAsciiDoc('illegal include macro tabsize argument')
                else:
                    self.tabsize = config.tabsize
                if 'depth' in attrs:
                    try:
                        val = int(attrs['depth'])
                        #if not val >= 1:
                        if val < 1:
                            raise ValueError('not >= 1')
                        self.max_depth = self.current_depth + val
                    except ValueError:
                        raise EAsciiDoc("include macro: illegal 'depth' argument")
                # Process included file.
                message.verbose('include: ' + fname, linenos=False)
                self.open(fname)
                self.current_depth = self.current_depth + 1
                result = Reader1.read(self)
        else:
            if not Reader1.eof(self):
                result = Reader1.read(self)
            else:
                result = None
        return result

    def eof(self):
        """Returns True if all lines have been read."""
        if not self.nxt:
            # End of current file.
            if self.parent:
                self.closefile()
                assign(self, self.parent)    # Restore parent reader.
                document.attributes['infile'] = self.infile
                document.attributes['indir'] = self.indir
                return Reader1.eof(self)
            else:
                return True
        else:
            return False

    def read_next(self):
        """Like read() but does not advance file pointer."""
        if Reader1.eof(self):
            return None
        else:
            return self.nxt[0][2]

    def unread(self, cursor):
        """Push the line (filename,linenumber,linetext) tuple back into the read
        buffer. Note that it's up to the caller to restore the previous
        cursor."""
        assert cursor
        self.nxt.insert(0, cursor)


class Reader(Reader1):
    """ Wraps (well, sought of) Reader1 class and implements conditional text
    inclusion."""

    def __init__(self):
        Reader1.__init__(self)
        self.depth = 0          # if nesting depth.
        self.skip = False       # true if we're skipping ifdef...endif.
        self.skipname = ''      # Name of current endif macro target.
        self.skipto = -1        # The depth at which skipping is reenabled.

    def read_super(self):
        result = Reader1.read(self, self.skip)
        if result is None and self.skip:
            raise EAsciiDoc('missing endif::%s[]' % self.skipname)
        return result

    def read(self):
        result = self.read_super()
        if result is None:
            return None
        while self.skip:
            mo = macros.match('+', r'ifdef|ifndef|ifeval|endif', result)
            if mo:
                name = mo.group('name')
                target = mo.group('target')
                attrlist = mo.group('attrlist')
                if name == 'endif':
                    self.depth -= 1
                    if self.depth < 0:
                        raise EAsciiDoc('mismatched macro: %s' % result)
                    if self.depth == self.skipto:
                        self.skip = False
                        if target and self.skipname != target:
                            raise EAsciiDoc('mismatched macro: %s' % result)
                else:
                    if name in ('ifdef', 'ifndef'):
                        if not target:
                            raise EAsciiDoc('missing macro target: %s' % result)
                        if not attrlist:
                            self.depth += 1
                    elif name == 'ifeval':
                        if not attrlist:
                            raise EAsciiDoc('missing ifeval condition: %s' % result)
                        self.depth += 1
            result = self.read_super()
            if result is None:
                return None
        mo = macros.match('+', r'ifdef|ifndef|ifeval|endif', result)
        if mo:
            name = mo.group('name')
            target = mo.group('target')
            attrlist = mo.group('attrlist')
            if name == 'endif':
                self.depth = self.depth-1
            else:
                if not target and name in ('ifdef', 'ifndef'):
                    raise EAsciiDoc('missing macro target: %s' % result)
                defined = is_attr_defined(target, document.attributes)
                if name == 'ifdef':
                    if attrlist:
                        if defined:
                            return attrlist
                    else:
                        self.skip = not defined
                elif name == 'ifndef':
                    if attrlist:
                        if not defined:
                            return attrlist
                    else:
                        self.skip = defined
                elif name == 'ifeval':
                    if safe():
                        message.unsafe('ifeval invalid')
                        raise EAsciiDoc('ifeval invalid safe document')
                    if not attrlist:
                        raise EAsciiDoc('missing ifeval condition: %s' % result)
                    cond = False
                    attrlist = subs_attrs(attrlist)
                    if attrlist:
                        try:
                            cond = eval(attrlist)
                        except Exception as e:
                            raise EAsciiDoc('error evaluating ifeval condition: %s: %s' %
                                            (result, str(e)))
                        message.verbose('ifeval: %s: %r' % (attrlist, cond))
                    self.skip = not cond
                if not attrlist or name == 'ifeval':
                    if self.skip:
                        self.skipto = self.depth
                        self.skipname = target
                    self.depth = self.depth+1
            result = self.read()
        if result:
            # Expand executable block macros.
            mo = macros.match('+', r'eval|sys|sys2', result)
            if mo:
                action = mo.group('name')
                cmd = mo.group('attrlist')
                result = system(action, cmd, is_macro=True)
                self.cursor[2] = result  # So we don't re-evaluate.
        if result:
            # Unescape escaped system macros.
            if macros.match('+', \
                            r'\\eval|\\sys|\\sys2|\\ifdef|' \
                            r'\\ifndef|\\endif|\\include|\\include1', \
                            result):
                result = result[1:]
        return result

    def eof(self):
        return self.read_next() is None

    def read_next(self):
        save_cursor = self.cursor
        result = self.read()
        if result is not None:
            self.unread(self.cursor)
            self.cursor = save_cursor
        return result

    def read_lines(self, count=1):
        """Return tuple containing count lines."""
        result = []
        i = 0
        while i < count and not self.eof():
            result.append(self.read())
        return tuple(result)

    def read_ahead(self, count=1):
        """Same as read_lines() but does not advance the file pointer."""
        result = []
        putback = []
        save_cursor = self.cursor
        try:
            i = 0
            while i < count and not self.eof():
                result.append(self.read())
                putback.append(self.cursor)
                i = i+1
            while putback:
                self.unread(putback.pop())
        finally:
            self.cursor = save_cursor
        return tuple(result)

    def skip_blank_lines(self):
        reader.read_until(r'\s*\S+')

    def read_until(self, terminators, same_file=False):
        """Like read() but reads lines up to (but not including) the first line
        that matches the terminator regular expression, regular expression
        object or list of regular expression objects. If same_file is True then
        the terminating pattern must occur in the file the was being read when
        the routine was called."""
        if same_file:
            fname = self.cursor[0]
        result = []
        if not isinstance(terminators, list):
            if isinstance(terminators, str):
                terminators = [re.compile(terminators)]
            else:
                terminators = [terminators]
        while not self.eof():
            save_cursor = self.cursor
            s = self.read()
            if not same_file or fname == self.cursor[0]:
                for reo in terminators:
                    if reo.match(s):
                        self.unread(self.cursor)
                        self.cursor = save_cursor
                        return tuple(result)
            result.append(s)
        return tuple(result)


class Writer:
    """Writes lines to output file."""

    def __init__(self):
        self.newline = '\r\n'            # End of line terminator.
        self.f = None                    # Output file object.
        self.fname = None                # Output file name.
        self.lines_out = 0               # Number of lines written.
        self.skip_blank_lines = False    # If True don't output blank lines.

    def open(self, fname, bom=None):
        '''
        bom is optional byte order mark.
        http://en.wikipedia.org/wiki/Byte-order_mark
        '''
        self.fname = fname
        if fname == '<stdout>':
            assert ad3in and ad3out
            ad3in.block_updating()
            ad3out.block_updating()
            self.f = sys.stdout
        else:
            self.f = open(fname, 'w', encoding=ad3out.get_output_encoding(fname), \
                          errors=ad3out.get_output_errors(fname))

        message.verbose('writing: '+writer.fname, False)
        #if bom: ... # BOM is ignored in AsciiDoc3
        self.lines_out = 0

    def close(self):
        if self.fname != '<stdout>':
            self.f.close()

    def write_line(self, line=None):
        if not (self.skip_blank_lines and (not line or not line.strip())):
            self.f.write((line or '') + self.newline)
            self.lines_out = self.lines_out + 1

    def write(self, *args, **kwargs):
        """Iterates arguments, writes tuple and list arguments one line per
        element, else writes argument as single line. If no arguments writes
        blank line. If argument is None nothing is written. self.newline is
        appended to each line."""
        if 'trace' in kwargs and len(args) > 0:
            trace(kwargs['trace'], args[0])
        if not args:
            self.write_line()
            self.lines_out = self.lines_out + 1
        else:
            for arg in args:
                if is_array(arg):
                    for s in arg:
                        self.write_line(s)
                elif arg is not None:
                    self.write_line(arg)

    def write_tag(self, tag, content, subs=None, d=None, **kwargs):
        """Write content enveloped by tag.
        Substitutions specified in the 'subs' list are perform on the
        'content'."""
        if subs is None:
            subs = config.subsnormal
        stag, etag = subs_tag(tag, d)
        content = Lex.subs(content, subs)
        if 'trace' in kwargs:
            trace(kwargs['trace'], [stag]+content+[etag])
        if stag:
            self.write(stag)
        if content:
            self.write(content)
        if etag:
            self.write(etag)

#---------------------------------------------------------------------------
# Configuration file processing.
#---------------------------------------------------------------------------

def _subs_specialwords(mo):
    """Special word substitution function called by
    Config.subs_specialwords()."""
    word = mo.re.pattern                    # The special word.
    template = config.specialwords[word]    # The corresponding markup template.
    if template not in config.sections:
        raise EAsciiDoc('missing special word template [%s]' % template)
    if mo.group()[0] == '\\':
        return mo.group()[1:]   # Return escaped word.
    args = {}
    args['words'] = mo.group()  # The full match string is argument 'words'.
    args.update(mo.groupdict()) # Add other named match groups to the arguments.
    # Delete groups that didn't participate in match.
    for k, v in list(args.items()):
        if v is None:
            del args[k]
    lines = subs_attrs(config.sections[template], args)
    if not lines:
        result = ''
    elif len(lines) == 1:
        result = lines[0]
    else:
        result = writer.newline.join(lines)
    return result


class Config:
    """Methods to process configuration files."""
    # Non-template section name regexp's.
    ENTRIES_SECTIONS = ('tags', 'miscellaneous', 'attributes', 'specialcharacters',
                        'specialwords', 'macros', 'replacements', 'quotes', 'titles',
                        r'paradef-.+', r'listdef-.+', r'blockdef-.+', r'tabledef-.+',
                        r'tabletags-.+', r'listtags-.+', 'replacements[23]',
                        r'old_tabledef-.+')

    def __init__(self):
        self.sections = collections.OrderedDict() # Keyed by section name containing
                                                  # lists of section lines.
        # Command-line options.
        self.verbose = False
        self.header_footer = True       # -s, --no-header-footer option.
        # [miscellaneous] section.
        self.tabsize = 8
        self.textwidth = 70             # DEPRECATED: Old tables only.
        self.newline = '\r\n'
        self.pagewidth = None
        self.pageunits = None
        self.outfilesuffix = ''
        self.subsnormal = SUBS_NORMAL
        self.subsverbatim = SUBS_VERBATIM
        self.tags = {}          # Values contain (stag,etag) tuples.
        self.specialchars = {}  # Values of special character substitutions.
        self.specialwords = {}  # Name is special word pattern, value is macro.
        # 'self.replacements': Key is find pattern, value is replace pattern.
        self.replacements = collections.OrderedDict()
        self.replacements2 = collections.OrderedDict()
        self.replacements3 = collections.OrderedDict()
        # 'self.specialsections': Name is special section name pattern,
        # value is corresponding section name.
        self.specialsections = {}
        self.quotes = collections.OrderedDict() # Values contain corresponding tag name.
        self.fname = ''         # Most recently loaded configuration file name.
        self.conf_attrs = {}    # Attributes entries from conf files.
        self.cmd_attrs = {}     # Attributes from command-line -a options.
        self.loaded = []        # Loaded conf files.
        self.include1 = {}      # Holds include1::[] files for {include1:}.
        self.dumping = False    # True if asciidoc3 -c option specified.
        self.filters = []       # Filter names specified by --filter option.

    def init(self, cmd):
        """
        Check Python version and locate the executable and configuration files
        directory.
        cmd is the asciidoc3 command or asciidoc3.py path.
        """
        if float(sys.version[:3]) < float(MIN_PYTHON_VERSION):
            message.stderr('FAILED: Python %s or better required' %
                           MIN_PYTHON_VERSION)
            sys.exit(1)
        if not os.path.exists(cmd):
            message.stderr('FAILED: Missing asciidoc3 command: %s' % cmd)
            sys.exit(1)
        global APP_FILE
        APP_FILE = os.path.realpath(cmd)
        global APP_DIR
        APP_DIR = os.path.dirname(APP_FILE)
        global USER_DIR
        USER_DIR = userdir()
        if USER_DIR is not None:
            USER_DIR = os.path.join(USER_DIR, '.asciidoc3')
            if not os.path.isdir(USER_DIR):
                USER_DIR = None

    def load_file(self, fname, dir=None, include=[], exclude=[]):
        """
        Loads sections dictionary with sections from file fname.
        Existing sections are overlaid.
        The 'include' list contains the section names to be loaded.
        The 'exclude' list contains section names not to be loaded.
        Return False if no file was found in any of the locations.
        """

        def update_section(section):
            """ Update section in sections with contents. """
            if section and contents:
                if section in sections and self.entries_section(section):
                    if ''.join(contents):
                        # Merge entries.
                        sections[section] += contents
                    else:
                        del sections[section]
                else:
                    if section.startswith('+'):
                        # Append section.
                        if section in sections:
                            sections[section] += contents
                        else:
                            sections[section] = contents
                    else:
                        # Replace section.
                        sections[section] = contents
        if dir:
            fname = os.path.join(dir, fname)
        # Silently skip missing configuration file.
        if not os.path.isfile(fname):
            return False
        # Don't load conf files twice (local and application conf files are the
        # same if the source file is in the application directory).
        if os.path.realpath(fname) in self.loaded:
            return True
        rdr = Reader()  # Reader processes system macros.
        message.linenos = False         # Disable document line numbers.
        rdr.open(fname)
        message.linenos = None
        self.fname = fname
        reo = re.compile(r'^\[(?P<section>\+?[^\W\d][\w-]*)\]\s*$')
        sections = collections.OrderedDict()
        section, contents = '', []
        while not rdr.eof():
            s = rdr.read()
            if s and s[0] == '#':       # Skip comment lines.
                continue
            if s[:2] == '\\#':          # Unescape lines starting with '#'.
                s = s[1:]
            s = s.rstrip()
            found = reo.findall(s)
            if found:
                update_section(section) # Store previous section.
                section = found[0].lower()
                contents = []
            else:
                contents.append(s)
        update_section(section)         # Store last section.
        rdr.close()
        if include:
            for s in set(sections) - set(include):
                del sections[s]
        if exclude:
            for s in set(sections) & set(exclude):
                del sections[s]
        attrs = {}
        self.load_sections(sections, attrs)
        if not include:
            # If all sections are loaded mark this file as loaded.
            self.loaded.append(os.path.realpath(fname))
        document.update_attributes(attrs) # So they are available immediately.
        return True

    def load_sections(self, sections, attrs=None):
        """
        Loads sections dictionary. Each dictionary entry contains a
        list of lines.
        Updates 'attrs' with parsed [attributes] section entries.
        """
        # Delete trailing blank lines from sections.
        for k in list(sections.keys()):
            for i in range(len(sections[k])-1, -1, -1):
                if not sections[k][i]:
                    del sections[k][i]
                elif not self.entries_section(k):
                    break
        # Update new sections.
        for k, v in list(sections.items()):
            if k.startswith('+'):
                # Append section.
                k = k[1:]
                if k in self.sections:
                    self.sections[k] += v
                else:
                    self.sections[k] = v
            else:
                # Replace section.
                self.sections[k] = v
        self.parse_tags()
        # Internally [miscellaneous] section entries are just attributes.
        d = {}
        parse_entries(sections.get('miscellaneous', ()), d, unquote=True,
                      allow_name_only=True)
        parse_entries(sections.get('attributes', ()), d, unquote=True,
                      allow_name_only=True)
        update_attrs(self.conf_attrs, d)
        if attrs is not None:
            attrs.update(d)
        # input/output encoding/errors are updated and fixed
        Ad3Codec.update_encoding(config.fname, attrs, config.cmd_attrs)
        d = {}
        parse_entries(sections.get('titles', ()), d)
        Title.load(d)
        parse_entries(sections.get('specialcharacters', ()), \
                      self.specialchars, escape_delimiter=False)
        parse_entries(sections.get('quotes', ()), self.quotes)
        self.parse_specialwords()
        self.parse_replacements()
        self.parse_replacements('replacements2')
        self.parse_replacements('replacements3')
        self.parse_specialsections()
        paragraphs.load(sections)
        lists.load(sections)
        blocks.load(sections)
        tables_OLD.load(sections)
        tables.load(sections)
        macros.load(sections.get('macros', ()))

    def get_load_dirs(self):
        """
        Return list of well known paths with conf files.
        """
        result = []
        if localapp():
            # Load from folders in asciidoc3 executable directory.
            result.append(APP_DIR)
        else:
            # Load from global configuration directory.
            result.append(CONF_DIR)
        # Load configuration files from ~/.asciidoc3 if it exists.
        if USER_DIR is not None:
            result.append(USER_DIR)
        return result

    def find_in_dirs(self, filename, dirs=None):
        """
        Find conf files from dirs list.
        Return list of found file paths.
        Return empty list if not found in any of the locations.
        """
        result = []
        if dirs is None:
            dirs = self.get_load_dirs()
        for d in dirs:
            f = os.path.join(d, filename)
            if os.path.isfile(f):
                result.append(f)
        result = [item for item in result if not item.endswith('asciidoc.conf')]
        return result

    def load_from_dirs(self, filename, dirs=None, include=[]):
        """
        Load conf file from dirs list.
        If dirs not specified try all the well known locations.
        Return False if no file was successfully loaded.
        """
        count = 0
        for f in self.find_in_dirs(filename, dirs):
            if self.load_file(f, include=include):
                count += 1
        return count != 0

    def load_backend(self, dirs=None):
        """
        Load the backend configuration files from dirs list.
        If dirs not specified try all the well known locations.
        If a <backend>.conf file was found return it's full path name,
        if not found return None.
        """
        result = None
        if dirs is None:
            dirs = self.get_load_dirs()
        conf = document.backend + '.conf'
        conf2 = document.backend + '-' + document.doctype + '.conf'
        # First search for filter backends.
        for d in [os.path.join(d, 'backends', document.backend) for d in dirs]:
            if self.load_file(conf, d):
                result = os.path.join(d, conf)
            self.load_file(conf2, d)
        if not result:
            # Search in the normal locations.
            for d in dirs:
                if self.load_file(conf, d):
                    result = os.path.join(d, conf)
                self.load_file(conf2, d)
        return result

    def load_filters(self, dirs=None):
        """
        Load filter configuration files from 'filters' directory in dirs list.
        If dirs not specified try all the well known locations.  Suppress
        loading if a file named __noautoload__ is in same directory as the conf
        file unless the filter has been specified with the --filter
        command-line option (in which case it is loaded unconditionally).
        """
        if dirs is None:
            dirs = self.get_load_dirs()
        for d in dirs:
            # Load filter .conf files.
            filtersdir = os.path.join(d, 'filters')
            for dirpath, __, filenames in os.walk(filtersdir):
                subdirs = dirpath[len(filtersdir):].split(os.path.sep)
                # True if processing a filter specified by a --filter option.
                filter_opt = len(subdirs) > 1 and subdirs[1] in self.filters
                if '__noautoload__' not in filenames or filter_opt:
                    for f in filenames:
                        if re.match(r'^.+\.conf$', f):
                            self.load_file(f, dirpath)

    def find_config_dir(self, *dirnames):
        """
        Return path of configuration directory.
        Try all the well known locations.
        Return None if directory not found.
        """
        for d in [os.path.join(d, *dirnames) for d in self.get_load_dirs()]:
            if os.path.isdir(d):
                return d
        return None

    def set_theme_attributes(self):
        theme = document.attributes.get('theme')
        if theme and 'themedir' not in document.attributes:
            themedir = self.find_config_dir('themes', theme)
            if themedir:
                document.attributes['themedir'] = themedir
                iconsdir = os.path.join(themedir, 'icons')
                if 'data-uri' in document.attributes and os.path.isdir(iconsdir):
                    document.attributes['iconsdir'] = iconsdir
            else:
                message.warning('missing theme: %s' % theme, linenos=False)

    def load_miscellaneous(self, d):
        """Set miscellaneous configuration entries from dictionary 'd'."""

        def set_if_int_ge(name, d, min_value):
            if name in d:
                try:
                    val = int(d[name])
                    if val < min_value:
                        raise ValueError("not >= " + str(min_value))
                    setattr(self, name, val)
                except ValueError:
                    raise EAsciiDoc('illegal [miscellaneous] %s entry' % name)
        set_if_int_ge('tabsize', d, 0)
        set_if_int_ge('textwidth', d, 1) # DEPRECATED: Old tables only.
        if 'pagewidth' in d:
            try:
                val = float(d['pagewidth'])
                self.pagewidth = val
            except ValueError:
                raise EAsciiDoc('illegal [miscellaneous] pagewidth entry')
        if 'pageunits' in d:
            self.pageunits = d['pageunits']
        if 'outfilesuffix' in d:
            self.outfilesuffix = d['outfilesuffix']
        if 'newline' in d:
            # Convert escape sequences to their character values.
            self.newline = literal_eval('"'+d['newline']+'"')
        if 'subsnormal' in d:
            self.subsnormal = parse_options(d['subsnormal'], SUBS_OPTIONS,
                                            'illegal [%s] %s: %s' %
                                            ('miscellaneous', 'subsnormal', d['subsnormal']))
        if 'subsverbatim' in d:
            self.subsverbatim = parse_options(d['subsverbatim'], SUBS_OPTIONS,
                                              'illegal [%s] %s: %s' %
                                              ('miscellaneous', 'subsverbatim', d['subsverbatim']))

    def validate(self):
        """Check the configuration for internal consistency. Called after all
        configuration files have been loaded."""
        message.linenos = False     # Disable document line numbers.
        # Heuristic to validate that at least one configuration file was loaded.
        if not self.specialchars or not self.tags or not lists:
            raise EAsciiDoc('incomplete configuration files')
        # Check special characters are only one character long.
        for k in list(self.specialchars.keys()):
            if len(k) != 1:
                raise EAsciiDoc('[specialcharacters] ' \
                                'must be a single character: %s' % k)
        # Check all special words have a corresponding inline macro body.
        for macro in list(self.specialwords.values()):
            if not is_name(macro):
                raise EAsciiDoc('illegal special word name: %s' % macro)
            if macro not in self.sections:
                message.warning('missing special word macro: [%s]' % macro)
        # Check all text quotes have a corresponding tag.
        for q in list(self.quotes.keys())[:]:
            tag = self.quotes[q]
            if not tag:
                del self.quotes[q]  # Undefine quote.
            else:
                if tag[0] == '#':
                    tag = tag[1:]
                if tag not in self.tags:
                    message.warning('[quotes] %s missing tag definition: %s' % (q, tag))
        # Check all specialsections section names exist.
        for k, v in list(self.specialsections.items()):
            if not v:
                del self.specialsections[k]
            elif v not in self.sections:
                message.warning('missing specialsections section: [%s]' % v)
        paragraphs.validate()
        lists.validate()
        blocks.validate()
        tables_OLD.validate()
        tables.validate()
        macros.validate()
        message.linenos = None

    def entries_section(self, section_name):
        """
        Return True if conf file section contains entries, not a markup
        template.
        """
        for name in self.ENTRIES_SECTIONS:
            if re.match(name, section_name):
                return True
        return False

    def dump(self):
        """Dump configuration to stdout."""
        # Header.
        hdr = ''
        hdr = hdr + '#' + writer.newline
        hdr = hdr + '# Generated by AsciiDoc3 %s for %s %s.%s' % \
            (VERSION, document.backend, document.doctype, writer.newline)
        t = time.asctime(time.localtime(time.time()))
        hdr = hdr + '# %s%s' % (t, writer.newline)
        hdr = hdr + '#' + writer.newline
        sys.stdout.write(hdr)
        # Dump special sections.
        # Dump only the configuration file and command-line attributes.
        # [miscellaneous] entries are dumped as part of the [attributes].
        d = {}
        d.update(self.conf_attrs)
        d.update(self.cmd_attrs)
        dump_section('attributes', d)
        Title.dump()
        dump_section('quotes', self.quotes)
        dump_section('specialcharacters', self.specialchars)
        d = {}
        for k, v in list(self.specialwords.items()):
            if v in d:
                d[v] = '%s "%s"' % (d[v], k)   # Append word list.
            else:
                d[v] = '"%s"' % k
        dump_section('specialwords', d)
        dump_section('replacements', self.replacements)
        dump_section('replacements2', self.replacements2)
        dump_section('replacements3', self.replacements3)
        dump_section('specialsections', self.specialsections)
        d = {}
        for k, v in list(self.tags.items()):
            d[k] = '%s|%s' % v
        dump_section('tags', d)
        paragraphs.dump()
        lists.dump()
        blocks.dump()
        tables_OLD.dump()
        tables.dump()
        macros.dump()
        # Dump remaining sections.
        for k in list(self.sections.keys()):
            if not self.entries_section(k):
                sys.stdout.write('[%s]%s' % (k, writer.newline))
                for line in self.sections[k]:
                    sys.stdout.write('%s%s' % (line, writer.newline))
                sys.stdout.write(writer.newline)

    def subs_section(self, section, d):
        """Section attribute substitution using attributes from
        document.attributes and 'd'.  Lines containing undefined
        attributes are deleted."""
        if section in self.sections:
            return subs_attrs(self.sections[section], d)
        else:
            message.warning('missing section: [%s]' % section)
            return ()

    def parse_tags(self):
        """Parse [tags] section entries into self.tags dictionary."""
        d = {}
        parse_entries(self.sections.get('tags', ()), d)
        for k, v in list(d.items()):
            if v is None:
                if k in self.tags:
                    del self.tags[k]
            elif v == '':
                self.tags[k] = (None, None)
            else:
                mo = re.match(r'(?P<stag>.*)\|(?P<etag>.*)', v)
                if mo:
                    self.tags[k] = (mo.group('stag'), mo.group('etag'))
                else:
                    raise EAsciiDoc('[tag] %s value malformed' % k)

    def tag(self, name, d=None):
        """Returns (starttag,endtag) tuple named name from configuration file
        [tags] section. Raise error if not found. If a dictionary 'd' is
        passed then merge with document attributes and perform attribute
        substitution on tags."""
        if name not in self.tags:
            raise EAsciiDoc('missing tag: %s' % name)
        stag, etag = self.tags[name]
        if d is not None:
            # TODO: Should we warn if substitution drops a tag?
            if stag:
                stag = subs_attrs(stag, d)
            if etag:
                etag = subs_attrs(etag, d)
        if stag is None:
            stag = ''
        if etag is None:
            etag = ''
        return (stag, etag)

    def parse_specialsections(self):
        """Parse specialsections section to self.specialsections dictionary."""
        # TODO: This is virtually the same as parse_replacements() and should
        # be factored to single routine.
        d = {}
        parse_entries(self.sections.get('specialsections', ()), d, unquote=True)
        for pat, sectname in list(d.items()):
            pat = strip_quotes(pat)
            if not is_re(pat):
                raise EAsciiDoc('[specialsections] entry ' \
                                'is not a valid regular expression: %s' % pat)
            if sectname is None:
                if pat in self.specialsections:
                    del self.specialsections[pat]
            else:
                self.specialsections[pat] = sectname

    def parse_replacements(self, sect='replacements'):
        """Parse replacements section into self.replacements dictionary."""
        d = collections.OrderedDict()
        parse_entries(self.sections.get(sect, ()), d, unquote=True)
        for pat, rep in list(d.items()):
            if not self.set_replacement(pat, rep, getattr(self, sect)):
                raise EAsciiDoc('[%s] entry in %s is not a valid' \
                                ' regular expression: %s' % (sect, self.fname, pat))

    @staticmethod
    def set_replacement(pat, rep, replacements):
        """Add pattern and replacement to replacements dictionary."""
        pat = strip_quotes(pat)
        if not is_re(pat):
            return False
        if rep is None:
            if pat in replacements:
                del replacements[pat]
        else:
            replacements[pat] = strip_quotes(rep)
        return True

    def subs_replacements(self, s, sect='replacements'):
        """Substitute patterns from self.replacements in 's'."""
        result = s
        for pat, rep in list(getattr(self, sect).items()):
            result = re.sub(pat, rep, result)
        return result

    def parse_specialwords(self):
        """Parse special words section into self.specialwords dictionary."""
        reo = re.compile(r'(?:\s|^)(".+?"|[^"\s]+)(?=\s|$)')
        for line in self.sections.get('specialwords', ()):
            e = parse_entry(line)
            if not e:
                raise EAsciiDoc('[specialwords] entry in %s is malformed: %s' \
                    % (self.fname, line))
            name, wordlist = e
            if not is_name(name):
                raise EAsciiDoc('[specialwords] name in %s is illegal: %s' \
                    % (self.fname, name))
            if wordlist is None:
                # Undefine all words associated with 'name'.
                for k, v in list(self.specialwords.items()):
                    if v == name:
                        del self.specialwords[k]
            else:
                words = reo.findall(wordlist)
                for word in words:
                    word = strip_quotes(word)
                    if not is_re(word):
                        raise EAsciiDoc('[specialwords] entry in %s ' \
                            'is not a valid regular expression: %s' \
                            % (self.fname, word))
                    self.specialwords[word] = name

    def subs_specialchars(self, s):
        """Perform special character substitution on string 's'."""
        """It may seem like a good idea to escape special characters with a '\'
        character, the reason we don't is because the escape character itself
        then has to be escaped and this makes including code listings
        problematic. Use the predefined {amp},{lt},{gt} attributes instead."""
        result = ''
        for ch in s:
            result = result + self.specialchars.get(ch, ch)
        return result

    def subs_specialchars_reverse(self, s):
        """Perform reverse special character substitution on string 's'."""
        result = s
        for k, v in list(self.specialchars.items()):
            result = result.replace(v, k)
        return result

    def subs_specialwords(self, s):
        """Search for word patterns from self.specialwords in 's' and
        substitute using corresponding macro."""
        result = s
        for word in list(self.specialwords.keys()):
            result = re.sub(word, _subs_specialwords, result)
        return result

    def expand_templates(self, entries):
        """Expand any template::[] macros in a list of section entries."""
        result = []
        for line in entries:
            mo = macros.match('+', r'template', line)
            if mo:
                s = mo.group('attrlist')
                if s in self.sections:
                    result += self.expand_templates(self.sections[s])
                else:
                    message.warning('missing section: [%s]' % s)
                    result.append(line)
            else:
                result.append(line)
        return result

    def expand_all_templates(self):
        for k, v in list(self.sections.items()):
            self.sections[k] = self.expand_templates(v)

    def section2tags(self, section, d={}, skipstart=False, skipend=False):
        """Perform attribute substitution on 'section' using document
        attributes plus 'd' attributes. Return tuple (stag,etag) containing
        pre and post | placeholder tags. 'skipstart' and 'skipend' are
        used to suppress substitution."""
        assert section is not None
        if section in self.sections:
            body = self.sections[section]
        else:
            message.warning('missing section: [%s]' % section)
            body = ()
        # Split macro body into start and end tag lists.
        stag = []
        etag = []
        in_stag = True
        for s in body:
            if in_stag:
                mo = re.match(r'(?P<stag>.*)\|(?P<etag>.*)', s)
                if mo:
                    if mo.group('stag'):
                        stag.append(mo.group('stag'))
                    if mo.group('etag'):
                        etag.append(mo.group('etag'))
                    in_stag = False
                else:
                    stag.append(s)
            else:
                etag.append(s)
        # Do attribute substitution last so {brkbar} can be used to escape |.
        # But don't do attribute substitution on title -- we've already done it.
        title = d.get('title')
        if title:
            d['title'] = chr(0)  # Replace with unused character.
        if not skipstart:
            stag = subs_attrs(stag, d)
        if not skipend:
            etag = subs_attrs(etag, d)
        # Put the {title} back.
        if title:
            stag = [x.replace(chr(0), title) for x in stag]
            etag = [x.replace(chr(0), title) for x in etag]
            d['title'] = title
        return (stag, etag)


#---------------------------------------------------------------------------
# Old table classes are no longer supported ...

class Table_OLD(AbstractBlock):
    COL_STOP = r"(`|'|\.)"  # RE.
    ALIGNMENTS = {'`':'left', "'":'right', '.':'center'}
    FORMATS = ('fixed', 'csv', 'dsv')

    def __init__(self):
        AbstractBlock.__init__(self)
        self.CONF_ENTRIES += ('template', 'fillchar', 'format', 'colspec',
                              'headrow', 'footrow', 'bodyrow', 'headdata',
                              'footdata', 'bodydata')
        # Configuration parameters.
        self.fillchar = None
        self.format = None        # 'fixed','csv','dsv'
        self.colspec = None
        self.headrow = None
        self.footrow = None
        self.bodyrow = None
        self.headdata = None
        self.footdata = None
        self.bodydata = None
        # Calculated parameters.
        self.underline = None     # RE matching current table underline.
        self.isnumeric = False    # True if numeric ruler.
        self.tablewidth = None    # Optional table width scale factor.
        self.columns = []         # List of Columns.
        # Other.
        self.check_msg = ''       # Message set by previous self.validate() call.

    def translate(self):
        raise EAsciiDoc("Deprecated old tables found --> "
                        "old tables are no longer supported in AsciiDoc3.py")


class Tables_OLD(AbstractBlocks):
    """List of tables."""
    BLOCK_TYPE = Table_OLD
    PREFIX = 'old_tabledef-'

    def __init__(self):
        AbstractBlocks.__init__(self)

    def load(self, sections):
        AbstractBlocks.load(self, sections)

    def validate(self):
        # Does not call AbstractBlocks.validate().
        # Check we have a default table definition,
        for i in range(len(self.blocks)):
            if self.blocks[i].defname == 'old_tabledef-default':
                default = self.blocks[i]
                break
        else:
            raise EAsciiDoc('missing section: [OLD_tabledef-default]')
        # Set default table defaults.
        if default.format is None:
            default.subs = 'fixed'
        # Propagate defaults to unspecified table parameters.
        for b in self.blocks:
            if b is not default:
                if b.fillchar is None:
                    b.fillchar = default.fillchar
                if b.format is None:
                    b.format = default.format
                if b.template is None:
                    b.template = default.template
                if b.colspec is None:
                    b.colspec = default.colspec
                if b.headrow is None:
                    b.headrow = default.headrow
                if b.footrow is None:
                    b.footrow = default.footrow
                if b.bodyrow is None:
                    b.bodyrow = default.bodyrow
                if b.headdata is None:
                    b.headdata = default.headdata
                if b.footdata is None:
                    b.footdata = default.footdata
                if b.bodydata is None:
                    b.bodydata = default.bodydata
        # Check all tables have valid fill character.
        for b in self.blocks:
            if not b.fillchar or len(b.fillchar) != 1:
                raise EAsciiDoc('[%s] missing or illegal fillchar' % b.defname)
        # Build combined tables delimiter patterns and assign defaults.
        delimiters = []
        for b in self.blocks:
            # Ruler is:
            #   (ColStop,(ColWidth,FillChar+)?)+, FillChar+, TableWidth?
            b.delimiter = r'^(' + Table_OLD.COL_STOP \
                + r'(\d*|' + re.escape(b.fillchar) + r'*)' \
                + r')+' \
                + re.escape(b.fillchar) + r'+' \
                + r'([\d\.]*)$'
            delimiters.append(b.delimiter)
            if not b.headrow:
                b.headrow = b.bodyrow
            if not b.footrow:
                b.footrow = b.bodyrow
            if not b.headdata:
                b.headdata = b.bodydata
            if not b.footdata:
                b.footdata = b.bodydata
        self.delimiters = re_join(delimiters)
        # Check table definitions are valid.
        for b in self.blocks:
            b.validate()
            if config.verbose:
                if b.check_msg:
                    message.warning('[%s] table definition: %s' % (b.defname, b.check_msg))

# End of deprecated old table classes.
#---------------------------------------------------------------------------

#---------------------------------------------------------------------------
# filter and theme plugin commands.
#---------------------------------------------------------------------------
def die(msg):
    message.stderr(msg)
    sys.exit(1)

def extract_zip(zip_file, destdir):
    """
    Unzip Zip file to destination directory.
    Throws exception if error occurs.
    """
    zipo = zipfile.ZipFile(zip_file, 'r')
    try:
        for zi in zipo.infolist():
            outfile = zi.filename
            if not outfile.endswith('/'):
                d, outfile = os.path.split(outfile)
                directory = os.path.normpath(os.path.join(destdir, d))
                if not os.path.isdir(directory):
                    os.makedirs(directory)
                outfile = os.path.join(directory, outfile)
                perms = (zi.external_attr >> 16) & 0o777
                message.verbose('extracting: %s' % outfile)
                flags = os.O_CREAT | os.O_WRONLY
                if sys.platform == 'win32':
                    flags |= os.O_BINARY
                if not perms:
                    # Zip files created under Windows do not include permissions.
                    fh = os.open(outfile, flags)
                else:
                    fh = os.open(outfile, flags, perms)
                try:
                    os.write(fh, zipo.read(zi.filename))
                finally:
                    os.close(fh)
    finally:
        zipo.close()

def create_zip(zip_file, src, skip_hidden=False):
    """
    Create Zip file. If src is a directory archive all contained files and
    subdirectories, if src is a file archive the src file.
    Files and directories names starting with . are skipped
    if skip_hidden is True.
    Throws exception if error occurs.
    """
    zipo = zipfile.ZipFile(zip_file, 'w')
    try:
        if os.path.isfile(src):
            arcname = os.path.basename(src)
            message.verbose('archiving: %s' % arcname)
            zipo.write(src, arcname, zipfile.ZIP_DEFLATED)
        elif os.path.isdir(src):
            srcdir = os.path.abspath(src)
            if srcdir[-1] != os.path.sep:
                srcdir += os.path.sep
            for root, dirs, files in os.walk(srcdir):
                arcroot = os.path.abspath(root)[len(srcdir):]
                if skip_hidden:
                    for d in dirs[:]:
                        if d.startswith('.'):
                            message.verbose('skipping: %s' % os.path.join(arcroot, d))
                            del dirs[dirs.index(d)]
                for f in files:
                    filename = os.path.join(root, f)
                    arcname = os.path.join(arcroot, f)
                    if skip_hidden and f.startswith('.'):
                        message.verbose('skipping: %s' % arcname)
                        continue
                    message.verbose('archiving: %s' % arcname)
                    zipo.write(filename, arcname, zipfile.ZIP_DEFLATED)
        else:
            raise ValueError('src must specify directory or file: %s' % src)
    finally:
        zipo.close()


class Plugin:
    """
    --filter and --theme option commands.
    """
    CMDS = ('install', 'remove', 'list', 'build')
    type = None     # 'backend', 'filter' or 'theme'.

    @staticmethod
    def get_dir():
        """
        Return plugins path (.asciidoc3/filters or .asciidoc3/themes) in user's
        home directory or None if user home not defined.
        """
        result = userdir()
        if result:
            result = os.path.join(result, '.asciidoc3', Plugin.type+'s')
        return result

    @staticmethod
    def install(args):
        """
        Install plugin Zip file.
        args[0] is plugin zip file path.
        args[1] is optional destination plugins directory.
        """
        if len(args) not in (1, 2):
            die('invalid number of arguments: --%s install %s'
                % (Plugin.type, ' '.join(args)))
        zip_file = args[0]
        if not os.path.isfile(zip_file):
            die('file not found: %s' % zip_file)
        reo = re.match(r'^\w+', os.path.split(zip_file)[1])
        if not reo:
            die('file name does not start with legal %s name: %s'
                % (Plugin.type, zip_file))
        plugin_name = reo.group()
        if len(args) == 2:
            plugins_dir = args[1]
            if not os.path.isdir(plugins_dir):
                die('directory not found: %s' % plugins_dir)
        else:
            plugins_dir = Plugin.get_dir()
            if not plugins_dir:
                die('user home directory is not defined')
        plugin_dir = os.path.join(plugins_dir, plugin_name)
        if os.path.exists(plugin_dir):
            die('%s is already installed: %s' % (Plugin.type, plugin_dir))
        try:
            os.makedirs(plugin_dir)
        except Exception as e:
            die('failed to create %s directory: %s' % (Plugin.type, str(e)))
        try:
            extract_zip(zip_file, plugin_dir)
        except Exception as e:
            if os.path.isdir(plugin_dir):
                shutil.rmtree(plugin_dir)
            die('failed to extract %s: %s' % (Plugin.type, str(e)))

    @staticmethod
    def remove(args):
        """
        Delete plugin directory.
        args[0] is plugin name.
        args[1] is optional plugin directory (defaults to ~/.asciidoc3/<plugin_name>).
        """
        if len(args) not in (1, 2):
            die('invalid number of arguments: --%s remove %s'
                % (Plugin.type, ' '.join(args)))
        plugin_name = args[0]
        if not re.match(r'^\w+$', plugin_name):
            die('illegal %s name: %s' % (Plugin.type, plugin_name))
        if len(args) == 2:
            d = args[1]
            if not os.path.isdir(d):
                die('directory not found: %s' % d)
        else:
            d = Plugin.get_dir()
            if not d:
                die('user directory is not defined')
        plugin_dir = os.path.join(d, plugin_name)
        if not os.path.isdir(plugin_dir):
            die('cannot find %s: %s' % (Plugin.type, plugin_dir))
        try:
            message.verbose('removing: %s' % plugin_dir)
            shutil.rmtree(plugin_dir)
        except Exception as e:
            die('failed to delete %s: %s' % (Plugin.type, str(e)))

    @staticmethod
    def list(args):
        """
        List all plugin directories (global and local).
        """
        for d in [os.path.join(d, Plugin.type+'s') for d in config.get_load_dirs()]:
            if os.path.isdir(d):
                # TODO pylint3 says: Generator 'generator' has no 'next' member (no-member)
                for f in os.walk(d).next()[1]:
                    message.stdout(os.path.join(d, f))

    @staticmethod
    def build(args):
        """
        Create plugin Zip file.
        args[0] is Zip file name.
        args[1] is plugin directory.
        """
        if len(args) != 2:
            die('invalid number of arguments: --%s build %s'
                % (Plugin.type, ' '.join(args)))
        zip_file = args[0]
        plugin_source = args[1]
        if not (os.path.isdir(plugin_source) or os.path.isfile(plugin_source)):
            die('plugin source not found: %s' % plugin_source)
        try:
            create_zip(zip_file, plugin_source, skip_hidden=True)
        except Exception as e:
            die('failed to create %s: %s' % (zip_file, str(e)))


#---------------------------------------------------------------------------
# Application code.
#---------------------------------------------------------------------------
# Constants
# ---------
APP_FILE = None             # This file's full path.
APP_DIR = None              # This file's directory.
USER_DIR = None             # ~/.asciidoc
# Global configuration files directory (set by Makefile build target).
CONF_DIR = '/etc/asciidoc3'
HELP_FILE = 'help.conf'     # Default (English) help file.

# Globals
# -------
document = Document()       # The document being processed.
config = Config()           # Configuration file reader.
reader = Reader()           # Input stream line reader.
writer = Writer()           # Output stream line writer.
message = Message()         # Message functions.
paragraphs = Paragraphs()   # Paragraph definitions.
lists = Lists()             # List definitions.
blocks = DelimitedBlocks()  # DelimitedBlock definitions.
tables_OLD = Tables_OLD()   # Table_OLD definitions.
tables = Tables()           # Table definitions.
macros = Macros()           # Macro definitions.
calloutmap = CalloutMap()   # Coordinates callouts and callout list.
trace = Trace()             # Implements trace attribute processing.
ad3in = Ad3In()             # Handles input-encoding
ad3out = Ad3Out()           # Handles output-encoding

### Used by asciidoc3api.py ###
# List of message strings written to stderr.
messages = message.messages

def asciidoc3(backend, doctype, confiles, infile, outfile, options):
    """Convert AsciiDoc3 document to DocBook document of type doctype.
    The AsciiDoc3 document is read from file object src the translated
    DocBook file written to file object dst."""

    def load_conffiles(include=[], exclude=[]):
        """Load conf files specified on the command-line and by
           the conf-files attribute."""
        files = document.attributes.get('conf-files', '')
        files = [f.strip() for f in files.split('|') if f.strip()]
        files += confiles
        if files:
            for f in files:
                if os.path.isfile(f):
                    config.load_file(f, include=include, exclude=exclude)
                else:
                    raise EAsciiDoc('missing configuration file: %s' % f)
    try:
        document.attributes['python3'] = sys.executable
        if os.name == 'nt':
            # This is only used under Windows using IDLE, because here we see
            # something like '...Python37-32\\pythonw.exe' as sys.executable.
            # But, to run filter with 'sys' we need '...python3.exe' (see line ~840).
            document.attributes['python3'], n = re.subn(r'pythonw\.exe', r'python3.exe', \
                                                        document.attributes['python3'], \
                                                        1, re.IGNORECASE)
            if n:
                message.verbose('sys.executable: pythonw.exe replaced with python3.exe')
        for f in config.filters:
            if not config.find_config_dir('filters', f):
                raise EAsciiDoc('missing filter: %s' % f)
        if doctype not in (None, 'article', 'manpage', 'book'):
            raise EAsciiDoc('illegal document type')
        # Set processing options.
        for o in options:
            if o == '-c':
                config.dumping = True
            if o == '-s':
                config.header_footer = False
            if o == '-v':
                config.verbose = True
        document.update_attributes()
        if '-e' not in options:
            # Load asciidoc3.conf files in two passes: the first for attributes
            # the second for everything. This is so that locally set attributes
            # available are in the global asciidoc3.conf
            if not config.load_from_dirs('asciidoc3.conf', include=['attributes']):
                raise EAsciiDoc('configuration file asciidoc3.conf missing')
            load_conffiles(include=['attributes'])
            config.load_from_dirs('asciidoc3.conf')
            if infile != '<stdin>':
                indir = os.path.dirname(infile)
                config.load_file('asciidoc3.conf', indir,
                                 include=['attributes', 'titles', 'specialchars'])
        else:
            load_conffiles(include=['attributes', 'titles', 'specialchars'])
        document.update_attributes()
        # Check the infile exists.
        if infile != '<stdin>':
            if not os.path.isfile(infile):
                raise EAsciiDoc('input file %s missing' % infile)
        document.infile = infile
        AttributeList.initialize()
        # Open input file and parse document header.
        reader.tabsize = config.tabsize
        reader.open(infile)
        has_header = document.parse_header(doctype, backend)
        # doctype is now finalized.
        document.attributes['doctype-'+document.doctype] = ''
        config.set_theme_attributes()
        # Load backend configuration files.
        if '-e' not in options:
            f = document.backend + '.conf'
            conffile = config.load_backend()
            if not conffile:
                raise EAsciiDoc('missing backend conf file: %s' % f)
            document.attributes['backend-confdir'] = os.path.dirname(conffile)
        # backend is now known.
        document.attributes['backend-'+document.backend] = ''
        document.attributes[document.backend+'-'+document.doctype] = ''
        doc_conffiles = []
        if '-e' not in options:
            # Load filters and language file.
            config.load_filters()
            document.load_lang()
            if infile != '<stdin>':
                # Load local conf files (files in the source file directory).
                config.load_file('asciidoc3.conf', indir)
                config.load_backend([indir])
                config.load_filters([indir])
                # Load document specific configuration files.
                f = os.path.splitext(infile)[0]
                doc_conffiles = [
                    f for f in (f+'.conf', f+'-'+document.backend+'.conf')
                    if os.path.isfile(f)]
                for f in doc_conffiles:
                    config.load_file(f)
        load_conffiles()
        # Build asciidoc3-args attribute.
        args = ''
        # Add custom conf file arguments.
        for f in doc_conffiles + confiles:
            args += ' --conf-file "%s"' % f
        # Add command-line and header attributes.
        attrs = {}
        attrs.update(AttributeEntry.attributes)
        attrs.update(config.cmd_attrs)
        if 'title' in attrs:    # Don't pass the header title.
            del attrs['title']
        for k, v in list(attrs.items()):
            if v:
                args += ' --attribute "%s=%s"' % (k, v)
            else:
                args += ' --attribute "%s"' % k
        document.attributes['asciidoc3-args'] = args
        # Build outfile name.
        if outfile is None:
            outfile = os.path.splitext(infile)[0] + '.' + document.backend
            if config.outfilesuffix:
                # Change file extension.
                outfile = os.path.splitext(outfile)[0] + config.outfilesuffix
        document.outfile = outfile
        # Document header attributes override conf file attributes.
        document.attributes.update(AttributeEntry.attributes)
        document.update_attributes()
        # Set the default embedded icons directory.
        if 'data-uri' in document.attributes \
           and not os.path.isdir(document.attributes['iconsdir']):
            document.attributes['iconsdir'] = os.path.join(
                document.attributes['asciidoc3-confdir'], 'images/icons')
        # Configuration is fully loaded.
        config.expand_all_templates()
        # Check configuration for consistency.
        config.validate()
        # Initialize top level block name.
        if document.attributes.get('blockname'):
            AbstractBlock.blocknames.append(document.attributes['blockname'])
        paragraphs.initialize()
        lists.initialize()
        if config.dumping:
            config.dump()
        else:
            Ad3Codec.fixed_encoding = True
            # to ensure encoding in subprocess and conf-files:
            Ad3Codec.add_encoding_for_compatibility()
            if 'quirks' in document.attributes:
                message.verbose('No quirks-mode in AsciiDoc3 any more!')
            writer.newline = config.newline
            try:
                writer.open(outfile, reader.bom)
                try:
                    document.translate(has_header) # Generate the output.
                finally:
                    writer.close()
            finally:
                reader.closefile()
    except KeyboardInterrupt:
        print("Execution stopped by user. Exit.")
        raise
    except Exception as e:
        # Cleanup
        if outfile and outfile != '<stdout>' and os.path.isfile(outfile):
            os.unlink(outfile)
        # Build and print error description.
        msg = 'FAILED: '
        if reader.cursor:
            msg = message.format('', msg)
        if isinstance(e, EAsciiDoc):
            message.stderr('%s%s' % (msg, str(e)))
        else:
            # __name__ == 'asciidoc3.asciidoc3' if installed via pip3
            if __name__ in ('__main__', 'asciidoc3.asciidoc3'):
                message.stderr(msg+'unexpected error:')
                message.stderr('-'*60)
                traceback.print_exc(file=sys.stderr)
                message.stderr('-'*60)
            else:
                message.stderr('%sunexpected error: %s' % (msg, str(e)))
        sys.exit(1)

def usage(msg=''):
    """Print help-info to stderr."""
    if msg:
        message.stderr(msg)
    show_help('default', sys.stderr)

def show_help(topic, f=None):
    """Print help topic to file object f."""
    if f is None:
        f = sys.stdout
    # Select help file.
    lang = config.cmd_attrs.get('lang')
    if lang and lang != 'en':
        help_file = 'help-' + lang + '.conf'
    else:
        help_file = HELP_FILE
    # Print [topic] section from help file.
    config.load_from_dirs(help_file)
    if not config.sections:
        # Default to English if specified language help files not found.
        help_file = HELP_FILE
        config.load_from_dirs(help_file)
    if not config.sections:
        message.stderr('no help topics found')
        sys.exit(1)
    n = 0
    for k in config.sections:
        if re.match(re.escape(topic), k):
            n += 1
            lines = config.sections[k]
    if not n:
        if topic != 'topics':
            message.stderr('help topic not found: [%s] in %s' % (topic, help_file))
        message.stderr('available help topics: %s' % ', '.join(list(config.sections.keys())))
        sys.exit(1)
    elif n > 1:
        message.stderr('ambiguous help topic: %s' % topic)
    else:
        for line in lines:
            print(line, file=f)

### Used by asciidoc3api.py ###
def execute(cmd, opts, args):
    """
    Execute asciidoc3 with command-line options and arguments.
    cmd is asciidoc3 command or asciidoc3.py path.
    opts and args conform to values returned by getopt.getopt().
    Raises SystemExit if an error occurs.
    """
    config.init(cmd)
    if len(args) > 1:
        usage('Too many arguments')
        sys.exit(1)
    backend = None
    doctype = None
    confiles = []
    outfile = None
    options = []
    help_option = False
    for o, v in opts:
        if o in ('--help', '-h'):
            help_option = True
        # DEPRECATED: --unsafe option is ignored!
        if o == '--unsafe':
            message.verbose('unsafe option is ignored!') #document.safe = False
        if o == '--safe':
            document.safe = True
        if o == '--version':
            print(('asciidoc3 %s' % VERSION))
            sys.exit(0)
        if o in ('-b', '--backend'):
            backend = v
        if o in ('-c', '--dump-conf'):
            options.append('-c')
        if o in ('-d', '--doctype'):
            doctype = v
        if o in ('-e', '--no-conf'):
            options.append('-e')
        # no asciidoc.conf allowed, use asciidoc3.conf instead
        if o in ('-f', '--conf-file') and not v.strip().lower().endswith('asciidoc.conf'):
            confiles.append(v)
        if o == '--filter':
            config.filters.append(v)
        if o in ('-n', '--section-numbers'):
            o = '-a'
            v = 'numbered'
        if o == '--theme':
            o = '-a'
            v = 'theme='+v
        if o in ('-a', '--attribute'):
            e = parse_entry(v, allow_name_only=True)
            if not e:
                usage('Illegal -a option: %s' % v)
                sys.exit(1)
            k, v = e
            # A @ suffix denotes don't override existing document attributes.
            if v and v[-1] == '@':
                document.attributes[k] = v[:-1]
            else:
                config.cmd_attrs[k] = v
        if o in ('-o', '--out-file'):
            outfile = v
        if o in ('-s', '--no-header-footer'):
            options.append('-s')
        if o in ('-v', '--verbose'):
            options.append('-v')
    if help_option:
        if not args:
            show_help('default')
        else:
            show_help(args[-1])
        sys.exit(0)
    if not args and not opts:
        usage()
        sys.exit(0)
    if not args:
        usage('No source file specified')
        sys.exit(1)
    stdin, stdout = sys.stdin, sys.stdout
    try:
        infile = args[0]
        if infile == '-':
            infile = '<stdin>'
        elif isinstance(infile, str):
            infile = os.path.abspath(infile)
        else:   # Input file is file object from API call.
            sys.stdin = infile
            infile = '<stdin>'
        if outfile == '-':
            outfile = '<stdout>'
        elif isinstance(outfile, str):
            outfile = os.path.abspath(outfile)
        elif outfile is None:
            if infile == '<stdin>':
                outfile = '<stdout>'
        else:   # Output file is file object from API call.
            sys.stdout = outfile
            outfile = '<stdout>'
        # Do the work.
        asciidoc3(backend, doctype, confiles, infile, outfile, options)
        if document.has_errors:
            sys.exit(1)
    finally:
        sys.stdin, sys.stdout = stdin, stdout

def main():
    # these four 'global' statements are probably not neccessary
    global args
    global count
    global opt_names
    global opts
    # Process command line options.
    try:
        #DEPRECATED: --unsafe option.
        opts, args = getopt.getopt(sys.argv[1:],
                                   'a:b:cd:ef:hno:svw:',
                                   ['attribute=', 'backend=', 'conf-file=',
                                    'doctype=', 'dump-conf', 'help', 'no-conf',
                                    'no-header-footer', 'out-file=',
                                    'section-numbers', 'verbose', 'version',
                                    'safe', 'unsafe', 'doctest', 'filter=', 'theme='])
    except getopt.GetoptError:
        message.stderr('illegal command options')
        sys.exit(1)
    opt_names = [opt[0] for opt in opts]
    if '--doctest' in opt_names:
        # No doctest in asciidoc3.py
        message.verbose('No doctest in asciidoc3.py')
        sys.exit("No doctest in asciidoc3.py")
    # Look for plugin management commands.
    count = 0
    for o, v in opts:
        if o in ('-b', '--backend', '--filter', '--theme'):
            if o == '-b':
                o = '--backend'
            plugin = o[2:]
            cmd = v
            if cmd not in Plugin.CMDS:
                continue
            count += 1
    if count > 1:
        die('--backend, --filter and --theme options are mutually exclusive')
    if count == 1:
        # Execute plugin management commands.
        if not cmd:
            die('missing --%s command' % plugin)
        if cmd not in Plugin.CMDS:
            die('illegal --%s command: %s' % (plugin, cmd))
        Plugin.type = plugin
        config.init(sys.argv[0])
        config.verbose = bool({'-v', '--verbose'} & set(opt_names))
        getattr(Plugin, cmd)(args)
    else:
        # Execute asciidoc3
        try:
            execute(sys.argv[0], opts, args)
        except KeyboardInterrupt:
            sys.exit(1)

if __name__ == '__main__':
    main()
