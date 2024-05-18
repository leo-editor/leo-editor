#!/usr/bin/python
#coding=utf-8
#@+leo-ver=5-thin
#@+node:bob.20170726143458.1: * @file babel_lib.py
#@@first
#@@first
#@@language python
#@@tabwidth -4

#@+<< documentation >>
#@+node:bob.20170726143458.2: ** << documentation >>
"""
The scheme for real-time streaming of stdout and stderr while the script is still executing is taken from:

http://stackoverflow.com/questions/18421757/live-output-from-subprocess-command


"""
#@-<< documentation >>
#@+<< version >>
#@+node:bob.20170726143458.3: ** << version >>
__version__ = '1.0.0'
#@-<< version >>
#@+<< imports >>
#@+node:bob.20170726143458.4: ** << imports >>
import collections
import datetime
import io
import os
import pathlib
import re
import signal
import six
import subprocess
import tempfile
import time

import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets


import leo.core.leoGlobals as leoG
import leo.core.leoNodes as leoNodes
#@-<< imports >>

#@+others
#@+node:bob.20170801125314.1: ** unl2clipboard(babelG)
def unl2clipboard(babelG):
    """ Put the UNL of the current node in the clipboard

    Arguments:
        babelG: Leo-Babel globals

    Returns:
        None
    """

    # with_proto=True forces with_file to be True. So there is always a file part.
    unl = babelG.cmdr.p.get_UNL(with_file=False, with_proto=True, with_index=False)
    clipboard = QtCore.QCoreApplication.instance().clipboard()
    clipboard.setText(unl)
    babelG.babelMenu.hide()
#@+node:bob.20170812170608.1: ** listRoots(cmdr)
def listRoots(cmdr):
    """
    Return an ordered list of all the current
    root positions in the target outline

    Arguments:
        cmdr:  The commander for the target outline

    Returns
        List of the the current root positions in the
        target outline in tree order.
    """

    root1 = cmdr.rootPosition()
    return [root.copy() for root in root1.self_and_siblings_iter()]
#@+node:bob.20170816103509.1: ** otpUnquote(otp)
def otpUnquote(otp):
    """
    Remove all otp-quoting from a string

    @param otp:  Otp-quoted outline path
    @param return:  Unquoted outline path

    """
    #@+others
    #@+node:bob.20231231133744.1: *3* quoteList = (...) tuple
    quoteList = (
        (six.u(' '), six.u('%20')),
        #(six.u('\t'), six.u('%09')),
        #(six.u("'"), six.u('%27')),
        )

    #@-others

    if otp:
        for un, qu in quoteList:
            otp = otp.replace(qu, un)
    return otp
#@+node:bob.20170816102949.1: ** unlSplit(unl)
def unlSplit(unl):
    """
    Split a UNL into a file pathname and an outline path.
    Unquote the filename and the outline path.

    Arguments:
        unl:   Uniform Node Locator

    Returns:
        (pathname, nodePart)
        pathname: Real absolute pathname unquoted.
            None if there is no filename in unl.
        nodePart: The node part of the unl
            None if there is no node part in the unl.
    """

    unl = unl.strip()
    if not unl:
        return None, None
    if unl.startswith('unl://'):
        unl = otpUnquote(unl[len('unl://') :])
    idx = unl.find('#')
    if idx == 0:
        # "#" is first character.
        return None, unl[1:]
    if idx < 0:
        # idx == -1 --> Not found
        pathname = unl
        nodePart = None
    else:
        pathname = unl[:idx]
        nodePart = unl[idx + 1 :]
    pathname = os.path.realpath(pathname)
    return pathname, nodePart
