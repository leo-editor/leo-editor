# -*- coding: utf-8 -*-
# Copyright (C) 2013 Almar Klein

"""
This module defines file system proxies to be used for the file browser.
For now, there is only one: the native file system. But in time,
we may add proxies for ftp, S3, remote computing, etc.

This may seem like an awkward way to use the file system, but (with
small modifications) this approach can probably be used also for
opening/saving files to any file system that we implement here. This
will make Pyzo truly powerful for use in remote computing.

"""

import time
import threading
from queue import Queue, Empty
import os.path as op

from . import QtCore
from .utils import isdir

class Task:
    """ Task(**params)
    
    A task object. Accepts params as keyword arguments.
    When overloading, dont forget to set __slots__.
    
    Overload and implement the 'process' method to create a task.
    Then use pushTask on a pathProxy object. Use the 'result' method to
    obtain the result (or raise an error).
    """
    __slots__ = ['_params', '_result', '_error']
    
    def __init__(self, **params):
        if not params:
            params = None
        self._params = params
        self._result = None
        self._error = None
    
    def process(self, proxy, **params):
        """ process(pathProxy, **params):
        This is the method that represents the task. Overload this to make
        the task do what is intended.
        """
        pass
    
    def _run(self, proxy):
        """ Run the task. Don't overload or use this.
        """
        try:
            params = self._params or {}
            self._result = self.process(proxy, **params)
        except Exception as err:
            self._error = 'Task failed: {}:\n{}'.format(self, str(err))
            print(self._error)
    
    def result(self):
        """ Get the result. Raises an error if the task failed.
        """
        if self._error:
            raise Exception(self._error)
        else:
            return self._result


## Proxy classes for directories and files


class PathProxy(QtCore.QObject):
    """ Proxy base class for DirProxy and FileProxy.
    
    A proxy object is used to get information on a path (folder
    contents, or file modification time), and keep being updated about
    changes in that information.
    
    One uses an object by connecting to the 'changed' or 'deleted' signal.
    Use setActive(True) to receive updates on these signals. If the proxy
    is no longer needed, use close() to unregister it.
    
    """
    
    changed = QtCore.Signal()
    deleted = QtCore.Signal()
    errored = QtCore.Signal(str) # Or should we pass an error per 'action'?
    
    taskFinished = QtCore.Signal(Task)
    
    def __init__(self, fsProxy, path):
        QtCore.QObject.__init__(self)
        self._lock = threading.RLock()
        self._fsProxy = fsProxy
        self._path = path
        self._cancelled = False
        # For tasks
        self._pendingTasks = []
        self._finishedTasks = []
    
    def __repr__(self):
        return '<{} "{}">'.format(self.__class__.__name__, self._path)
    
    def path(self):
        """ Get the path of this proxy.
        """
        return self._path
    
    def track(self):
        """ Start tracking this proxy object in the idle time of the
        FSProxy thread.
        """
        self._fsProxy._track(self)
    
    def push(self):
        """ Process this proxy object asap; the object is put in the queue
        of the FSProxy, so it is updated as fast as possible.
        """
        self._cancelled = False
        self._fsProxy._push(self)
    
    def cancel(self):
        """ Stop tracking this proxy object. Cancel processing if this
        object was in the queue.
        """
        self._fsProxy._unTrack(self)
        self._cancelled = True
    
    def pushTask(self, task):
        """ pushTask(task)
        Give a task to the proxy to be executed in the FSProxy
        thread. The taskFinished signal will be emitted with the given
        task when it is done.
        """
        shouldPush = False
        with self._lock:
            if not self._pendingTasks:
                shouldPush = True
            self._pendingTasks.append(task)
        if shouldPush:
            self.push()
    
    def _processTasks(self):
        # Get pending tasks
        with self._lock:
            pendingTasks = self._pendingTasks
            self._pendingTasks = []
        # Process pending tasks
        finishedTasks = []
        for task in pendingTasks:
            task._run(self)
            finishedTasks.append(task)
        # Emit signal if there are finished tasks
        for task in finishedTasks:
            self.taskFinished.emit(task)



class DirProxy(PathProxy):
    """ Proxy object for a directory. Obtain an instance of this class
    using filesystemProx.dir()
    """
    
    def __init__(self, *args):
        PathProxy.__init__(self, *args)
        self._dirs = set()
        self._files = set()
    
    def dirs(self):
        with self._lock:
            return set(self._dirs)
    
    def files(self):
        with self._lock:
            return set(self._files)
    
    def _process(self, forceUpdate=False):
        # Get info
        dirs = self._fsProxy.listDirs(self._path)
        files = self._fsProxy.listFiles(self._path)
        # Is it deleted?
        if dirs is None or files is None:
            self.deleted.emit()
            return
        # All seems ok. Update if necessary
        dirs, files = set(dirs), set(files)
        if (dirs != self._dirs) or (files != self._files):
            with self._lock:
                self._dirs, self._files = dirs, files
            self.changed.emit()
        elif forceUpdate:
            self.changed.emit()



class FileProxy(PathProxy):
    """ Proxy object for a file. Obtain an instance of this class
    using filesystemProx.dir()
    """
    
    def __init__(self, *args):
        PathProxy.__init__(self, *args)
        self._modified = 0
    
    def modified(self):
        with self._lock:
            return self._modified
    
    def _process(self, forceUpdate=False):
        # Get info
        modified = self._fsProxy.modified(self._path)
        # Is it deleted?
        if modified is None:
            self.deleted.emit()
            return
        # All seems ok. Update if necessary
        if modified != self._modified:
            with self._lock:
                self._modified = modified
            self.changed.emit()
        elif forceUpdate:
            self.changed.emit()
    
    def read(self):
        pass # ?
    
    def save(self):
        pass # ?


