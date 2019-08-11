# -*- coding: utf-8 -*-
"""
A new module containing (for now) *copies* of config-related code.
"""

import leo.core.leoGlobals as leo_g
assert leo_g
# from leo.core.leoQt import QtCore, QtGui #, QtWidgets
import os
import re
import sys
import time

# From zon.py...
# pylint: disable=trailing-comma-tuple
string_types = str,
integer_types = int,
float_types = float,

try:  # pragma: no cover
    from collections import OrderedDict as _dict
except ImportError:
    _dict = dict
    
def isidentifier(s):
    # http://stackoverflow.com/questions/2544972/
    if not isinstance(s, str):
        return False
    return re.match(r'^\w+$', s, re.UNICODE) and re.match(r'^[0-9]', s) is None
class Dict(_dict):
    """ A dict in which the items can be get/set as attributes.
    """

    __reserved_names__ = dir(_dict())  # Also from OrderedDict
    __pure_names__ = dir(dict())
    __slots__ = []

    def __repr__(self):
        identifier_items = []
        nonidentifier_items = []
        for key, val in self.items():
            if isidentifier(key):
                identifier_items.append('%s=%r' % (key, val))
            else:
                nonidentifier_items.append('(%r, %r)' % (key, val))
        if nonidentifier_items:
            return 'Dict([%s], %s)' % (', '.join(nonidentifier_items),
                                       ', '.join(identifier_items))
        return 'Dict(%s)' % (', '.join(identifier_items))
    def __getattribute__(self, key):
        # pylint: disable=inconsistent-return-statements
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            if key in self:
                return self[key]
            raise
    def __dir__(self):
        names = [k for k in self.keys() if isidentifier(k)]
        return Dict.__reserved_names__ + names

    def __setattr__(self, key, val):

        if key in Dict.__reserved_names__:
            # Either let OrderedDict do its work, or disallow
            if key not in Dict.__pure_names__:
                return _dict.__setattr__(self, key, val)
            raise AttributeError('Reserved name, this key can only ' +
                                     'be set via ``d[%r] = X``' % key)
        # if isinstance(val, dict): val = Dict(val) -> no, makes a copy!
        self[key] = val
        return None # EKR: change.

# EKR:change
    # Struct = Dict
    # Struct.__is_ssdf_struct__ = True
ssdf_Struct = Dict
ssdf_Struct.__is_ssdf_struct__ = True
    
## Public functions
# SSDF compatibility
def isstruct(ob):  # SSDF compatibility
    """ isstruct(ob)

    Returns whether the given object is an SSDF struct.
    """
    if hasattr(ob, '__is_ssdf_struct__'):
        return bool(ob.__is_ssdf_struct__)
    return False
def new():
    """ new()

    Create a new Dict object. The same as "Dict()".
    """
    return Dict()

ssdf_new = new
def clear(d):  # SSDF compatibility
    """ clear(d)

    Clear all elements of the given Dict object.
    """
    d.clear()

ssdf_clear = clear
def copy(object):
    """ copy(objec)

    Return a deep copy the given object. The object and its children
    should be dict-compatible data types. Note that dicts are converted
    to Dict and tuples to lists.
    """
    if isstruct(object) or isinstance(object, dict):
        newObject = Dict()
        for key in object:
            val = object[key]
            newObject[key] = copy(val)
        return newObject
    if isinstance(object, (tuple, list)):
        return [copy(ob) for ob in object]
    return object  # immutable
def count(object, cache=None):
    """ count(object):

    Count the number of elements in the given object. An element is
    defined as one of the 6 datatypes supported by ZON (dict,
    tuple/list, string, int, float, None).
    """
    cache = cache or []
    if isstruct(object) or isinstance(object, (dict, list)):
        if id(object) in cache:
            raise RuntimeError('recursion!')
        cache.append(id(object))
    n = 1
    if isstruct(object) or isinstance(object, dict):
        for key in object:
            val = object[key]
            n += count(val, cache)
    elif isinstance(object, (tuple, list)):
        for val in object:
            n += count(val, cache)
    return n
def loads(text):
    """ loads(text)

    Load a Dict from the given Unicode) string in ZON syntax.
    """
    if not isinstance(text, string_types):
        raise ValueError('zon.loads() expects a string.')
    reader = ReaderWriter()
    return reader.read(text)
def load(file_):
    """ load(filename)

    Load a Dict from the given file or filename.
    """
    if isinstance(file_, string_types):
        file = open(file_, 'rb')
    text = file.read().decode('utf-8')
    return loads(text)

