#!/usr/bin/python
#coding=utf-8
#@+leo-ver=5-thin
#@+node:bob.20180206123613.1: * @file leo_babel/tests/idle_time.py
#@@first
#@@first
#@@language python
#@@tabwidth -4

#@+<< imports >>
#@+node:bob.20180206123613.2: ** << imports >>
import os
import time
# import traceback

import leo.core.leoGlobals as leoG
assert leoG
#@-<< imports >>
#@+<< version >>
#@+node:bob.20180206123613.3: ** << version >>
version = '1.0'
#@-<< version >>

#@+others
#@+node:bob.20180206123725.1: ** class IdleTime
class IdleTime:
    """ This is an implementation of the Leo-Editor
    class IdleTime() for use with Leo-Bridge.
    """
    #@+others
    #@+node:bob.20180206125732.1: *3* Class Parameters
    list_active = list()
    list_inactive = list()
    #@+node:bob.20180206123842.1: *3* __init__()
    def __init__(self, handler, delay=500, tag=None):
        """ Create an Idle Time Object Instance

        Arguments:
            handler: Function to execute when idle
            delay: Minimum time in milliseconds between
                calls to handler
            tag:  Identifier for the purpose of the handler

        Returns:
            None
        """

        self._handler = handler
        self._delay = delay / 1000.
        self._tag = tag
        self._active = False
        IdleTime.list_inactive.append(self)
        #traceStk = [lix.strip() for lix in traceback.format_stack()]
        #leoG.trace('Trace: {0}'.format(traceStk[-2]))
        #leoG.trace('IdleTime() {0}'.format(id(self)))
    #@+node:bob.20180206124140.1: *3* start()
    def start(self):
        """ Start an Idle Time Instance

        Arguments:
            self:  IdleTime instance

        Returns:
            None
        """

        #leoG.trace(id(self))
        IdleTime.list_inactive.remove(self)
        self._nexttime = time.process_time()
        IdleTime.list_active.insert(0, self)
        self._active = True
    #@+node:bob.20180206125022.1: *3* stop()
    def stop(self):
        """ Stop an Idle Time Instance

        Arguments:
            self:  IdleTime instance

        Returns:
            None
        """

        #leoG.trace(id(self))
        if self._active:
            IdleTime.list_active.remove(self)
            IdleTime.list_inactive.append(self)
            self._active = False
    #@+node:bob.20180206123934.1: *3* idle() Class method
    @classmethod
    def idle(cls):
        """ Application idle -- Except for Idle Time
        handler execution

        Arguments:
            cls:  The IdleTime class object

        Returns:
            None
        """

        #traceStk = [lix.strip() for lix in traceback.format_stack()]
        #leoG.trace('Trace: {0}'.format(traceStk[-2]))
        itoLast = 0
        while True:
            if not cls.list_active:
                break
            # pylint: disable=no-member
            os.sched_yield()
            timeCur = time.process_time()
            idleTimeObj = cls.list_active.pop(0)
            #leoG.trace('Popped {0} leaving {1}'.format(id(idleTimeObj), [id(ent) for ent in cls.list_active]))
            if timeCur >= idleTimeObj._nexttime:
                nexttime = timeCur + idleTimeObj._delay
                idleTimeObj._nexttime = nexttime
                for idx, idleTimeObj2 in enumerate(cls.list_active):
                    if nexttime < idleTimeObj2._nexttime:
                        #leoG.trace('Insert at {0}'.format(idx))
                        cls.list_active.insert(idx, idleTimeObj)
                        break
                else:
                    #leoG.trace('Append')
                    cls.list_active.append(idleTimeObj)
                if itoLast != idleTimeObj:
                    itoLast = idleTimeObj
                    #leoG.trace('Run {0} cls.list_active={1}'.format(id(idleTimeObj), [id(ent) for ent in cls.list_active]))
                idleTimeObj._handler(idleTimeObj)
                #leoG.trace('Handler return. cls.list_active={0}'.format([id(ent) for ent in cls.list_active]))
            else:
                # Nothing to run yet
                cls.list_active.insert(0, idleTimeObj)
        #leoG.trace('Exiting cls.list_active={0}'.format([id(ent) for ent in cls.list_active]))
    #@-others
#@+node:bob.20180206123613.16: ** main()
def main():
    """ Command Line Program Entry point
    """

    raise NotImplementedError('{0} is not a command line program.'.format(__file__))
#@-others

if __name__ == "__main__":
    main()
#@-leo
