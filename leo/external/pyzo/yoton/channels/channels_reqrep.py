# -*- coding: utf-8 -*-
# Copyright (C) 2013, the Pyzo development team
#
# Yoton is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module yoton.channels.channels_reqprep

Defines the channel classes for the req/rep pattern.

"""

import time
import threading

import yoton
from yoton.misc import basestring, bytes
from yoton.misc import getErrorMsg
from yoton.channels import BaseChannel, OBJECT


# For the req/rep channels to negotiate (simple load balancing)
REQREP_SEQ_REF = 2**63

# Define object to recognize errors
ERROR_OBJECT = 'yoton_ERROR_HANDLING_REQUEST'


# Define exceoptions
class TimeoutError(Exception):
    pass
class CancelledError(Exception):
    pass
# # Try loading the exceptions from the concurrency framework
# # (or maybe not; it makes yoton less lightweight)
# try:
#     from concurrent.futures import TimeoutError, CancelledError
# except ImportError:
#     pass



class Future(object):
    """ Future(req_channel, req, request_id)
    
    The Future object represents the future result of a request done at
    a yoton.ReqChannel.
    
    It enables:
      * checking whether the request is done.
      * getting the result or the exception raised during handling the request.
      * canceling the request (if it is not yet running)
      * registering callbacks to handle the result when it is available
    
    """
    
    def __init__(self, req_channel, req, request_id):
        
        # For being a Future object
        self._result = None
        self._status = 0 # 0:waiting, 1:running, 2:canceled, 3:error, 4:success
        self._callbacks = []
        
        # For handling req/rep
        self._req_channel = req_channel
        self._req = req
        self._request_id = request_id
        self._rep = bytes()
        self._replier = 0
        
        # For resending
        self._first_send_time = time.time()
        self._next_send_time = self._first_send_time + 0.5
        self._auto_cancel_timeout = 10.0
    
    
    def _send(self, msg):
        """ _send(msg)
        
        For sending pre-request messages 'req?', 'req-'.
        
        """
        msg = msg.encode('utf-8')
        try:
            self._req_channel._send(msg, 0, self._request_id+REQREP_SEQ_REF)
        except IOError:
            # if self._closed, will call _send again, and catch IOerror,
            # which will result in one more call to cancel().
            self.cancel()
    
    
    def _resend_if_necessary(self):
        """ _resend_if_necessary()
        
        Resends the pre-request message if we have not done so for the last
        0.5 second.
        
        This will also auto-cancel the message if it is resend over 20 times.
        
        """
        timetime = time.time()
        if self._status != 0:
            pass
        elif timetime > self._first_send_time + self._auto_cancel_timeout:
            self.cancel()
        elif timetime > self._next_send_time:
            self._send('req?')
            self._next_send_time = timetime + 0.5
    
    
    def set_auto_cancel_timeout(self, timeout):
        """ set_auto_cancel_timeout(timeout):
        
        Set the timeout after which the call is automatically cancelled
        if it is not done yet. By default, this value is 10 seconds.
        
        If timeout is None, there is no limit to the wait time.
        
        """
        if timeout is None:
            timeout = 999999999999999999.0
        if timeout > 0:
            self._auto_cancel_timeout = float(timeout)
        else:
            raise ValueError('A timeout cannot be negative')
    
    
    def cancel(self):
        """ cancel()
        
        Attempt to cancel the call. If the call is currently being executed
        and cannot be cancelled then the method will return False, otherwise
        the call will be cancelled and the method will return True.
        
        """
        
        if self._status == 1:
            # Running, cannot cancel
            return False
        elif self._status == 0:
            # Cancel now
            self._status = 2
            self._send('req-')
            for fn in self._callbacks:
                yoton.call_later(fn, 0, self)
            return True
        else:
            # Already done or canceled
            return True
    
    
    def cancelled(self):
        """ cancelled()
        
        Return True if the call was successfully cancelled.
        
        """
        return self._status == 2
    
    
    def running(self):
        """ running()
        
        Return True if the call is currently being executed and cannot be
        cancelled.
        
        """
        return self._status == 1
    
    
    def done(self):
        """ done()
        
        Return True if the call was successfully cancelled or finished running.
        
        """
        return self._status in [2,3,4]
    
    
    def _wait(self, timeout):
        """ _wait(timeout)
        
        Wait for the request to be handled for the specified amount of time.
        While waiting, the ReqChannel local event loop is called so that
        pre-request messages can be exchanged.
        
        """
        
        # No timout means a veeeery long timeout
        if timeout is None:
            timeout = 999999999999999999.0
        
        # Receive packages untill we receive the one we want,
        # or untill time runs out
        timestamp = time.time() + timeout
        while (self._status < 2) and (time.time() < timestamp):
            self._req_channel._process_events_local()
            time.sleep(0.01) # 10 ms
    
    
    def result(self, timeout=None):
        """ result(timeout=None)
        
        Return the value returned by the call. If the call hasn’t yet
        completed then this method will wait up to timeout seconds. If
        the call hasn’t completed in timeout seconds, then a TimeoutError
        will be raised. timeout can be an int or float. If timeout is not
        specified or None, there is no limit to the wait time.

        If the future is cancelled before completing then CancelledError
        will be raised.

        If the call raised, this method will raise the same exception.

        """
        
        # Wait
        self._wait(timeout)
        
        # Return or raise error
        if self._status < 2 :
            raise TimeoutError('Result unavailable within the specified time.')
        elif self._status == 2:
            raise CancelledError('Result unavailable because request was cancelled.')
        elif self._status == 3:
            raise self._result
        else:
            return self._result
    
    
    def result_or_cancel(self, timeout=1.0):
        """ result_or_cancel(timeout=1.0)
        
        Return the value returned by the call. If the call hasn’t yet
        completed then this method will wait up to timeout seconds. If
        the call hasn’t completed in timeout seconds, then the call is
        cancelled and the method will return None.
        
        """
        
        # Wait
        self._wait(timeout)
        
        # Return
        if self._status == 4:
            return self._result
        else:
            self.cancel()
            return None
    
    
    def exception(self, timeout=None):
        """ exception(timeout)
        
        Return the exception raised by the call. If the call hasn’t yet
        completed then this method will wait up to timeout seconds. If
        the call hasn’t completed in timeout seconds, then a TimeoutError
        will be raised. timeout can be an int or float. If timeout is not
        specified or None, there is no limit to the wait time.
        
        If the future is cancelled before completing then CancelledError
        will be raised.
        
        If the call completed without raising, None is returned.
        
        """
        
        # Wait
        self._wait(timeout)
        
        # Return or raise error
        if self._status < 2 :
            raise TimeoutError('Exception unavailable within the specified time.')
        elif self._status == 2:
            raise CancelledError('Exception unavailable because request was cancelled.')
        elif self._status == 3:
            return self._result
        else:
            return None # no exception
    
    
    def add_done_callback(self, fn):
        """ add_done_callback(fn)
        
        Attaches the callable fn to the future. fn will be called, with
        the future as its only argument, when the future is cancelled or
        finishes running.
        
        Added callables are called in the order that they were added. If
        the callable raises a Exception subclass, it will be logged and
        ignored. If the callable raises a BaseException subclass, the
        behavior is undefined.
        
        If the future has already completed or been cancelled, fn will be
        called immediately.
        
        """
        
        # Check
        if not hasattr(fn, '__call__'):
            raise ValueError('add_done_callback expects a callable.')
        
        # Add
        if self.done():
            yoton.call_later(fn, 0, self)
        else:
            self._callbacks.append(fn)
    
    
    def set_running_or_notify_cancel(self):
        """ set_running_or_notify_cancel()
        
        This method should only be called by Executor implementations before
        executing the work associated with the Future and by unit tests.
        
        If the method returns False then the Future was cancelled, i.e.
        Future.cancel() was called and returned True.
        
        If the method returns True then the Future was not cancelled and
        has been put in the running state, i.e. calls to Future.running()
        will return True.
        
        This method can only be called once and cannot be called after
        Future.set_result() or Future.set_exception() have been called.
        
        """
        
        if self._status == 2:
            return False
        elif self._status == 0:
            self._status = 1
            return True
        else:
            raise RuntimeError('set_running_or_notify_cancel should be called when in a clear state.')
    
    
    def set_result(self, result):
        """ set_result(result)
        
        Sets the result of the work associated with the Future to result.
        This method should only be used by Executor implementations and
        unit tests.
        
        """
        
        # Set result if indeed in running state
        if self._status == 1:
            self._result = result
            self._status = 4
            for fn in self._callbacks:
                yoton.call_later(fn, 0, self)
    
    
    def set_exception(self, exception):
        """ set_exception(exception)
        
        Sets the result of the work associated with the Future to the
        Exception exception. This method should only be used by Executor
        implementations and unit tests.
        
        """
        
        # Check
        if isinstance(exception, basestring):
            exception = Exception(exception)
        if not isinstance(exception, Exception):
            raise ValueError('exception must be an Exception instance.')
        
        # Set result if indeed in running state
        if self._status == 1:
            self._result = exception
            self._status = 3
            for fn in self._callbacks:
                yoton.call_later(fn, 0, self)


class ReqChannel(BaseChannel):
    """ ReqChannel(context, slot_base)
    
    The request part of the request/reply messaging pattern.
    A ReqChannel instance sends request and receive the corresponding
    replies. The requests are replied by a yoton.RepChannel instance.
    
    This class adopts req/rep in a remote procedure call (RPC) scheme.
    The handling of the result is done using a yoton.Future object, which
    follows the approach specified in PEP 3148. Note that for the use
    of callbacks, the yoton event loop must run.
    
    Basic load balancing is performed by first asking all potential
    repliers whether they can handle a request. The actual request
    is then send to the first replier to respond.
    
    Parameters
    ----------
    context : yoton.Context instance
        The context that this channel uses to send messages in a network.
    slot_base : string
        The base slot name. The channel appends an extension to indicate
        message type and messaging pattern to create the final slot name.
        The final slot is used to connect channels at different contexts
        in a network
    
    Usage
    -----
    One performs a call on a virtual method of this object. The actual
    method is executed by the yoton.RepChannel instance. The method can be
    called with normal and keyword arguments, which can be (a
    combination of): None, bool, int, float, string, list, tuple, dict.
    
    Example
    -------
    # Fast, but process is idling when waiting for the response.
    reply = req.add(3,4).result(2.0) # Wait two seconds
    
    # Asynchronous processing, but no waiting.
    def reply_handler(future):
        ... # Handle reply
    future = req.add(3,4)
    future.add_done_callback(reply_handler)
    
    """
    
    # Notes on load balancing:
    #
    # Firstly, each request has an id. Which is an integer number
    # which is increased at each new request. The id is send via
    # the dest_seq. For pre-request messages an offset is added
    # to recognize these meta-messages.
    #
    # We use an approach I call pre-request. The req channel sends
    # a pre-request to all repliers (on the same slot) asking whether
    # they want to handle a request. The content is 'req?' and the
    # dest_seq is the request-id + offset.
    #
    # The repliers collects and queues all pre-requests. It will then
    # send a reply to acknowledge the first received pre-request. The
    # content is 'req!' and dest_seq is again request-id + offset.
    #
    # The replier is now in a state of waiting for the actual request.
    # It will not acknowledge pre-requests, but keeps queing them.
    #
    # Upon receiving the acknowledge, the requester sends (directed
    # at only the first replier to acknowledge) the real request.
    # The content is the real request and dest_seq is the request-id.
    # Right after this, a pre-request cancel message is sent to all
    # repliers. The content is 'req-' and dest_seq is request-id + offset.
    #
    # When a replier receives a pre-request cancel message, it will
    # remove the pre-request from the list. If this cancels the
    # request it was currently waiting for, the replier will go back
    # to its default state, and acknowledge the first next pre-request
    # in the queue.
    #
    # When the replier answers a request, it will go back to its default
    # state, and acknowledge the first next pre-request in the queue.
    # The replier tries to answer as quickly to pre-requests as possible.
    #
    # On the request channel, a dictionary of request items is maintained.
    # Each item has an attribute specifying whether a replier has
    # acknowledged it (and which one).
    
    
    def __init__(self, context, slot_base):
        BaseChannel.__init__(self, context, slot_base, OBJECT)
        
        # Queue with pending requests
        self._request_items = {}
        
        # Timeout
        self._next_recheck_time = time.time() + 0.2
        
        # Counter
        self._request_counter = 0
        
        # The req channel is always in event driven mode
        self._run_mode = 1
        
        # Bind signals to process the events for this channel
        # Bind to "received" signal for quick response and a timer
        # so we can resend requests if we do not receive anything.
        self.received.bind(self._process_events_local)
        self._timer = yoton.events.Timer(0.5, False)
        self._timer.bind(self._process_events_local)
        self._timer.start()
    
    
    def _messaging_patterns(self):
        return 'req-rep', 'rep-req'
    
   
    def __getattr__(self, name):
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            def proxy_function(*args, **kwargs):
                return self._handle_request(name, *args, **kwargs)
            return proxy_function
    
    
    def _handle_request(self, name, *args, **kwargs):
        """ _handle_request(request, callback, **kwargs)
        
        Post a request. This creates a Future instance and stores
        it. A message is send asking any repliers to respond.
        
        The actual request will be send when a reply to our pre-request
        is received. This all hapens in the yoton event loop.
        
        """
        
        # Create request object
        request = name, args, kwargs
        
        # Check and convert request message
        bb = self.message_to_bytes(request)
        
        # Get new request id
        request_id = self._request_counter = self._request_counter + 1
        
        # Create new item for this request and store under the request id
        item = Future(self, bb, request_id)
        self._request_items[request_id] = item
        
        # Send pre-request (ask repliers who want to reply to a request)
        item._send('req?')
        
        # Return the Future instance
        return item
    
    
    def _resend_requests(self):
        """ _resend_requests()
        
        See if we should resend our older requests. Periodically calling
        this method enables doing a request while the replier is not yet
        attached to the network.
        
        This also allows the Future objects to cancel themselves if it
        takes too long.
        
        """
        for request_id in [key for key in self._request_items.keys()]:
            item = self._request_items[request_id]
            # Remove items that are really old
            if item.cancelled():
                self._request_items.pop(request_id)
            else:
                item._resend_if_necessary()
    
    
    def _recv_item(self):
        """ _recv_item()
        
        Receive item. If a reply is send that is an acknowledgement
        of a replier that it wants to handle our request, the
        correpsonding request is send to that replier.
        
        This is a kind of mini-event loop thingy that should be
        called periodically to keep things going.
        
        """
        
        # Receive package
        package = self._recv(False)
        if not package:
            return
        
        # Get the package reply id and sequence number
        dest_id = package._dest_id
        request_id = package._dest_seq
        
        # Check dest_id
        if not dest_id:
            return # We only want messages that are directed directly at us
        elif dest_id != self._context._id:
            return # This should not happen; context should make sure
        
        if request_id > REQREP_SEQ_REF:
            # We received a reply to us asking who can handle the request.
            # Get item, send actual request. We set the replier to indicate
            # that this request is being handled, and we can any further
            # acknowledgements from other repliers.
            request_id -= REQREP_SEQ_REF
            item = self._request_items.get(request_id, None)
            
            if item and not item._replier:
                # Status now changes to "running" canceling is not possible
                ok = item.set_running_or_notify_cancel()
                if not ok:
                    return
                
                # Send actual request to specific replier
                try:
                    self._send(item._req, package._source_id, request_id)
                except IOError:
                    pass # Channel closed, will auto-cancel at item._send()
                item._replier = package._source_id # mark as being processed
                
                # Send pre-request-cancel message to everyone
                item._send('req-')
        
        elif request_id > 0:
            # We received a reply to an actual request
            
            # Get item, remove from queue, set reply, return
            item = self._request_items.pop(request_id, None)
            if item:
                item._rep = package._data
                return item
    
    
    def _process_events_local(self, dummy=None):
        """ _process_events_local()
        
        Process events only for this object. Used by _handle_now().
        
        """
        
        # Check periodically if we should resend (or clean up) old requests
        if time.time() > self._next_recheck_time:
            self._resend_requests()
            self._next_recheck_time = time.time() + 0.1
        
        # Process all received messages
        while self.pending:
            item = self._recv_item()
            if item:
                reply = self.message_from_bytes(item._rep)
                if isinstance(reply, tuple) and len(reply)==2 and reply[0]==ERROR_OBJECT:
                    item.set_exception(reply[1])
                else:
                    item.set_result(reply)



class RepChannel(BaseChannel):
    """ RepChannel(context, slot_base)
    
    The reply part of the request/reply messaging pattern.
    A RepChannel instance receives request and sends the corresponding
    replies. The requests are send from a yoton.ReqChannel instance.
    
    This class adopts req/rep in a remote procedure call (RPC) scheme.
    
    To use a RepChannel, subclass this class and implement the methods
    that need to be available. The reply should be (a combination of)
    None, bool, int, float, string, list, tuple, dict.
    
    This channel needs to be set to event or thread mode to function
    (in the first case yoton events need to be processed too).
    To stop handling events again, use set_mode('off').
    
    Parameters
    ----------
    context : yoton.Context instance
        The context that this channel uses to send messages in a network.
    slot_base : string
        The base slot name. The channel appends an extension to indicate
        message type and messaging pattern to create the final slot name.
        The final slot is used to connect channels at different contexts
        in a network
    
    """
    
    def __init__(self, context, slot_base):
        BaseChannel.__init__(self, context, slot_base, OBJECT)
        
        # Pending pre-requests
        self._pre_requests = []
        
        # Current pre-request and time that it was acknowledged
        self._pre_request = None
        self._pre_request_time = 0
        
        # Create thread
        self._thread = ThreadForReqChannel(self)
        
        # Create timer (do not start)
        self._timer = yoton.events.Timer(2.0, False)
        self._timer.bind(self._process_events_local)
        
        # By default, the replier is off
        self._run_mode = 0
    
    
    def _messaging_patterns(self):
        return 'rep-req', 'req-rep'
    
    
    # Node that setters for normal and event_driven mode are specified in
    # channels_base.py
    def set_mode(self, mode):
        """ set_mode(mode)
        
        Set the replier to its operating mode, or turn it off.
        
        Modes:
          * 0 or 'off': do not process requests
          * 1 or 'event': use the yoton event loop to process requests
          * 2 or 'thread': process requests in a separate thread
        
        """
        
        if isinstance(mode, basestring):
            mode = mode.lower()
        
        if mode in [0, 'off']:
            self._run_mode = 0
        elif mode in [1, 'event', 'event-driven']:
            self._run_mode = 1
            self.received.bind(self._process_events_local)
            self._timer.start()
        elif mode in [2, 'thread', 'thread-driven']:
            self._run_mode = 2
            if not self._thread.isAlive():
                self._thread.start()
        else:
            raise ValueError('Invalid mode for ReqChannel instance.')
    
    
    def _handle_request(self, message):
        """ _handle_request(message)
        
        This method is called for each request, and should return
        a reply. The message contains the name of the method to call,
        this function calls that method.
        
        """
        # Get name and args
        name, args, kwargs = message
        
        # Get function
        if not hasattr(self, name):
            raise RuntimeError("Method '%s' not implemented." % name)
        else:
            func = getattr(self, name)
        
        # Call
        return func(*args, **kwargs)
    
    
    def _acknowledge_next_pre_request(self):
        
        # Cancel current pre-request ourselves if it takes too long.
        # Failsafe, only for if resetting by requester fails somehow.
        if time.time() - self._pre_request_time > 10.0:
            self._pre_request = None
        
        # Send any pending pre requests
        if self._pre_requests and not self._pre_request:

            # Set current pre-request and its ack time
            package = self._pre_requests.pop(0)
            self._pre_request = package
            self._pre_request_time = time.time()
            
            # Send acknowledgement
            msg = 'req!'.encode('utf-8')
            try:
                self._send(msg, package._source_id, package._dest_seq)
            except IOError:
                pass # Channel closed, nothing we can do about that
            #
            #print 'ack', self._context.id,  package._dest_seq-REQREP_SEQ_REF
    
    
    def _replier_iteration(self, package):
        """ _replier_iteration()
        
        Do one iteration: process one request.
        
        """
        
        # Get request id
        request_id = package._dest_seq
        
        if request_id > REQREP_SEQ_REF:
            # Pre-request stuff
            
            # Remove offset
            request_id -= REQREP_SEQ_REF
            
            # Get action and pre request id
            action = package._data.decode('utf-8')
            
            # Remove pre-request from pending requests in case of both actions:
            # Cancel pending pre-request, prevent stacking of the same request.
            for prereq in [prereq for prereq in self._pre_requests]:
                if (    package._source_id == prereq._source_id and
                        package._dest_seq == prereq._dest_seq):
                    self._pre_requests.remove(prereq)
            
            if action == 'req-':
                # Cancel current pre-request
                if (    self._pre_request and
                        package._source_id == self._pre_request._source_id and
                        package._dest_seq == self._pre_request._dest_seq):
                    self._pre_request = None
            
            elif action == 'req?':
                # New pre-request
                self._pre_requests.append(package)
        
        else:
            # We are asked to handle an actual request
            
            # We can reset the state
            self._pre_request = None
            
            # Get request
            request = self.message_from_bytes(package._data)
            
            # Get reply
            try:
                reply = self._handle_request(request)
            except Exception:
                reply = ERROR_OBJECT, getErrorMsg()
                print('yoton.RepChannel: error handling request:')
                print(reply[1])
            
            # Send reply
            if True:
                try:
                    bb = self.message_to_bytes(reply)
                    self._send(bb, package._source_id, request_id)
                except IOError:
                    pass # Channel is closed
                except Exception:
                    # Probably wrong type of reply returned by handle_request()
                    print('Warning: request could not be send:')
                    print(getErrorMsg())
    
    
    def _process_events_local(self, dummy=None):
        """ _process_events_local()
        
        Called when a message (or more) has been received.
        
        """
        
        # If closed, unregister from signal and stop the timer
        if self.closed or self._run_mode!=1:
            self.received.unbind(self._process_events_local)
            self._timer.stop()
        
        # Iterate while we receive data
        while True:
            package = self._recv(False)
            if package:
                self._replier_iteration(package)
                self._acknowledge_next_pre_request()
            else:
                # We always enter this the last time
                self._acknowledge_next_pre_request()
                return
    
    
    def echo(self, arg1, sleep=0.0):
        """ echo(arg1, sleep=0.0)
        
        Default procedure that can be used for testing. It returns
        a tuple (first_arg, context_id)
        
        """
        time.sleep(sleep)
        return arg1, hex(self._context.id)



class ThreadForReqChannel(threading.Thread):
    """ ThreadForReqChannel(channel)
    
    Thread to run a RepChannel in threaded mode.
    
    """
    
    def __init__(self, channel):
        threading.Thread.__init__(self)
        
        # Check channel
        if not isinstance(channel, RepChannel):
            raise ValueError('The given channel must be a REP channel.')
        
        # Store channel
        self._channel = channel
        
        # Make deamon
        self.setDaemon(True)
    
    
    def run(self):
        """ run()
        
        The handler's main loop.
        
        """
        
        # Get ref to channel. Remove ref from instance
        channel = self._channel
        del self._channel
        
        while True:
            
            # Stop?
            if channel.closed or channel._run_mode!=2:
                break

            # Wait for data (blocking, look Rob, without spinlocks :)
            package = channel._recv(2.0)
            if package:
                channel._replier_iteration(package)
                channel._acknowledge_next_pre_request()
            else:
                channel._acknowledge_next_pre_request()
