"""
signal_manager.py - SignalManager - light weight signal management

Terry Brown, terrynbrown@gmail.com, Thu Mar 23 21:13:38 2017
"""

class SignalManager(object):
    """SignalManager - light weight signal management.
    
    Extremely light weight.  No enforcement of signal arguments, or
    even explicit listing of which signals exist.
    """

    class MsgSignalHandled:
        """A listener can return SignalManager.MsgSignalHandled to prevent
        other listeners from being called
        """
        pass

    @staticmethod
    def _signal_emit(source, signal_name, *args, **kwargs):
        """Emit signal to all listeners"""
        if not hasattr(source, '_signal_data'):
            return
        for listener in source._signal_data.listeners.get(signal_name, []):
            response = listener(*args, **kwargs)
            if response == SignalManager.MsgSignalHandled:
                break
                
    @staticmethod
    def _signal_connect(source, signal_name, listener):
        """Connect to signal"""
        if not hasattr(source, '_signal_data'):
            source._signal_data = type("SimpleNameSpace", tuple(), {})()
            source._signal_data.listeners = {}
        source._signal_data.listeners.setdefault(signal_name, []).append(listener)

    def signal_emit(self, signal_name, *args, **kwargs):
        """Emit signal to all listeners"""
        self._signal_emit(self, signal_name, *args, **kwargs)
    def signal_connect(self, signal_name, listener):
        """Connect to signal"""
        self._signal_connect(self, signal_name, listener)

def main():
    """trivial demo of SignalManager"""

    class DemoA(SignalManager):
        def increment(self):
            self.signal_emit('increment', 2, words='7')

    def note_inc(n, words):
        print("INCREMENT: %s(%s)" % (n, words))

    mixedin = DemoA()
    mixedin.signal_connect('increment', note_inc)
    mixedin.increment()
    
    # intended to be a mixin, but can be used without an instance
    some_obj = type("SimpleNameSpace", tuple(), {})()
    SignalManager._signal_connect(some_obj, 'aNewOne', note_inc)
    # presumably some_obj would call this on itself
    SignalManager._signal_emit(some_obj, 'aNewOne', -1, words='-1')

if __name__ == '__main__':
    main()