#@+node:bob.20170812164857.1: ** unl2pos(unl, cmdr=None)
def unl2pos(unl, cmdr=None):
    """ Univeral Node Locator to Leo-Editor Position

    Arguments:
        unl: Universal Node Locator
        cmdr:  Optional Leo-Editor commander for the file containing the node(s) specified
            by unl. Default:  None

    Returns:
        cmdrUnl: Commander for the file containing the position(s) in posList.
        posList:   A list containing in tree order all the positions that satisfy the UNL.
            [] (empty list) --> No position satisfies the UNL

    Exceptions:
        ValueError

            If unl contains a file pathname part and cmdr is not None, then ValueError is raised because
            both the pathname part and the cmdr specify files.  This is either redundant or contradictory.

            If unl does NOT contain a file pathname and cmdr is None, then ValueError is raised because
            there is no specification of the target file.

    """

    pathname, nodePart = unlSplit(unl)
    if (not pathname) and (cmdr is None):
        raise ValueError('No commander and No pathname in {0}'.format(unl))
    if pathname and (cmdr is not None):
        raise ValueError('Commander for {0} and pathname in {1}'.format(cmdr.fileName(), unl))
    if pathname:
        cmdrUnl = leoG.openWithFileName(pathname)
    else:
        cmdrUnl = cmdr
    unlList = _unlParseNodePart(nodePart)
    return cmdrUnl, _descendHdl(cmdrUnl, unlList)
#@+node:bob.20170812171044.1: *3* _unlParseNodePart()
def _unlParseNodePart(nodePart):
    """
    Parse the Node part of a UNL

    Arguments:
        nodePart: The node part of a UNL

    Returns:
        unlList: List of node part parameters
            in root to position order.

    """

    if not nodePart:
        if nodePart is None:
            return None
        else:
            return ['']
    return nodePart.split('-->')
#@+node:bob.20170812165239.1: *3* _descendHdl()
def _descendHdl(cmdrUnl, unlList):
    """
    Descend the target outline matching the Headline outline path

    Arguments:
        cmdrUnl:  Commander for the target outline
        unlList:  Root to position list of headlines.
            None --> UNL specifies all root nodes.

    Returns:
        posList:   A list containing in tree order all
            the positions that satisfy the UNL.
            [] (empty list) --> No position satisfies the UNL

    """

    def appendList(lst, entry):
        lstNew = lst[:]
        lstNew.append(entry)
        return lstNew

    if unlList is None:
        return listRoots(cmdrUnl)
    soFarList = [[(childVnode, idx)] for idx, childVnode in
        enumerate(cmdrUnl.hiddenRootNode.children)]
    lastUnlIdx = len(unlList) - 1
    for idx1, hdl in enumerate(unlList):
        if idx1 == lastUnlIdx:
            soFarList = [stk for stk in soFarList if stk[-1][0].h == hdl]
        else:
            soFarList = [appendList(stk, (childVnode, idx2)) for stk
                in soFarList for idx2, childVnode
                in enumerate(stk[-1][0].children) if stk[-1][0].h == hdl]
        if not soFarList:
            return list()
    return [leoNodes.position(stk[-1][0], childIndex=stk[-1][1],
        stack=stk[:-1]) for stk in soFarList]