## Proxy classes for the file system


class BaseFSProxy(threading.Thread):
    """ Abstract base class for file system proxies.
    
    The file system proxy defines an interface that subclasses can implement
    to "become" a usable file system proxy.
    
    This class implements the polling of information for the DirProxy
    and FileProxy objects, and keeping them up-to-date. For this purpose
    it keeps a set of PathProxy instances that are polled when idle.
    There is also a queue for items that need processing asap. This is
    where objects are put in when they are activated.
    
    This class has methods to use the file system (list files and
    directories, etc.). These can be used directly, but may be slow.
    Therefor it is recommended to use the FileProxy and DirProxy objects
    instead.
    
    """
    
    # Define how often the registered dirs and files are checked
    IDLE_TIMEOUT = 1.0
    
    # For testing to induce extra delay. Should normally be close to zero,
    # but not exactly zero!
    IDLE_DELAY = 0.01
    QUEUE_DELAY = 0.01  # 0.5
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        #
        self._interrupt = False
        self._exit = False
        #
        self._lock = threading.RLock()
        self._q = Queue()
        self._pathProxies = set()
        #
        self.start()
    
    def _track(self, pathProxy):
        # todo: use weak references
        with self._lock:
            self._pathProxies.add(pathProxy)
    
    def _unTrack(self, pathProxy):
        with self._lock:
            self._pathProxies.discard(pathProxy)
    
    def _push(self, pathProxy):
        # todo: use weak ref here too?
        self._q.put(pathProxy)
        self._interrupt = True
    
    def stop(self, *, timeout=1.0):
        with self._lock:
            self._exit = True
            self._interrupt = True
            self._pathProxies.clear()
        self.join(timeout)
    
    def dir(self, path):
        """ Convenience function to create a new DirProxy object.
        """
        return DirProxy(self, path)
    
    def file(self, path):
        """ Convenience function to create a new FileProxy object.
        """
        return FileProxy(self, path)
    
    
    def run(self):
        
        try:
            try:
                self._run()
            except Exception as err:
                if Empty is None or self._lock is None:
                    pass  # Shutting down ...
                else:
                    print('Exception in proxy thread: ' + str(err))
        
        except Exception:
            pass  # Interpreter is shutting down
    
    
    def _run(self):
        
        last_sleep = time.time()
        
        while True:
            
            # Check and reset
            self._interrupt = False
            if self._exit:
                return
            
            # Sleep
            now = time.time()
            if now - last_sleep > 0.1:
                last_sleep = now
                time.sleep(0.05)
            
            try:
                # Process items from the queue
                item = self._q.get(True, self.IDLE_TIMEOUT)
                if item is not None and not item._cancelled:
                    self._processItem(item, True)
            except Empty:
                # Queue empty, check items periodically
                self._idle()
    
    def _idle(self):
        # Make a copy of the set if item
        with self._lock:
            items = set(self._pathProxies)
        # Process them
        for item in items:
            if self._interrupt:
                return
            self._processItem(item)
    
    def _processItem(self, pathProxy, forceUpdate=False):
        
        # Slow down a bit
        if forceUpdate:
            time.sleep(self.QUEUE_DELAY)
        else:
            time.sleep(self.IDLE_DELAY)
        
        # Process
        try:
            pathProxy._process(forceUpdate)
        except Exception as err:
            pathProxy.errored.emit(str(err))
        
        # Process tasks
        pathProxy._processTasks()
    
    
    # To overload ...
    
    def listDirs(self, path):
        raise NotImplemented() # Should rerurn None if it does not exist
    
    def listFiles(self, path):
        raise NotImplemented() # Should rerurn None if it does not exist
    
    def modified(self, path):
        raise NotImplemented() # Should rerurn None if it does not exist
    
    def fileSize(self, path):
        raise NotImplemented() # Should rerurn None if it does not exist
    
    def read(self, path):
        raise NotImplemented() # Should rerurn None if it does not exist
    
    def write(self, path, bb):
        raise NotImplemented()
    
    def rename(self, path):
        raise NotImplemented()
    
    def remove(self, path):
        raise NotImplemented()
    
    def createDir(self, path):
        raise NotImplemented()


import os

class NativeFSProxy(BaseFSProxy):
    """ File system proxy for the native file system.
    """
    
    def listDirs(self, path):
        if isdir(path):
            pp = [op.join(path, p) for p in os.listdir(path)]
            return [str(p) for p in pp if isdir(p)]
    
    def listFiles(self, path):
        if isdir(path):
            pp = [op.join(path, p) for p in os.listdir(path)]
            return [str(p) for p in pp if op.isfile(p)]
    
    def modified(self, path):
        if op.isfile(path):
            return op.getmtime(path)
    
    def fileSize(self, path):
        if op.isfile(path):
            return op.getsize(path)
    
    def read(self, path):
        if op.isfile(path):
            return open(path, 'rb').read()
    
    def write(self, path, bb):
        with open(path, 'wb') as f:
            f.write(bb)
    
    def rename(self, path1, path2):
        os.rename(path1, path2)
    
    def remove(self, path):
        if op.isfile(path):
            os.remove(path)
        elif isdir(path):
            os.rmdir(path)
    
    def createDir(self, path):
        if not isdir(path):
            os.makedirs(path)
