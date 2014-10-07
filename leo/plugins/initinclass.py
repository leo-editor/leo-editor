#@+leo-ver=5-thin
#@+node:ekr.20101110092851.5812: * @file initinclass.py
#@+<< docstring >>
#@+node:ekr.20101112180523.5421: ** << docstring >>
""" Modifies the Python @auto importer so that the importer
puts the __init__ method (ctor) into the body of the class node.

This makes it easier to keep the instance variable docs in the class
docstring in sync. with the ivars as manipulated by __init__, saves
repeating explanations in both places.

Note that this is done *after* the consistency checks by the @auto
import code, so using this plugin is at your own risk.  It will change
the order of declarations if other methods are declared before __init__.
"""
#@-<< docstring >>


__version__ = "0.1"
__plugin_name__ = "__init__ in class"

import leo.core.leoPlugins as leoPlugins
import leo.core.leoGlobals as g

#@@language python
#@@tabwidth -4
#@+others
#@+node:ekr.20101110093301.5816: ** InitInClass
def InitInClass(tag, keywords):
    '''Move __init__ into the class node body in python @auto imports'''

    cull = []  # __init__ nodes to remove

    parent = keywords['p']

    def moveInit(parent):
        for p in parent.children_iter():
            if '__init__' in p.headString():
                cull.append(p.copy())
                old = parent.bodyString().strip().split('\n')
                new = '\n'.join(['    '+i if i.strip() else ''
                    for i in p.bodyString().strip().split('\n')])
                new = '\n%s\n' % new

                # insert before @others
                for n, i in enumerate(old):
                    if i.strip() == '@others':
                        if parent.numberOfChildren() == 1:
                            del old[n]
                        old.insert(n,new)
                        old.append('')
                        break
                else:
                    old.append(new)
                parent.setBodyString('\n'.join(old))

            moveInit(p)

    moveInit(parent)

    cull.reverse()  # leaves first
    for i in cull:
        i._unlink()
#@+node:ekr.20101110093301.5817: ** init
def init():
    '''Return True if the plugin has loaded successfully.'''
    leoPlugins.registerHandler("after-auto", InitInClass)
    g.plugin_signon(__name__)
    return True
#@-others
#@-leo
