# -*- coding: utf-8 -*-
# Copyright (C) 2013, the Pyzo development team
#
# Yoton is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module yoton.channels.channels_pubsub

Defines the channel classes for the pub/sub pattern.

"""

import time

from yoton.misc import bytes, xrange
from yoton.channels import BaseChannel

QUEUE_NULL = 0
QUEUE_OK = 1
QUEUE_FULL = 2


class PubChannel(BaseChannel):
    """ PubChannel(context, slot_base, message_type=yoton.TEXT)
    
    The publish part of the publish/subscribe messaging pattern.
    Sent messages are received by all yoton.SubChannel instances with
    the same slot.
    
    There are no limitations for this channel if events are not processed.
    
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
        Users can create their own message_type class to let channels
        any type of message they want.
    
    """
    
    def __init__(self, *args, **kwargs):
        BaseChannel.__init__(self, *args, **kwargs)
        self._source_set = set()
    
    
    def _messaging_patterns(self):
        return 'pub-sub', 'sub-pub'
    
    
    def send(self, message):
        """ send(message)
        
        Send a message over the channel. What is send as one
        message will also be received as one message.
        
        The message is queued and delivered to all corresponding
        SubChannels (i.e. with the same slot) in the network.
        
        """
        self._send( self.message_to_bytes(message) )
    
    
    def _recv_package(self, package):
        """ Overloaded to set blocking mode.
        Do not call _maybe_emit_received(), a PubChannel never emits
        the "received" signal.
        """
        
        message = package._data.decode('utf-8')
        source_id = package._source_id
        
        # Keep track of who's queues are full
        if message == 'full':
            self._source_set.add(source_id)
        else:
            self._source_set.discard(source_id)
        
        # Set lock if there is a channel with a full queue,
        # Unset if there are none
        if self._source_set:
            self._set_send_lock(True)
            #sys.stderr.write('setting lock\n')
        else:
            self._set_send_lock(False)
            #sys.stderr.write('unsetting lock\n')



class SubChannel(BaseChannel):
    """ SubChannel(context, slot_base, message_type=yoton.TEXT)
    
    The subscribe part of the publish/subscribe messaging pattern.
    Received messages were sent by a yoton.PubChannel instance at the
    same slot.
    
    This channel can be used as an iterator, which yields all pending
    messages. The function yoton.select_sub_channel can
    be used to synchronize multiple SubChannel instances.
    
    If no events being processed this channel works as normal, except
    that the received signal will not be emitted, and sync mode will
    not work.
    
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
        Users can create their own message_type class to let channels
        any type of message they want.
    
    """
    
    def __init__(self, *args, **kwargs):
        BaseChannel.__init__(self, *args, **kwargs)
        
        # To detect when to block the sending side
        self._queue_status = QUEUE_NULL
        self._queue_status_timeout = 0
        self._HWM = 32
        self._LWM = 16
        
        # Automatically check queue status when new data
        # enters the system
        self.received.bind(self._check_queue_status)
    
    
    def _messaging_patterns(self):
        return 'sub-pub', 'pub-sub'
    
    
    def __iter__(self):
        return self
    
    
    def __next__(self): # Python 3.x
        m = self.recv(False)
        if m:
            return m
        else:
            raise StopIteration()
    
    
    def next(self): # Python 2.x
        """ next()
        
        Return the next message, or raises StopIteration if non available.
        
        """
        return self.__next__()
    
    
    ## For sync mode
    
    def set_sync_mode(self, value):
        """ set_sync_mode(value)
        
        Set or unset the SubChannel in sync mode. When in sync mode, all
        channels that send messages to this channel are blocked if
        the queue for this SubChannel reaches a certain size.
        
        This feature can be used to limit the rate of senders if the consumer
        (i.e. the one that calls recv()) cannot keep up with processing
        the data.
        
        This feature requires the yoton event loop to run at the side
        of the SubChannel (not necessary for the yoton.PubChannel side).
        
        """
        value = bool(value)
        
        # First reset block status if necessary
        if self._queue_status == QUEUE_FULL:
            self._send_block_message_to_senders('ok')
        
        # Set new queue status flag
        if value:
            self._queue_status = QUEUE_OK
        else:
            self._queue_status = QUEUE_NULL
    
    
    def _send_block_message_to_senders(self, what):
        """ _send_block_message_to_senders(what)
        
        Send a message to the PubChannel side to make it block/unblock.
        
        """
        
        # Check
        if not self._context.connection_count:
            return
        
        # Send
        try:
            self._send(what.encode('utf-8'))
        except IOError:
            # If self._closed
            self._check_queue_status = QUEUE_NULL
    
    
    def _check_queue_status(self, dummy=None):
        """ _check_queue_status()
        
        Check the queue status. Returns immediately unless this receiving
        channel runs in sync mode.
        
        If the queue is above a certain size, will send out a package that
        will make the sending side block. If the queue is below a certain
        size, will send out a package that will make the sending side unblock.
        
        """
        
        if self._queue_status == QUEUE_NULL:
            return
        elif len(self._q_in) > self._HWM:
            if self._queue_status == QUEUE_OK:
                self._queue_status = QUEUE_FULL
                self._queue_status_timeout = time.time() + 4.0
                self._send_block_message_to_senders('full')
        elif len(self._q_in) < self._LWM:
            if self._queue_status == QUEUE_FULL:
                self._queue_status = QUEUE_OK
                self._queue_status_timeout = time.time() + 4.0
                self._send_block_message_to_senders('ok')
        
        # Resend every so often. After 10s the PubChannel will unlock itself
        if self._queue_status_timeout < time.time():
            self._queue_status_timeout = time.time() + 4.0
            if self._queue_status == QUEUE_OK:
                self._send_block_message_to_senders('ok')
            else:
                self._send_block_message_to_senders('full')
    
    
    ## Receive methods
    
    
    def recv(self, block=True):
        """ recv(block=True)
        
        Receive a message from the channel. What was send as one
        message is also received as one message.
        
        If block is False, returns empty message if no data is available.
        If block is True, waits forever until data is available.
        If block is an int or float, waits that many seconds.
        If the channel is closed, returns empty message.
        
        """
        
        # Check queue status, maybe we need to block the sender
        self._check_queue_status()
        
        # Get package
        package = self._recv(block)
        
        # Return message content or None
        if package is not None:
            return self.message_from_bytes(package._data)
        else:
            return self.message_from_bytes(bytes())
    
    
    def recv_all(self):
        """ recv_all()
        
        Receive a list of all pending messages. The list can be empty.
        
        """
        
        # Check queue status, maybe we need to block the sender
        self._check_queue_status()
        
        # Pop all messages and return as a list
        pop = self._q_in.pop
        packages = [pop() for i in xrange(len(self._q_in))]
        return [self.message_from_bytes(p._data) for p in packages]
    
    
    def recv_selected(self):
        """ recv_selected()
        
        Receive a list of messages. Use only after calling
        yoton.select_sub_channel with this channel as one of the arguments.
        
        The returned messages are all received before the first pending
        message in the other SUB-channels given to select_sub_channel.
        
        The combination of this method and the function select_sub_channel
        enables users to combine multiple SUB-channels in a way that
        preserves the original order of the messages.
        
        """
        
        # No need to check queue status, we've done that in the
        # _get_pending_sequence_numbers() method
        
        # Prepare
        q = self._q_in
        ref_seq = self._ref_seq
        popped = []
        
        # Pop all messages that have sequence number lower than reference
        try:
            for i in xrange(len(q)):
                part = q.pop()
                if part._recv_seq > ref_seq:
                    q.insert(part) # put back in queue
                    break
                else:
                    popped.append(part)
        except IndexError:
            pass
        
        # Done; return messages
        return [self.message_from_bytes(p._data) for p in popped]
    
    
    def _get_pending_sequence_numbers(self):
        """ _get_pending_sequence_numbers()
        
        Get the sequence numbers of the first and last pending messages.
        Returns (-1,-1) if no messages are pending.
        
        Used by select_sub_channel() to determine which channel should
        be read from first and what the reference sequence number is.
        
        """
        
        # Check queue status, maybe we need to block the sender
        self._check_queue_status()
        
        # Peek
        try:
            q = self._q_in
            return q.peek(0)._recv_seq, q.peek(-1)._recv_seq + 1
        except IndexError:
            return -1, -1



def select_sub_channel(*args):
    """ select_sub_channel(channel1, channel2, ...)
    
    Returns the channel that has the oldest pending message of all
    given yoton.SubCannel instances. Returns None if there are no pending
    messages.
    
    This function can be used to read from SubCannels instances in the
    order that the messages were send.
    
    After calling this function, use channel.recv_selected() to obtain
    all messages that are older than any pending messages in the other
    given channels.
    
    """
    
    # Init
    smallest_seq1 = 99999999999999999999999999
    smallest_seq2 = 99999999999999999999999999
    first_channel = None
    
    # For each channel ...
    for channel in args:
        
        # Check if channel is of right type
        if not isinstance(channel, SubChannel):
            raise ValueError('select_sub_channel() only accepts SUB channels.')
        
        # Get and check sequence
        seq1, seq2 = channel._get_pending_sequence_numbers()
        if seq1 >= 0:
            if seq1 < smallest_seq1:
                # Cannot go beyond number of packages in queue,
                # or than seq1 of earlier selected channel.
                smallest_seq2 = min(smallest_seq1, smallest_seq2, seq2)
                # Store
                smallest_seq1 = seq1
                first_channel = channel
            else:
                # The first_channel cannot go beyond the 1st package in THIS queue
                smallest_seq2 = min(smallest_seq2, seq1)
    
    # Set flag at channel and return
    if first_channel:
        first_channel._ref_seq = smallest_seq2
        return first_channel
    else:
        return None
