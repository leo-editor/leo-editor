# -*- coding: utf-8 -*-
# Copyright (C) 2013, the Pyzo development team
#
# Yoton is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module yoton.channels.channels_base

Defines the base channel class and the MessageType class.

"""

import time
import threading

import yoton
from yoton.misc import basestring
from yoton.misc import slot_hash, PackageQueue
from yoton.core import Package
from yoton.context import Context
from yoton.channels.message_types import MessageType, TEXT


class BaseChannel(object):
    """ BaseChannel(context, slot_base, message_type=yoton.TEXT)
    
    Abstract class for all channels.
    
    Parameters
    ----------
    context : yoton.Context instance
        The context that this channel uses to send messages in a network.
    slot_base : string
        The base slot name. The channel appends an extension to indicate
        message type and messaging pattern to create the final slot name.
        The final slot is used to connect channels at different contexts
        in a network
    message_type : yoton.MessageType instance
        (default is yoton.TEXT)
        Object to convert messages to bytes and bytes to messages.
        Users can create their own message_type class to enable
        communicating any type of message they want.
    
    Details
    -------
    Messages send via a channel are delivered asynchronically to the
    corresponding channels.
    
    All channels are associated with a context and can be used to send
    messages to other channels in the network. Each channel is also
    associated with a slot, which is a string that represents a kind
    of address. A message send by a channel at slot X can only be received
    by a channel with slot X.
    
    Note that the channel appends an extension
    to the user-supplied slot name, that represents the message type
    and messaging pattern of the channel. In this way, it is prevented
    that for example a PubChannel can communicate with a RepChannel.
    
    """
    
    def __init__(self, context, slot_base, message_type=None):
        
        # Store context
        if not isinstance(context, Context):
            raise ValueError('Context not valid.')
        self._context = context
        
        # Check message type
        if message_type is None:
            message_type = TEXT
        if isinstance(message_type, type) and issubclass(message_type, MessageType):
            message_type = message_type()
        if isinstance(message_type, MessageType):
            message_type = message_type
        else:
            raise ValueError('message_type should be a MessageType instance.')
        
        # Store message type and conversion methods
        self._message_type_instance = message_type
        self.message_from_bytes = message_type.message_from_bytes
        self.message_to_bytes = message_type.message_to_bytes
        
        # Queue for incoming trafic (not used for pure sending channels)
        self._q_in = PackageQueue(*context._queue_params)
        
        # For sending channels: to lock the channel for sending
        self._send_condition = threading.Condition()
        self._is_send_locked = 0 # "True" is the timeout time
        
        # Signal for receiving data
        self._received_signal = yoton.events.Signal()
        self._posted_received_event = False
        
        # Channels can be closed
        self._closed = False
        
        # Event driven mode
        self._run_mode = 0
        
        # Init slots
        self._init_slots(slot_base)
    
    
    def _init_slots(self, slot_base):
        """ _init_slots(slot_base)
        
        Called from __init__ to initialize the slots and perform all checks.
        
        """
        
        # Check if slot is string
        if not isinstance(slot_base, basestring):
            raise ValueError('slot_base must be a string.')
        
        # Get full slot names, init byte versions
        slots_t = []
        slots_h = []
        
        # Get extension for message type and messaging pattern
        ext_type = self._message_type_instance.message_type_name()
        ext_patterns = self._messaging_patterns() # (incoming, outgoing)
        
        # Normalize and check slot names
        for ext_pattern in ext_patterns:
            if not ext_pattern:
                slots_t.append(None)
                slots_h.append(0)
                continue
            # Get full name
            slot = slot_base + '.' + ext_type + '.' + ext_pattern
            # Store text version
            slots_t.append(slot)
            # Strip and make lowercase
            slot = slot.strip().lower()
            # Hash
            slots_h.append(slot_hash(slot))
        
        # Store slots
        self._slot_out = slots_t[0]
        self._slot_in = slots_t[1]
        self._slot_out_h = slots_h[0]
        self._slot_in_h = slots_h[1]
        
        # Register slots (warn if neither slot is valid)
        if self._slot_out_h:
            self._context._register_sending_channel(self, self._slot_out_h, self._slot_out)
        if self._slot_in_h:
            self._context._register_receiving_channel(self, self._slot_in_h, self._slot_in)
        if not self._slot_out_h and not self._slot_in_h:
            raise ValueError('This channel does not have valid slots.')
    
    
    def _messaging_patterns(self):
        """ _messaging_patterns()
        
        Implement to return a string that specifies the pattern
        for sending and receiving, respecitively.
        
        """
        raise NotImplementedError()
    
    
    def close(self):
        """ close()
        
        Close the channel, i.e. unregisters this channel at the context.
        A closed channel cannot be reused.
        
        Future attempt to send() messages will result in an IOError
        being raised. Messages currently in the channel's queue can
        still be recv()'ed, but no new messages will be delivered at
        this channel.
        
        """
        # We keep a reference to the context, otherwise we need locks
        # The context clears the reference to this channel when unregistering.
        self._closed = True
        self._context._unregister_channel(self)
    
    
    def _send(self, message, dest_id=0, dest_seq=0):
        """ _send(message, dest_id=0, dest_seq=0)
        
        Sends a message of raw bytes without checking whether they're bytes.
        Optionally, dest_id and dest_seq represent the message that
        this message  replies to. These are used for the request/reply
        pattern.
        
        Returns the package that will be send (or None). The context
        will set _source_id on the package right before
        sending it away.
        
        """
        
        # Check if still open
        if self._closed:
            className = self.__class__.__name__
            raise IOError("Cannot send from closed %s %i." % (className, id(self)))
        
        
        if message:
            # If send_locked, wait at most one second
            if self._is_send_locked:
                self._send_condition.acquire()
                try:
                    self._send_condition.wait(1.0) # wait for notify
                finally:
                    self._send_condition.release()
                    if time.time() > self._is_send_locked:
                        self._is_send_locked = 0
            # Push it on the queue as a package
            slot = self._slot_out_h
            cid = self._context._id
            p = Package(message, slot, cid, 0, dest_id, dest_seq, 0)
            self._context._send_package(p)
            # Return package
            return p
        else:
            return None
    
    
    def _recv(self, block):
        """ _recv(block)
        
        Receive a package (or None).
        
        """
    
        if block is True:
            # Block for 0.25 seconds so that KeyboardInterrupt works
            while not self._closed:
                try:
                    return self._q_in.pop(0.25)
                except self._q_in.Empty:
                    continue
        
        else:
            # Block normal
            try:
                return self._q_in.pop(block)
            except self._q_in.Empty:
                return None
    
    
    def _set_send_lock(self, value):
        """ _set_send_lock(self, value)
        
        Set or unset the blocking for the _send() method.
        
        """
        # Set send lock variable. We adopt a timeout (10s) just in case
        # the SubChannel that locks the PubChannel gets disconnected and
        # is unable to unlock it.
        if value:
            self._is_send_locked = time.time() + 10.0
        else:
            self._is_send_locked = 0
        # Notify any threads that are waiting in _send()
        if not value:
            self._send_condition.acquire()
            try:
                self._send_condition.notifyAll()
            finally:
                self._send_condition.release()
    
    
    ## How packages are inserted in this channel for receiving
    
    
    def _inject_package(self, package):
        """ _inject_package(package)
        
        Same as _recv_package, but by definition do not block.
        _recv_package is overloaded in SubChannel. _inject_package is not.
        
        """
        self._q_in.push(package)
        self._maybe_emit_received()
    
    
    def _recv_package(self, package):
        """ _recv_package(package)
        
        Put package in the queue.
        
        """
        self._q_in.push(package)
        self._maybe_emit_received()
    
    
    def _maybe_emit_received(self):
        """ _maybe_emit_received()
        
        We want to emit a signal, but in such a way that multiple
        arriving packages result in a single emit. This methods
        only posts an event if it has not been done, or if the previous
        event has been handled.
        
        """
        if not self._posted_received_event:
            self._posted_received_event = True
            event = yoton.events.Event(self._emit_received)
            yoton.app.post_event(event)
    
    
    def _emit_received(self):
        """ _emit_received()
        
        Emits the "received" signal. This method is called once new data
        has been received. However, multiple arrived messages may
        result in a single call to this method. There is also no
        guarantee that recv() has not been called in the mean time.
        
        Also sets the variabele so that a new event for this may be
        created. This method is called from the event loop.
        
        """
        self._posted_received_event = False # Reset
        self.received.emit_now(self)
    
    
    # Received property sits on the BaseChannel because is is used by almost
    # all channels. Note that PubChannels never emit this signal as they
    # catch status messages from the SubChannel by overloading _recv_package().
    @property
    def received(self):
        """ Signal that is emitted when new data is received. Multiple
        arrived messages may result in a single call to this method.
        There is no guarantee that recv() has not been called in the
        mean time. The signal is emitted with the channel instance
        as argument.
        """
        return self._received_signal
    
    
    ## Properties
    
    
    @property
    def pending(self):
        """ Get the number of pending incoming messages.
        """
        return len(self._q_in)
    
    
    @property
    def closed(self):
        """ Get whether the channel is closed.
        """
        return self._closed
    
    
    @property
    def slot_outgoing(self):
        """ Get the outgoing slot name.
        """
        return self._slot_out
    
    
    @property
    def slot_incoming(self):
        """ Get the incoming slot name.
        """
        return self._slot_in