#@+node:bob.20170726143458.9: ** class MenuPopUp(QtWidgets.QMenu)
class MenuPopUp(QtWidgets.QMenu):
    """ Pop-up Menu
    """

    #@+others
    #@+node:bob.20170726143458.10: *3* __init__()
    def __init__(self, babelG, parent=None):
        """ Initialize a Pop Up Menu

        Arguments:
            babelG:  Leo-Babel globals
            parent:  Parent of this menu

        Returns:
            None

        """
        LabelActionHint = collections.namedtuple('LabelActionHint', 'label action hint')

        super(MenuPopUp, self).__init__(parent=parent)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle('LeoPopUp')  # I configure i3 to run all windows named LeoPopUp as floating
        self.hovered.connect(self._actionHovered)

        actTDL = QtWidgets.QAction('Leo-Babel Menu', self)
        self.addAction(actTDL)
        actTDL.setToolTip('Menu of Leo-Babel Commands')
        actTDL.triggered.connect(lambda x: self._info(
            'The menu title is "Leo-Babel Menu"'))
        for eidx, labelActionHint in enumerate((
        LabelActionHint('&Copy UNL to clipboard',
        (lambda: unl2clipboard(babelG)),
        'Copy the UNL of the current position to the clipboard.'),)):
            actTDL = QtWidgets.QAction(labelActionHint.label, self)
            self.addAction(actTDL)
            actTDL.setToolTip(labelActionHint.hint)
            actTDL.triggered.connect(labelActionHint.action)
            if not eidx:
                # First action is the default action
                self.setDefaultAction(actTDL)
    #@+node:bob.20170726143458.11: *3* _actionHovered()
    def _actionHovered(self, action):
        """ Cursor hovering over a menu item.

        Arguments:
            action:  The action object for the menu item
                over which the cursor is hovering

        Returns:
            None
        """

        tip = action.toolTip()
        QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), tip)
    #@+node:bob.20170726143458.13: *3* _info()
    def _info(self, what):
        QtWidgets.QMessageBox.information(self, 'Information Only', what)
        self.exec_(QtWidgets.QApplication.desktop().screen().rect().center() -
            self.rect().center())  # type:ignore
    #@-others

#@+node:bob.20170726143458.15: ** babelMenu(event)
def babelMenu(event):
    """ Show the Leo-Babel Menu

    Arguments:
        event: Instance of leo.core.leoGui.LeoKeyEvent
            event.get('c'):  Leo-Editor Commander
                cmdr.p:  Current node position

    Returns:
        None
    """

    cmdr = event.get('c')
    babelG = leoG.user_dict['leo_babel']
    babelG.cmdr = cmdr
    babelG.babelMenu.exec_(QtWidgets.QApplication.desktop().screen().rect().center() -
        babelG.babelMenu.rect().center())