ssdf_load = load
def saves(d):
    """ saves(d)

    Serialize the given dict to a (Unicode) string.
    """
    if not (isstruct(d) or isinstance(d, dict)):
        raise ValueError('ssdf.saves() expects a dict.')
    writer = ReaderWriter()
    text = writer.save(d)
    return text
def save(file, d):
    """ save(file, d)

    Serialize the given dict to the given file or filename.
    """
    text = saves(d)
    if isinstance(file, string_types):
        file = open(file, 'wb')
    with file:
        file.write(text.encode('utf-8'))
## The core

class ReaderWriter():

    def read(self, text):

        indent = 0
        root = Dict()
        container_stack = [(0, root)]
        new_container = None

        for i, line in enumerate(text.splitlines()):
            linenr = i + 1

            # Strip line
            line2 = line.lstrip()

            # Skip comments and empty lines
            if not line2 or line2[0] == '#':
                continue

            # Find the indentation
            prev_indent = indent
            indent = len(line) - len(line2)
            if indent == prev_indent:
                pass
            elif indent < prev_indent:
                while container_stack[-1][0] > indent:
                    container_stack.pop(-1)
                if container_stack[-1][0] != indent:
                    print('ZON: Ignoring wrong dedentation at %i' % linenr)
            elif indent > prev_indent and new_container is not None:
                container_stack.append((indent, new_container))
                new_container = None
            else:
                print('ZON: Ignoring wrong indentation at %i' % linenr)
                indent = prev_indent

            # Split name and data using a regular expression
            m = re.search(r"^\w+? *?=", line2) # EKR:change
            if m:
                i = m.end(0)
                name = line2[:i-1].strip()
                data = line2[i:].lstrip()
            else:
                name = None
                data = line2

            # Get value
            value = self.to_object(data, linenr)

            # Store the value
            _indent, current_container = container_stack[-1]
            if isinstance(current_container, dict):
                if name:
                    current_container[name] = value
                else:
                    print('ZON: unnamed item in dict on line %i' % linenr)
            elif isinstance(current_container, list):
                if name:
                    print('ZON: named item in list on line %i' % linenr)
                else:
                    current_container.append(value)
            else:
                raise RuntimeError('Invalid container %r' % current_container)

            # Prepare for next round
            if isinstance(value, (dict, list)):
                new_container = value

        return root
    def save(self, d):

        pyver = '%i.%i.%i' % sys.version_info[:3]
        ct = time.asctime()
        lines = []
        lines.append('# -*- coding: utf-8 -*-')
        lines.append('# This Zoof Object Notation (ZON) file was')
        lines.append('# created from Python %s on %s.\n' % (pyver, ct))
        lines.append('')
        lines.extend(self.from_dict(d, -2)[1:])

        return '\r\n'.join(lines)
        # todo: pop toplevel dict
    def from_object(self, name, value, indent):

        # Get object's data
        if value is None:
            data = 'Null'
        elif isinstance(value, integer_types):
            data = self.from_int(value)
        elif isinstance(value, float_types):
            data = self.from_float(value)
        elif isinstance(value, bool):
            data = self.from_int(int(value))
        elif isinstance(value, string_types):
            data = self.from_unicode(value)
        elif isinstance(value, dict):
            data = self.from_dict(value, indent)
        elif isinstance(value, (list, tuple)):
            data = self.from_list(value, indent)
        else:
            # We do not know
            data = 'Null'
            tmp = repr(value)
            if len(tmp) > 64:
                tmp = tmp[:64] + '...'
            if name is not None:
                print("ZON: %s is unknown object: %s" %  (name, tmp))
            else:
                print("ZON: unknown object: %s" % tmp)

        # Finish line (or first line)
        if isinstance(data, string_types):
            data = [data]
        if name:
            data[0] = '%s%s = %s' % (' ' * indent, name, data[0])
        else:
            data[0] = '%s%s' % (' ' * indent, data[0])

        return data
    def to_object(self, data, linenr):

        data = data.lstrip()

        # Determine what type of object we're dealing with by reading
        # like a human.
        if not data:
            print('ZON: no value specified at line %i.' % linenr)
            return None
        if data[0] in '-.0123456789':
            return self.to_int_or_float(data, linenr)
        if data[0] == "'":
            return self.to_unicode(data, linenr)
        if data.startswith('dict:'):
            return self.to_dict(data, linenr)
        if data.startswith('list:') or data[0] == '[':
            return self.to_list(data, linenr)
        if data.startswith('Null') or data.startswith('None'):
            return None
        print("ZON: invalid type on line %i." % linenr)
        return None
    def to_int_or_float(self, data, linenr):
        line = data.partition('#')[0]
        try:
            return int(line)
        except ValueError:
            try:
                return float(line)
            except ValueError:
                print("ZON: could not parse number on line %i." % linenr)
                return None
    def from_int(self, value):
        return repr(int(value)).rstrip('L')
    def from_float(self, value):
        # Use general specifier with a very high precision.
        # Any spurious zeros are automatically removed. The precision
        # should be sufficient such that any numbers saved and loaded
        # back will have the exact same value again.
        # see e.g. http://bugs.python.org/issue1580
        return repr(float(value))  # '%0.17g' % value
    def from_unicode(self, value):
        value = value.replace('\\', '\\\\')
        value = value.replace('\n','\\n')
        value = value.replace('\r','\\r')
        value = value.replace('\x0b', '\\x0b').replace('\x0c', '\\x0c')
        value = value.replace("'", "\\'")
        return "'" + value + "'"
    def to_unicode(self, data, linenr):
        # Encode double slashes
        line = data.replace('\\\\','0x07') # temp

        # Find string using a regular expression
        m = re.search("'.*?[^\\\\]'|''", line)
        if not m:
            print("ZON: string not ended correctly on line %i." % linenr)
            return None # return not-a-string
        # Decode stuff
        line = m.group(0)[1:-1]
        line = line.replace('\\n','\n')
        line = line.replace('\\r','\r')
        line = line.replace('\\x0b', '\x0b').replace('\\x0c', '\x0c')
        line = line.replace("\\'","'")
        line = line.replace('0x07','\\')
        return line
    def from_dict(self, value, indent):
        lines = ["dict:"]
        # Process children
        for key, val in value.items():
            # Skip all the builtin stuff
            if key.startswith("__"):
                continue
            # Skip methods, or anything else we can call
            if hasattr(val, '__call__'):
                continue  # Note: py3.x does not have function callable
            # Add!
            lines.extend(self.from_object(key, val, indent+2))
        return lines
    def to_dict(self, data, linenr):
        return Dict()
    def from_list(self, value, indent):
        # Collect subdata and check whether this is a "small list"
        isSmallList = True
        allowedTypes = integer_types + float_types + string_types
        subItems = []
        for element in value:
            if not isinstance(element, allowedTypes):
                isSmallList = False
            subdata = self.from_object(None, element, 0)  # No indent
            subItems.extend(subdata)
        isSmallList = isSmallList and len(subItems) < 256

        # Return data
        if isSmallList:
            return '[%s]' % (', '.join(subItems))
        data = ["list:"]
        ind = ' ' * (indent + 2)
        for item in subItems:
            data.append(ind + item)
        return data
    def to_list(self, data, linenr):
        value = []
        if data[0] == 'l': # list:
            return list()
       
        i0 = 1
        pieces = []
        inString = False
        escapeThis = False
        line = data
        for i in range(1,len(line)):
            if inString:
                # Detect how to get out
                if escapeThis:
                    escapeThis = False
                    continue
                elif line[i] == "\\":
                    escapeThis = True
                elif line[i] == "'":
                    inString = False
            else:
                # Detect going in a string, break, or end
                if line[i] == "'":
                    inString = True
                elif line[i] == ",":
                    pieces.append(line[i0:i])
                    i0 = i+1
                elif line[i] == "]":
                    piece = line[i0:i]
                    if piece.strip(): # Do not add if empty
                        pieces.append(piece)
                    break
        else:
            print("ZON: short list not closed right on line %i." % linenr)

        # Cut in pieces and process each piece
        value = []
        for piece in pieces:
            v = self.to_object(piece, linenr)
            value.append(v)
        return value
