#@+leo-ver=5-thin
#@+node:tbrown.20171028115541.1: * @file signal_manager.py
"""
signal_manager.py - SignalManager - light weight signal management

Extremely light weight.  No enforcement of signal arguments, or
even explicit listing of which signals exist.

Terry Brown, terrynbrown@gmail.com, Thu Mar 23 21:13:38 2017
"""
from collections import defaultdict
#@+others
#@+node:tbrown.20171028115601.2: ** class SignalData
class SignalData:
    
    def __init__(self):
        self.listeners = defaultdict(list)
        self.emitters = []
        self.locked = False
#@+node:tbrown.20171028115601.4: ** class MsgSignalHandled
class MsgSignalHandled:
    """A listener can return SignalManager.MsgSignalHandled to prevent
    other listeners from being called
    """
    pass

#@+node:tbrown.20171028115601.5: ** _setup
def _setup(obj):
    if not hasattr(obj, '_signal_data'):
        obj._signal_data = SignalData()

#@+node:tbrown.20171028115601.6: ** emit
def emit(source, signal_name, *args, **kwargs):
    """Emit signal to all listeners"""
    if not hasattr(source, '_signal_data'):
        return
    if '_sig_lock' in kwargs:
        obj_to_lock = kwargs.pop('_sig_lock')
        _setup(obj_to_lock)
        obj_to_lock._signal_data.locked = True
    else:
        obj_to_lock = None

    for listener in source._signal_data.listeners[signal_name]:
        try:
            if listener.__self__._signal_data.locked:
                continue
        except AttributeError:
            pass
        response = listener(*args, **kwargs)
        if response == MsgSignalHandled:
            break

    if obj_to_lock is not None:
        obj_to_lock._signal_data.locked = False

#@+node:tbrown.20171028115601.7: ** connect
def connect(source, signal_name, listener):
    """Connect to signal"""
    _setup(source)
    source._signal_data.listeners[signal_name].append(listener)

    if hasattr(listener, '__self__'):
        obj = listener.__self__
        _setup(obj)
        obj._signal_data.emitters.append(source)

#@+node:tbrown.20171028115601.8: ** disconnect_all
def disconnect_all(listener):
    """Disconnect from all signals"""
    for emitter in listener._signal_data.emitters:
        for signal in emitter._signal_data.listeners:
            emitter._signal_data.listeners[signal] = [
                i for i in emitter._signal_data.listeners[signal]
                if getattr(i, '__self__', None) != listener
            ]
#@+node:tbrown.20171028115601.9: ** is_locked
def is_locked(obj):
    return hasattr(obj, '_signal_data') and obj._signal_data.locked

#@+node:tbrown.20171028115601.10: ** lock
def lock(obj):
    _setup(obj)
    obj._signal_data.locked = True

#@+node:tbrown.20171028115601.11: ** unlock
def unlock(obj):
    _setup(obj)
    obj._signal_data.locked = False
#@+node:tbrown.20171028115601.12: ** class SignalManager
class SignalManager:
    """SignalManager - light weight signal management mixin."""

    #@+others
    #@+node:tbrown.20171028115601.13: *3* emit
    def emit(self, signal_name, *args, **kwargs):
        """Emit signal to all listeners"""
        emit(self, signal_name, *args, **kwargs)

    #@+node:tbrown.20171028115601.14: *3* connect
    def connect(self, signal_name, listener):
        """Connect to signal"""
        connect(self, signal_name, listener)


    #@-others
#@+node:tbrown.20171028115601.15: ** main
def main():
    """test of SignalManager"""

    # simple use

    class Emitter(SignalManager):
        def some_emission(self):
            self.emit('the_emission', 12, [1,2,3])

    def hear_emit(n, l):
        print(f"Got {n} {l}")

    emitter = Emitter()
    emitter.connect('the_emission', hear_emit)
    emitter.some_emission()

    # use with proxy and locking

    class Tester:
        def __init__(self, name, relay):
            self.name = name
            self.relay = relay
            connect(self.relay, 'work_done', self.check_work)
        def do_work(self):
            emit(self.relay, 'work_done', 4.2, animal='otters', _sig_lock=self)
        def check_work(self, num, animal='eels'):
            if is_locked(self):
                return
            print(f"{self.name} heard about {num} {animal}")

    class SomeProxy:
        """Like a public notice board"""
        pass

    relay = SomeProxy()
    a = Tester('A', relay)
    a.do_work()
    b = Tester('B', relay)
    a.do_work()
    b.do_work()

#@-others
if __name__ == '__main__':
    main()

#@@language python
#@@tabwidth -4
#@-leo
