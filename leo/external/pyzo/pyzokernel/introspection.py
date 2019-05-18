# -*- coding: utf-8 -*-
# Copyright (C) 2016, the Pyzo development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import sys
import yoton
import inspect  # noqa - used in eval()


try:
    import thread # Python 2
except ImportError:
    import _thread as thread # Python 3


class PyzoIntrospector(yoton.RepChannel):
    """ This is a RepChannel object that runs a thread to respond to
    requests from the IDE.
    """
    
    def _getNameSpace(self, name=''):
        """ _getNameSpace(name='')
        
        Get the namespace to apply introspection in.
        If name is given, will find that name. For example sys.stdin.
        
        """
        
        # Get namespace
        NS1 = sys._pyzoInterpreter.locals
        NS2 = sys._pyzoInterpreter.globals
        if not NS2:
            NS = NS1
        else:
            NS = NS2.copy()
            NS.update(NS1)
        
        # Look up a name?
        if not name:
            return NS
        else:
            try:
                # Get object
                ob = eval(name, None, NS)
                
                # Get namespace for this object
                if isinstance(ob, dict):
                    NS = ob
                elif isinstance(ob, (list, tuple)):
                    NS = {}
                    count = -1
                    for el in ob:
                        count += 1
                        NS['[%i]'%count] = el
                else:
                    keys = dir(ob)
                    NS = {}
                    for key in keys:
                        try:
                            NS[key] = getattr(ob, key)
                        except Exception:
                            NS[key] = '<unknown>'
                
                # Done
                return NS
            
            except Exception:
                return {}
    
    
    def _getSignature(self, objectName):
        """ _getSignature(objectName)
        
        Get the signature of builtin, function or method.
        Returns a tuple (signature_string, kind), where kind is a string
        of one of the above. When none of the above, both elements in
        the tuple are an empty string.
        
        """
        
        # if a class, get init
        # not if an instance! -> try __call__ instead
        # what about self?
        
        # Get valid object names
        parts = objectName.rsplit('.')
        objectNames = ['.'.join(parts[-i:]) for i in range(1,len(parts)+1)]
        
        # find out what kind of function, or if a function at all!
        NS = self._getNameSpace()
        fun1 = eval("inspect.isbuiltin(%s)"%(objectName), None, NS)
        fun2 = eval("inspect.isfunction(%s)"%(objectName), None, NS)
        fun3 = eval("inspect.ismethod(%s)"%(objectName), None, NS)
        fun4 = False
        fun5 = False
        if not (fun1 or fun2 or fun3):
            # Maybe it's a class with an init?
            if eval("hasattr(%s,'__init__')"%(objectName), None, NS):
                objectName += ".__init__"
                fun4 = eval("inspect.ismethod(%s)"%(objectName), None, NS)
            #  Or a callable object?
            elif eval("hasattr(%s,'__call__')"%(objectName), None, NS):
                objectName += ".__call__"
                fun5 = eval("inspect.ismethod(%s)"%(objectName), None, NS)
        
        sigs = ""
        if True:
            # the first line in the docstring is usually the signature
            tmp = eval("%s.__doc__"%(objectNames[-1]), {}, NS )
            sigs = ''
            if tmp:
                sigs = tmp.splitlines()[0].strip()
            # Test if doc has signature
            hasSig = False
            for name in objectNames: # list.append -> L.apend(objec) -- blabla
                name +="("
                if name in sigs:
                    hasSig = True
            # If not a valid signature, do not bother ...
            if (not hasSig) or (sigs.count("(") != sigs.count(")")):
                sigs = ""
        
        if fun1 or fun2 or fun3 or fun4 or fun5:
            
            if fun1:
                kind = 'builtin'
            elif fun2:
                kind = 'function'
            elif fun3:
                kind = 'method'
            elif fun4:
                kind = 'class'
            elif fun5:
                kind = 'callable'
            
            if not sigs:
                # Use intospection
                
                # collect
                try:
                    tmp = eval("inspect.getargspec(%s)"%(objectName), None, NS)
                except Exception:  # the above fails on 2.4 (+?) for builtins
                    tmp = None
                    kind = ''
                
                if tmp is not None:
                    args, varargs, varkw, defaults = tmp
                    
                    # prepare defaults
                    if defaults is None:
                        defaults = ()
                    defaults = list(defaults)
                    defaults.reverse()
                    # make list (back to forth)
                    args2 = []
                    for i in range(len(args)-fun4):
                        arg = args.pop()
                        if i < len(defaults):
                            args2.insert(0, "%s=%s" % (arg, defaults[i]) )
                        else:
                            args2.insert(0, arg )
                    # append varargs and kwargs
                    if varargs:
                        args2.append( "*"+varargs )
                    if varkw:
                        args2.append( "**"+varkw )
                    
                    # append the lot to our  string
                    funname = objectName.split('.')[-1]
                    sigs = "%s(%s)" % ( funname, ", ".join(args2) )
        
        elif sigs:
            kind = "function"
        else:
            sigs = ""
            kind = ""
        
        return sigs, kind
    
    
    # todo: variant that also says whether it's a property/function/class/other
    def dir(self, objectName):
        """ dir(objectName)
        
        Get list of attributes for the given name.
        
        """
        #sys.__stdout__.write('handling '+objectName+'\n')
        #sys.__stdout__.flush()
        
        # Get namespace
        NS = self._getNameSpace()
        
        # Init names
        names = set()
        
        # Obtain all attributes of the class
        try:
            command = "dir(%s.__class__)" % (objectName)
            d = eval(command, {}, NS)
        except Exception:
            pass
        else:
            names.update(d)
        
        # Obtain instance attributes
        try:
            command = "%s.__dict__.keys()" % (objectName)
            d = eval(command, {}, NS)
        except Exception:
            pass
        else:
            names.update(d)
            
        # That should be enough, but in case __dir__ is overloaded,
        # query that as well
        try:
            command = "dir(%s)" % (objectName)
            d = eval(command, {}, NS)
        except Exception:
            pass
        else:
            names.update(d)
        
        # Respond
        return list(names)
    
    
    def dir2(self, objectName):
        """ dir2(objectName)
        
        Get variable names in currently active namespace plus extra information.
        Returns a list with strings, which each contain a (comma separated)
        list of elements: name, type, kind, repr.
        
        """
        try:
            name = ''
            names = ['','']
            def storeInfo(name, val):
                # Determine type
                typeName = type(val).__name__
                # Determine kind
                kind = typeName
                if typeName != 'type':
                    if hasattr(val, '__array__') and hasattr(val, 'dtype'):
                        kind = 'array'
                    elif isinstance(val, list):
                        kind = 'list'
                    elif isinstance(val, tuple):
                        kind = 'tuple'
                # Determine representation
                if kind == 'array':
                    tmp = 'x'.join([str(s) for s in val.shape])
                    if tmp:
                        repres = '<array %s %s>' % (tmp, val.dtype.name)
                    elif val.size:
                        tmp = str(float(val))
                        if 'int' in val.dtype.name:
                            tmp = str(int(val))
                        repres = '<array scalar %s (%s)>' % (val.dtype.name, tmp)
                    else:
                        repres = '<array empty %s>' % (val.dtype.name)
                elif kind == 'list':
                    repres = '<list with %i elements>' % len(val)
                elif kind == 'tuple':
                    repres = '<tuple with %i elements>' % len(val)
                else:
                    repres = repr(val)
                    if len(repres) > 80:
                        repres = repres[:77] + '...'
                # Store
                tmp = ','.join([name, typeName, kind, repres])
                names.append(tmp)
            
            # Get locals
            NS = self._getNameSpace(objectName)
            for name in NS.keys():  # name can be a key in a dict, i.e. not str
                if hasattr(name, 'startswith') and name.startswith('__'):
                    continue
                try:
                    storeInfo(str(name), NS[name])
                except Exception:
                    pass
            
            return names
            
        except Exception:
            return []
    
    
    def signature(self, objectName):
        """ signature(objectName)
        
        Get signature.
        
        """
        try:
            text, kind = self._getSignature(objectName)
            return text
        except Exception:
            return None
    
    
    def doc(self, objectName):
        """ doc(objectName)
        
        Get documentation for an object.
        
        """
        
        # Get namespace
        NS = self._getNameSpace()
        
        try:
            
            # collect docstring
            h_text = ''
            # Try using the class (for properties)
            try:
                className = eval("%s.__class__.__name__"%(objectName), {}, NS)
                if '.' in objectName:
                    tmp = objectName.rsplit('.',1)
                    tmp[1] += '.'
                else:
                    tmp = [objectName, '']
                if className not in ['type', 'module', 'builtin_function_or_method', 'function']:
                    cmd = "%s.__class__.%s__doc__"
                    h_text = eval(cmd % (tmp[0],tmp[1]), {}, NS)
            except Exception:
                pass
            
            # Normal doc
            if not h_text:
                h_text = eval("%s.__doc__"%(objectName), {}, NS )
            
            # collect more data
            h_repr = eval("repr(%s)"%(objectName), {}, NS )
            try:
                h_class = eval("%s.__class__.__name__"%(objectName), {}, NS )
            except Exception:
                h_class = "unknown"
            
            # docstring can be None, but should be empty then
            if not h_text:
                h_text = ""
            
            # get and correct signature
            h_fun, kind = self._getSignature(objectName)
            if kind == 'builtin' or not h_fun:
                h_fun = ""  # signature already in docstring or not available
            
            # cut repr if too long
            if len(h_repr) > 200:
                h_repr = h_repr[:200] + "..."
            # replace newlines so we can separates the different parts
            h_repr = h_repr.replace('\n', '\r')
            
            # build final text
            text = '\n'.join([objectName, h_class, h_fun, h_repr, h_text])
            
        except Exception:
            type, value, tb = sys.exc_info()
            del tb
            text = '\n'.join([objectName, '', '', '', 'No help available. ', str(value)])

        # Done
        return text
    
    
    def eval(self, command):
        """ eval(command)
        
        Evaluate a command and return result.
        
        """
        
        # Get namespace
        NS = self._getNameSpace()
        
        try:
            # here globals is None, so we can look into sys, time, etc...
            return eval(command, None, NS)
        except Exception:
            return 'Error evaluating: ' + command
    
    
    def interrupt(self, command=None):
        """ interrupt()
        
        Interrupt the main thread. This does not work if the main thread
        is running extension code.
        
        A bit of a hack to do this in the introspector, but it's the
        easeast way and prevents having to launch another thread just
        to wait for an interrupt/terminare command.
        
        Note that on POSIX we can send an OS INT signal, which is faster
        and maybe more effective in some situations.
        
        """
        thread.interrupt_main()
    
    
    def terminate(self, command=None):
        """ terminate()
        
        Ask the kernel to terminate by closing the stdin.
        
        """
        sys.stdin._channel.close()