## Define some functions

# todo: move some stuff out of this module ...
def loadConfig(defaultsOnly=False):
    """ loadConfig(defaultsOnly=False)
    Load default and site-wide configuration file(s) and that of the user (if it exists).
    Any missing fields in the user config are set to the defaults.
    """

    # Function to insert names from one config in another
    def replaceFields(base, new):
        for key in new:
            if key in base and isinstance(base[key], ssdf_Struct):
                replaceFields(base[key], new[key])
            else:
                base[key] = new[key]
                
    config = ssdf_new()

    # Reset our pyzo.config structure
    ssdf_clear(config) # EKR:change.

    # Load default and inject in the pyzo.config
    fname = os.path.join(pyzoDir, 'resources', 'defaultConfig.ssdf')
    defaultConfig = ssdf_load(fname) # EKR:change
    replaceFields(config, defaultConfig)

    # Platform specific keybinding: on Mac, Ctrl+Tab (actually Cmd+Tab) is a system shortcut
    if sys.platform == 'darwin':
        config.shortcuts2.view__select_previous_file = 'Alt+Tab,'

    # Load site-wide config if it exists and inject in pyzo.config
    fname = os.path.join(pyzoDir, 'resources', 'siteConfig.ssdf')
    if os.path.isfile(fname):
        try:
            siteConfig = ssdf_load(fname) # EKR:change
            replaceFields(config, siteConfig) # EKR:change
        except Exception:
            t = 'Error while reading config file %r, maybe its corrupt?'
            print(t % fname)
            raise

    # Load user config and inject in pyzo.config
    fname = os.path.join(appDataDir, "config.ssdf")
    if os.path.isfile(fname):
        try:
            userConfig = ssdf_load(fname) # EKR:change
            replaceFields(config, userConfig)
        except Exception:
            t = 'Error while reading config file %r, maybe its corrupt?'
            print(t % fname)
            raise
    return config
