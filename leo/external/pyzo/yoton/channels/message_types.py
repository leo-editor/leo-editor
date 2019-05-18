# -*- coding: utf-8 -*-
# Copyright (C) 2013, the Pyzo development team
#
# Yoton is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module yoton.channels.message_types

Defines a few basic message_types for the channels. A MessageType object
defines how a message of that type should be converted to bytes and
vice versa.

The Packer and Unpacker classes for the ObjectMessageType are based on
the xdrrpc Python module by Rob Reilink and Windel Bouwman.

"""

import sys
import struct
from yoton.misc import bytes, basestring, long

# To decode P2k strings that are not unicode
if sys.__stdin__ and sys.__stdin__.encoding:
    STDINENC = sys.__stdin__.encoding
elif sys.stdin and sys.stdin.encoding:
    STDINENC = sys.stdin.encoding
else:
    STDINENC = 'utf-8'


class MessageType(object):
    """ MessageType()
    
    Instances of this class are used to convert messages to bytes and
    bytes to messages.
    
    Users can easily inherit from this class to make channels work for
    user specific message types. Three methods should be overloaded:
      * message_to_bytes()  - given a message, returns bytes
      * message_from_bytes() - given bytes, returns the message
      * message_type_name() - a string (for example 'text', 'array')
    
    The message_type_name() method is used by the channel to add an
    extension to the slot name, such that only channels of the same
    message type (well, with the same message type name) can connect.
    
    """
    
    def message_to_bytes(self, message):
        raise NotImplementedError()
    
    def message_from_bytes(self, bb):
        raise NotImplementedError()
    
    def message_type_name(self):
        raise NotImplementedError()



class BinaryMessageType(MessageType):
    """ BinaryMessageType()
    
    To let channels handle binary messages.
    Available as yoton.BINARY.
    
    """
    
    def message_type_name(self):
        return 'bin'
    
    
    def message_to_bytes(self, message):
        if not isinstance(message, bytes):
            raise ValueError("Binary channel requires byte messages.")
        return message
    
    
    def message_from_bytes(self, bb):
        return bb



class TextMessageType(MessageType):
    """ BinaryMessageType()
    
    To let channels handle Unicode text messages.
    Available as yoton.TEXT.
    
    """
    
    def message_type_name(self):
        return 'txt'
    
    def message_to_bytes(self, message):
        
        # Check
        if not isinstance(message, basestring):
            raise ValueError("Text channel requires string messages.")
        
        # If using py2k and the string is not unicode, make unicode first
        # by try encoding using UTF-8. When a piece of code stored
        # in a unicode string is executed, str objects are utf-8 encoded.
        # Otherwise they are encoded using __stdin__.encoding. In specific
        # cases, a non utf-8 encoded str might be succesfully encoded
        # using utf-8, but this is rare. Since I would not
        # know how to tell the encoding beforehand, we'll take our
        # chances... Note that in Pyzo (for which this package was created,
        # all executed code is unicode, so str instrances are always
        # utf-8 encoded.
        if isinstance(message, bytes):
            try:
                message = message.decode('utf-8')
            except UnicodeError:
                try:
                    message = message.decode(STDINENC)
                except UnicodeError:
                    # Probably not really a string then?
                    message = repr(message)
        
        # Encode and send
        return message.encode('utf-8')
    
    
    def message_from_bytes(self, bb):
        return bb.decode('utf-8')



class ObjectMessageType(MessageType):
    """ ObjectMessageType()
    
    To let channels handle messages consisting of any of the following
    Python objects: None, bool, int, float, string, list, tuple, dict.
    Available as yoton.OBJECT.
    
    """
    
    def message_type_name(self):
        return 'obj'
    
    def message_to_bytes(self, message):
        packer = Packer()
        packer.pack_object(message)
        return packer.get_buffer()
    
    def message_from_bytes(self, bb):
        if bb:
            unpacker = Unpacker(bb)
            return unpacker.unpack_object()
        else:
            return None



# Formats
_FMT_TYPE = '<B'
_FMT_BOOL = '<B'
_FMT_INT = '<q'
_FMT_FLOAT = '<d'

# Types
_TYPE_NONE = ord('n')
_TYPE_BOOL = ord('b')
_TYPE_INT = ord('i')
_TYPE_FLOAT = ord('f')
_TYPE_STRING = ord('s')
_TYPE_LIST = ord('l')
_TYPE_TUPLE = ord('t')
_TYPE_DICT = ord('d')


class Packer:
    
    # Note that while xdrlib uses StringIO/BytesIO, this approach using
    # a list is actually faster.
    
    def __init__(self):
        self._buf = []
    
    def get_buffer(self):
        return bytes().join(self._buf)
    
    def write(self, bb):
        self._buf.append(bb)
    
    def write_number(self, n):
        if n < 255:
            self.write( struct.pack('<B', n) )
        else:
            self.write( struct.pack('<B', 255) )
            self.write( struct.pack('<Q', n) )
    
    def pack_object(self, object):
        
        if object is None:
            self.write( struct.pack(_FMT_TYPE, _TYPE_NONE) )
        elif isinstance(object, bool):
            self.write( struct.pack(_FMT_TYPE, _TYPE_BOOL) )
            self.write( struct.pack(_FMT_BOOL, object) )
        elif isinstance(object, (int, long)):
            self.write( struct.pack(_FMT_TYPE, _TYPE_INT) )
            self.write( struct.pack(_FMT_INT, object) )
        elif isinstance(object, float):
            self.write( struct.pack(_FMT_TYPE, _TYPE_FLOAT) )
            self.write( struct.pack(_FMT_FLOAT, object) )
        elif isinstance(object, basestring):
            bb = object.encode('utf-8')
            self.write( struct.pack(_FMT_TYPE, _TYPE_STRING) )
            self.write_number(len(bb))
            self.write( bb )
        elif isinstance(object, list):
            self.write( struct.pack(_FMT_TYPE, _TYPE_LIST) )
            self.write_number(len(object))
            for value in object:
                self.pack_object(value) # call recursive
        elif isinstance(object, tuple):
            self.write( struct.pack(_FMT_TYPE, _TYPE_TUPLE) )
            self.write_number(len(object))
            for value in object:
                self.pack_object(value) # call recursive
        elif isinstance(object, dict):
            self.write( struct.pack(_FMT_TYPE, _TYPE_DICT) )
            self.write_number(len(object))
            # call recursive
            for key in object:
                self.pack_object(key)
                self.pack_object(object[key])
        else:
            raise ValueError("Unsupported type: %s" % repr(type(object)))


class Unpacker:
    
    def __init__(self, data):
        self._buf = data
        self._pos = 0
    
    def read(self, n):
        i1 = self._pos
        i2 = self._pos + n
        if i2 > len(self._buf):
            raise EOFError
        else:
            self._pos = i2
            return self._buf[i1:i2]
    
    def read_number(self):
        n, = struct.unpack('<B', self.read(1))
        if n == 255:
            n, = struct.unpack('<Q', self.read(8))
        return n
    
    def unpack(self, fmt, n):
        i1 = self._pos
        i2 = self._pos + n
        if i2 > len(self._buf):
            raise EOFError
        else:
            self._pos = i2
            data = self._buf[i1:i2]
            return struct.unpack(fmt, data)[0]
    
    def unpack_object(self):
        
        object_type = self.unpack(_FMT_TYPE, 1)
        
        if object_type == _TYPE_NONE:
            return None
        elif object_type == _TYPE_BOOL:
            return bool( self.unpack(_FMT_BOOL, 1) )
        elif object_type == _TYPE_INT:
            return self.unpack(_FMT_INT, 8)
        elif object_type == _TYPE_FLOAT:
            return self.unpack(_FMT_FLOAT, 8)
        elif object_type == _TYPE_STRING:
            n = self.read_number()
            return self.read(n).decode('utf-8')
        elif object_type == _TYPE_LIST:
            object = []
            for i in range(self.read_number()):
                object.append( self.unpack_object() )
            return object
        elif object_type == _TYPE_TUPLE:
            object = []
            for i in range(self.read_number()):
                object.append( self.unpack_object() )
            return tuple(object)
        elif object_type == _TYPE_DICT:
            object = {}
            for i in range(self.read_number()):
                key = self.unpack_object()
                object[key] = self.unpack_object()
            return object
        else:
            raise ValueError("Unsupported type: %s" % repr(object_type))


# Define constants
TEXT = TextMessageType()
BINARY = BinaryMessageType()
OBJECT = ObjectMessageType()


if __name__ == '__main__':
    # Test
    
    s = {}
    s['foo'] = 3
    s['bar'] = 9
    s['empty'] = []
    s[(2,'aa',3)] = ['pretty', ('nice', 'eh'), 4]
    
    bb = OBJECT.message_to_bytes(s)
    s2 = OBJECT.message_from_bytes(bb)
    print(s)
    print(s2)
    
    
