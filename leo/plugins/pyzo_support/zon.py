#@+leo-ver=5-thin
#@+node:ekr.20190811124150.1: * @file pyzo_support/zon.py
"""pyzo_support/zon.py"""

import leo.core.leoGlobals as g
assert g
import re
import sys
import time

# pylint: disable=trailing-comma-tuple
string_types = str,
integer_types = int,
float_types = float,

try:  # pragma: no cover
    from collections import OrderedDict as _dict
except ImportError:
    _dict = dict

#@+others
#@+node:ekr.20190811124441.2: ** isidentifier
def isidentifier(s):
    # http://stackoverflow.com/questions/2544972/
    if not isinstance(s, str):
        return False
    return re.match(r'^\w+$', s, re.UNICODE) and re.match(r'^[0-9]', s) is None
#@+node:ekr.20190811124441.3: ** class Dict(_dict)
class Dict(_dict):
    """ A dict in which the items can be get/set as attributes.
    """

    __reserved_names__ = dir(_dict())  # Also from OrderedDict
    __pure_names__ = dir(dict())
    __slots__ = []

    #@+others
    #@+node:ekr.20190811124441.4: *3* Dict.__repr__
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
    #@+node:ekr.20190811124441.5: *3* Dict.__getattribute__
    def __getattribute__(self, key):
        # pylint: disable=inconsistent-return-statements
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            if key in self:
                return self[key]
            raise
    #@+node:ekr.20190811124441.6: *3* Dict.__dir__
    def __dir__(self):
        names = [k for k in self.keys() if isidentifier(k)]
        return Dict.__reserved_names__ + names

    #@+node:ekr.20190811124441.7: *3* Dict.__setattr__
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
    #@-others

Struct = Dict
Struct.__is_ssdf_struct__ = True
    
## Public functions
#@+node:ekr.20190811124441.8: ** SSDF compatibility
# SSDF compatibility
#@+node:ekr.20190811124441.9: *3* isstruct
def isstruct(ob):  # SSDF compatibility
    """ isstruct(ob)

    Returns whether the given object is an SSDF struct.
    """
    if hasattr(ob, '__is_ssdf_struct__'):
        return bool(ob.__is_ssdf_struct__)
    return False
#@+node:ekr.20190811124441.10: *3* new
def new():
    """ new()

    Create a new Dict object. The same as "Dict()".
    """
    return Dict()

ssdf_new = new
#@+node:ekr.20190811124441.11: *3* clear
def clear(d):  # SSDF compatibility
    """ clear(d)

    Clear all elements of the given Dict object.
    """
    d.clear()
#@+node:ekr.20190811124441.12: *3* copy
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
#@+node:ekr.20190811124441.13: *3* count
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
#@+node:ekr.20190811124441.14: *3* loads
def loads(text):
    """ loads(text)

    Load a Dict from the given Unicode) string in ZON syntax.
    """
    if not isinstance(text, string_types):
        raise ValueError('zon.loads() expects a string.')
    reader = ReaderWriter()
    return reader.read(text)
#@+node:ekr.20190811124441.15: *3* load
def load(file_):
    """ load(filename)

    Load a Dict from the given file or filename.
    """
    if isinstance(file_, string_types):
        file = open(file_, 'rb')
    text = file.read().decode('utf-8')
    return loads(text)
#@+node:ekr.20190811124441.16: *3* saves
def saves(d):
    """ saves(d)

    Serialize the given dict to a (Unicode) string.
    """
    if not (isstruct(d) or isinstance(d, dict)):
        raise ValueError('ssdf.saves() expects a dict.')
    writer = ReaderWriter()
    text = writer.save(d)
    return text
#@+node:ekr.20190811124441.17: *3* save
def save(file, d):
    """ save(file, d)

    Serialize the given dict to the given file or filename.
    """
    text = saves(d)
    if isinstance(file, string_types):
        file = open(file, 'wb')
    with file:
        file.write(text.encode('utf-8'))
#@+node:ekr.20190811124441.18: ** class ReaderWriter
## The core

class ReaderWriter:

    #@+others
    #@+node:ekr.20190811124441.19: *3* ReaderWriter.read
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
    #@+node:ekr.20190811124441.20: *3* ReaderWriter.save
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
    #@+node:ekr.20190811124441.21: *3* ReaderWriter.from_object
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
    #@+node:ekr.20190811124441.22: *3* ReaderWriter.to_object
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
    #@+node:ekr.20190811124441.23: *3* ReaderWriter.to_int_or_float
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
    #@+node:ekr.20190811124441.24: *3* ReaderWriter.from_int
    def from_int(self, value):
        return repr(int(value)).rstrip('L')
    #@+node:ekr.20190811124441.25: *3* ReaderWriter.from_float
    def from_float(self, value):
        # Use general specifier with a very high precision.
        # Any spurious zeros are automatically removed. The precision
        # should be sufficient such that any numbers saved and loaded
        # back will have the exact same value again.
        # see e.g. http://bugs.python.org/issue1580
        return repr(float(value))  # '%0.17g' % value
    #@+node:ekr.20190811124441.26: *3* ReaderWriter.from_unicode
    def from_unicode(self, value):
        value = value.replace('\\', '\\\\')
        value = value.replace('\n','\\n')
        value = value.replace('\r','\\r')
        value = value.replace('\x0b', '\\x0b').replace('\x0c', '\\x0c')
        value = value.replace("'", "\\'")
        return "'" + value + "'"
    #@+node:ekr.20190811124441.27: *3* ReaderWriter.to_unicode
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
    #@+node:ekr.20190811124441.28: *3* ReaderWriter.from_dict
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
    #@+node:ekr.20190811124441.29: *3* ReaderWriter.to_dict
    def to_dict(self, data, linenr):
        return Dict()
    #@+node:ekr.20190811124441.30: *3* ReaderWriter.from_list
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
    #@+node:ekr.20190811124441.31: *3* ReaderWriter.to_list
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
    #@-others
#@-others
#@@language python
#@@tabwidth -4

#@-leo