def appdata_dir(appname=None, roaming=False, macAsLinux=False):
    """ appdata_dir(appname=None, roaming=False,  macAsLinux=False)
    Get the path to the application directory, where applications are allowed
    to write user specific files (e.g. configurations). For non-user specific
    data, consider using common_appdata_dir().
    If appname is given, a subdir is appended (and created if necessary).
    If roaming is True, will prefer a roaming directory (Windows Vista/7).
    If macAsLinux is True, will return the Linux-like location on Mac.
    """

    # Define default user directory
    userDir = os.path.expanduser('~')

    # Get system app data dir
    path = None
    if sys.platform.startswith('win'):
        path1, path2 = os.getenv('LOCALAPPDATA'), os.getenv('APPDATA')
        path = (path2 or path1) if roaming else (path1 or path2)
    elif sys.platform.startswith('darwin') and not macAsLinux:
        path = os.path.join(userDir, 'Library', 'Application Support')
    # On Linux and as fallback
    if not (path and os.path.isdir(path)):
        path = userDir

    # Maybe we should store things local to the executable (in case of a
    # portable distro or a frozen application that wants to be portable)
    prefix = sys.prefix
    if getattr(sys, 'frozen', None): # See application_dir() function
        prefix = os.path.abspath(os.path.dirname(sys.executable))
    for reldir in ('settings', '../settings'):
        localpath = os.path.abspath(os.path.join(prefix, reldir))
        if os.path.isdir(localpath):
            try:
                open(os.path.join(localpath, 'test.write'), 'wb').close()
                os.remove(os.path.join(localpath, 'test.write'))
            except IOError:
                pass # We cannot write in this directory
            else:
                path = localpath
                break

    # Get path specific for this app
    if appname:
        if path == userDir:
            appname = '.' + appname.lstrip('.') # Make it a hidden directory
        path = os.path.join(path, appname)
        if not os.path.isdir(path):
            os.mkdir(path)

    # Done
    return path
def getResourceDirs(): # From pyzo.__init__.py
    """ getResourceDirs()
    Get the directories to the resources: (pyzoDir, appDataDir).
    Also makes sure that the appDataDir has a "tools" directory and
    a style file.
    """

    ### Always commented out.
        #     # Get root of the Pyzo code. If frozen its in a subdir of the app dir
        #     pyzoDir = paths.application_dir()
        #     if paths.is_frozen():
        #         pyzoDir = os.path.join(pyzoDir, 'source')

    ###
        # pyzoDir = os.path.abspath(os.path.dirname(__file__))
        # if '.zip' in pyzoDir:
            # raise RuntimeError('The Pyzo package cannot be run from a zipfile.')
    pyzoDir = leo_g.os_path_finalize_join(leo_g.app.loadDir, '..', 'external')

    # Get where the application data is stored (use old behavior on Mac)
    appDataDir = appdata_dir('pyzo', roaming=True, macAsLinux=True)

    ###
        # # Create tooldir if necessary
        # toolDir = os.path.join(appDataDir, 'tools')
        # if not os.path.isdir(toolDir):
            # os.mkdir(toolDir)
    return pyzoDir, appDataDir

pyzoDir, appDataDir = getResourceDirs()
