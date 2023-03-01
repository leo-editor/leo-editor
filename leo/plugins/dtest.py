#@+leo-ver=5-thin
#@+node:ekr.20070119094733.1: * @file ../plugins/dtest.py
#@+<< docstring >>
#@+node:ekr.20070119094733.4: ** << docstring >>
""" Sends code to the doctest module and reports the result.

When the Dtest plugin is enabled, the ``dtest`` command is active.
Typing::

    Alt-X dtest

will run doctest on a file consisting of the current node and it's children.
If text is selected only the selection is tested.

From Wikipedia::

    'Doctest' is a module included in the Python programming language's
    standard library that allows for easy generation of tests based on
    output from the standard Python interpreter.

http://tinyurl.com/cqh53 - Python.org doctest page

http://tinyurl.com/pxhlq - Jim Fulton's presentation::

    Literate Testing:
    Automated Testing with doctest

"""
#@-<< docstring >>
#@+<< imports >>
#@+node:ekr.20070119094733.2: ** <<imports>>
import copy
import doctest
import os
from leo.core import leoGlobals as g
from leo.core.leoPlugins import BaseLeoPlugin
#@-<< imports >>

#@+others
#@+node:ekr.20070119094733.5: ** init
def init():
    """Return True if the plugin has loaded successfully."""
    g.registerHandler('after-create-leo-frame', DT)
    g.plugin_signon(__name__)
    return True
#@+node:ekr.20070119094733.6: ** class DT
class DT(BaseLeoPlugin):

    """Sends code to the doctest module and reports the result
    If text is selected, tests only the selection.

    >>> print("hello world")
    hello world
    >>> g.es('hello world')
    >>> print(c.p.h)
    Docstring
    >>> import notfound
    Traceback (most recent call last):
        ...
    ImportError: No module named notfound
    >>>
    """

    #@+others
    #@+node:ekr.20070119094733.8: *3* __init__
    def __init__(self, tag, keywords):

        """Init doctest plugin
        """
        super().__init__(tag, keywords)
        self.setCommand('dt', self.dtest)

        self.c = keywords['c']
    #@+node:ekr.20070119094733.9: *3* dtest
    def dtest(self, event):
        """The handler for dtest
        """
        # get a valid temporary filename
        createfile, tempfilename = g.create_temp_file()
        createfile.close()

        selected = False

        # if text is selected, only test selection
        if self.c.frame.body.hasTextSelection():
            selected = True
            selection = self.c.frame.body.getSelectedText()
            tempfile = open(tempfilename, 'w')
            tempfile.write(selection)
            tempfile.close()

        # if no selection, test this subtree
        else:
            self.c.importCommands.flattenOutline(tempfilename)

        tempfile = open(tempfilename)
        text = tempfile.readlines()
        tempfile.close()
        # strip trailing whitespace, an annoying source of doctest failures
        text_s = "\n".join(line.rstrip() for line in text)
        tempfile = open(tempfilename, 'w')
        tempfile.write(text_s)
        tempfile.close()

        # build globals dictionary
        globals = {'c': copy.copy(self.c), 'g': g}

        # run doctest on temporary file
        failures, tests = doctest.testfile(tempfilename, module_relative=False,
                            optionflags=doctest.ELLIPSIS, globs=globals)

        #@+<<report summary of results>>
        #@+node:ekr.20070119094733.10: *4* <<report summary of results>>
        if selected:
            g.es('Result of running doctest on selected text;')
        else:
            g.es('Result of running doctest on this subtree;')
        if failures == 0:
            g.blue("%s tests run successfully" % tests)
        if failures == 1:
            g.error("There was one failure in %s tests" % tests)
        if failures > 1:
            g.error("%s failures in %s tests" % (failures, tests))
        #@-<<report summary of results>>

        # clean up temp file
        os.remove(tempfilename)
    #@-others

#@-others
#@@language python
#@@tabwidth -4
#@-leo
