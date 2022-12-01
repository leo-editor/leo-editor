# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:tbrown.20171028115541.1: * @file signal_manager.py
#@@first
#@+<< signal_manager docstring >>
#@+node:ekr.20220901092728.1: ** << signal_manager docstring >>
"""
signal_manager.py - SignalManager - light weight signal management

Extremely light weight.  No enforcement of signal arguments, or
even explicit listing of which signals exist.

Terry Brown, terrynbrown@gmail.com, Thu Mar 23 21:13:38 2017
"""
#@-<< signal_manager docstring >>
#@+<< signal_manager imports >>
#@+node:ekr.20220901092745.1: ** << signal_manager imports >>
from collections import defaultdict
from typing import Any, Callable, Dict, List, TYPE_CHECKING
#@-<< signal_manager imports >>
#@+<< signal_manager annotations >>
#@+node:ekr.20220901092755.1: ** << signal_manager annotations >>
if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent as Event
    from leo.core.leoNodes import Position
else:
    Cmdr = Any
    Event = Any
    Position = Any
#@-<< signal_manager annotations >>
#@+others
#@+node:tbrown.20171028115601.2: ** class SignalData
class SignalData:

    def __init__(self) -> None:
        self.listeners: Dict[Any, Any] = defaultdict(list)
        self.emitters: List[Callable] = []
        self.locked = False
#@+node:tbrown.20171028115601.4: ** class MsgSignalHandled
class MsgSignalHandled:
    """A listener can return SignalManager.MsgSignalHandled to prevent
    other listeners from being called
    """
    pass
#@+node:tbrown.20171028115601.5: ** _setup
def _setup(obj: Any) -> None:
    if not hasattr(obj, '_signal_data'):
        obj._signal_data = SignalData()
#@+node:tbrown.20171028115601.6: ** emit
def emit(source: Any, signal_name: str, *args: Any, **kwargs: Any) -> None:
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
def connect(source: Any, signal_name: str, listener: Any) -> None:
    """Connect to signal"""
    _setup(source)
    source._signal_data.listeners[signal_name].append(listener)

    if hasattr(listener, '__self__'):
        obj = listener.__self__
        _setup(obj)
        obj._signal_data.emitters.append(source)
#@+node:tbrown.20171028115601.8: ** disconnect_all
def disconnect_all(listener: Any) -> None:
    """Disconnect from all signals"""
    for emitter in listener._signal_data.emitters:
        for signal in emitter._signal_data.listeners:
            emitter._signal_data.listeners[signal] = [
                i for i in emitter._signal_data.listeners[signal]
                if getattr(i, '__self__', None) != listener
            ]
#@+node:tbrown.20171028115601.9: ** is_locked
def is_locked(obj: Any) -> bool:
    return hasattr(obj, '_signal_data') and obj._signal_data.locked
#@+node:tbrown.20171028115601.10: ** lock
def lock(obj: Any) -> None:
    _setup(obj)
    obj._signal_data.locked = True
#@+node:tbrown.20171028115601.11: ** unlock
def unlock(obj: Any) -> None:
    _setup(obj)
    obj._signal_data.locked = False
#@+node:tbrown.20171028115601.12: ** class SignalManager
class SignalManager:
    """SignalManager - light weight signal management mixin."""
    #@+others
    #@+node:tbrown.20171028115601.13: *3* emit
    def emit(self, signal_name: str, *args: Any, **kwargs: Any) -> None:
        """Emit signal to all listeners"""
        emit(self, signal_name, *args, **kwargs)
    #@+node:tbrown.20171028115601.14: *3* connect
    def connect(self, signal_name: str, listener: Any) -> None:
        """Connect to signal"""
        connect(self, signal_name, listener)
    #@-others
#@+node:tbrown.20171028115601.15: ** main
def main() -> None:
    """test of SignalManager"""

    # simple use


    class Emitter(SignalManager):

        def some_emission(self) -> None:
            self.emit('the_emission', 12, [1, 2, 3])

    def hear_emit(n: int, obj: Any) -> None:
        print(f"Got {n} {obj}")

    emitter = Emitter()
    emitter.connect('the_emission', hear_emit)
    emitter.some_emission()

    # use with proxy and locking


    class Tester:

        def __init__(self, name: str, relay: Any) -> None:
            self.name = name
            self.relay = relay
            connect(self.relay, 'work_done', self.check_work)

        def do_work(self) -> None:
            emit(self.relay, 'work_done', 4.2, animal='otters', _sig_lock=self)

        def check_work(self, num: Any, animal: str='eels') -> None:
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
