#!/usr/bin/python
#coding=utf-8
#@+leo-ver=5-thin
#@+node:bob.20170716140541.1: * @file babel_api.py
#@@first
#@@first
#@@language python
#@@tabwidth -4

#@+<< version >>
#@+node:bob.20170716140706.1: ** << version >>
__version__ = '1.0.0'
#@-<< version >>
#@+<< imports >>
#@+node:bob.20170716142204.1: ** << imports >>
import os.path
import sys

from leo.plugins.leo_babel import babel_lib

import leo.core.leoGlobals as leoG
_ = leoG  # Keep pyflakes happy if leoG isn't used.
#@-<< imports >>

#@+others
#@+node:bob.20170910145203.1: ** Library Functions included in API
unl2pos = babel_lib.unl2pos
#@+node:bob.20170716142236.1: ** class BABEL_ERROR(Exception)
class BABEL_ERROR(Exception):
    pass

class BABEL_LANGUAGE(BABEL_ERROR):
    """ Language specified is not currently
    supported by Leo-Babel
    """
    pass

class BABEL_ROOT(BABEL_ERROR):
    """ Script Root or Results Root Error
    """
    pass

class BABEL_UNL_NO_POS(BABEL_ERROR):
    """ The UNL does not correspond to
    any current position.
    """
    pass

#@+node:bob.20170726143547.1: ** class BabelGlobals(object)
class BabelGlobals(object):
    """ Globals used by leo-Babel
    """
    #@+others
    #@+node:bob.20170726143547.2: *3* __init__()
    def __init__(self):
        """ Initialize the Leo-Babel globals

        Arguments:
            None

        Returns:
            None

        """

        if leoG.app.gui.guiName() == "qt":
            self.babelMenu = babel_lib.MenuPopUp(self)
        self.pathBabelKill = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'babel_kill.py')
        self.babel_api = sys.modules[__name__]
    #@-others
#@+node:bob.20180318164514.1: ** class BabelCmdr(object)
class BabelCmdr(object):
    """ Globals used by leo-Babel
    """
    #@+others
    #@+node:bob.20180318164514.2: *3* __init__(self, cmdr)
    def __init__(self, cmdr):
        """ Initialize the Leo-Babel Parameters specific to this Leo-Editor file

        Arguments:
            cmdr:  Leo-editor "commander" for the current .leo file

        Returns:
            None

        """

        #@+others
        #@+node:bob.20180318164514.3: *4* _getColor()
        def _getColor(cmdr, settingName, default=None):
            """ Add a default option to c.config.getColor()
            """

            colorx = cmdr.config.getColor(settingName)
            if colorx:
                return colorx
            else:
                return default
        #@+node:bob.20180318164514.4: *4* _getString()
        def _getString(cmdr, settingName, default=None):
            """ Add a default option to c.config.getString()
            """

            strx = cmdr.config.getString(settingName)
            if strx:
                return strx
            else:
                return default
        #@-others

        self.cmdr = cmdr
        self.colorStdout = _getColor(cmdr, 'Leo-Babel-stdout', default='#000000')
        self.colorStderr = _getColor(cmdr, 'Leo-Babel-stderr', default='#ff3300')
        self.colorInformation = _getColor(cmdr, 'Leo-Babel-completion')
        if self.colorInformation is None:
            self.colorInformation = _getColor(cmdr, 'Leo-Babel-information', default='#3333ff')
        self.nodeCreationDefault = \
            cmdr.config.getBool('Leo-Babel-Node-Creation-Default', default=None)
        if self.nodeCreationDefault is None:
            self.nodeCreationDefault = \
                cmdr.config.getBool('Leo-Babel-Node-Creation', default=True)
        self.interpreterPython = _getString(cmdr, 'Leo-Babel-Python', default='/usr/bin/python3')
        self.interpreterShell = _getString(cmdr, 'Leo-Babel-Shell', default='/user/bin/bash')
        self.babel_sudo = cmdr.config.getBool('Leo-Babel-Sudo', default=False)
        self.babel_prefix_information = _getString(cmdr, 'Leo-Babel-Prefix-Information',  default="- ")
        self.babel_prefix_stdout = _getString(cmdr, 'Leo-Babel-Prefix-stdout', default="| ")
        self.babel_prefix_stderr = _getString(cmdr, 'Leo-Babel-Prefix-stderr', default="* ")
        self.babel_tab_babel = cmdr.config.getBool('Leo-Babel-Tab-Babel', default=True)
        self.babel_polling_delay = cmdr.config.getInt("Leo-Babel-Polling-Delay", default=1)

        self.babelExecCnt = 0
        self.cmdDoneFlag = False
        self.cmdDoneStdPolled = False
        self.cmdDoneErrPolled = False
        self.reo = None
        self.termMsg = None
        self.etMsg = None
    #@-others
#@-others
#@-leo