#@+node:bob.20170726143458.16: ** babelExec(event)
def babelExec(event):
    """ Execute a Script

    Arguments:
        event: Instance of leo.core.leoGui.LeoKeyEvent
            event.get('c'):  Leo-Editor Commander for cmdr.p
                cmdr.p:  Current node position

    Returns:
        None

    """

    #@+others
    #@+node:bob.20180402153922.1: *3* _babelExec(babelG, babelCmdr, babelRoot)
    def _babelExec(babelG, babelCmdr, babelRoot):
        """ Execute a Script

        Arguments:
            babelG: Babel globals
            babelCmdr: Leo-Editor commander for the file containing
                the script to execute
            babelRoot:  The "Babel Root" for the script to execute

        Returns:
            None

        Side Effects:
            For each line <line> in the target node body,
                A child node is created with empty body and headline "<elapsed time> - <line>"
                If <line> writes any non-blanks to stdout, then a child node is created with
                headline "stdout - <line>" and body containing the standard output.
                If <line> writes any non-blanks to stderr, then a child node is created with
                headline "stderr - <line>" and body containing the standard error output.

        Most importantly the output nodes are created in real time when they occur, not
        later when the <line> terminates.

        If there is a selected range, then this selected range is executed.
        If there is no selected range, then the whole body of the currently selected
        node is executed.

        If the language at the current cursor position is "python," then the
        Python interpreter executes the target text.
        If the language at the current cursor position is "shell," then the
        Bash interpreter executes the target text.

        The scheme for real-time streaming of stdout and stderr while the script is still executing is taken from:

        http://stackoverflow.com/questions/18421757/live-output-from-subprocess-command


        """

        # Execute the Python script in the body of the Babel Root node.  This sets
        # Leo-Babel options.
        script = getScript(cmdr, babelRoot, useSelectedText=False, language='python')
        code = compile(script, 'Babel Parameter Script', 'exec')

        gld = {'babel': babelG.babel_api,
            'b': babelG.babel_api,
            '__file__': 'Babel Parameter Script',
            'c': cmdr,
            'g': leoG,
            'p': babelRoot}
        exec(code, gld)     # This adds all the variables set by "code" to dictionary gld. [It also adds Python built-in's to gld.]

        # Copy Babel Parameter settings from gld to babelCmdr
        for paramName in ['babel_color_information', 'babel_color_stderr', 'babel_color_stdout', 'babel_interpreter_python',
            'babel_interpreter_shell', 'babel_node_creation', 'babel_polling_delay', 'babel_prefix_information',
            'babel_prefix_stderr', 'babel_prefix_stdout', 'babel_redirect_stdout', 'babel_results', 'babel_script',
            'babel_script_args',  'babel_sudo', 'babel_tab_babel']:
            paramValue = gld.get(paramName, None)
            if not paramValue is None:
                setattr(babelCmdr, paramName, paramValue)

        cmdrScr, scriptRoot = scrOrResRoot(cmdr, babelCmdr, babelG, babelRoot, 'script')
        if babelCmdr.babel_node_creation:
            cmdrRes, resultsRoot = scrOrResRoot(cmdr, babelCmdr, babelG, babelRoot, 'results')
        else:
            cmdrRes = None
            resultsRoot = None

        if babelCmdr.babel_sudo:
            # Run the script with sudo
            cmdList = ['sudo']
        else:
            cmdList = list()

        # Determine the language and then the interpreter
        langx = leoG.scanForAtLanguage(cmdrScr, scriptRoot)
        if langx == 'python':
            interpreter = babelCmdr.babel_interpreter_python
            cmdList.extend([interpreter, '-u'])
            extX = '.py'
        elif langx == 'shell':
            interpreter = babelCmdr.babel_interpreter_shell
            cmdList.append(interpreter)
            extX = '.sh'
        else:
            babelCmdr.babelExecCnt += 1
            raise babelG.babel_api.BABEL_LANGUAGE('Unknown language "{0}"'.format(langx))

        script = f'#! {interpreter}\n' + getScript(cmdrScr, scriptRoot, useSelectedText=False, language=langx)

        cmdrScr.setCurrentDirectoryFromContext(scriptRoot)
        cwd = leoG.os_path_abspath(os.getcwd())

        scriptfilepathGS = cmdr.config.settingsDict['scriptfilepath']
        sfSetting = scriptfilepathGS.val
        plPath = pathlib.Path(sfSetting)
        pathStr = str(plPath.parent.joinpath(plPath.stem)) + extX
        try:
            scriptfilepathGS.val = pathStr
            pathScript = cmdr.writeScriptFile(script)
        finally:
            scriptfilepathGS.val = sfSetting
        cmdList.append(pathScript)
        if getattr(babelCmdr, 'babel_script_args', None):
            cmdList.extend(babelCmdr.babel_script_args)

        leoG.es(f'{babelCmdr.babel_prefix_information}Script\'s CWD: "{cwd}"', color=babelCmdr.babel_color_information, tabName= 'Babel' if babelCmdr.babel_tab_babel else 'Log')
        leoG.es(f'{babelCmdr.babel_prefix_information}Command list: {cmdList}', color=babelCmdr.babel_color_information, tabName= 'Babel' if babelCmdr.babel_tab_babel else 'Log')

        # pylint: disable=unexpected-keyword-arg
        wro = tempfile.NamedTemporaryFile(buffering=0)
        wre = tempfile.NamedTemporaryFile(buffering=0)
        reo = io.open(wro.name, 'rb', buffering=0)
        ree = io.open(wre.name, 'rb', buffering=0)

        if getattr(babelCmdr, 'babel_redirect_stdout', None):
            # Redirect stdout to stderr
            wro = wre

        babelCmdr.cmdDoneFlag = False
        babelCmdr.cmdDoneStdPolled = False
        babelCmdr.cmdDoneErrPolled = False

        start = time.time()
        subPscript = subprocess.Popen(cmdList, cwd=cwd, stdout=wro, stderr=wre)
        subPbabKill = subprocess.Popen([babelG.pathBabelKill, str(subPscript.pid)])

        babelCmdr.reo = reo  # Kludge to allow itf() to determine which output it polls
        itOut = leoG.IdleTime(lambda ito, prefix=babelCmdr.babel_prefix_stdout, color=babelCmdr.babel_color_stdout, fdr=reo, babelCmdr=babelCmdr: itf(prefix, color, fdr, babelCmdr), delay=babelCmdr.babel_polling_delay)
        itErr = leoG.IdleTime(lambda ito, prefix=babelCmdr.babel_prefix_stderr, color=babelCmdr.babel_color_stderr, fdr=ree, babelCmdr=babelCmdr: itf(prefix, color, fdr, babelCmdr), delay=babelCmdr.babel_polling_delay)
        if (not itOut) or (not itErr):
            raise babelG.babel_api.BABEL_ERROR('leoG.IdleTime() failed')
        itOut.start()
        itErr.start()

        itPoll = leoG.IdleTime((lambda itobj: itp(itobj, cmdr, cmdrRes, resultsRoot,
            subPscript, subPbabKill, wro, reo, wre, ree, itOut, itErr, start,
            babelCmdr.babel_node_creation)), delay=1000)
        if not itPoll:
            raise babelG.babel_api.BABEL_ERROR('leoG.IdleTime() failed')
        itPoll.start()
    #@+node:bob.20170726143458.17: *3* getScript(c, p, useSelectedText=True, forcePythonSentinels=True, sentinels=True, language='python', )
    def getScript(c, p,
        useSelectedText=True,
        forcePythonSentinels=True,
        sentinels=True,
        language='python',
    ):
        '''
        Return the expansion of the selected text of node p.
        Return the expansion of all of node p's body text if
        p is not the current node or if there is no text selection.
        '''

        #@+others
        #@+node:bob.20170726143458.18: *4* extractExecutableString(c, p, s, language='python')
        def extractExecutableString(c, p, s, language='python'):
            '''
            Return all lines for the given @language directive.

            Ignore all lines under control of any other @language directive.
            '''
            if leoG.unitTesting:
                return s  # Regretable, but necessary.

            langCur = language
            pattern = re.compile(r'\s*@language\s+(\w+)')
            result: list[str] = []
            for line in leoG.splitLines(s):
                m = pattern.match(line)
                if m:  # Found an @language directive.
                    langCur = m.group(1)
                elif langCur == language:
                    result.append(line)
            return ''.join(result)
        #@+node:bob.20170726143458.19: *4* composeScript(c, p, s, forcePythonSentinels=True, sentinels=True)
        def composeScript(c, p, s, forcePythonSentinels=True, sentinels=True):
            '''Compose a script from p.b.'''

            if s.strip():
                # Important: converts unicode to utf-8 encoded strings.
                script = c.atFileCommands.stringToString(p.copy(), s,
                    forcePythonSentinels=forcePythonSentinels,
                    sentinels=sentinels)
                script = script.replace("\r\n", "\n")  # Use brute force.
                # Important, the script is an **encoded string**, not a unicode string.
                return script
            else:
                return ''
        #@-others

        w = c.frame.body.wrapper
        if not p: p = c.p
        try:
            if leoG.app.inBridge:
                s = p.b
            elif w and p == c.p and useSelectedText and w.hasSelection():
                s = w.getSelectedText()
            else:
                s = p.b
            s = extractExecutableString(c, p, s, language)
            script = composeScript(c, p, s,
                        forcePythonSentinels=forcePythonSentinels,
                        sentinels=sentinels)
        except Exception:
            leoG.es_print("unexpected exception in Leo-Babel getScript()", tabName= 'Babel' if babelCmdr.babel_tab_babel else 'Log')
            raise
        return script
    #@+node:bob.20170726143458.20: *3* itf(linePrefix, color, fdr, babelCmdr)
    def itf(linePrefix, color, fdr, babelCmdr):
        """ Echo stdout to the log pane

        Arguments:
            linePrefix: Line prefix
            color: Color of text to put in the log pane
            fdr:  Read File Descriptor for the stdout or stderr log file.
            babelCmdr: Leo-Editor for the file containing the current command

        Returns:
            None
        """

        while True:
            lix = fdr.read()
            if lix:
                for lineX in lix.decode('utf-8').split('\n'):
                    if lineX:
                        leoG.es(linePrefix + lineX, color=color, tabName= 'Babel' if babelCmdr.babel_tab_babel else 'Log')
            else:
                break
        if babelCmdr.cmdDoneFlag:
            if babelCmdr.reo == fdr:
                babelCmdr.cmdDoneStdPolled = True
            else:
                babelCmdr.cmdDoneErrPolled = True
    #@+node:bob.20170726143458.22: *3* itp(itPoll, cmdrB, cmdrRes, resultsRoot, subPscript, subPbabKill, wro, reo, wre, ree, itOut, itErr, start, babel_node_creation)
    def itp(itPoll, cmdrB, cmdrRes, resultsRoot, subPscript,
        subPbabKill, wro, reo, wre, ree,
        itOut, itErr,
        start, babel_node_creation):
        """ Poll for subprocess done

        Arguments:
            itPoll:  Idle time object for itp()
            cmdrB: Leo-Editor commander for the Leo-Babel root node
            cmdRes: Leo-Editor commander for resultsRoot
            resultsRoot: Results root
            subPscript:  Script subprocess object
            subPbabKill:  babel_kill subprocess object
            wro: File Descriptor
            reo: File Descriptor
            wre: File Descriptor
            ree: File Descriptor
            itOut: Idle time object
            itErr: Idle time object
            start:  Script start time
            babel_node_creation: False --> Don't create results nodes
                True --> Create results nodes

        Returns:
            None
        """

        babelCmdr = cmdrB.user_dict['leo_babel']
        if babelCmdr.cmdDoneFlag:
            if babelCmdr.cmdDoneStdPolled and babelCmdr.cmdDoneErrPolled:
                itOut.stop()
                itErr.stop()
                itPoll.stop()
                wro.close()
                wre.close()
                babel_color_information = babelCmdr.babel_color_information
                leoG.es(babelCmdr.babel_prefix_information + babelCmdr.termMsg, color=babel_color_information, tabName= 'Babel' if babelCmdr.babel_tab_babel else 'Log')
                leoG.es(babelCmdr.babel_prefix_information + babelCmdr.etMsg, color=babel_color_information, tabName= 'Babel' if babelCmdr.babel_tab_babel else 'Log')
                if babel_node_creation:
                    makeBabelNodes(cmdrRes, resultsRoot, reo, ree,
                        babelCmdr.termMsg, babelCmdr.etMsg)
                reo.close()
                ree.close()
                babelCmdr.babelExecCnt += 1
        else:
            rc = subPscript.poll()
            if not rc is None:
                end = time.time()
                babelCmdr.cmdDoneFlag = True
                if subPbabKill.poll() is None:
                    # Kill subprocess has not terminated
                    # pylint: disable=no-member
                    os.kill(subPbabKill.pid, signal.SIGHUP)
                babelCmdr.termMsg = '{0} Subprocess Termination Code'.format(rc)
                et = int(round(end - start))
                minutes, secs = divmod(et, 60)
                hours, minutes = divmod(minutes, 60)
                babelCmdr.etMsg = '{hr:02d}:{mi:02d}:{se:02d} Elapsed Time. {end} End Time'.format(
                    hr=hours, mi=minutes, se=secs,
                    end=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    #@+node:bob.20170726143458.21: *3* makeBabelNodes(cmdrRes, resultsRoot, reo, ree, termMsg, etMsg)
    def makeBabelNodes(cmdrRes, resultsRoot, reo, ree, termMsg, etMsg):
        """ Create the Babel Ouput Nodes

        Arguments:
            cmdrRes: Leo-Editor command for resultsRoot
            resultsRoot: Results root
            reo: File Descriptor for reading the stdout output
            ree: File Descriptor for reading the stderr output
            termMsg:  Termination message
            etMsg:  Elapsted time message

        Returns:
            None

        """

        undoer = cmdrRes.undoer; undoType = 'Leo-Babel Add Nodes'
        undoData = undoer.beforeInsertNode(babelRoot)

        # posET
        posET = resultsRoot.insertAsNthChild(0)
        posET.h = etMsg
        posET.b = termMsg

        # posSO
        posSO = posET.insertAsLastChild()
        posSO.h = 'stdout'
        reo.seek(0)
        posSO.b = reo.read().decode('utf-8')

        # posSE
        posSE = posET.insertAsLastChild()
        posSE.h = 'stderr'
        ree.seek(0)
        posSE.b = ree.read().decode('utf-8')

        undoer.afterInsertNode(posET, undoType, undoData)

        cmdrRes.bringToFront()
        cmdrRes.selectPosition(posET)
        cmdrRes.expandSubtree(posET)
        cmdrRes.redraw()
        cmdrRes.save()
    #@+node:bob.20170828151625.1: *3* scrOrResRoot(leoCmdrB, rootX, babelG, babelRoot, scrOrRes)
    def scrOrResRoot(leoCmdrB, babelCmdr, babelG, babelRoot, scrOrRes):
        """ Get the Script or Results Root

        Arguments:
            leoCmdrB:  Leo-Editor commander for the Babel Root
            babelCmdr: Babel commander
            babelG: Babel globals
            babelRoot:  Babel Root
            scrOrRes: "script" for Script root
                "results" for Results root

        Returns:
            (leoCmdrX, posX):
                leoCmdrX: Leo Commander for posX
                posX: Root position
        """
        
        posX = None  # EKR: to keep ruff happy.

        if getattr(babelCmdr, scrOrRes, None) is None:
            leoCmdrX = leoCmdrB
            posX = babelRoot.getNthChild({'script': 0, 'results': 1}[scrOrRes])
            if not posX:
                childOrd = {'script': 'First', 'results': 'Second'}[scrOrRes]
                raise babelG.babel_api.BABEL_ROOT(f'{childOrd} child '
                    f'of current node must be the {scrOrRes} root.')
        elif isinstance(posX, type('abc')):
            pathname, nodePart = unlSplit(posX)
            if pathname is None:
                leoCmdrX = leoCmdrB
            else:
                leoCmdrX = None
            leoCmdrX, posList = unl2pos(posX, cmdr=leoCmdrX)
            if not posList:
                raise babelG.babel_api.BABEL_UNL_NO_POS(f'{scrOrRes.capitalize()} Root UNL does not match any '
                    'position.')
            else:
                posX = posList[0]
                if len(posList) > 1:
                    warning = f'{scrOrRes.capitalize()} Root UNL satisfies {len(posList)} positions.'
                    leoG.warning(warning)
        posX = posX.copy()
        return leoCmdrX, posX
    #@-others

    babelG = leoG.user_dict['leo_babel']
    cmdr = event.get('c')
    babelCmdr = cmdr.user_dict.get('leo_babel')
    if babelCmdr is None:
        babelCmdr = babelG.babel_api.BabelCmdr(cmdr)
        cmdr.user_dict['leo_babel'] = babelCmdr
        #cmdr.frame.log.createTab('Babel')
    pos = cmdr.p
    babelRoot = pos.copy()

    # End editing in *this* outline, so typing in a new outline works.  Just in case there is a new outline.
    cmdr.endEditing()
    cmdr.redraw()

    try:
        _babelExec(babelG, babelCmdr, babelRoot)
    except Exception:
        babelCmdr.babelExecCnt += 1
        raise
#@-others
#@-leo
