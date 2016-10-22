# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20161021130627.1: * @file ../commands/commanderCommands.py
#@@first
'''Standard Commander commands.'''
# To do: change event=None to event.
# To do: import this file from the Commands class init logic.
#@+<< imports >>
#@+node:ekr.20161021130713.1: ** << imports >> (commanderCommands.py)
import leo.core.leoGlobals as g
import leo.core.leoNodes as leoNodes
import leo.core.leoCommands as commander
import builtins
import imp
import os
import sys
import tabnanny
import time
import tokenize

#@-<< imports >>
cmd = g.command
#@+others
#@+node:ekr.20161022121128.1: ** Clone find commands
if 0:
    #@+others
    #@+node:ekr.20161022121128.2: *3* 'clone-find-all-marked' & 'cfam'
    @cmd('clone-find-all-marked')
    @cmd('cfam')
    def cloneFindAllMarked(self, event=None):
        '''
        clone-find-all-marked, aka cfam.

        Create an organizer node whose descendants contain clones of all marked
        nodes. The list is *not* flattened: clones appear only once in the
        descendants of the organizer node.
        '''
        c = self
        c.cloneFindMarkedHelper(flatten=False)

    #@+node:ekr.20161022154549.1: *3* 'clone-find-all-flattened-marked' & 'cffm'
    @cmd('clone-find-all-flattened-marked')
    @cmd('cffm')
    def cloneFindAllFlattenedMarked(self, event=None):
        '''
        clone-find-all-flattened-marked, aka cffm.

        Create an organizer node whose direct children are clones of all marked
        nodes. The list is flattened: every cloned node appears as a direct
        child of the organizer node, even if the clone also is a descendant of
        another cloned node.
        '''
        c = self
        c.cloneFindMarkedHelper(flatten=True)
    #@+node:ekr.20161022121128.3: *3* 'clone-find-parents'
    @cmd('clone-find-parents')
    def cloneFindParents(self, event=None):
        '''
        Create an organizer node whose direct children are clones of all
        parents of the selected node, which must be a clone.
        '''
        c, u = self, self.undoer
        p = c.p
        if not p: return
        if not p.isCloned():
            g.es('not a clone: %s' % p.h)
            return
        p0 = p.copy()
        undoType = 'Find Clone Parents'
        aList = c.vnode2allPositions(p.v)
        if not aList:
            g.trace('can not happen: no parents')
            return
        # Create the node as the last top-level node.
        # All existing positions remain valid.
        u.beforeChangeGroup(p0, undoType)
        top = c.rootPosition()
        while top.hasNext():
            top.moveToNext()
        b = u.beforeInsertNode(p0)
        found = top.insertAfter()
        found.h = 'Found: parents of %s' % p.h
        u.afterInsertNode(found, 'insert', b)
        seen = []
        for p2 in aList:
            parent = p2.parent()
            if parent and parent.v not in seen:
                seen.append(parent.v)
                b = u.beforeCloneNode(parent)
                clone = parent.clone()
                clone.moveToLastChildOf(found)
                u.afterCloneNode(clone, 'clone', b, dirtyVnodeList=[])
        u.afterChangeGroup(p0, undoType)
        c.selectPosition(found)
        c.setChanged(True)
        c.redraw()
    #@+node:ekr.20161022121128.4: *3* c.cloneFindByPredicate
    def cloneFindByPredicate(self,
        generator,     # The generator used to traverse the tree.
        predicate,     # A function of one argument p, returning True
                       # if p should be included in the results.
        failMsg=None,  # Failure message. Default is no message.
        flatten=False, # True: Put all matches at the top level.
        iconPath=None, # Full path to icon to attach to all matches.
        redraw=True,   # True: redraw the outline,
        undoType=None, # The undo name, shown in the Edit:Undo menu.
                       # The default is 'clone-find-predicate'
    ):
        '''
        Traverse the tree given using the generator, cloning all positions for
        which predicate(p) is True. Undoably move all clones to a new node, created
        as the last top-level node. Returns the newly-created node. Arguments:

        generator,      The generator used to traverse the tree.
        predicate,      A function of one argument p returning true if p should be included.
        failMsg=None,   Message given if nothing found. Default is no message.
        flatten=False,  True: Move all node to be parents of the root node.
        iconPath=None,  Full path to icon to attach to all matches.
        redraw=True,    True: redraw the screen.
        undo_type=None, The undo/redo name shown in the Edit:Undo menu.
                        The default is 'clone-find-predicate'
        '''
        c = self
        u, undoType = c.undoer, undoType or 'clone-find-predicate'
        clones, root, seen = [], None, set(),
        for p in generator():
            if predicate(p) and p.v not in seen:
                c.setCloneFindByPredicateIcon(iconPath, p)
                if flatten:
                    seen.add(p.v)
                else:
                    for p2 in p.self_and_subtree():
                        seen.add(p2.v)
                clones.append(p.copy())
        if clones:
            undoData = u.beforeInsertNode(c.p)
            root = c.createCloneFindPredicateRoot(flatten, undoType)
            for p in clones:
                clone = p.clone()
                clone.moveToLastChildOf(root)
            u.afterInsertNode(root, undoType, undoData, dirtyVnodeList=[])
            if redraw:
                c.selectPosition(root)
                c.setChanged(True)
                c.contractAllHeadlines()
                root.expand()
                c.redraw()
                c.selectPosition(root)
        elif failMsg:
            g.es_print(failMsg, color='red')
        return root
    #@+node:ekr.20161022121128.5: *4* c.setCloneFindByPredicateIcon
    def setCloneFindByPredicateIcon(self, iconPath, p):
        '''Attach an icon to p.v.u.'''
        if iconPath and g.os_path_exists(iconPath) and not g.os_path_isdir(iconPath):
            aList = p.v.u.get('icons', [])
            for d in aList:
                if d.get('file') == iconPath:
                    break
            else:
                aList.append({
                    'type': 'file',
                    'file': iconPath,
                    'on': 'VNode',
                    # 'relPath': iconPath,
                    'where': 'beforeHeadline',
                    'xoffset': 2, 'xpad': 1,
                    'yoffset': 0,

                })
                p.v.u ['icons'] = aList
        elif iconPath:
            g.trace('bad icon path', iconPath)
    #@+node:ekr.20161022121128.6: *4* c.createCloneFindPredicateRoot
    def createCloneFindPredicateRoot(self, flatten, undoType):
        '''Create a root node for clone-find-predicate.'''
        c = self
        root = c.lastTopLevel().insertAfter()
        root.h = undoType + (' (flattened)' if flatten else '')
        return root
    #@+node:ekr.20161022121128.7: *3* c.cloneFindMarkedHelper
    def cloneFindMarkedHelper(self, flatten):
        '''Helper for clone-find-marked commands.'''

        def isMarked(p):
            return p.isMarked()

        self.cloneFindByPredicate(
            generator = self.all_unique_positions,
            predicate = isMarked,
            failMsg = 'No marked nodes',
            flatten = flatten,
            undoType = 'clone-find-marked',
        )
    #@-others
#@+node:ekr.20161021130640.48: ** Edit commands
if 0:
    #@+others
    #@+node:ekr.20161021130640.49: *3* Edit commands
    #@+node:ekr.20161021130640.51: *4* 'execute-script'
    @cmd('execute-script')
    def executeScript(self, event=None,
        args=None, p=None, script=None, useSelectedText=True,
        define_g=True, define_name='__main__',
        silent=False, namespace=None, raiseFlag=False,
    ):
        '''
        Execute a *Leo* script.
        Keyword args:
        args=None               Not None: set script_args in the execution environment.
        p=None                  Get the script from p.b, unless script is given.
        script=None             None: use script in p.b or c.p.b
        useSelectedText=True    False: use all the text in p.b or c.p.b.
        define_g=True           True: define g for the script.
        define_name='__main__'  Not None: define the name symbol.
        silent=False            No longer used.
        namespace=None          Not None: execute the script in this namespace.
        raiseFlag=False         True: reraise any exceptions.
        '''
        c, script1 = self, script
        if not script:
            if c.forceExecuteEntireBody:
                useSelectedText = False
            script = g.getScript(c, p or c.p, useSelectedText=useSelectedText)
        script_p = p or c.p
            # Only for error reporting below.
        self.redirectScriptOutput()
        try:
            oldLog = g.app.log
            log = c.frame.log
            g.app.log = log
            if script.strip():
                sys.path.insert(0, '.') # New in Leo 5.0
                sys.path.insert(0, c.frame.openDirectory) # per SegundoBob
                script += '\n' # Make sure we end the script properly.
                try:
                    # We *always* execute the script with p = c.p.
                    c.executeScriptHelper(args, define_g, define_name, namespace, script)
                except Exception:
                    if raiseFlag:
                        raise
                    else:
                        g.handleScriptException(c, script_p, script, script1)
                finally:
                    del sys.path[0]
                    del sys.path[0]
            else:
                tabName = log and hasattr(log, 'tabName') and log.tabName or 'Log'
                g.warning("no script selected", tabName=tabName)
        finally:
            g.app.log = oldLog
            self.unredirectScriptOutput()
    #@+node:ekr.20161021130640.52: *5* c.executeScriptHelper
    def executeScriptHelper(self, args, define_g, define_name, namespace, script):
        c = self
        p = c.p.copy() # *Always* use c.p and pass c.p to script.
        c.setCurrentDirectoryFromContext(p)
        d = {'c': c, 'g': g, 'p': p} if define_g else {}
        if define_name: d['__name__'] = define_name
        d['script_args'] = args or []
        if namespace: d.update(namespace)
        # A kludge: reset c.inCommand here to handle the case where we *never* return.
        # (This can happen when there are multiple event loops.)
        # This does not prevent zombie windows if the script puts up a dialog...
        try:
            c.inCommand = False
            g.inScript = g.app.inScript = True
                # g.inScript is a synonym for g.app.inScript.
            if c.write_script_file:
                scriptFile = self.writeScriptFile(script)
                # pylint: disable=undefined-variable, no-member
                if g.isPython3:
                    exec(compile(script, scriptFile, 'exec'), d)
                else:
                    builtins.execfile(scriptFile, d)
            else:
                exec(script, d)
        finally:
            g.inScript = g.app.inScript = False
    #@+node:ekr.20161021130640.53: *5* c.redirectScriptOutput
    def redirectScriptOutput(self):
        c = self
        # g.trace('original')
        if c.config.redirect_execute_script_output_to_log_pane:
            g.redirectStdout() # Redirect stdout
            g.redirectStderr() # Redirect stderr
    #@+node:ekr.20161021130640.54: *5* c.setCurrentDirectoryFromContext
    def setCurrentDirectoryFromContext(self, p):
        trace = False and not g.unitTesting
        c = self
        aList = g.get_directives_dict_list(p)
        path = c.scanAtPathDirectives(aList)
        curDir = g.os_path_abspath(os.getcwd())
        # g.trace(p.h,'\npath  ',path,'\ncurDir',curDir)
        if path and path != curDir:
            if trace: g.trace('calling os.chdir(%s)' % (path))
            try:
                os.chdir(path)
            except Exception:
                pass
    #@+node:ekr.20161021130640.55: *5* c.unredirectScriptOutput
    def unredirectScriptOutput(self):
        c = self
        # g.trace('original')
        if c.exists and c.config.redirect_execute_script_output_to_log_pane:
            g.restoreStderr()
            g.restoreStdout()
    #@+node:ekr.20161021130640.59: *4* 'hide-invisibles' & 'show-invisibles' & 'toggle-invisibles'
    @cmd('hide-invisibles')
    def hideInvisibles(self, event=None):
        '''Hide invisible (whitespace) characters.'''
        c = self; c.showInvisiblesHelper(False)

    @cmd('show-invisibles')
    def showInvisibles(self, event=None):
        '''Show invisible (whitespace) characters.'''
        c = self; c.showInvisiblesHelper(True)

    @cmd('toggle-invisibles')
    def toggleShowInvisibles(self, event=None):
        '''Toggle showing of invisible (whitespace) characters.'''
        c = self; colorizer = c.frame.body.getColorizer()
        val = 0 if colorizer.showInvisibles else 1
        c.showInvisiblesHelper(val)

    def showInvisiblesHelper(self, val):
        c, frame = self, self.frame
        colorizer = frame.body.getColorizer()
        colorizer.showInvisibles = val
        colorizer.highlighter.showInvisibles = val
        # It is much easier to change the menu name here than in the menu updater.
        menu = frame.menu.getMenu("Edit")
        index = frame.menu.getMenuLabel(menu,
            'Hide Invisibles' if val else 'Show Invisibles')
        if index is None:
            if val: frame.menu.setMenuLabel(menu, "Show Invisibles", "Hide Invisibles")
            else: frame.menu.setMenuLabel(menu, "Hide Invisibles", "Show Invisibles")
        # 2016/03/09: Set the status bits here.
        # May fix #240: body won't scroll to end of text
        # https://github.com/leo-editor/leo-editor/issues/240
        if hasattr(frame.body, 'set_invisibles'):
            frame.body.set_invisibles(c)
        c.frame.body.recolor(c.p)
    #@+node:ekr.20161021130640.50: *4* 'set-colors'
    @cmd('set-colors')
    def colorPanel(self, event=None):
        '''Open the color dialog.'''
        c = self; frame = c.frame
        if not frame.colorPanel:
            frame.colorPanel = g.app.gui.createColorPanel(c)
        frame.colorPanel.bringToFront()
    #@+node:ekr.20161021130640.56: *4* 'set-font'
    @cmd('set-font')
    def fontPanel(self, event=None):
        '''Open the font dialog.'''
        c = self; frame = c.frame
        if not frame.fontPanel:
            frame.fontPanel = g.app.gui.createFontPanel(c)
        frame.fontPanel.bringToFront()
    #@+node:ekr.20161021130640.58: *4* 'settings'
    @cmd('settings')
    def preferences(self, event=None):
        '''Handle the preferences command.'''
        c = self
        c.openLeoSettings()
    #@+node:ekr.20161021130640.61: *3* Edit body commands
    #@+node:ekr.20161021130640.63: *4* 'convert-all-blanks'
    @cmd('convert-all-blanks')
    def convertAllBlanks(self, event=None):
        '''Convert all blanks to tabs in the selected outline.'''
        c = self; u = c.undoer; undoType = 'Convert All Blanks'
        current = c.p
        if g.app.batchMode:
            c.notValidInBatchMode(undoType)
            return
        d = c.scanAllDirectives()
        tabWidth = d.get("tabwidth")
        count = 0; dirtyVnodeList = []
        u.beforeChangeGroup(current, undoType)
        for p in current.self_and_subtree():
            # g.trace(p.h,tabWidth)
            innerUndoData = u.beforeChangeNodeContents(p)
            if p == current:
                changed, dirtyVnodeList2 = c.convertBlanks(event)
                if changed:
                    count += 1
                    dirtyVnodeList.extend(dirtyVnodeList2)
            else:
                changed = False; result = []
                text = p.v.b
                # assert(g.isUnicode(text))
                lines = text.split('\n')
                for line in lines:
                    i, w = g.skip_leading_ws_with_indent(line, 0, tabWidth)
                    s = g.computeLeadingWhitespace(w, abs(tabWidth)) + line[i:] # use positive width.
                    if s != line: changed = True
                    result.append(s)
                if changed:
                    count += 1
                    dirtyVnodeList2 = p.setDirty()
                    dirtyVnodeList.extend(dirtyVnodeList2)
                    result = '\n'.join(result)
                    p.setBodyString(result)
                    u.afterChangeNodeContents(p, undoType, innerUndoData)
        u.afterChangeGroup(current, undoType, dirtyVnodeList=dirtyVnodeList)
        if not g.unitTesting:
            g.es("blanks converted to tabs in", count, "nodes")
                # Must come before c.redraw().
        if count > 0:
            c.redraw_after_icons_changed()
    #@+node:ekr.20161021130640.64: *4* 'convert-all-tabs'
    @cmd('convert-all-tabs')
    def convertAllTabs(self, event=None):
        '''Convert all tabs to blanks in the selected outline.'''
        c = self; u = c.undoer; undoType = 'Convert All Tabs'
        current = c.p
        if g.app.batchMode:
            c.notValidInBatchMode(undoType)
            return
        theDict = c.scanAllDirectives()
        tabWidth = theDict.get("tabwidth")
        count = 0; dirtyVnodeList = []
        u.beforeChangeGroup(current, undoType)
        for p in current.self_and_subtree():
            undoData = u.beforeChangeNodeContents(p)
            if p == current:
                changed, dirtyVnodeList2 = self.convertTabs(event)
                if changed:
                    count += 1
                    dirtyVnodeList.extend(dirtyVnodeList2)
            else:
                result = []; changed = False
                text = p.v.b
                # assert(g.isUnicode(text))
                lines = text.split('\n')
                for line in lines:
                    i, w = g.skip_leading_ws_with_indent(line, 0, tabWidth)
                    s = g.computeLeadingWhitespace(w, -abs(tabWidth)) + line[i:] # use negative width.
                    if s != line: changed = True
                    result.append(s)
                if changed:
                    count += 1
                    dirtyVnodeList2 = p.setDirty()
                    dirtyVnodeList.extend(dirtyVnodeList2)
                    result = '\n'.join(result)
                    p.setBodyString(result)
                    u.afterChangeNodeContents(p, undoType, undoData)
        u.afterChangeGroup(current, undoType, dirtyVnodeList=dirtyVnodeList)
        if not g.unitTesting:
            g.es("tabs converted to blanks in", count, "nodes")
        if count > 0:
            c.redraw_after_icons_changed()
    #@+node:ekr.20161021130640.65: *4* 'convert-blanks'
    @cmd('convert-blanks')
    def convertBlanks(self, event=None):
        '''Convert all blanks to tabs in the selected node.'''
        c = self; changed = False; dirtyVnodeList = []
        head, lines, tail, oldSel, oldYview = c.getBodyLines(expandSelection=True)
        # Use the relative @tabwidth, not the global one.
        theDict = c.scanAllDirectives()
        tabWidth = theDict.get("tabwidth")
        if tabWidth:
            result = []
            for line in lines:
                s = g.optimizeLeadingWhitespace(line, abs(tabWidth)) # Use positive width.
                if s != line: changed = True
                result.append(s)
            if changed:
                undoType = 'Convert Blanks'
                result = ''.join(result)
                oldSel = None
                dirtyVnodeList = c.updateBodyPane(head, result, tail, undoType, oldSel, oldYview) # Handles undo
        return changed, dirtyVnodeList
    #@+node:ekr.20161021130640.66: *4* 'convert-tabs'
    @cmd('convert-tabs')
    def convertTabs(self, event=None):
        '''Convert all tabs to blanks in the selected node.'''
        c = self; changed = False; dirtyVnodeList = []
        head, lines, tail, oldSel, oldYview = self.getBodyLines(expandSelection=True)
        # Use the relative @tabwidth, not the global one.
        theDict = c.scanAllDirectives()
        tabWidth = theDict.get("tabwidth")
        if tabWidth:
            result = []
            for line in lines:
                i, w = g.skip_leading_ws_with_indent(line, 0, tabWidth)
                s = g.computeLeadingWhitespace(w, -abs(tabWidth)) + line[i:] # use negative width.
                if s != line: changed = True
                result.append(s)
            if changed:
                undoType = 'Convert Tabs'
                result = ''.join(result)
                oldSel = None
                dirtyVnodeList = c.updateBodyPane(head, result, tail, undoType, oldSel, oldYview) # Handles undo
        return changed, dirtyVnodeList
    #@+node:ekr.20161021130640.70: *4* 'extract'
    @cmd('extract')
    def extract(self, event=None):
        '''
        Create child node from the selected body text.

        1. If the selection starts with a section reference, the section name become
           the child's headline. All following lines become the child's body text.
           The section reference line remains in the original body text.

        2. If the selection looks like a Python class or definition line, the
           class/function/method name becmes child's headline and all selected lines
           become the child's body text.

        3. Otherwise, the first line becomes the child's headline, and all selected
           lines become the child's body text.
        '''
        c, current, u, undoType = self, self.p, self.undoer, 'Extract'
        head, lines, tail, oldSel, oldYview = self.getBodyLines()
        if not lines:
            return # Nothing selected.
        # Remove leading whitespace.
        junk, ws = g.skip_leading_ws_with_indent(lines[0], 0, c.tab_width)
        lines = [g.removeLeadingWhitespace(s, ws, c.tab_width) for s in lines]
        h = lines[0].strip()
        ref_h = c.extractRef(h).strip()
        def_h = c.extractDef(h).strip()
        if ref_h:
            # h,b,middle = ref_h,lines[1:],lines[0]
            # 2012/02/27: Change suggested by vitalije (vitalijem@gmail.com)
            h, b, middle = ref_h, lines[1:], ' ' * ws + lines[0]
        elif def_h:
            h, b, middle = def_h, lines, ''
        else:
            h, b, middle = lines[0].strip(), lines[1:], ''
        u.beforeChangeGroup(current, undoType)
        undoData = u.beforeInsertNode(current)
        p = c.createLastChildNode(current, h, ''.join(b))
        u.afterInsertNode(p, undoType, undoData)
        c.updateBodyPane(head, middle, tail,
            undoType=undoType, oldSel=None, oldYview=oldYview)
        u.afterChangeGroup(current, undoType=undoType)
        p.parent().expand()
        c.redraw(p.parent()) # A bit more convenient than p.
        c.bodyWantsFocus()
    # Compatibility

    extractSection = extract
    extractPythonMethod = extract
    #@+node:ekr.20161021130640.71: *5* c.extractDef
    def extractDef(self, s):
        '''Return the defined function/method name if
        s looks like Python def or class line.
        '''
        s = s.strip()
        for tag in ('def', 'class'):
            if s.startswith(tag):
                i = g.skip_ws(s, len(tag))
                j = g.skip_id(s, i, chars='_')
                if j > i:
                    name = s[i: j]
                    if tag == 'class':
                        return name
                    else:
                        k = g.skip_ws(s, j)
                        if g.match(s, k, '('):
                            return name
        return ''
    #@+node:ekr.20161021130640.72: *5* c.extractRef
    def extractRef(self, s):
        '''Return s if it starts with a section name.'''
        i = s.find('<<')
        j = s.find('>>')
        if -1 < i < j:
            return s
        i = s.find('@<')
        j = s.find('@>')
        if -1 < i < j:
            return s
        return ''
    #@+node:ekr.20161021130640.73: *4* 'extract-names'
    @cmd('extract-names')
    def extractSectionNames(self, event=None):
        '''Create child nodes for every section reference in the selected text.
        The headline of each new child node is the section reference.
        The body of each child node is empty.'''
        c = self; u = c.undoer; undoType = 'Extract Section Names'
        body = c.frame.body; current = c.p
        head, lines, tail, oldSel, oldYview = self.getBodyLines()
        if not lines:
            g.warning('No lines selected')
            return
        u.beforeChangeGroup(current, undoType)
        found = False
        for s in lines:
            name = c.findSectionName(s)
            if name:
                undoData = u.beforeInsertNode(current)
                p = self.createLastChildNode(current, name, None)
                u.afterInsertNode(p, undoType, undoData)
                found = True
        c.validateOutline()
        if found:
            u.afterChangeGroup(current, undoType)
            c.redraw(p)
        else:
            g.warning("selected text should contain section names")
        # Restore the selection.
        i, j = oldSel
        w = body.wrapper
        if w:
            w.setSelectionRange(i, j)
            w.setFocus()
    #@+node:ekr.20161021130640.74: *5* c.findSectionName
    def findSectionName(self, s):
        head1 = s.find("<<")
        if head1 > -1:
            head2 = s.find(">>", head1)
        else:
            head1 = s.find("@<")
            if head1 > -1:
                head2 = s.find("@>", head1)
        if head1 == -1 or head2 == -1 or head1 > head2:
            name = None
        else:
            name = s[head1: head2 + 2]
        return name
    #@+node:ekr.20161021130640.76: *4* 'indent-region'
    @cmd('indent-region')
    def indentBody(self, event=None):
        '''
        The indent-region command indents each line of the selected body text,
        or each line of a node if there is no selected text. The @tabwidth directive
        in effect determines amount of indentation. (not yet) A numeric argument
        specifies the column to indent to.
        '''
        c, undoType = self, 'Indent Region'
        tab_width = c.getTabWidth(c.p)
        head, lines, tail, oldSel, oldYview = self.getBodyLines()
        changed, result = False, []
        for line in lines:
            i, width = g.skip_leading_ws_with_indent(line, 0, tab_width)
            s = g.computeLeadingWhitespace(width + abs(tab_width), tab_width) + line[i:]
            if s != line: changed = True
            result.append(s)
        if changed:
            result = ''.join(result)
            c.updateBodyPane(head, result, tail, undoType, oldSel, oldYview)
    #@+node:ekr.20161021130640.84: *4* 'insert-body-time'
    @cmd('insert-body-time')
    def insertBodyTime(self, event=None):
        '''Insert a time/date stamp at the cursor.'''
        c = self; undoType = 'Insert Body Time'
        w = c.frame.body.wrapper
        if g.app.batchMode:
            c.notValidInBatchMode(undoType)
            return
        oldSel = w.getSelectionRange()
        w.deleteTextSelection()
        s = self.getTime(body=True)
        i = w.getInsertPoint()
        w.insert(i, s)
        c.frame.body.onBodyChanged(undoType, oldSel=oldSel)
    #@+node:ekr.20161021130640.85: *5* c.getTime
    def getTime(self, body=True):
        c = self
        default_format = "%m/%d/%Y %H:%M:%S" # E.g., 1/30/2003 8:31:55
        # Try to get the format string from settings.
        if body:
            format = c.config.getString("body_time_format_string")
            gmt = c.config.getBool("body_gmt_time")
        else:
            format = c.config.getString("headline_time_format_string")
            gmt = c.config.getBool("headline_gmt_time")
        if format is None:
            format = default_format
        try:
            # import time
            if gmt:
                s = time.strftime(format, time.gmtime())
            else:
                s = time.strftime(format, time.localtime())
        except(ImportError, NameError):
            g.warning("time.strftime not available on this platform")
            return ""
        except Exception:
            g.es_exception() # Probably a bad format string in leoSettings.leo.
            s = time.strftime(default_format, time.gmtime())
        return s
    #@+node:ekr.20161021130640.62: *4* 'match-brackets' & 'select-to-matching-bracket'
    @cmd('match-brackets')
    @cmd('select-to-matching-bracket')
    def findMatchingBracket(self, event=None):
        '''Select the text between matching brackets.'''
        #@+others
        #@-others
        c, p = self, self.p
        if g.app.batchMode:
            c.notValidInBatchMode("Match Brackets")
            return
        language = g.getLanguageAtPosition(c, p)
        if language == 'perl':
            g.es('match-brackets not supported for', language)
        else:
            g.MatchBrackets(c, p, language).run()
    #@+node:ekr.20161021130640.87: *4* 'reformat-paragraph'
    @cmd('reformat-paragraph')
    def reformatParagraph(self, event=None, undoType='Reformat Paragraph'):
        '''
        Reformat a text paragraph

        Wraps the concatenated text to present page width setting. Leading tabs are
        sized to present tab width setting. First and second line of original text is
        used to determine leading whitespace in reformatted text. Hanging indentation
        is honored.

        Paragraph is bound by start of body, end of body and blank lines. Paragraph is
        selected by position of current insertion cursor.
        '''
        c = self
        body = c.frame.body
        w = body.wrapper
        if g.app.batchMode:
            c.notValidInBatchMode("reformat-paragraph")
            return
        if w.hasSelection():
            i, j = w.getSelectionRange()
            w.setInsertPoint(i)
        oldSel, oldYview, original, pageWidth, tabWidth = c.rp_get_args()
        head, lines, tail = c.findBoundParagraph()
        if lines:
            indents, leading_ws = c.rp_get_leading_ws(lines, tabWidth)
            result = c.rp_wrap_all_lines(indents, leading_ws, lines, pageWidth)
            c.rp_reformat(head, oldSel, oldYview, original, result, tail, undoType)
    #@+node:ekr.20161021130640.88: *5* c.findBoundParagraph & helpers
    def findBoundParagraph(self, event=None):
        '''Return the lines of a paragraph to be reformatted.'''
        c = self
        trace = False and not g.unitTesting
        head, ins, tail = c.frame.body.getInsertLines()
        head_lines = g.splitLines(head)
        tail_lines = g.splitLines(tail)
        if trace:
            g.trace("head_lines:\n%s" % ''.join(head_lines))
            g.trace("ins: ", ins)
            g.trace("tail_lines:\n%s" % ''.join(tail_lines))
            g.trace('*****')
        result = []
        insert_lines = g.splitLines(ins)
        para_lines = insert_lines + tail_lines
        # If the present line doesn't start a paragraph,
        # scan backward, adding trailing lines of head to ins.
        if insert_lines and not c.startsParagraph(insert_lines[0]):
            n = 0 # number of moved lines.
            for i, s in enumerate(reversed(head_lines)):
                if c.endsParagraph(s) or c.singleLineParagraph(s):
                    break
                elif c.startsParagraph(s):
                    n += 1
                    break
                else: n += 1
            if n > 0:
                para_lines = head_lines[-n:] + para_lines
                head_lines = head_lines[: -n]
        ended, started = False, False
        for i, s in enumerate(para_lines):
            if trace: g.trace(
                # 'i: %s started: %5s single: %5s starts: %5s: ends: %5s %s' % (
                i, started,
                c.singleLineParagraph(s),
                c.startsParagraph(s),
                c.endsParagraph(s), repr(s))
            if started:
                if c.endsParagraph(s) or c.startsParagraph(s):
                    ended = True
                    break
                else:
                    result.append(s)
            elif s.strip():
                result.append(s)
                started = True
                if c.endsParagraph(s) or c.singleLineParagraph(s):
                    i += 1
                    ended = True
                    break
            else:
                head_lines.append(s)
        if started:
            head = g.joinLines(head_lines)
            tail_lines = para_lines[i:] if ended else []
            tail = g.joinLines(tail_lines)
            return head, result, tail # string, list, string
        else:
            if trace: g.trace('no paragraph')
            return None, None, None
    #@+node:ekr.20161021130640.89: *6* c.endsParagraph & c.singleLineParagraph
    def endsParagraph(self, s):
        '''Return True if s is a blank line.'''
        return not s.strip()

    def singleLineParagraph(self, s):
        '''Return True if s is a single-line paragraph.'''
        return s.startswith('@') or s.strip() in ('"""', "'''")
    #@+node:ekr.20161021130640.90: *6* c.startsParagraph
    def startsParagraph(self, s):
        '''Return True if line s starts a paragraph.'''
        trace = False and not g.unitTesting
        if not s.strip():
            val = False
        elif s.strip() in ('"""', "'''"):
            val = True
        elif s[0].isdigit():
            i = 0
            while i < len(s) and s[i].isdigit():
                i += 1
            val = g.match(s, i, ')') or g.match(s, i, '.')
        elif s[0].isalpha():
            # Careful: single characters only.
            # This could cause problems in some situations.
            val = (
                (g.match(s, 1, ')') or g.match(s, 1, '.')) and
                (len(s) < 2 or s[2] in (' \t\n')))
        else:
            val = s.startswith('@') or s.startswith('-')
        if trace: g.trace(val, repr(s))
        return val
    #@+node:ekr.20161021130640.86: *5* c.reformatBody
    def reformatBody(self, event=None):
        '''Reformat all paragraphs in the body.'''
        c, p = self, self.p
        undoType = 'reformat-body'
        w = c.frame.body.wrapper
        c.undoer.beforeChangeGroup(p, undoType)
        w.setInsertPoint(0)
        while 1:
            progress = w.getInsertPoint()
            c.reformatParagraph(event, undoType=undoType)
            ins = w.getInsertPoint()
            s = w.getAllText()
            w.setInsertPoint(ins)
            if ins <= progress or ins >= len(s):
                break
        c.undoer.afterChangeGroup(p, undoType)
    #@+node:ekr.20161021130640.91: *5* c.rp_get_args
    def rp_get_args(self):
        '''Compute and return oldSel,oldYview,original,pageWidth,tabWidth.'''
        c = self
        body = c.frame.body
        w = body.wrapper
        d = c.scanAllDirectives()
        # g.trace(c.editCommands.fillColumn)
        if c.editCommands.fillColumn > 0:
            pageWidth = c.editCommands.fillColumn
        else:
            pageWidth = d.get("pagewidth")
        tabWidth = d.get("tabwidth")
        original = w.getAllText()
        oldSel = w.getSelectionRange()
        oldYview = w.getYScrollPosition()
        return oldSel, oldYview, original, pageWidth, tabWidth
    #@+node:ekr.20161021130640.92: *5* c.rp_get_leading_ws
    def rp_get_leading_ws(self, lines, tabWidth):
        '''Compute and return indents and leading_ws.'''
        # c = self
        indents = [0, 0]
        leading_ws = ["", ""]
        for i in (0, 1):
            if i < len(lines):
                # Use the original, non-optimized leading whitespace.
                leading_ws[i] = ws = g.get_leading_ws(lines[i])
                indents[i] = g.computeWidth(ws, tabWidth)
        indents[1] = max(indents)
        if len(lines) == 1:
            leading_ws[1] = leading_ws[0]
        return indents, leading_ws
    #@+node:ekr.20161021130640.93: *5* c.rp_reformat
    def rp_reformat(self, head, oldSel, oldYview, original, result, tail, undoType):
        '''Reformat the body and update the selection.'''
        c = self; body = c.frame.body; w = body.wrapper
        # This destroys recoloring.
        junk, ins = body.setSelectionAreas(head, result, tail)
        changed = original != head + result + tail
        if changed:
            s = w.getAllText()
            # Fix an annoying glitch when there is no
            # newline following the reformatted paragraph.
            if not tail and ins < len(s): ins += 1
            # 2010/11/16: stay in the paragraph.
            body.onBodyChanged(undoType, oldSel=oldSel, oldYview=oldYview)
        else:
            # Advance to the next paragraph.
            s = w.getAllText()
            ins += 1 # Move past the selection.
            while ins < len(s):
                i, j = g.getLine(s, ins)
                line = s[i: j]
                # 2010/11/16: it's annoying, imo, to treat @ lines differently.
                if line.isspace():
                    ins = j + 1
                else:
                    ins = i
                    break
            # setSelectionAreas has destroyed the coloring.
            c.recolor()
        w.setSelectionRange(ins, ins, insert=ins)
        # 2011/10/26: Calling see does more harm than good.
            # w.see(ins)
        # Make sure we never scroll horizontally.
        w.setXScrollPosition(0)
    #@+node:ekr.20161021130640.94: *5* c.rp_wrap_all_lines
    def rp_wrap_all_lines(self, indents, leading_ws, lines, pageWidth):
        '''Compute the result of wrapping all lines.'''
        c = self
        trailingNL = lines and lines[-1].endswith('\n')
        lines = [z[: -1] if z.endswith('\n') else z for z in lines]
        if len(lines) > 0: # Bug fix: 2013/12/22.
            s = lines[0]
            if c.startsParagraph(s):
                # Adjust indents[1]
                # Similar to code in c.startsParagraph(s)
                i = 0
                if s[0].isdigit():
                    while i < len(s) and s[i].isdigit():
                        i += 1
                    if g.match(s, i, ')') or g.match(s, i, '.'):
                        i += 1
                elif s[0].isalpha():
                    if g.match(s, 1, ')') or g.match(s, 1, '.'):
                        i = 2
                elif s[0] == '-':
                    i = 1
                # Never decrease indentation.
                i = g.skip_ws(s, i + 1)
                if i > indents[1]:
                    indents[1] = i
                    leading_ws[1] = ' ' * i
        # Wrap the lines, decreasing the page width by indent.
        result = g.wrap_lines(lines,
            pageWidth - indents[1],
            pageWidth - indents[0])
        # prefix with the leading whitespace, if any
        paddedResult = []
        paddedResult.append(leading_ws[0] + result[0])
        for line in result[1:]:
            paddedResult.append(leading_ws[1] + line)
        # Convert the result to a string.
        result = '\n'.join(paddedResult)
        if trailingNL: result = result + '\n'
        return result
    #@+node:ekr.20161021130640.95: *4* 'unformat-paragraph'
    @cmd('unformat-paragraph')
    def unformatParagraph(self, event=None, undoType='Unformat Paragraph'):
        '''
        Unformat a text paragraph. Removes all extra whitespace in a paragraph.

        Paragraph is bound by start of body, end of body and blank lines. Paragraph is
        selected by position of current insertion cursor.
        '''
        c = self
        body = c.frame.body
        w = body.wrapper
        if g.app.batchMode:
            c.notValidInBatchMode("unformat-paragraph")
            return
        if w.hasSelection():
            i, j = w.getSelectionRange()
            w.setInsertPoint(i)
        oldSel, oldYview, original, pageWidth, tabWidth = c.rp_get_args()
        head, lines, tail = c.findBoundParagraph()
        if lines:
            result = ' '.join([z.strip() for z in lines]) + '\n'
            c.unreformat(head, oldSel, oldYview, original, result, tail, undoType)
    #@+node:ekr.20161021130640.96: *5* c.unreformat
    def unreformat(self, head, oldSel, oldYview, original, result, tail, undoType):
        '''unformat the body and update the selection.'''
        c = self; body = c.frame.body; w = body.wrapper
        # This destroys recoloring.
        junk, ins = body.setSelectionAreas(head, result, tail)
        changed = original != head + result + tail
        if changed:
            body.onBodyChanged(undoType, oldSel=oldSel, oldYview=oldYview)
        # Advance to the next paragraph.
        s = w.getAllText()
        ins += 1 # Move past the selection.
        while ins < len(s):
            i, j = g.getLine(s, ins)
            line = s[i: j]
            if line.isspace():
                ins = j + 1
            else:
                ins = i
                break
        # setSelectionAreas has destroyed the coloring.
        c.recolor()
        w.setSelectionRange(ins, ins, insert=ins)
        # More useful than for reformat-paragraph.
        w.see(ins)
        # Make sure we never scroll horizontally.
        w.setXScrollPosition(0)
    #@+node:ekr.20161021130640.68: *4* 'unindent-region'
    @cmd('unindent-region')
    def dedentBody(self, event=None):
        '''Remove one tab's worth of indentation from all presently selected lines.'''
        c, undoType = self, 'Unindent'
        tab_width = c.getTabWidth(c.p)
        head, lines, tail, oldSel, oldYview = self.getBodyLines()
        changed, result = False, []
        for line in lines:
            i, width = g.skip_leading_ws_with_indent(line, 0, tab_width)
            s = g.computeLeadingWhitespace(width - abs(tab_width), tab_width) + line[i:]
            if s != line: changed = True
            result.append(s)
        if changed:
            result = ''.join(result)
            c.updateBodyPane(head, result, tail, undoType, oldSel, oldYview)
    #@+node:ekr.20161021130640.67: *4* c.createLastChildNode
    def createLastChildNode(self, parent, headline, body):
        '''A helper function for the three extract commands.'''
        c = self
        if body and len(body) > 0:
            body = body.rstrip()
        if not body or len(body) == 0:
            body = ""
        p = parent.insertAsLastChild()
        p.initHeadString(headline)
        p.setBodyString(body)
        p.setDirty()
        c.validateOutline()
        return p
    #@+node:ekr.20161021130640.75: *4* c.getBodyLines
    def getBodyLines(self, expandSelection=False):
        """
        Return head,lines,tail where:

        before is string containg all the lines before the selected text
        (or the text before the insert point if no selection) lines is a
        list of lines containing the selected text (or the line containing
        the insert point if no selection) after is a string all lines
        after the selected text (or the text after the insert point if no
        selection)
        """
        c = self
        body = c.frame.body
        w = body.wrapper
        oldVview = w.getYScrollPosition()
        if expandSelection:
            s = w.getAllText()
            head = tail = ''
            oldSel = 0, len(s)
            lines = g.splitLines(s) # Retain the newlines of each line.
        else:
            # Note: lines is the entire line containing the insert point if no selection.
            head, s, tail = body.getSelectionLines()
            lines = g.splitLines(s) # Retain the newlines of each line.
            # Expand the selection.
            i = len(head)
            j = max(i, len(head) + len(s) - 1)
            oldSel = i, j
        return head, lines, tail, oldSel, oldVview # string,list,string,tuple.
    #@+node:ekr.20161021130640.77: *4* c.insert/removeComments & helpers
    #@+node:ekr.20161021130640.78: *5* c.hasAmbiguousLangauge
    def hasAmbiguousLanguage(self, p):
        '''Return True if p.b contains different @language directives.'''
        # c = self
        languages, tag = set(), '@language'
        for s in g.splitLines(p.b):
            if g.match_word(s, 0, tag):
                i = g.skip_ws(s, len(tag))
                j = g.skip_id(s, i)
                word = s[i: j]
                languages.add(word)
        return len(list(languages)) > 1
    #@+node:ekr.20161021130640.79: *5* c.getLanguageAtCursor
    def getLanguageAtCursor(self, p, language):
        '''
        Return the language in effect at the present insert point.
        Use the language argument as a default if no @language directive seen.
        '''
        c = self
        tag = '@language'
        w = c.frame.body.wrapper
        ins = w.getInsertPoint()
        n = 0
        for s in g.splitLines(p.b):
            # g.trace(ins,n,repr(s))
            if g.match_word(s, 0, tag):
                i = g.skip_ws(s, len(tag))
                j = g.skip_id(s, i)
                language = s[i: j]
            if n <= ins < n + len(s):
                break
            else:
                n += len(s)
        # g.trace(ins,n,language)
        return language
    #@+node:ekr.20161021130640.80: *5* 'add-comments'
    @cmd('add-comments')
    def addComments(self, event=None):
        #@+<< addComments docstring >>
        #@+node:ekr.20161021130640.81: *6* << addComments docstring >>
        #@@pagewidth 50
        '''
        Converts all selected lines to comment lines using
        the comment delimiters given by the applicable @language directive.

        Inserts single-line comments if possible; inserts
        block comments for languages like html that lack
        single-line comments.

        @bool indent_added_comments

        If True (the default), inserts opening comment
        delimiters just before the first non-whitespace
        character of each line. Otherwise, inserts opening
        comment delimiters at the start of each line.

        *See also*: delete-comments.
        '''
        #@-<< addComments docstring >>
        c = self; p = c.p
        head, lines, tail, oldSel, oldYview = self.getBodyLines()
        if not lines:
            g.warning('no text selected')
            return
        # The default language in effect at p.
        language = c.frame.body.colorizer.scanColorDirectives(p)
        if c.hasAmbiguousLanguage(p):
            language = c.getLanguageAtCursor(p, language)
        # g.trace(language,p.h)
        d1, d2, d3 = g.set_delims_from_language(language)
        d2 = d2 or ''; d3 = d3 or ''
        if d1:
            openDelim, closeDelim = d1 + ' ', ''
        else:
            openDelim, closeDelim = d2 + ' ', ' ' + d3
        # Comment out non-blank lines.
        indent = c.config.getBool('indent_added_comments', default=True)
        result = []
        for line in lines:
            if line.strip():
                i = g.skip_ws(line, 0)
                if indent:
                    result.append(line[0: i] + openDelim + line[i:].replace('\n', '') + closeDelim + '\n')
                else:
                    result.append(openDelim + line.replace('\n', '') + closeDelim + '\n')
            else:
                result.append(line)
        result = ''.join(result)
        c.updateBodyPane(head, result, tail, undoType='Add Comments', oldSel=None, oldYview=oldYview)
    #@+node:ekr.20161021130640.82: *5* 'delete-comments'
    @cmd('delete-comments')
    def deleteComments(self, event=None):
        #@+<< deleteComments docstring >>
        #@+node:ekr.20161021130640.83: *6* << deleteComments docstring >>
        #@@pagewidth 50
        '''
        Removes one level of comment delimiters from all
        selected lines.  The applicable @language directive
        determines the comment delimiters to be removed.

        Removes single-line comments if possible; removes
        block comments for languages like html that lack
        single-line comments.

        *See also*: add-comments.
        '''
        #@-<< deleteComments docstring >>
        c = self; p = c.p
        head, lines, tail, oldSel, oldYview = self.getBodyLines()
        result = []
        if not lines:
            g.warning('no text selected')
            return
        # The default language in effect at p.
        language = c.frame.body.colorizer.scanColorDirectives(p)
        if c.hasAmbiguousLanguage(p):
            language = c.getLanguageAtCursor(p, language)
        d1, d2, d3 = g.set_delims_from_language(language)
        if d1:
            # Remove the single-line comment delim in front of each line
            d1b = d1 + ' '
            n1, n1b = len(d1), len(d1b)
            for s in lines:
                i = g.skip_ws(s, 0)
                if g.match(s, i, d1b):
                    result.append(s[: i] + s[i + n1b:])
                elif g.match(s, i, d1):
                    result.append(s[: i] + s[i + n1:])
                else:
                    result.append(s)
        else:
            # Remove the block comment delimiters from each line.
            n2, n3 = len(d2), len(d3)
            for s in lines:
                i = g.skip_ws(s, 0)
                j = s.find(d3, i + n2)
                if g.match(s, i, d2) and j > -1:
                    first = i + n2
                    if g.match(s, first, ' '): first += 1
                    last = j
                    if g.match(s, last - 1, ' '): last -= 1
                    result.append(s[: i] + s[first: last] + s[j + n3:])
                else:
                    result.append(s)
        result = ''.join(result)
        c.updateBodyPane(head, result, tail, undoType='Delete Comments', oldSel=None, oldYview=oldYview)
    #@+node:ekr.20161021130640.97: *4* c.updateBodyPane (handles changeNodeContents)
    def updateBodyPane(self, head, middle, tail, undoType, oldSel, oldYview):
        '''Handle changed text in the body pane.'''
        c, p = self, self.p
        body = c.frame.body
        # Update the text and notify the event handler.
        body.setSelectionAreas(head, middle, tail)
        # Expand the selection.
        head = head or ''
        middle = middle or ''
        tail = tail or ''
        i = len(head)
        j = max(i, len(head) + len(middle) - 1)
        newSel = i, j
        body.wrapper.setSelectionRange(i, j)
        # This handles the undo.
        body.onBodyChanged(undoType, oldSel=oldSel or newSel, oldYview=oldYview)
        # Update the changed mark and icon.
        c.setChanged(True)
        if p.isDirty():
            dirtyVnodeList = []
        else:
            dirtyVnodeList = p.setDirty()
        c.redraw_after_icons_changed()
        # Scroll as necessary.
        if oldYview:
            body.wrapper.setYScrollPosition(oldYview)
        else:
            body.wrapper.seeInsertPoint()
        body.wrapper.setFocus()
        c.recolor()
        return dirtyVnodeList
    #@+node:ekr.20161021130640.98: *3* Edit headline submenu
    #@+node:ekr.20161021130640.99: *4* 'edit-headline'
    @cmd('edit-headline')
    def editHeadline(self, event=None):
        '''Begin editing the headline of the selected node.'''
        c = self; k = c.k; tree = c.frame.tree
        if g.app.batchMode:
            c.notValidInBatchMode("Edit Headline")
            return
        e, wrapper = tree.editLabel(c.p)
        if k:
            # k.setDefaultInputState()
            k.setEditingState()
            k.showStateAndMode(w=wrapper)
        return e, wrapper
    #@+node:ekr.20161021130640.100: *4* 'toggle-angle-brackets'
    @cmd('toggle-angle-brackets')
    def toggleAngleBrackets(self, event=None):
        '''Add or remove double angle brackets from the headline of the selected node.'''
        c = self; p = c.p
        if g.app.batchMode:
            c.notValidInBatchMode("Toggle Angle Brackets")
            return
        c.endEditing()
        s = p.h.strip()
        if (s[0: 2] == "<<" or
            s[-2:] == ">>" # Must be on separate line.
        ): 
            if s[0: 2] == "<<": s = s[2:]
            if s[-2:] == ">>": s = s[: -2]
            s = s.strip()
        else:
            s = g.angleBrackets(' ' + s + ' ')
        p.setHeadString(s)
        c.redrawAndEdit(p, selectAll=True)
    #@-others
#@+node:ekr.20161021130640.2: ** File commands
if 0:
    #@+others
    #@+node:ekr.20161021130640.40: *3* Export commands
    #@+node:ekr.20161021130640.41: *4* 'export-headlines'
    @cmd('export-headlines')
    def exportHeadlines(self, event=None):
        '''Export all headlines to an external file.'''
        c = self
        filetypes = [("Text files", "*.txt"), ("All files", "*")]
        fileName = g.app.gui.runSaveFileDialog(c,
            initialfile="headlines.txt",
            title="Export Headlines",
            filetypes=filetypes,
            defaultextension=".txt")
        c.bringToFront()
        if fileName:
            g.setGlobalOpenDir(fileName)
            g.chdir(fileName)
            c.importCommands.exportHeadlines(fileName)
    #@+node:ekr.20161021130640.42: *4* 'flatten-outline'
    @cmd('flatten-outline')
    def flattenOutline(self, event=None):
        '''
        Export the selected outline to an external file.
        The outline is represented in MORE format.
        '''
        c = self
        filetypes = [("Text files", "*.txt"), ("All files", "*")]
        fileName = g.app.gui.runSaveFileDialog(c,
            initialfile="flat.txt",
            title="Flatten Selected Outline",
            filetypes=filetypes,
            defaultextension=".txt")
        c.bringToFront()
        if fileName:
            g.setGlobalOpenDir(fileName)
            g.chdir(fileName)
            c.importCommands.flattenOutline(fileName)
    #@+node:ekr.20161021130640.43: *4* 'flatten-outline-to-node'
    @cmd('flatten-outline-to-node')
    def flattenOutlineToNode(self, event=None):
        '''
        Append the body text of all descendants of the selected node to the
        body text of the selected node.
        '''
        c, root, u = self, self.p, self.undoer
        if not root.hasChildren():
            return
        language = g.getLanguageAtPosition(c, root)
        if language:
            single,start,end = g.set_delims_from_language(language)
        else:
            single,start,end = '#', None, None
        bunch = u.beforeChangeNodeContents(root)
        aList = []
        for p in root.subtree():
            if single:
                aList.append('\n\n===== %s %s\n\n' % (single, p.h))
            else:
                aList.append('\n\n===== %s %s %s\n\n' % (start, p.h, end))
            if p.b.strip():
                lines = g.splitLines(p.b)
                aList.extend(lines)
        root.b = root.b.rstrip() + '\n' + ''.join(aList).rstrip() + '\n'
        u.afterChangeNodeContents(root, 'flatten-outline-to-node', bunch)
    #@+node:ekr.20161021130640.44: *4* 'outline-to-cweb'
    @cmd('outline-to-cweb')
    def outlineToCWEB(self, event=None):
        '''
        Export the selected outline to an external file.
        The outline is represented in CWEB format.
        '''
        c = self
        filetypes = [
            ("CWEB files", "*.w"),
            ("Text files", "*.txt"),
            ("All files", "*")]
        fileName = g.app.gui.runSaveFileDialog(c,
            initialfile="cweb.w",
            title="Outline To CWEB",
            filetypes=filetypes,
            defaultextension=".w")
        c.bringToFront()
        if fileName:
            g.setGlobalOpenDir(fileName)
            g.chdir(fileName)
            c.importCommands.outlineToWeb(fileName, "cweb")
    #@+node:ekr.20161021130640.45: *4* 'outline-to-noweb'
    @cmd('outline-to-noweb')
    def outlineToNoweb(self, event=None):
        '''
        Export the selected outline to an external file.
        The outline is represented in noweb format.
        '''
        c = self
        filetypes = [
            ("Noweb files", "*.nw"),
            ("Text files", "*.txt"),
            ("All files", "*")]
        fileName = g.app.gui.runSaveFileDialog(c,
            initialfile=self.outlineToNowebDefaultFileName,
            title="Outline To Noweb",
            filetypes=filetypes,
            defaultextension=".nw")
        c.bringToFront()
        if fileName:
            g.setGlobalOpenDir(fileName)
            g.chdir(fileName)
            c.importCommands.outlineToWeb(fileName, "noweb")
            c.outlineToNowebDefaultFileName = fileName
    #@+node:ekr.20161021130640.46: *4* 'remove-sentinels'
    @cmd('remove-sentinels')
    def removeSentinels(self, event=None):
        '''Import one or more files, removing any sentinels.'''
        c = self
        types = [
            ("All files", "*"),
            ("C/C++ files", "*.c"),
            ("C/C++ files", "*.cpp"),
            ("C/C++ files", "*.h"),
            ("C/C++ files", "*.hpp"),
            ("Java files", "*.java"),
            ("Lua files", "*.lua"),
            ("Pascal files", "*.pas"),
            ("Python files", "*.py")]
        names = g.app.gui.runOpenFileDialog(c,
            title="Remove Sentinels",
            filetypes=types,
            defaultextension=".py",
            multiple=True)
        c.bringToFront()
        if names:
            g.chdir(names[0])
            c.importCommands.removeSentinelsCommand(names)
    #@+node:ekr.20161021130640.47: *4* 'weave'
    @cmd('weave')
    def weave(self, event=None):
        '''Simulate a literate-programming weave operation by writing the outline to a text file.'''
        c = self
        filetypes = [("Text files", "*.txt"), ("All files", "*")]
        fileName = g.app.gui.runSaveFileDialog(c,
            initialfile="weave.txt",
            title="Weave",
            filetypes=filetypes,
            defaultextension=".txt")
        c.bringToFront()
        if fileName:
            g.setGlobalOpenDir(fileName)
            g.chdir(fileName)
            c.importCommands.weave(fileName)
    #@+node:ekr.20161021130640.3: *3* File commands
    #@+node:ekr.20161021130640.4: *4* 'close-window'
    @cmd('close-window')
    def close(self, event=None, new_c=None):
        '''Close the Leo window, prompting to save it if it has been changed.'''
        g.app.closeLeoWindow(self.frame, new_c=new_c)

    commander.close = close
    #@+node:ekr.20161021130640.5: *4* 'import-file'
    @cmd('import-file')
    def importAnyFile(self, event=None):
        '''Import one or more files.'''
        c = self
        ic = c.importCommands
        types = [
            ("All files", "*"),
            ("C/C++ files", "*.c"),
            ("C/C++ files", "*.cpp"),
            ("C/C++ files", "*.h"),
            ("C/C++ files", "*.hpp"),
            ("FreeMind files", "*.mm.html"),
            ("Java files", "*.java"),
            # ("JSON files", "*.json"),
            ("Mindjet files", "*.csv"),
            ("MORE files", "*.MORE"),
            ("Lua files", "*.lua"),
            ("Pascal files", "*.pas"),
            ("Python files", "*.py"),
            ("Tabbed files", "*.txt"),
        ]
        names = g.app.gui.runOpenFileDialog(c,
            title="Import File",
            filetypes=types,
            defaultextension=".py",
            multiple=True)
        c.bringToFront()
        if names:
            g.chdir(names[0])
        else:
            names = []
        if not names:
            if g.unitTesting:
                # a kludge for unit testing.
                c.init_error_dialogs()
                c.raise_error_dialogs(kind='read')
            return
        # New in Leo 4.9: choose the type of import based on the extension.
        c.init_error_dialogs()
        derived = [z for z in names if c.looksLikeDerivedFile(z)]
        others = [z for z in names if z not in derived]
        if derived:
            ic.importDerivedFiles(parent=c.p, paths=derived)
        for fn in others:
            junk, ext = g.os_path_splitext(fn)
            if ext.startswith('.'):
                ext = ext[1:]
            if ext == 'csv':
                ic.importMindMap([fn])
            elif ext in ('cw', 'cweb'):
                ic.importWebCommand([fn], "cweb")
            # Not useful. Use @auto x.json instead.
            # elif ext == 'json':
                # ic.importJSON([fn])
            elif fn.endswith('mm.html'):
                ic.importFreeMind([fn])
            elif ext in ('nw', 'noweb'):
                ic.importWebCommand([fn], "noweb")
            elif ext == 'txt':
                ic.importFlattenedOutline([fn])
            else:
                ic.importFilesCommand([fn], '@clean')
        c.raise_error_dialogs(kind='read')

    # Compatibility: used by unit tests.
    importAtFile = importAnyFile
    importAtRoot = importAnyFile
    importCWEBFiles = importAnyFile
    importDerivedFile = importAnyFile
    importFlattenedOutline = importAnyFile
    importMOREFiles = importAnyFile
    importNowebFiles = importAnyFile
    importTabFiles = importAnyFile
    #@+node:ekr.20161021130640.6: *5* c.looksLikeDerivedFile
    def looksLikeDerivedFile(self, fn):
        '''Return True if fn names a file that looks like an
        external file written by Leo.'''
        # c = self
        try:
            f = open(fn, 'r')
        except IOError:
            return False
        try:
            s = f.read()
        except Exception:
            s = ''
        finally:
            f.close()
        val = s.find('@+leo-ver=') > -1
        return val
    #@+node:ekr.20161021130640.7: *4* 'new'
    @cmd('new')
    def new(self, event=None, gui=None):
        '''Create a new Leo window.'''
        lm = g.app.loadManager
        # Clean out the update queue so it won't interfere with the new window.
        self.outerUpdate()
        # Send all log messages to the new frame.
        g.app.setLog(None)
        g.app.lockLog()
        c = g.app.newCommander(fileName=None, gui=gui)
        frame = c.frame
        g.app.unlockLog()
        frame.setInitialWindowGeometry()
        frame.deiconify()
        frame.lift()
        frame.resizePanesToRatio(frame.ratio, frame.secondary_ratio)
            # Resize the _new_ frame.
        c.frame.createFirstTreeNode()
        lm.createMenu(c)
        lm.finishOpen(c)
        g.app.writeWaitingLog(c)
        g.doHook("new", old_c=self, c=c, new_c=c)
        c.setLog()
        c.redraw()
        return c # For unit tests and scripts.
    #@+node:ekr.20161021130640.8: *4* 'open-outline'
    @cmd('open-outline')
    def open(self, event=None):
        '''Open a Leo window containing the contents of a .leo file.'''
        c = self
        #@+<< Set closeFlag if the only open window is empty >>
        #@+node:ekr.20161021130640.9: *5* << Set closeFlag if the only open window is empty >>
        #@+at
        # If this is the only open window was opened when the app started, and
        # the window has never been written to or saved, then we will
        # automatically close that window if this open command completes
        # successfully.
        #@@c
        closeFlag = (
            c.frame.startupWindow and # The window was open on startup
            not c.changed and not c.frame.saved and # The window has never been changed
            g.app.numberOfUntitledWindows == 1) # Only one untitled window has ever been opened
        #@-<< Set closeFlag if the only open window is empty >>
        table = [
            # 2010/10/09: Fix an interface blunder. Show all files by default.
            ("All files", "*"),
            ("Leo files", "*.leo"),
            ("Python files", "*.py"),]
        fileName = ''.join(c.k.givenArgs)
        if not fileName:
            fileName = g.app.gui.runOpenFileDialog(c,
                title="Open",
                filetypes=table,
                defaultextension=".leo")
        c.bringToFront()
        c.init_error_dialogs()
        ok = False
        if fileName:
            if fileName.endswith('.leo'):
                c2 = g.openWithFileName(fileName, old_c=c)
                if c2:
                    g.chdir(fileName)
                    g.setGlobalOpenDir(fileName)
                if c2 and closeFlag:
                    g.app.destroyWindow(c.frame)
            elif c.looksLikeDerivedFile(fileName):
                # Create an @file node for files containing Leo sentinels.
                ok = c.importCommands.importDerivedFiles(parent=c.p,
                    paths=[fileName], command='Open')
            else:
                # otherwise, create an @edit node.
                ok = c.createNodeFromExternalFile(fileName)
        c.raise_error_dialogs(kind='write')
        g.app.runAlreadyOpenDialog(c)
        # openWithFileName sets focus if ok.
        if not ok:
            c.initialFocusHelper()
    #@+node:ekr.20161021130640.10: *5* c.createNodeFromExternalFile
    def createNodeFromExternalFile(self, fn):
        '''Read the file into a node.
        Return None, indicating that c.open should set focus.'''
        c = self
        s, e = g.readFileIntoString(fn)
        if s is None: return
        head, ext = g.os_path_splitext(fn)
        if ext.startswith('.'): ext = ext[1:]
        language = g.app.extension_dict.get(ext)
        if language:
            prefix = '@color\n@language %s\n\n' % language
        else:
            prefix = '@killcolor\n\n'
        p2 = c.insertHeadline(op_name='Open File', as_child=False)
        p2.h = '@edit %s' % fn # g.shortFileName(fn)
        p2.b = prefix + s
        w = c.frame.body.wrapper
        if w: w.setInsertPoint(0)
        c.redraw()
        c.recolor()
    #@+node:ekr.20161021130640.11: *4* 'open-with'
    # This is *not* a command.
    # @cmd('open-with')
    def openWith(self, event=None, d=None):
        '''
        Handles the items in the Open With... menu.

        See ExternalFilesController.open_with for details about d.
        '''
        c = self
        if d and g.app.externalFilesController:
            # Select an ancestor @<file> node if possible.
            if not d.get('p'):
                p = c.p
                while p:
                    if p.isAnyAtFileNode():
                        d ['p'] = p
                        break
                    p.moveToParent()
            g.app.externalFilesController.open_with(c, d)
        elif not d:
            g.trace('can not happen: no d', g.callers())
    #@+node:ekr.20161021130640.12: *4* 'refresh-from-disk'
    @cmd('refresh-from-disk')
    def refreshFromDisk(self, event=None):
        '''Refresh an @<file> node from disk.'''
        c, p, u = self, self.p, self.undoer
        c.nodeConflictList = []
        fn = p.anyAtFileNodeName()
        if fn:
            b = u.beforeChangeTree(p)
            redraw_flag = True
            at = c.atFileCommands
            c.recreateGnxDict()
                # Fix bug 1090950 refresh from disk: cut node ressurection.
            i = g.skip_id(p.h, 0, chars='@')
            word = p.h[0: i]
            if word == '@auto':
                p.deleteAllChildren()
                at.readOneAtAutoNode(fn, p)
            elif word in ('@thin', '@file'):
                p.deleteAllChildren()
                at.read(p, force=True)
            elif word in ('@clean',):
                # Wishlist 148: use @auto parser if the node is empty.
                if p.b.strip() or p.hasChildren():
                    at.readOneAtCleanNode(p)
                else:
                    at.readOneAtAutoNode(fn, p)
            elif word == '@shadow ':
                p.deleteAllChildren()
                at.read(p, force=True, atShadow=True)
            elif word == '@edit':
                p.deleteAllChildren()
                at.readOneAtEditNode(fn, p)
            else:
                g.es_print('can not refresh from disk\n%s' % p.h)
                redraw_flag = False
        else:
            g.warning('not an @<file> node:\n%s' % (p.h))
            redraw_flag = False
        if redraw_flag:
            u.afterChangeTree(p, command='refresh-from-disk', bunch=b)
            # Create the 'Recovered Nodes' tree.
            c.fileCommands.handleNodeConflicts()
            c.redraw()
    #@+node:ekr.20161021130640.13: *4* 'save-file'
    @cmd('save-file')
    def save(self, event=None, fileName=None):
        '''Save a Leo outline to a file.'''
        c = self; p = c.p
        # Do this now: w may go away.
        w = g.app.gui.get_focus(c)
        inBody = g.app.gui.widget_name(w).startswith('body')
        if inBody:
            p.saveCursorAndScroll()
        if g.unitTesting and g.app.unitTestDict.get('init_error_dialogs') is not None:
            # A kludge for unit testing:
            # indicated that c.init_error_dialogs and c.raise_error_dialogs
            # will be called below, *without* actually saving the .leo file.
            c.init_error_dialogs()
            c.raise_error_dialogs(kind='write')
            return
        if g.app.disableSave:
            g.es("save commands disabled", color="purple")
            return
        c.init_error_dialogs()
        # 2013/09/28: use the fileName keyword argument if given.
        # This supports the leoBridge.
        # Make sure we never pass None to the ctor.
        if fileName:
            c.frame.title = g.computeWindowTitle(fileName)
            c.mFileName = fileName
        if not c.mFileName:
            c.frame.title = ""
            c.mFileName = ""
        if c.mFileName:
            # Calls c.setChanged(False) if no error.
            g.app.syntax_error_files = []
            c.fileCommands.save(c.mFileName)
            c.syntaxErrorDialog()
        else:
            root = c.rootPosition()
            if not root.next() and root.isAtEditNode():
                # There is only a single @edit node in the outline.
                # A hack to allow "quick edit" of non-Leo files.
                # See https://bugs.launchpad.net/leo-editor/+bug/381527
                fileName = None
                # Write the @edit node if needed.
                if root.isDirty():
                    c.atFileCommands.writeOneAtEditNode(root,
                        toString=False, force=True)
                c.setChanged(False)
            else:
                fileName = ''.join(c.k.givenArgs)
                if not fileName:
                    fileName = g.app.gui.runSaveFileDialog(c,
                        initialfile=c.mFileName,
                        title="Save",
                        filetypes=[("Leo files", "*.leo")],
                        defaultextension=".leo")
            c.bringToFront()
            if fileName:
                # Don't change mFileName until the dialog has suceeded.
                c.mFileName = g.ensure_extension(fileName, ".leo")
                c.frame.title = c.computeWindowTitle(c.mFileName)
                c.frame.setTitle(c.computeWindowTitle(c.mFileName))
                    # 2013/08/04: use c.computeWindowTitle.
                c.openDirectory = c.frame.openDirectory = g.os_path_dirname(c.mFileName)
                    # Bug fix in 4.4b2.
                if g.app.qt_use_tabs and hasattr(c.frame, 'top'):
                    c.frame.top.leo_master.setTabName(c, c.mFileName)
                c.fileCommands.save(c.mFileName)
                g.app.recentFilesManager.updateRecentFiles(c.mFileName)
                g.chdir(c.mFileName)
        # Done in FileCommands.save.
        # c.redraw_after_icons_changed()
        c.raise_error_dialogs(kind='write')
        # *Safely* restore focus, without using the old w directly.
        if inBody:
            c.bodyWantsFocus()
            p.restoreCursorAndScroll()
        else:
            c.treeWantsFocus()
    #@+node:ekr.20161021130640.14: *5* c.syntaxErrorDialog
    def syntaxErrorDialog(self):
        '''Warn about syntax errors in files.'''
        c = self
        if g.app.syntax_error_files and c.config.getBool('syntax-error-popup', default=False):
            aList = sorted(set(g.app.syntax_error_files))
            g.app.syntax_error_files = []
            message = 'Syntax error in:\n\n%s' % '\n'.join(aList)
            g.app.gui.runAskOkDialog(c,
                title='Syntax Error',
                message=message,
                text="Ok")
    #@+node:ekr.20161021130640.15: *4* 'save-all'
    @cmd('save-all')
    def saveAll(self, event=None):
        '''Save all open tabs windows/tabs.'''
        c = self
        c.save() # Force a write of the present window.
        for f in g.app.windowList:
            c = f.c
            if c.isChanged():
                c.save()
        # Restore the present tab.
        c = self
        dw = c.frame.top # A DynamicWindow
        dw.select(c)
    #@+node:ekr.20161021130640.16: *4* 'save-file-as'
    @cmd('save-file-as')
    def saveAs(self, event=None, fileName=None):
        '''Save a Leo outline to a file with a new filename.'''
        c = self; p = c.p
        # Do this now: w may go away.
        w = g.app.gui.get_focus(c)
        inBody = g.app.gui.widget_name(w).startswith('body')
        if inBody: p.saveCursorAndScroll()
        if g.app.disableSave:
            g.es("save commands disabled", color="purple")
            return
        c.init_error_dialogs()
        # 2013/09/28: add fileName keyword arg for leoBridge scripts.
        if fileName:
            c.frame.title = g.computeWindowTitle(fileName)
            c.mFileName = fileName
        # Make sure we never pass None to the ctor.
        if not c.mFileName:
            c.frame.title = ""
        if not fileName:
            fileName = ''.join(c.k.givenArgs)
        if not fileName:
            fileName = g.app.gui.runSaveFileDialog(c,
                initialfile=c.mFileName,
                title="Save As",
                filetypes=[("Leo files", "*.leo")],
                defaultextension=".leo")
        c.bringToFront()
        if fileName:
            # Fix bug 998090: save file as doesn't remove entry from open file list.
            if c.mFileName:
                g.app.forgetOpenFile(c.mFileName)
            # Don't change mFileName until the dialog has suceeded.
            c.mFileName = g.ensure_extension(fileName, ".leo")
            # Part of the fix for https://bugs.launchpad.net/leo-editor/+bug/1194209
            c.frame.title = title = c.computeWindowTitle(c.mFileName)
            c.frame.setTitle(title)
                # 2013/08/04: use c.computeWindowTitle.
            c.openDirectory = c.frame.openDirectory = g.os_path_dirname(c.mFileName)
                # Bug fix in 4.4b2.
            # Calls c.setChanged(False) if no error.
            if g.app.qt_use_tabs and hasattr(c.frame, 'top'):
                c.frame.top.leo_master.setTabName(c, c.mFileName)
            c.fileCommands.saveAs(c.mFileName)
            g.app.recentFilesManager.updateRecentFiles(c.mFileName)
            g.chdir(c.mFileName)
        # Done in FileCommands.saveAs.
        # c.redraw_after_icons_changed()
        c.raise_error_dialogs(kind='write')
        # *Safely* restore focus, without using the old w directly.
        if inBody:
            c.bodyWantsFocus()
            p.restoreCursorAndScroll()
        else:
            c.treeWantsFocus()
    #@+node:ekr.20161021130640.17: *4* 'save-file-to'
    @cmd('save-file-to')
    def saveTo(self, event=None, fileName=None):
        '''Save a Leo outline to a file, leaving the file associated with the Leo outline unchanged.'''
        c = self; p = c.p
        # Do this now: w may go away.
        w = g.app.gui.get_focus(c)
        inBody = g.app.gui.widget_name(w).startswith('body')
        if inBody:
            p.saveCursorAndScroll()
        if g.app.disableSave:
            g.es("save commands disabled", color="purple")
            return
        c.init_error_dialogs()
        old_mFileName = c.mFileName
            # 2015/04/21: Save.
        # 2013/09/28: add fileName keyword arg for leoBridge scripts.
        if fileName:
            c.frame.title = g.computeWindowTitle(fileName)
            c.mFileName = fileName
        # Make sure we never pass None to the ctor.
        if not c.mFileName:
            c.frame.title = ""
        # Add fileName keyword arg for leoBridge scripts.
        if not fileName:
            # set local fileName, _not_ c.mFileName
            fileName = ''.join(c.k.givenArgs)
        if not fileName:
            fileName = g.app.gui.runSaveFileDialog(c,
                initialfile=c.mFileName,
                title="Save To",
                filetypes=[("Leo files", "*.leo")],
                defaultextension=".leo")
        c.bringToFront()
        if fileName:
            fileName = g.ensure_extension(fileName, ".leo")
            c.fileCommands.saveTo(fileName)
            g.app.recentFilesManager.updateRecentFiles(fileName)
            g.chdir(fileName)
        c.mFileName = old_mFileName
            # 2015/04/21: save-to must not change c.mFileName.
        # Does not change icons status.
        # c.redraw_after_icons_changed()
        c.raise_error_dialogs(kind='write')
        # *Safely* restore focus, without using the old w directly.
        if inBody:
            c.bodyWantsFocus()
            p.restoreCursorAndScroll()
        else:
            c.treeWantsFocus()
    #@+node:ekr.20161021130640.18: *4* 'revert'
    @cmd('revert')
    def revert(self, event=None):
        '''Revert the contents of a Leo outline to last saved contents.'''
        c = self
        # Make sure the user wants to Revert.
        fn = c.mFileName
        if not fn:
            g.es('can not revert unnamed file.')
        if not g.os_path_exists(fn):
            g.es('Can not revert unsaved file: %s' % fn)
            return
        reply = g.app.gui.runAskYesNoDialog(c, "Revert",
            "Revert to previous version of %s?" % fn)
        c.bringToFront()
        if reply == "yes":
            g.app.loadManager.revertCommander(c)
    #@+node:ekr.20161021130640.19: *4* 'save-file-as-unzipped' & 'save-file-as-zipped'
    @cmd('save-file-as-unzipped')
    def saveAsUnzipped(self, event=None):
        '''Save a Leo outline to a file with a new filename,
        ensuring that the file is not compressed.'''
        self.saveAsZippedHelper(False)

    @cmd('save-file-as-zipped')
    def saveAsZipped(self, event=None):
        '''Save a Leo outline to a file with a new filename,
        ensuring that the file is compressed.'''
        self.saveAsZippedHelper(True)

    def saveAsZippedHelper(self, isZipped):
        c = self
        oldZipped = c.isZipped
        c.isZipped = isZipped
        try:
            c.saveAs()
        finally:
            c.isZipped = oldZipped
    #@+node:ekr.20161022115410.1: *3* Help commands
    #@+node:ekr.20161021130640.217: *4* 'about-leo'
    @cmd('about-leo')
    def about(self, event=None):
        '''Bring up an About Leo Dialog.'''
        c = self
        import datetime
        # Don't use triple-quoted strings or continued strings here.
        # Doing so would add unwanted leading tabs.
        version = g.app.signon + '\n\n'
        theCopyright = (
            "Copyright 1999-%s by Edward K. Ream\n" +
            "All Rights Reserved\n" +
            "Leo is distributed under the MIT License") % datetime.date.today().year
        url = "http://leoeditor.com/"
        email = "edreamleo@gmail.com"
        g.app.gui.runAboutLeoDialog(c, version, theCopyright, url, email)
    #@+node:ekr.20161021130640.221: *4* 'open-local-settings'
    @cmd('open-local-settings')
    def selectAtSettingsNode(self, event=None):
        '''Select the @settings node, if there is one.'''
        c = self
        p = c.config.settingsRoot()
        if p:
            c.selectPosition(p)
            c.redraw()
        else:
            g.es('no local @settings tree.')
    #@+node:ekr.20161021130640.216: *3* Open .leo file commands
    if 0:
        #@+others
        #@+node:ekr.20161021130640.222: *4* 'open-cheat-sheet-leo'
        @cmd('open-cheat-sheet-leo')
        def openCheatSheet(self, event=None, redraw=True):
            '''Open leo/doc/cheatSheet.leo'''
            c = self
            fn = g.os_path_finalize_join(g.app.loadDir, '..', 'doc', 'CheatSheet.leo')
            # g.es_debug(g.os_path_exists(fn),fn)
            if g.os_path_exists(fn):
                c2 = g.openWithFileName(fn, old_c=c)
                if redraw:
                    p = g.findNodeAnywhere(c2, "Leo's cheat sheet")
                    if p:
                        c2.selectPosition(p, enableRedrawFlag=False)
                        p.expand()
                    c2.redraw()
                return c2
            else:
                g.es('file not found: %s' % fn)
                return None
        #@+node:ekr.20161021130640.218: *4* 'open-leoDocs-leo'
        @cmd('open-leoDocs-leo')
        def leoDocumentation(self, event=None):
            '''Open LeoDocs.leo in a new Leo window.'''
            c = self
            name = "LeoDocs.leo"
            fileName = g.os_path_finalize_join(g.app.loadDir, "..", "doc", name)
            # Bug fix: 2012/04/09: only call g.openWithFileName if the file exists.
            if g.os_path_exists(fileName):
                c2 = g.openWithFileName(fileName, old_c=c)
                if c2: return
            g.es("not found:", name)
        #@+node:ekr.20161021130640.223: *4* 'open-leoPlugins-leo'
        @cmd('open-leoPlugins-leo')
        def openLeoPlugins(self, event=None):
            '''Open leoPlugins.leo in a new Leo window.'''
            c = self
            names = ('leoPlugins.leo', 'leoPluginsRef.leo',) # Used in error message.
            for name in names:
                fileName = g.os_path_finalize_join(g.app.loadDir, "..", "plugins", name)
                # Bug fix: 2012/04/09: only call g.openWithFileName if the file exists.
                if g.os_path_exists(fileName):
                    c2 = g.openWithFileName(fileName, old_c=c)
                    if c2: return
            g.es('not found:', ', '.join(names))
        #@+node:ekr.20161021130640.224: *4* 'open-leoPy-leo'
        @cmd('open-leoPy-leo')
        def openLeoPy(self, event=None):
            '''Open leoPy.leo in a new Leo window.'''
            c = self
            names = ('leoPy.leo', 'LeoPyRef.leo',) # Used in error message.
            for name in names:
                fileName = g.os_path_finalize_join(g.app.loadDir, "..", "core", name)
                # Only call g.openWithFileName if the file exists.
                if g.os_path_exists(fileName):
                    c2 = g.openWithFileName(fileName, old_c=c)
                    if c2: return
            g.es('not found:', ', '.join(names))
        #@+node:ekr.20161021130640.226: *4* 'open-leoSettings-leo'
        @cmd('open-leoSettings-leo')
        def openLeoSettings(self, event=None):
            '''Open leoSettings.leo in a new Leo window.'''
            c, lm = self, g.app.loadManager
            path = lm.computeLeoSettingsPath()
            if path:
                return g.openWithFileName(path, old_c=c)
            else:
                g.es('not found: leoSettings.leo')
                return None

        #@+node:ekr.20161022115224.1: *4* 'open-myLeoSettings-leo'
        @cmd('open-myLeoSettings-leo')
        def openMyLeoSettings(self, event=None):
            '''Open myLeoSettings.leo in a new Leo window.'''
            c, lm = self, g.app.loadManager
            path = lm.computeMyLeoSettingsPath()
            if path:
                return g.openWithFileName(path, old_c=c)
            else:
                g.es('not found: myLeoSettings.leo')
                return c.createMyLeoSettings()
        #@+node:ekr.20161021130640.227: *5* c.createMyLeoSettings
        def createMyLeoSettings(self):
            """createMyLeoSettings - Return true if myLeoSettings.leo created ok
            """
            name = "myLeoSettings.leo"
            c = self
            homeLeoDir = g.app.homeLeoDir
            loadDir = g.app.loadDir
            configDir = g.app.globalConfigDir
            # check it doesn't already exist
            for path in homeLeoDir, loadDir, configDir:
                fileName = g.os_path_join(path, name)
                if g.os_path_exists(fileName):
                    return None
            ok = g.app.gui.runAskYesNoDialog(c,
                title = 'Create myLeoSettings.leo?',
                message = 'Create myLeoSettings.leo in %s?' % (homeLeoDir),
            )
            if ok == 'no':
                return
            # get '@enabled-plugins' from g.app.globalConfigDir
            fileName = g.os_path_join(configDir, "leoSettings.leo")
            leosettings = g.openWithFileName(fileName, old_c=c)
            enabledplugins = g.findNodeAnywhere(leosettings, '@enabled-plugins')
            enabledplugins = enabledplugins.b
            leosettings.close()
            # now create "~/.leo/myLeoSettings.leo"
            fileName = g.os_path_join(homeLeoDir, name)
            c2 = g.openWithFileName(fileName, old_c=c)
            # add content to outline
            nd = c2.rootPosition()
            nd.h = "Settings README"
            nd.b = (
                "myLeoSettings.leo personal settings file created {time}\n\n"
                "Only nodes that are descendants of the @settings node are read.\n\n"
                "Only settings you need to modify should be in this file, do\n"
                "not copy large parts of leoSettings.py here.\n\n"
                "For more information see http://leoeditor.com/customizing.html"
                "".format(time=time.asctime())
            )
            nd = nd.insertAfter()
            nd.h = '@settings'
            nd = nd.insertAsNthChild(0)
            nd.h = '@enabled-plugins'
            nd.b = enabledplugins
            nd = nd.insertAfter()
            nd.h = '@keys'
            nd = nd.insertAsNthChild(0)
            nd.h = '@shortcuts'
            nd.b = (
                "# You can define keyboard shortcuts here of the form:\n"
                "#\n"
                "#    some-command Shift-F5\n"
            )
            c2.redraw()
            return c2
        #@+node:ekr.20161021130640.220: *4* 'open-quickstart-leo'
        @cmd('open-quickstart-leo')
        def leoQuickStart(self, event=None):
            '''Open quickstart.leo in a new Leo window.'''
            c = self; name = "quickstart.leo"
            fileName = g.os_path_finalize_join(g.app.loadDir, "..", "doc", name)
            # Bug fix: 2012/04/09: only call g.openWithFileName if the file exists.
            if g.os_path_exists(fileName):
                c2 = g.openWithFileName(fileName, old_c=c)
                if c2: return
            g.es("not found:", name)
        #@+node:ekr.20161021130640.225: *4* 'open-scripts-leo'
        @cmd('open-scripts-leo')
        def openLeoScripts(self, event=None):
            '''Open scripts.leo.'''
            c = self
            fileName = g.os_path_finalize_join(g.app.loadDir, '..', 'scripts', 'scripts.leo')
            # Bug fix: 2012/04/09: only call g.openWithFileName if the file exists.
            if g.os_path_exists(fileName):
                c2 = g.openWithFileName(fileName, old_c=c)
                if c2: return
            g.es('not found:', fileName)
        #@+node:ekr.20161021130640.230: *4* 'open-unittest-leo'
        @cmd('open-unittest-leo')
        def openUnittest(self, event=None):
            '''Open unittest.leo.'''
            c = self
            fileName = g.os_path_finalize_join(g.app.loadDir, '..', 'test', 'unitTest.leo')
            if g.os_path_exists(fileName):
                c2 = g.openWithFileName(fileName, old_c=c)
                if c2: return
            g.es('not found:', fileName)
        #@-others
    #@+node:ekr.20161022115523.1: *3* Open web pages commands
    #@+node:ekr.20161021130640.219: *4* 'open-online-home'
    @cmd('open-online-home')
    def leoHome(self, event=None):
        '''Open Leo's Home page in a web browser.'''
        import webbrowser
        url = "http://leoeditor.com/"
        try:
            webbrowser.open_new(url)
        except Exception:
            g.es("not found:", url)
    #@+node:ekr.20161021130640.228: *4* 'open-online-toc'
    @cmd('open-online-toc')
    def openLeoTOC(self, event=None):
        '''Open Leo's tutorials page in a web browser.'''
        import webbrowser
        url = "http://leoeditor.com/leo_toc.html"
        try:
            webbrowser.open_new(url)
        except Exception:
            g.es("not found:", url)
    #@+node:ekr.20161021130640.229: *4* 'open-online-tutorials'
    @cmd('open-online-tutorials')
    def openLeoTutorials(self, event=None):
        '''Open Leo's tutorials page in a web browser.'''
        import webbrowser
        url = "http://leoeditor.com/tutorial.html"
        try:
            webbrowser.open_new(url)
        except Exception:
            g.es("not found:", url)
    #@+node:ekr.20161021130640.232: *4* 'open-online-videos'
    @cmd('open-online-videos')
    def openLeoVideos(self, event=None):
        '''Open Leo's videos page in a web browser.'''
        import webbrowser
        url = "http://leoeditor.com/screencasts.html"
        try:
            webbrowser.open_new(url)
        except Exception:
            g.es("not found:", url)
    #@+node:ekr.20161021130640.231: *4* 'open-users-guide'
    @cmd('open-users-guide')
    def openLeoUsersGuide(self, event=None):
        '''Open Leo's users guide in a web browser.'''
        import webbrowser
        url = "http://leoeditor.com/usersguide.html"
        try:
            webbrowser.open_new(url)
        except Exception:
            g.es("not found:", url)
    #@+node:ekr.20161021130640.25: *3* Read & write commands
    #@+node:ekr.20161021130640.26: *4* 'read-at-auto-nodes'
    @cmd('read-at-auto-nodes')
    def readAtAutoNodes(self, event=None):
        '''Read all @auto nodes in the presently selected outline.'''
        c = self; u = c.undoer; p = c.p
        c.endEditing()
        c.init_error_dialogs()
        undoData = u.beforeChangeTree(p)
        c.importCommands.readAtAutoNodes()
        u.afterChangeTree(p, 'Read @auto Nodes', undoData)
        c.redraw()
        c.raise_error_dialogs(kind='read')
    #@+node:ekr.20161021130640.27: *4* 'read-at-file-nodes'
    @cmd('read-at-file-nodes')
    def readAtFileNodes(self, event=None):
        '''Read all @file nodes in the presently selected outline.'''
        c = self; u = c.undoer; p = c.p
        c.endEditing()
        # c.init_error_dialogs() # Done in at.readAll.
        undoData = u.beforeChangeTree(p)
        c.fileCommands.readAtFileNodes()
        u.afterChangeTree(p, 'Read @file Nodes', undoData)
        c.redraw()
        # c.raise_error_dialogs(kind='read') # Done in at.readAll.
    #@+node:ekr.20161021130640.28: *4* 'read-at-shadow-nodes'
    @cmd('read-at-shadow-nodes')
    def readAtShadowNodes(self, event=None):
        '''Read all @shadow nodes in the presently selected outline.'''
        c = self; u = c.undoer; p = c.p
        c.endEditing()
        c.init_error_dialogs()
        undoData = u.beforeChangeTree(p)
        c.atFileCommands.readAtShadowNodes(p)
        u.afterChangeTree(p, 'Read @shadow Nodes', undoData)
        c.redraw()
        c.raise_error_dialogs(kind='read')
    #@+node:ekr.20161021130640.29: *4* 'read-file-into-node'
    @cmd('read-file-into-node')
    def readFileIntoNode(self, event=None):
        '''Read a file into a single node.'''
        c = self
        undoType = 'Read File Into Node'
        c.endEditing()
        filetypes = [("All files", "*"), ("Python files", "*.py"), ("Leo files", "*.leo"),]
        fileName = g.app.gui.runOpenFileDialog(c,
            title="Read File Into Node",
            filetypes=filetypes,
            defaultextension=None)
        if not fileName: return
        s, e = g.readFileIntoString(fileName)
        if s is None:
            return
        g.chdir(fileName)
        s = '@nocolor\n' + s
        w = c.frame.body.wrapper
        p = c.insertHeadline(op_name=undoType)
        p.setHeadString('@read-file-into-node ' + fileName)
        p.setBodyString(s)
        w.setAllText(s)
        c.redraw(p)
    #@+node:ekr.20161021130640.30: *4* 'read-outline-only'
    @cmd('read-outline-only')
    def readOutlineOnly(self, event=None):
        '''Open a Leo outline from a .leo file, but do not read any derived files.'''
        c = self
        c.endEditing()
        fileName = g.app.gui.runOpenFileDialog(c,
            title="Read Outline Only",
            filetypes=[("Leo files", "*.leo"), ("All files", "*")],
            defaultextension=".leo")
        if not fileName:
            return
        try:
            theFile = open(fileName, 'r')
            g.chdir(fileName)
            c = g.app.newCommander(fileName)
            frame = c.frame
            frame.deiconify()
            frame.lift()
            c.fileCommands.readOutlineOnly(theFile, fileName) # closes file.
        except Exception:
            g.es("can not open:", fileName)
    #@+node:ekr.20161021130640.31: *4* 'write-file-from-node'
    @cmd('write-file-from-node')
    def writeFileFromNode(self, event=None):
        '''If node starts with @read-file-into-node, use the full path name in the headline.
        Otherwise, prompt for a file name.
        '''
        c = self; p = c.p
        c.endEditing()
        h = p.h.rstrip()
        s = p.b
        tag = '@read-file-into-node'
        if h.startswith(tag):
            fileName = h[len(tag):].strip()
        else:
            fileName = None
        if not fileName:
            filetypes = [("All files", "*"), ("Python files", "*.py"), ("Leo files", "*.leo"),]
            fileName = g.app.gui.runSaveFileDialog(c,
                initialfile=None,
                title='Write File From Node',
                filetypes=filetypes,
                defaultextension=None)
        if fileName:
            try:
                theFile = open(fileName, 'w')
                g.chdir(fileName)
            except IOError:
                theFile = None
            if theFile:
                if s.startswith('@nocolor\n'):
                    s = s[len('@nocolor\n'):]
                if not g.isPython3: # 2010/08/27
                    s = g.toEncodedString(s, reportErrors=True)
                theFile.write(s)
                theFile.flush()
                g.blue('wrote:', fileName)
                theFile.close()
            else:
                g.error('can not write %s', fileName)
    #@+node:ekr.20161021130640.20: *3* Recent Files commands
    #@+node:ekr.20161021130640.23: *4* 'clean-recent-files'
    @cmd('clean-recent-files')
    def cleanRecentFiles(self, event=None):
        '''Remove items from the recent files list that are no longer valid.'''
        c = self
        g.app.recentFilesManager.cleanRecentFiles(c)
    #@+node:ekr.20161021130640.21: *4* 'clear-recent-files'
    @cmd('clear-recent-files')
    def clearRecentFiles(self, event=None):
        """Clear the recent files list, then add the present file."""
        c = self
        g.app.recentFilesManager.clearRecentFiles(c)
    #@+node:ekr.20161021130640.24: *4* 'sort-recent-files'
    @cmd('sort-recent-files')
    def sortRecentFiles(self, event=None):
        '''Sort the recent files list.'''
        c = self
        g.app.recentFilesManager.sortRecentFiles(c)
    #@+node:ekr.20161021130640.22: *4* c.openRecentFile
    def openRecentFile(self, fn=None):
        c = self
        # Automatically close the previous window if...
        closeFlag = (
            c.frame.startupWindow and
                # The window was open on startup
            not c.changed and not c.frame.saved and
                # The window has never been changed
            g.app.numberOfUntitledWindows == 1)
                # Only one untitled window has ever been opened.
        if g.doHook("recentfiles1", c=c, p=c.p, v=c.p, fileName=fn, closeFlag=closeFlag):
            return
        c2 = g.openWithFileName(fn, old_c=c)
        if closeFlag and c2 and c2 != c:
            g.app.destroyWindow(c.frame)
            c2.setLog()
            g.doHook("recentfiles2",
                c=c2, p=c2.p, v=c2.p, fileName=fn, closeFlag=closeFlag)
    #@+node:ekr.20161021130640.32: *3* Tangle & Untange commands
    #@+node:ekr.20161021130640.35: *4* 'tangle'
    @cmd('tangle')
    def tangle(self, event=None):
        '''
        Tangle all @root nodes in the selected outline.

        **Important**: @root and all tangle and untangle commands are
        deprecated. They are documented nowhere but in these docstrings.
        '''
        c = self
        c.tangleCommands.tangle()
    #@+node:ekr.20161021130640.33: *4* 'tangle-all'
    @cmd('tangle-all')
    def tangleAll(self, event=None):
        '''
        Tangle all @root nodes in the entire outline.

        **Important**: @root and all tangle and untangle commands are
        deprecated. They are documented nowhere but in these docstrings.
        '''
        c = self
        c.tangleCommands.tangleAll()
    #@+node:ekr.20161021130640.34: *4* 'tangle-marked'
    @cmd('tangle-marked')
    def tangleMarked(self, event=None):
        '''
        Tangle all marked @root nodes in the entire outline.

        **Important**: @root and all tangle and untangle commands are
        deprecated. They are documented nowhere but in these docstrings.
        '''
        c = self
        c.tangleCommands.tangleMarked()
    #@+node:ekr.20161021130640.39: *4* 'untangle'
    @cmd('untangle')
    def untangle(self, event=None):
        '''Untangle all @root nodes in the selected outline.

        **Important**: @root and all tangle and untangle commands are
        deprecated. They are documented nowhere but in these docstrings.
        '''
        c = self
        c.tangleCommands.untangle()
        c.undoer.clearUndoState()
    #@+node:ekr.20161021130640.37: *4* 'untangle-all'
    @cmd('untangle-all')
    def untangleAll(self, event=None):
        '''
        Untangle all @root nodes in the entire outline.

        **Important**: @root and all tangle and untangle commands are
        deprecated. They are documented nowhere but in these docstrings.
        '''
        c = self
        c.tangleCommands.untangleAll()
        c.undoer.clearUndoState()
    #@+node:ekr.20161021130640.38: *4* 'untangle-marked'
    @cmd('untangle-marked')
    def untangleMarked(self, event=None):
        '''
        Untangle all marked @root nodes in the entire outline.

        **Important**: @root and all tangle and untangle commands are
        deprecated. They are documented nowhere but in these docstrings.
        '''
        c = self
        c.tangleCommands.untangleMarked()
        c.undoer.clearUndoState()
    #@-others
#@+node:ekr.20161021130640.102: ** Outline commands
if 0:
    #@+others
    #@+node:ekr.20161021130640.131: *3* Check outline commands
    #@+node:ekr.20161021130640.132: *4* 'check-outline'
    @cmd('check-outline')
    def fullCheckOutline(self, event=None):
        '''
        Performs a full check of the consistency of a .leo file.

        As of Leo 5.1, Leo performs checks of gnx's and outline structure
        before writes and after reads, pastes and undo/redo.
        '''
        return self.checkOutline(check_links=True)
    #@+node:ekr.20161021130640.133: *5* c.checkGnxs
    def checkGnxs(self):
        '''
        Check the consistency of all gnx's and remove any tnodeLists.
        Reallocate gnx's for duplicates or empty gnx's.
        Return the number of structure_errors found.
        '''
        c = self
        d = {} # Keys are gnx's; values are lists of vnodes with that gnx.
        ni = g.app.nodeIndices
        t1 = time.time()

        def new_gnx(v):
            '''Set v.fileIndex.'''
            v.fileIndex = ni.getNewIndex(v)

        count, gnx_errors = 0, 0
        for p in c.safe_all_positions():
            count += 1
            v = p.v
            if hasattr(v, "tnodeList"):
                delattr(v, "tnodeList")
                v._p_changed = True
            gnx = v.fileIndex
            if gnx:
                aSet = d.get(gnx, set())
                aSet.add(v)
                d[gnx] = aSet
            else:
                gnx_errors += 1
                new_gnx(v)
                g.es_print('empty v.fileIndex: %s new: %r' % (v, p.v.gnx), color='red')
        for gnx in sorted(d.keys()):
            aList = list(d.get(gnx))
            if len(aList) != 1:
                g.es_print('multiple vnodes with gnx: %r' % (gnx), color='red')
                for v in aList:
                    gnx_errors += 1
                    g.es_print('new gnx: %s %s' % (v.fileIndex, v), color='red')
                    new_gnx(v)
        ok = not gnx_errors and not g.app.structure_errors
        t2 = time.time()
        if not ok:
            g.es_print('check-outline ERROR! %s %s nodes, %s gnx errors, %s structure errors' % (
                c.shortFileName(), count, gnx_errors, g.app.structure_errors), color='red')
        elif c.verbose_check_outline and not g.unitTesting:
            print('check-outline OK: %4.2f sec. %s %s nodes' % (t2 - t1, c.shortFileName(), count))
        return g.app.structure_errors
    #@+node:ekr.20161021130640.134: *5* c.checkLinks & helpers
    def checkLinks(self):
        '''Check the consistency of all links in the outline.'''
        c = self
        t1 = time.time()
        count, errors = 0, 0
        for p in c.safe_all_positions():
            count += 1
            try:
                c.checkThreadLinks(p)
                c.checkSiblings(p)
                c.checkParentAndChildren(p)
            except AssertionError:
                errors += 1
                junk, value, junk = sys.exc_info()
                g.error("test failed at position %s\n%s" % (repr(p), value))
        t2 = time.time()
        g.es_print('check-links: %4.2f sec. %s %s nodes' % (
            t2 - t1, c.shortFileName(), count), color='blue')
        return errors
    #@+node:ekr.20161021130640.135: *6* c.checkParentAndChildren
    def checkParentAndChildren(self, p):
        '''Check consistency of parent and child data structures.'''
        # Check consistency of parent and child links.
        if p.hasParent():
            n = p.childIndex()
            assert p == p.parent().moveToNthChild(n), "p!=parent.moveToNthChild"
        for child in p.children():
            assert p == child.parent(), "p!=child.parent"
        if p.hasNext():
            assert p.next().parent() == p.parent(), "next.parent!=parent"
        if p.hasBack():
            assert p.back().parent() == p.parent(), "back.parent!=parent"
        # Check consistency of parent and children arrays.
        # Every nodes gets visited, so a strong test need only check consistency
        # between p and its parent, not between p and its children.
        parent_v = p._parentVnode()
        n = p.childIndex()
        assert parent_v.children[n] == p.v, 'fail 1'
    #@+node:ekr.20161021130640.136: *6* c.checkSiblings
    def checkSiblings(self, p):
        '''Check the consistency of next and back links.'''
        back = p.back()
        next = p.next()
        if back:
            assert p == back.next(), 'p!=p.back().next(),  back: %s\nback.next: %s' % (
                back, back.next())
        if next:
            assert p == next.back(), 'p!=p.next().back, next: %s\nnext.back: %s' % (
                next, next.back())
    #@+node:ekr.20161021130640.137: *6* c.checkThreadLinks
    def checkThreadLinks(self, p):
        '''Check consistency of threadNext & threadBack links.'''
        threadBack = p.threadBack()
        threadNext = p.threadNext()
        if threadBack:
            assert p == threadBack.threadNext(), "p!=p.threadBack().threadNext()"
        if threadNext:
            assert p == threadNext.threadBack(), "p!=p.threadNext().threadBack()"
    #@+node:ekr.20161022114909.1: *5* c.checkOutline
    def checkOutline(self, event=None, check_links=False):
        """
        Check for errors in the outline.
        Return the count of serious structure errors.
        """
        c = self
        g.app.structure_errors = 0
        structure_errors = c.checkGnxs()
        if check_links and not structure_errors:
            structure_errors += c.checkLinks()
        return structure_errors
    #@+node:ekr.20161021130640.145: *4* 'dump-outline'
    @cmd('dump-outline')
    def dumpOutline(self, event=None):
        """ Dump all nodes in the outline."""
        c = self
        seen = {}
        print('')
        print('=' * 40)
        v = c.hiddenRootNode
        v.dump()
        seen[v] = True
        for p in c.all_positions():
            if p.v not in seen:
                seen[p.v] = True
                p.v.dump()
    #@+node:ekr.20161021130640.115: *3* Clone commands
    #@+node:ekr.20161021130640.119: *4* 'clone-node'
    @cmd('clone-node')
    def clone(self, event=None):
        '''Create a clone of the selected outline.'''
        c = self; u = c.undoer; p = c.p
        if not p:
            return None
        undoData = c.undoer.beforeCloneNode(p)
        c.endEditing() # Capture any changes to the headline.
        clone = p.clone()
        dirtyVnodeList = clone.setAllAncestorAtFileNodesDirty()
        c.setChanged(True)
        if c.validateOutline():
            u.afterCloneNode(clone, 'Clone Node', undoData, dirtyVnodeList=dirtyVnodeList)
            c.redraw(clone)
            return clone # For mod_labels and chapters plugins.
        else:
            clone.doDelete()
            c.setCurrentPosition(p)
            return None
    #@+node:ekr.20161021130640.120: *4* 'clone-to-at-spot'
    @cmd('clone-to-at-spot')
    def cloneToAtSpot(self, event=None):
        '''
        Create a clone of the selected node and move it to the last @spot node
        of the outline. Create the @spot node if necessary.
        '''
        c = self; u = c.undoer; p = c.p
        if not p:
            return
        # 2015/12/27: fix bug 220: do not allow clone-to-at-spot on @spot node.
        if p.h.startswith('@spot'):
            g.es("can not clone @spot node", color='red')
            return
        last_spot = None
        for p2 in c.all_positions():
            if g.match_word(p2.h, 0, '@spot'):
                last_spot = p2.copy()
        if not last_spot:
            last = c.lastTopLevel()
            last_spot = last.insertAfter()
            last_spot.h = '@spot'
        undoData = c.undoer.beforeCloneNode(p)
        c.endEditing() # Capture any changes to the headline.
        clone = p.copy()
        clone._linkAsNthChild(last_spot,
                              n=last_spot.numberOfChildren(),
                              adjust=True)
        dirtyVnodeList = clone.setAllAncestorAtFileNodesDirty()
        c.setChanged(True)
        if c.validateOutline():
            u.afterCloneNode(clone,
                             'Clone Node',
                             undoData,
                             dirtyVnodeList=dirtyVnodeList)
            c.contractAllHeadlines()
            c.redraw()
            c.selectPosition(clone)
        else:
            clone.doDelete()
            c.setCurrentPosition(p)
    #@+node:ekr.20161021130640.121: *4* 'clone-node-to-last-node'
    @cmd('clone-node-to-last-node')
    def cloneToLastNode(self, event=None):
        '''
        Clone the selected node and move it to the last node.
        Do *not* change the selected node.
        '''
        c, p, u = self, self.p, self.undoer
        if not p: return
        prev = p.copy()
        undoData = c.undoer.beforeCloneNode(p)
        c.endEditing() # Capture any changes to the headline.
        clone = p.clone()
        last = c.rootPosition()
        while last and last.hasNext():
            last.moveToNext()
        clone.moveAfter(last)
        dirtyVnodeList = clone.setAllAncestorAtFileNodesDirty()
        c.setChanged(True)
        u.afterCloneNode(clone, 'Clone Node To Last', undoData, dirtyVnodeList=dirtyVnodeList)
        c.redraw(prev)
        # return clone # For mod_labels and chapters plugins.
    #@+node:ekr.20161021130640.104: *3* Cut, copy & paste outline commands
    #@+node:ekr.20161021130640.105: *4* 'cut-node'
    @cmd('cut-node')
    def cutOutline(self, event=None):
        '''Delete the selected outline and send it to the clipboard.'''
        c = self
        if c.canDeleteHeadline():
            c.copyOutline()
            c.deleteOutline("Cut Node")
            c.recolor()
    #@+node:ekr.20161021130640.106: *4* 'copy-node'
    @cmd('copy-node')
    def copyOutline(self, event=None):
        '''Copy the selected outline to the clipboard.'''
        # Copying an outline has no undo consequences.
        c = self
        c.endEditing()
        s = c.fileCommands.putLeoOutline()
        g.app.paste_c = c
        g.app.gui.replaceClipboardWith(s)
    #@+node:ekr.20161021130640.107: *4* 'paste-node'
    # To cut and paste between apps, just copy into an empty body first, then copy to Leo's clipboard.

    @cmd('paste-node')
    def pasteOutline(self, event=None,
        reassignIndices=True,
        redrawFlag=True,
        s=None,
        tempOutline=False, # True: don't make entries in the gnxDict.
        undoFlag=True
    ):
        '''
        Paste an outline into the present outline from the clipboard.
        Nodes do *not* retain their original identify.
        '''
        c = self
        if s is None:
            s = g.app.gui.getTextFromClipboard()
        pasteAsClone = not reassignIndices
        if pasteAsClone and g.app.paste_c != c:
            g.es('illegal paste-retaining-clones', color='red')
            g.es('only valid in same outline.')
            return
        undoType = 'Paste Node' if reassignIndices else 'Paste As Clone'
        c.endEditing()
        if not s or not c.canPasteOutline(s):
            return # This should never happen.
        isLeo = g.match(s, 0, g.app.prolog_prefix_string)
        vnodeInfoDict = c.computeVnodeInfoDict() if pasteAsClone else {}
        # create a *position* to be pasted.
        if isLeo:
            pasted = c.fileCommands.getLeoOutlineFromClipboard(s, reassignIndices, tempOutline)
        if not pasted:
            # 2016/10/06:
            # We no longer support pasting MORE outlines. Use import-MORE-files instead.
            return None
        if pasteAsClone:
            copiedBunchList = c.computeCopiedBunchList(pasted, vnodeInfoDict)
        else:
            copiedBunchList = []
        if undoFlag:
            undoData = c.undoer.beforeInsertNode(c.p,
                pasteAsClone=pasteAsClone, copiedBunchList=copiedBunchList)
        c.validateOutline()
        c.checkOutline()
        c.selectPosition(pasted)
        pasted.setDirty()
        c.setChanged(True)
        # paste as first child if back is expanded.
        back = pasted.back()
        if back and back.hasChildren() and back.isExpanded():
            # 2011/06/21: fixed hanger: test back.hasChildren().
            pasted.moveToNthChildOf(back, 0)
        if pasteAsClone:
            # Set dirty bits for ancestors of *all* pasted nodes.
            # Note: the setDescendentsDirty flag does not do what we want.
            for p in pasted.self_and_subtree():
                p.setAllAncestorAtFileNodesDirty(
                    setDescendentsDirty=False)
        if undoFlag:
            c.undoer.afterInsertNode(pasted, undoType, undoData)
        if redrawFlag:
            c.redraw(pasted)
            c.recolor()
        return pasted
    #@+node:ekr.20161021130640.108: *5* c.computeVnodeInfoDict
    #@+at
    # 
    # We don't know yet which nodes will be affected by the paste, so we remember
    # everything. This is expensive, but foolproof.
    # 
    # The alternative is to try to remember the 'before' values of nodes in the
    # FileCommands read logic. Several experiments failed, and the code is very ugly.
    # In short, it seems wise to do things the foolproof way.
    # 
    #@@c

    def computeVnodeInfoDict(self):
        c, d = self, {}
        for v in c.all_unique_nodes():
            if v not in d:
                d[v] = g.Bunch(v=v, head=v.h, body=v.b)
        return d
    #@+node:ekr.20161021130640.109: *5* c.computeCopiedBunchList
    def computeCopiedBunchList(self, pasted, vnodeInfoDict):
        # Create a dict containing only copied vnodes.
        d = {}
        for p in pasted.self_and_subtree():
            d[p.v] = p.v
        # g.trace(sorted(list(d.keys())))
        aList = []
        for v in vnodeInfoDict:
            if d.get(v):
                bunch = vnodeInfoDict.get(v)
                aList.append(bunch)
        return aList
    #@+node:ekr.20161021130640.110: *4* 'paste-retaining-clones'
    @cmd('paste-retaining-clones')
    def pasteOutlineRetainingClones(self, event=None):
        '''Paste an outline into the present outline from the clipboard.
        Nodes *retain* their original identify.'''
        c = self
        return c.pasteOutline(reassignIndices=False)
    #@+node:ekr.20161021130640.146: *3* Expand & contract commands
    #@+node:ekr.20161021130640.148: *4* 'contract-all'
    @cmd('contract-all')
    def contractAllHeadlines(self, event=None):
        '''Contract all nodes in the outline.'''
        c = self
        for p in c.all_positions():
            p.contract()
        # Select the topmost ancestor of the presently selected node.
        p = c.p
        while p and p.hasParent():
            p.moveToParent()
        c.redraw(p, setFocus=True)
        c.expansionLevel = 1 # Reset expansion level.
    #@+node:ekr.20161021130640.149: *4* 'contract-all-other-nodes'
    @cmd('contract-all-other-nodes')
    def contractAllOtherNodes(self, event=None):
        '''Contract all nodes except those needed to make the
        presently selected node visible.'''
        c = self; leaveOpen = c.p
        for p in c.rootPosition().self_and_siblings():
            c.contractIfNotCurrent(p, leaveOpen)
        c.redraw()
    #@+node:ekr.20161021130640.150: *5* c.contractIfNotCurrent
    def contractIfNotCurrent(self, p, leaveOpen):
        c = self
        if p == leaveOpen or not p.isAncestorOf(leaveOpen):
            p.contract()
        for child in p.children():
            if child != leaveOpen and child.isAncestorOf(leaveOpen):
                c.contractIfNotCurrent(child, leaveOpen)
            else:
                for p2 in child.self_and_subtree():
                    p2.contract()
    #@+node:ekr.20161021130640.151: *4* 'contract-node'
    @cmd('contract-node')
    def contractNode(self, event=None):
        '''Contract the presently selected node.'''
        c = self; p = c.p
        p.contract()
        if p.isCloned():
            c.redraw() # A full redraw is necessary to handle clones.
        else:
            c.redraw_after_contract(p=p, setFocus=True)
    #@+node:ekr.20161021130640.152: *4* 'contract-or-go-left'
    @cmd('contract-or-go-left')
    def contractNodeOrGoToParent(self, event=None):
        """Simulate the left Arrow Key in folder of Windows Explorer."""
        trace = False and not g.unitTesting
        c, cc, p = self, self.chapterController, self.p
        parent = p.parent()
        redraw = False
        if trace: g.trace(p.h,
            'children:', p.hasChildren(),
            'expanded:', p.isExpanded(),
            'shouldBeExpanded:', c.shouldBeExpanded(p))
        # Bug fix: 2016/04/19: test p.v.isExpanded().
        if p.hasChildren() and (p.v.isExpanded() or p.isExpanded()):
            c.contractNode()
        elif parent and parent.isVisible(c):
            # New in Leo 4.9.1: contract all children first.
            if c.collapse_on_lt_arrow:
                for child in parent.children():
                    if child.isExpanded():
                        child.contract()
                        redraw = True
            if cc and cc.inChapter and parent.h.startswith('@chapter '):
                if trace: g.trace('root is selected chapter', parent.h)
            else:
                if trace: g.trace('not an @chapter node', parent.h)
                c.goToParent()
        # This is a bit off-putting.
        # elif not parent and not c.hoistStack:
            # p = c.rootPosition()
            # while p:
                # if p.isExpanded():
                    # p.contract()
                    # redraw = True
                # p.moveToNext()
        if redraw:
            c.redraw()
    #@+node:ekr.20161021130640.153: *4* 'contract-parent'
    @cmd('contract-parent')
    def contractParent(self, event=None):
        '''Contract the parent of the presently selected node.'''
        c = self; p = c.p
        parent = p.parent()
        if not parent: return
        parent.contract()
        c.redraw_after_contract(p=parent)
    #@+node:ekr.20161021130640.154: *4* 'expand-all'
    @cmd('expand-all')
    def expandAllHeadlines(self, event=None):
        '''Expand all headlines.
        Warning: this can take a long time for large outlines.'''
        c = self
        p = c.rootPosition()
        while p:
            c.expandSubtree(p)
            p.moveToNext()
        c.redraw_after_expand(p=c.rootPosition(), setFocus=True)
        c.expansionLevel = 0 # Reset expansion level.
    #@+node:ekr.20161021130640.155: *4* 'expand-all-subheads'
    @cmd('expand-all-subheads')
    def expandAllSubheads(self, event=None):
        '''Expand all children of the presently selected node.'''
        c = self; p = c.p
        if not p: return
        child = p.firstChild()
        c.expandSubtree(p)
        while child:
            c.expandSubtree(child)
            child = child.next()
        c.redraw(p, setFocus=True)
    #@+node:ekr.20161021130640.160: *4* 'expand-ancestors-only'
    @cmd('expand-ancestors-only')
    def expandOnlyAncestorsOfNode(self, event=None, p=None):
        '''Contract all nodes in the outline.'''
        trace = False and not g.unitTesting
        c = self
        level = 1
        if p: c.selectPosition(p) # 2013/12/25
        root = c.p
        if trace: g.trace(root.h)
        for p in c.all_unique_positions():
            p.v.expandedPositions = []
            p.v.contract()
        for p in root.parents():
            if trace: g.trace('call p.expand', p.h, p._childIndex)
            p.expand()
            level += 1
        c.redraw(setFocus=True)
        c.expansionLevel = level # Reset expansion level.
    #@+node:ekr.20161021130640.159: *4* 'expand-and-go-right' & 'expand-or-go-right'
    @cmd('expand-and-go-right')
    def expandNodeAndGoToFirstChild(self, event=None):
        """If a node has children, expand it if needed and go to the first child."""
        c = self; p = c.p
        if p.hasChildren():
            if p.isExpanded():
                c.selectPosition(p.firstChild())
            else:
                c.expandNode()
                # Fix bug 930726
                # expandNodeAndGoToFirstChild only expands or only goes to first child .
                c.selectPosition(p.firstChild())
        c.treeFocusHelper()

    @cmd('expand-or-go-right')
    def expandNodeOrGoToFirstChild(self, event=None):
        """Simulate the Right Arrow Key in folder of Windows Explorer."""
        c = self; p = c.p
        if p.hasChildren():
            if not p.isExpanded():
                c.expandNode() # Calls redraw_after_expand.
            else:
                c.redraw_after_expand(p.firstChild(), setFocus=True)
    #@+node:ekr.20161021130640.157: *4* 'expand-next-level'
    @cmd('expand-next-level')
    def expandNextLevel(self, event=None):
        '''Increase the expansion level of the outline and
        Expand all nodes at that level or lower.'''
        c = self
        # Expansion levels are now local to a particular tree.
        if c.expansionNode != c.p:
            c.expansionLevel = 1
            c.expansionNode = c.p.copy()
        # g.trace(c.expansionLevel)
        self.expandToLevel(c.expansionLevel + 1)
    #@+node:ekr.20161021130640.158: *4* 'expand-node'
    @cmd('expand-node')
    def expandNode(self, event=None):
        '''Expand the presently selected node.'''
        trace = False and not g.unitTesting
        c = self; p = c.p
        p.expand()
        if p.isCloned():
            if trace: g.trace('***redraw')
            c.redraw() # Bug fix: 2009/10/03.
        else:
            c.redraw_after_expand(p, setFocus=True)
    #@+node:ekr.20161021130640.161: *4* 'expand-prev-level'
    @cmd('expand-prev-level')
    def expandPrevLevel(self, event=None):
        '''Decrease the expansion level of the outline and
        Expand all nodes at that level or lower.'''
        c = self
        # Expansion levels are now local to a particular tree.
        if c.expansionNode != c.p:
            c.expansionLevel = 1
            c.expansionNode = c.p.copy()
        self.expandToLevel(max(1, c.expansionLevel - 1))
    #@+node:ekr.20161021130640.156: *4* 'expand-to-level-*'
    @cmd('expand-to-level-1')
    def expandLevel1(self, event=None):
        '''Expand the outline to level 1'''
        self.expandToLevel(1)

    @cmd('expand-to-level-2')
    def expandLevel2(self, event=None):
        '''Expand the outline to level 2'''
        self.expandToLevel(2)

    @cmd('expand-to-level-3')
    def expandLevel3(self, event=None):
        '''Expand the outline to level 3'''
        self.expandToLevel(3)

    @cmd('expand-to-level-4')
    def expandLevel4(self, event=None):
        '''Expand the outline to level 4'''
        self.expandToLevel(4)

    @cmd('expand-to-level-5')
    def expandLevel5(self, event=None):
        '''Expand the outline to level 5'''
        self.expandToLevel(5)

    @cmd('expand-to-level-6')
    def expandLevel6(self, event=None):
        '''Expand the outline to level 6'''
        self.expandToLevel(6)

    @cmd('expand-to-level-7')
    def expandLevel7(self, event=None):
        '''Expand the outline to level 7'''
        self.expandToLevel(7)

    @cmd('expand-to-level-8')
    def expandLevel8(self, event=None):
        '''Expand the outline to level 8'''
        self.expandToLevel(8)

    @cmd('expand-to-level-9')
    def expandLevel9(self, event=None):
        '''Expand the outline to level 9'''
        self.expandToLevel(9)
    #@+node:ekr.20161021130640.163: *4* c.contractSubtree
    def contractSubtree(self, p):
        for p in p.subtree():
            p.contract()
    #@+node:ekr.20161021130640.164: *4* c.expandSubtree
    def expandSubtree(self, v):
        c = self
        last = v.lastNode()
        while v and v != last:
            v.expand()
            v = v.threadNext()
        c.redraw()
    #@+node:ekr.20161021130640.165: *4* c.expandToLevel
    def expandToLevel(self, level):
        trace = False and not g.unitTesting
        c = self
        n = c.p.level()
        old_expansion_level = c.expansionLevel
        max_level = 0
        for p in c.p.self_and_subtree():
            if p.level() - n + 1 < level:
                p.expand()
                max_level = max(max_level, p.level() - n + 1)
            else:
                p.contract()
        c.expansionNode = c.p.copy()
        c.expansionLevel = max_level + 1
        if c.expansionLevel != old_expansion_level:
            if trace: g.trace('level', level, 'max_level', max_level+1)
            c.redraw()
        # It's always useful to announce the level.
        # c.k.setLabelBlue('level: %s' % (max_level+1))
        # g.es('level', max_level + 1)
        c.frame.putStatusLine('level: %s' % (max_level+1))
            # bg='red', fg='red')
    #@+node:ekr.20161021130640.190: *3* Goto commands
    #@+node:ekr.20161021130640.200: *4* 'find-next-clone'
    @cmd('find-next-clone')
    def findNextClone(self, event=None):
        '''Select the next cloned node.'''
        c = self; p = c.p; cc = c.chapterController
        if not p: return
        if p.isCloned():
            p.moveToThreadNext()
        flag = False
        while p:
            if p.isCloned():
                flag = True; break
            else:
                p.moveToThreadNext()
        if flag:
            if cc:
                # name = cc.findChapterNameForPosition(p)
                cc.selectChapterByName('main')
            c.selectPosition(p)
            c.redraw_after_select(p)
        else:
            g.blue('no more clones')
    #@+node:ekr.20161021130640.192: *4* 'go-back'
    @cmd('go-back')
    def goPrevVisitedNode(self, event=None):
        '''Select the previously visited node.'''
        c = self
        p = c.nodeHistory.goPrev()
        if p:
            c.nodeHistory.skipBeadUpdate = True
            try:
                c.selectPosition(p)
            finally:
                c.nodeHistory.skipBeadUpdate = False
                c.redraw_after_select(p)
    #@+node:ekr.20161021130640.191: *4* 'go-forward'
    @cmd('go-forward')
    def goNextVisitedNode(self, event=None):
        '''Select the next visited node.'''
        c = self
        p = c.nodeHistory.goNext()
        if p:
            c.nodeHistory.skipBeadUpdate = True
            try:
                c.selectPosition(p)
            finally:
                c.nodeHistory.skipBeadUpdate = False
                c.redraw_after_select(p)
    #@+node:ekr.20161021130640.193: *4* 'goto-first-node'
    @cmd('goto-first-node')
    def goToFirstNode(self, event=None):
        '''Select the first node of the entire outline.'''
        c = self
        p = c.rootPosition()
        c.selectPosition(p)
        c.expandOnlyAncestorsOfNode()
        c.redraw()
        c.treeSelectHelper(p)
    #@+node:ekr.20161021130640.194: *4* 'goto-first-sibling'
    @cmd('goto-first-sibling')
    def goToFirstSibling(self, event=None):
        '''Select the first sibling of the selected node.'''
        c = self; p = c.p
        if p.hasBack():
            while p.hasBack():
                p.moveToBack()
        c.treeSelectHelper(p)
    #@+node:ekr.20161021130640.195: *4* 'goto-first-visible-node'
    @cmd('goto-first-visible-node')
    def goToFirstVisibleNode(self, event=None):
        '''Select the first visible node of the selected chapter or hoist.'''
        c = self
        p = c.firstVisible()
        if p:
            c.selectPosition(p)
            c.expandOnlyAncestorsOfNode()
            c.redraw_after_select(p)
            c.treeSelectHelper(p)
    #@+node:ekr.20161021130640.196: *4* 'goto-last-node'
    @cmd('goto-last-node')
    def goToLastNode(self, event=None):
        '''Select the last node in the entire tree.'''
        c = self
        p = c.rootPosition()
        while p and p.hasThreadNext():
            p.moveToThreadNext()
        c.selectPosition(p)
        c.treeSelectHelper(p)
        c.expandOnlyAncestorsOfNode()
        c.redraw()
    #@+node:ekr.20161021130640.197: *4* 'goto-last-sibling'
    @cmd('goto-last-sibling')
    def goToLastSibling(self, event=None):
        '''Select the last sibling of the selected node.'''
        c = self; p = c.p
        if p.hasNext():
            while p.hasNext():
                p.moveToNext()
        c.treeSelectHelper(p)
    #@+node:ekr.20161021130640.198: *4* 'goto-last-visible-node'
    @cmd('goto-last-visible-node')
    def goToLastVisibleNode(self, event=None):
        '''Select the last visible node of selected chapter or hoist.'''
        c = self
        p = c.lastVisible()
        if p:
            c.selectPosition(p)
            c.expandOnlyAncestorsOfNode()
            c.redraw_after_select(p)
            c.treeSelectHelper(p)
    #@+node:ekr.20161021130640.201: *4* 'goto-next-changed'
    @cmd('goto-next-changed')
    def goToNextDirtyHeadline(self, event=None):
        '''Select the node that is marked as changed.'''
        c = self; p = c.p
        if not p: return
        p.moveToThreadNext()
        wrapped = False
        while 1:
            if p and p.isDirty():
                break
            elif p:
                p.moveToThreadNext()
            elif wrapped:
                break
            else:
                wrapped = True
                p = c.rootPosition()
        if not p: g.blue('done')
        c.treeSelectHelper(p) # Sets focus.
    #@+node:ekr.20161021130640.199: *4* 'goto-next-clone'
    @cmd('goto-next-clone')
    def goToNextClone(self, event=None):
        '''
        Select the next node that is a clone of the selected node.
        If the selected node is not a clone, do find-next-clone.
        '''
        c, p = self, self.p
        cc = c.chapterController; p = c.p
        if not p:
            return
        if not p.isCloned():
            c.findNextClone()
            return
        v = p.v
        p.moveToThreadNext()
        wrapped = False
        while 1:
            if p and p.v == v:
                break
            elif p:
                p.moveToThreadNext()
            elif wrapped:
                break
            else:
                wrapped = True
                p = c.rootPosition()
        if p:
            if cc:
                # Fix bug #252: goto-next clone activate chapter.
                # https://github.com/leo-editor/leo-editor/issues/252
                chapter = cc.getSelectedChapter()
                old_name = chapter and chapter.name
                new_name = cc.findChapterNameForPosition(p)
                if new_name == old_name:
                    c.selectPosition(p)
                    c.redraw_after_select(p)
                else:
                    c.selectPosition(p)
                    cc.selectChapterByName(new_name)
            else:
                c.selectPosition(p)
                c.redraw_after_select(p)
        else:
            g.blue('done')
    #@+node:ekr.20161021130640.202: *4* 'goto-next-marked'
    @cmd('goto-next-marked')
    def goToNextMarkedHeadline(self, event=None):
        '''Select the next marked node.'''
        c = self; p = c.p
        if not p: return
        p.moveToThreadNext()
        wrapped = False
        while 1:
            if p and p.isMarked():
                break
            elif p:
                p.moveToThreadNext()
            elif wrapped:
                break
            else:
                wrapped = True
                p = c.rootPosition()
        if not p: g.blue('done')
        c.treeSelectHelper(p) # Sets focus.
    #@+node:ekr.20161021130640.207: *4* 'goto-next-node'
    @cmd('goto-next-node')
    def selectThreadNext(self, event=None):
        '''Select the node following the selected node in outline order.'''
        c = self; p = c.p
        if not p: return
        p.moveToThreadNext()
        c.treeSelectHelper(p)
    #@+node:ekr.20161021130640.203: *4* 'goto-next-sibling'
    @cmd('goto-next-sibling')
    def goToNextSibling(self, event=None):
        '''Select the next sibling of the selected node.'''
        c = self; p = c.p
        c.treeSelectHelper(p and p.next())
    #@+node:ekr.20161021130640.209: *4* 'goto-next-visible'
    @cmd('goto-next-visible')
    def selectVisNext(self, event=None):
        '''Select the visible node following the presently selected node.'''
        c, p = self, self.p
        if not p:
            return
        if c.canSelectVisNext():
            p.moveToVisNext(c)
            c.treeSelectHelper(p)
        else:
            c.endEditing() # 2011/05/28: A special case.
    #@+node:ekr.20161021130640.204: *4* 'goto-parent'
    @cmd('goto-parent')
    def goToParent(self, event=None):
        '''Select the parent of the selected node.'''
        c = self; p = c.p
        c.treeSelectHelper(p and p.parent())
    #@+node:ekr.20161021130640.206: *4* 'goto-prev-node'
    @cmd('goto-prev-node')
    def selectThreadBack(self, event=None):
        '''Select the node preceding the selected node in outline order.'''
        c = self; p = c.p
        if not p: return
        p.moveToThreadBack()
        c.treeSelectHelper(p)
    #@+node:ekr.20161021130640.205: *4* 'goto-prev-sibling'
    @cmd('goto-prev-sibling')
    def goToPrevSibling(self, event=None):
        '''Select the previous sibling of the selected node.'''
        c = self; p = c.p
        c.treeSelectHelper(p and p.back())
    #@+node:ekr.20161021130640.208: *4* 'goto-prev-visible'
    @cmd('goto-prev-visible')
    def selectVisBack(self, event=None):
        '''Select the visible node preceding the presently selected node.'''
        # This has an up arrow for a control key.
        c, p = self, self.p
        if not p:
            return
        if c.canSelectVisBack():
            p.moveToVisBack(c)
            c.treeSelectHelper(p)
        else:
            c.endEditing() # 2011/05/28: A special case.
    #@+node:ekr.20161021130640.111: *3* Hoist, promote & demote commands
    #@+node:ekr.20161021130640.112: *4* 'de-hoist' & 'dehoist'
    @cmd('de-hoist')
    @cmd('dehoist')
    def dehoist(self, event=None):
        '''Undo a previous hoist of an outline.'''
        c = self
        if not c.p or not c.hoistStack:
            return
        # Don't de-hoist an @chapter node.
        if c.chapterController and c.p.h.startswith('@chapter '):
            if not g.unitTesting:
                g.es('can not de-hoist an @chapter node.',color='blue')
            return
        bunch = c.hoistStack.pop()
        p = bunch.p
        if bunch.expanded: p.expand()
        else: p.contract()
        c.setCurrentPosition(p)
        c.redraw()
        c.frame.clearStatusLine()
        c.frame.putStatusLine("De-Hoist: " + p.h)
        c.undoer.afterDehoist(p, 'DeHoist')
        g.doHook('hoist-changed', c=c)
    #@+node:ekr.20161021130640.181: *4* 'demote'
    @cmd('demote')
    def demote(self, event=None):
        '''Make all following siblings children of the selected node.'''
        c = self; u = c.undoer
        p = c.p
        if not p or not p.hasNext():
            c.treeFocusHelper()
            return
        # Make sure all the moves will be valid.
        next = p.next()
        while next:
            if not c.checkMoveWithParentWithWarning(next, p, True):
                c.treeFocusHelper()
                return
            next.moveToNext()
        c.endEditing()
        parent_v = p._parentVnode()
        n = p.childIndex()
        followingSibs = parent_v.children[n + 1:]
        # g.trace('sibs2\n',g.listToString(followingSibs2))
        # Remove the moved nodes from the parent's children.
        parent_v.children = parent_v.children[: n + 1]
        # Add the moved nodes to p's children
        p.v.children.extend(followingSibs)
        # Adjust the parent links in the moved nodes.
        # There is no need to adjust descendant links.
        for child in followingSibs:
            child.parents.remove(parent_v)
            child.parents.append(p.v)
        p.expand()
        # Even if p is an @ignore node there is no need to mark the demoted children dirty.
        dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
        c.setChanged(True)
        u.afterDemote(p, followingSibs, dirtyVnodeList)
        c.redraw(p, setFocus=True)
        c.updateSyntaxColorer(p) # Moving can change syntax coloring.
    #@+node:ekr.20161021130640.114: *4* 'hoist'
    @cmd('hoist')
    def hoist(self, event=None):
        '''Make only the selected outline visible.'''
        c = self
        p = c.p
        if not p:
            return
        # Don't hoist an @chapter node.
        if c.chapterController and p.h.startswith('@chapter '):
            if not g.unitTesting:
                g.es('can not hoist an @chapter node.',color='blue')
            return
        # Remember the expansion state.
        bunch = g.Bunch(p=p.copy(), expanded=p.isExpanded())
        c.hoistStack.append(bunch)
        p.expand()
        c.redraw(p)
        c.frame.clearStatusLine()
        c.frame.putStatusLine("Hoist: " + p.h)
        c.undoer.afterHoist(p, 'Hoist')
        g.doHook('hoist-changed', c=c)
    #@+node:ekr.20161021130640.188: *4* 'promote'
    @cmd('promote')
    def promote(self, event=None, undoFlag=True, redrawFlag=True):
        '''Make all children of the selected nodes siblings of the selected node.'''
        c = self; u = c.undoer; p = c.p
        if not p or not p.hasChildren():
            c.treeFocusHelper()
            return
        isAtIgnoreNode = p.isAtIgnoreNode()
        inAtIgnoreRange = p.inAtIgnoreRange()
        c.endEditing()
        parent_v = p._parentVnode()
        children = p.v.children
        # Add the children to parent_v's children.
        n = p.childIndex() + 1
        z = parent_v.children[:]
        parent_v.children = z[: n]
        parent_v.children.extend(children)
        parent_v.children.extend(z[n:])
        # Remove v's children.
        p.v.children = []
        # Adjust the parent links in the moved children.
        # There is no need to adjust descendant links.
        for child in children:
            child.parents.remove(p.v)
            child.parents.append(parent_v)
        c.setChanged(True)
        if undoFlag:
            if not inAtIgnoreRange and isAtIgnoreNode:
                # The promoted nodes have just become newly unignored.
                dirtyVnodeList = p.setDirty() # Mark descendent @thin nodes dirty.
            else: # No need to mark descendents dirty.
                dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
            u.afterPromote(p, children, dirtyVnodeList)
        if redrawFlag:
            c.redraw(p, setFocus=True)
            c.updateSyntaxColorer(p) # Moving can change syntax coloring.
    #@+node:ekr.20161021130640.113: *4* c.clearAllHoists
    def clearAllHoists(self):
        '''Undo a previous hoist of an outline.'''
        c = self
        c.hoistStack = []
        c.frame.putStatusLine("Hoists cleared")
        g.doHook('hoist-changed', c=c)
    #@+node:ekr.20161022114506.1: *3* Insert & delete outline commands
    #@+node:ekr.20161021130640.122: *4* 'delete-node'
    @cmd('delete-node')
    def deleteOutline(self, event=None, op_name="Delete Node"):
        """Deletes the selected outline."""
        c, u = self, self.undoer
        p = c.p
        if not p: return
        c.endEditing() # Make sure we capture the headline for Undo.
        if p.hasVisBack(c): newNode = p.visBack(c)
        else: newNode = p.next() # _not_ p.visNext(): we are at the top level.
        if not newNode: return
        undoData = u.beforeDeleteNode(p)
        dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
        p.doDelete(newNode)
        c.setChanged(True)
        u.afterDeleteNode(newNode, op_name, undoData, dirtyVnodeList=dirtyVnodeList)
        c.redraw(newNode)
        c.validateOutline()
    #@+node:ekr.20161021130640.123: *4* 'insert-child'
    @cmd('insert-child')
    def insertChild(self, event=None):
        '''Insert a node after the presently selected node.'''
        c = self
        return c.insertHeadline(event=event, op_name='Insert Child', as_child=True)
    #@+node:ekr.20161021130640.124: *4* 'insert-node'
    @cmd('insert-node')
    def insertHeadline(self, event=None, op_name="Insert Node", as_child=False):
        '''Insert a node after the presently selected node.'''
        trace = False and not g.unitTesting
        c = self; u = c.undoer
        current = c.p
        if not current: return
        c.endEditing()
        if trace: g.trace('==========', c.p.h, g.app.gui.get_focus())
        undoData = c.undoer.beforeInsertNode(current)
        # Make sure the new node is visible when hoisting.
        if (as_child or
            (current.hasChildren() and current.isExpanded()) or
            (c.hoistStack and current == c.hoistStack[-1].p)
        ):
            if c.config.getBool('insert_new_nodes_at_end'):
                p = current.insertAsLastChild()
            else:
                p = current.insertAsNthChild(0)
        else:
            p = current.insertAfter()
        g.doHook('create-node', c=c, p=p)
        p.setDirty(setDescendentsDirty=False)
        dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
        c.setChanged(True)
        u.afterInsertNode(p, op_name, undoData, dirtyVnodeList=dirtyVnodeList)
        c.redrawAndEdit(p, selectAll=True)
        return p
    #@+node:ekr.20161021130640.125: *4* 'insert-node-before'
    @cmd('insert-node-before')
    def insertHeadlineBefore(self, event=None):
        '''Insert a node before the presently selected node.'''
        c, current, u = self, self.p, self.undoer
        op_name = 'Insert Node Before'
        if not current: return
        # Can not insert before the base of a hoist.
        if c.hoistStack and current == c.hoistStack[-1].p:
            g.warning('can not insert a node before the base of a hoist')
            return
        c.endEditing()
        undoData = u.beforeInsertNode(current)
        p = current.insertBefore()
        g.doHook('create-node', c=c, p=p)
        p.setDirty(setDescendentsDirty=False)
        dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
        c.setChanged(True)
        u.afterInsertNode(p, op_name, undoData, dirtyVnodeList=dirtyVnodeList)
        c.redrawAndEdit(p, selectAll=True)
        return p
    #@+node:ekr.20161021130640.166: *3* Mark commands
    #@+node:ekr.20161021130640.167: *4* 'clone-marked-nodes'
    @cmd('clone-marked-nodes')
    def cloneMarked(self, event=None):
        """Clone all marked nodes as children of a new node."""
        c = self; u = c.undoer; p1 = c.p.copy()
        # Create a new node to hold clones.
        parent = p1.insertAfter()
        parent.h = 'Clones of marked nodes'
        cloned, n, p = [], 0, c.rootPosition()
        while p:
            # Careful: don't clone already-cloned nodes.
            if p == parent:
                p.moveToNodeAfterTree()
            elif p.isMarked() and p.v not in cloned:
                cloned.append(p.v)
                if 0: # old code
                    # Calling p.clone would cause problems
                    p.clone().moveToLastChildOf(parent)
                else: # New code.
                    # Create the clone directly as a child of parent.
                    p2 = p.copy()
                    n = parent.numberOfChildren()
                    p2._linkAsNthChild(parent, n, adjust=True)
                p.moveToNodeAfterTree()
                n += 1
            else:
                p.moveToThreadNext()
        if n:
            c.setChanged(True)
            parent.expand()
            c.selectPosition(parent)
            u.afterCloneMarkedNodes(p1)
        else:
            parent.doDelete()
            c.selectPosition(p1)
        if not g.unitTesting:
            g.blue('cloned %s nodes' % (n))
        c.redraw()
    #@+node:ekr.20161021130640.168: *4* 'copy-marked-nodes'
    @cmd('copy-marked-nodes')
    def copyMarked(self, event=None):
        """Copy all marked nodes as children of a new node."""
        c = self; u = c.undoer; p1 = c.p.copy()
        # Create a new node to hold clones.
        parent = p1.insertAfter()
        parent.h = 'Copies of marked nodes'
        copied, n, p = [], 0, c.rootPosition()
        while p:
            # Careful: don't clone already-cloned nodes.
            if p == parent:
                p.moveToNodeAfterTree()
            elif p.isMarked() and p.v not in copied:
                copied.append(p.v)
                p2 = p.copyWithNewVnodes(copyMarked=True)
                p2._linkAsNthChild(parent, n, adjust=True)
                p.moveToNodeAfterTree()
                n += 1
            else:
                p.moveToThreadNext()
        if n:
            c.setChanged(True)
            parent.expand()
            c.selectPosition(parent)
            u.afterCopyMarkedNodes(p1)
        else:
            parent.doDelete()
            c.selectPosition(p1)
        if not g.unitTesting:
            g.blue('copied %s nodes' % (n))
        c.redraw()
    #@+node:ekr.20161021130640.169: *4* 'delete-marked-nodes'
    @cmd('delete-marked-nodes')
    def deleteMarked(self, event=None):
        """Delete all marked nodes."""
        c = self; u = c.undoer; p1 = c.p.copy()
        undo_data, p = [], c.rootPosition()
        while p:
            if p.isMarked():
                undo_data.append(p.copy())
                next = p.positionAfterDeletedTree()
                p.doDelete()
                p = next
            else:
                p.moveToThreadNext()
        if undo_data:
            u.afterDeleteMarkedNodes(undo_data, p1)
            if not g.unitTesting:
                g.blue('deleted %s nodes' % (len(undo_data)))
            c.setChanged(True)
        # Don't even *think* about restoring the old position.
        c.contractAllHeadlines()
        c.selectPosition(c.rootPosition())
        c.redraw()
    #@+node:ekr.20161021130640.176: *4* 'mark'
    @cmd('mark')
    def markHeadline(self, event=None):
        '''Toggle the mark of the selected node.'''
        c = self; u = c.undoer; p = c.p
        if not p: return
        c.endEditing()
        undoType = 'Unmark' if p.isMarked() else 'Mark'
        bunch = u.beforeMark(p, undoType)
        if p.isMarked():
            c.clearMarked(p)
        else:
            c.setMarked(p)
        dirtyVnodeList = p.setDirty()
        c.setChanged(True)
        u.afterMark(p, undoType, bunch, dirtyVnodeList=dirtyVnodeList)
        c.redraw_after_icons_changed()
    #@+node:ekr.20161021130640.172: *4* 'mark-changed-items'
    @cmd('mark-changed-items')
    def markChangedHeadlines(self, event=None):
        '''Mark all nodes that have been changed.'''
        c = self; u = c.undoer; undoType = 'Mark Changed'
        current = c.p
        c.endEditing()
        u.beforeChangeGroup(current, undoType)
        for p in c.all_unique_positions():
            if p.isDirty() and not p.isMarked():
                bunch = u.beforeMark(p, undoType)
                c.setMarked(p)
                c.setChanged(True)
                u.afterMark(p, undoType, bunch)
        u.afterChangeGroup(current, undoType)
        if not g.unitTesting:
            g.blue('done')
        c.redraw_after_icons_changed()
    #@+node:ekr.20161021130640.177: *4* 'mark-subheads'
    @cmd('mark-subheads')
    def markSubheads(self, event=None):
        '''Mark all children of the selected node as changed.'''
        c = self; u = c.undoer; undoType = 'Mark Subheads'
        current = c.p
        if not current: return
        c.endEditing()
        u.beforeChangeGroup(current, undoType)
        dirtyVnodeList = []
        for p in current.children():
            if not p.isMarked():
                bunch = u.beforeMark(p, undoType)
                c.setMarked(p)
                dirtyVnodeList2 = p.setDirty()
                dirtyVnodeList.extend(dirtyVnodeList2)
                c.setChanged(True)
                u.afterMark(p, undoType, bunch)
        u.afterChangeGroup(current, undoType, dirtyVnodeList=dirtyVnodeList)
        c.redraw_after_icons_changed()
    #@+node:ekr.20161021130640.170: *4* 'move-marked-nodes'
    @cmd('move-marked-nodes')
    def moveMarked(self, event=None):
        '''
        Move all marked nodes as children of a new node.
        This command is not undoable.
        Consider using clone-marked-nodes, followed by copy/paste instead.
        '''
        c = self
        p1 = c.p.copy()
        # Check for marks.
        for v in c.all_unique_nodes():
            if v.isMarked():
                break
        else:
            return g.warning('no marked nodes')
        result = g.app.gui.runAskYesNoDialog(c,
            'Move Marked Nodes?',
            message='move-marked-nodes is not undoable\nProceed?',
        )
        if result == 'no':
            return
        # Create a new *root* node to hold the moved nodes.
        # This node's position remains stable while other nodes move.
        parent = c.createMoveMarkedNode()
        assert not parent.isMarked()
        moved = []
        p = c.rootPosition()
        while p:
            assert parent == c.rootPosition()
            # Careful: don't move already-moved nodes.
            if p.isMarked() and not parent.isAncestorOf(p):
                moved.append(p.copy())
                next = p.positionAfterDeletedTree()
                p.moveToLastChildOf(parent)
                    # This does not change parent's position.
                p = next
            else:
                p.moveToThreadNext()
        if moved:
            # Find a position p2 outside of parent's tree with p2.v == p1.v.
            # Such a position may not exist.
            p2 = c.rootPosition()
            while p2:
                if p2 == parent:
                    p2.moveToNodeAfterTree()
                elif p2.v == p1.v:
                    break
                else:
                    p2.moveToThreadNext()
            else:
                # Not found.  Move to last top-level.
                p2 = c.lastTopLevel()
            parent.moveAfter(p2)
            # u.afterMoveMarkedNodes(moved, p1)
            if not g.unitTesting:
                g.blue('moved %s nodes' % (len(moved)))
            c.setChanged(True)
        # c.contractAllHeadlines()
            # Causes problems when in a chapter.
        c.selectPosition(parent)
        c.redraw()
    #@+node:ekr.20161021130640.171: *5* c.createMoveMarkedNode
    def createMoveMarkedNode(self):
        c = self
        oldRoot = c.rootPosition()
        p = oldRoot.insertAfter()
        p.moveToRoot(oldRoot)
        c.setHeadString(p, 'Moved marked nodes')
        return p
    #@+node:ekr.20161021130640.178: *4* 'unmark-all'
    @cmd('unmark-all')
    def unmarkAll(self, event=None):
        '''Unmark all nodes in the entire outline.'''
        c = self; u = c.undoer; undoType = 'Unmark All'
        current = c.p
        if not current: return
        c.endEditing()
        u.beforeChangeGroup(current, undoType)
        changed = False
        p = None # To keep pylint happy.
        for p in c.all_unique_positions():
            if p.isMarked():
                bunch = u.beforeMark(p, undoType)
                # c.clearMarked(p) # Very slow: calls a hook.
                p.v.clearMarked()
                p.v.setDirty()
                u.afterMark(p, undoType, bunch)
                changed = True
        dirtyVnodeList = [p.v for p in c.all_unique_positions() if p.v.isDirty()]
        if changed:
            g.doHook("clear-all-marks", c=c, p=p, v=p)
            c.setChanged(True)
        u.afterChangeGroup(current, undoType, dirtyVnodeList=dirtyVnodeList)
        c.redraw_after_icons_changed()
    #@+node:ekr.20161021130640.174: *4* c.markAllAtFileNodesDirty
    def markAllAtFileNodesDirty(self, event=None):
        '''Mark all @file nodes as changed.'''
        c = self; p = c.rootPosition()
        c.endEditing()
        while p:
            if p.isAtFileNode() and not p.isDirty():
                p.setDirty()
                c.setChanged(True)
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
        c.redraw_after_icons_changed()
    #@+node:ekr.20161021130640.175: *4* c.markAtFileNodesDirty
    def markAtFileNodesDirty(self, event=None):
        '''Mark all @file nodes in the selected tree as changed.'''
        c = self
        p = c.p
        if not p: return
        c.endEditing()
        after = p.nodeAfterTree()
        while p and p != after:
            if p.isAtFileNode() and not p.isDirty():
                p.setDirty()
                c.setChanged(True)
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
        c.redraw_after_icons_changed()
    #@+node:ekr.20161021130640.173: *4* c.markChangedRoots
    def markChangedRoots(self, event=None):
        '''Mark all changed @root nodes.'''
        c = self; u = c.undoer; undoType = 'Mark Changed'
        current = c.p
        c.endEditing()
        u.beforeChangeGroup(current, undoType)
        for p in c.all_unique_positions():
            if p.isDirty() and not p.isMarked():
                s = p.b
                flag, i = g.is_special(s, 0, "@root")
                if flag:
                    bunch = u.beforeMark(p, undoType)
                    c.setMarked(p)
                    c.setChanged(True)
                    u.afterMark(p, undoType, bunch)
        u.afterChangeGroup(current, undoType)
        if not g.unitTesting:
            g.blue('done')
        c.redraw_after_icons_changed()
    #@+node:ekr.20161021130640.179: *3* Move & drag node commands
    #@+node:ekr.20161021130640.182: *4* 'move-outline-down'
    #@+at
    # Moving down is more tricky than moving up; we can't move p to be a child of
    # itself. An important optimization: we don't have to call
    # checkMoveWithParentWithWarning() if the parent of the moved node remains the
    # same.
    #@@c

    @cmd('move-outline-down')
    def moveOutlineDown(self, event=None):
        '''Move the selected node down.'''
        c = self; u = c.undoer; p = c.p
        if not p: return
        if not c.canMoveOutlineDown():
            if c.hoistStack: self.cantMoveMessage()
            c.treeFocusHelper()
            return
        inAtIgnoreRange = p.inAtIgnoreRange()
        parent = p.parent()
        next = p.visNext(c)
        while next and p.isAncestorOf(next):
            next = next.visNext(c)
        if not next:
            if c.hoistStack: self.cantMoveMessage()
            c.treeFocusHelper()
            return
        c.endEditing()
        undoData = u.beforeMoveNode(p)
        #@+<< Move p down & set moved if successful >>
        #@+node:ekr.20161021130640.183: *5* << Move p down & set moved if successful >>
        if next.hasChildren() and next.isExpanded():
            # Attempt to move p to the first child of next.
            moved = c.checkMoveWithParentWithWarning(p, next, True)
            if moved:
                dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
                p.moveToNthChildOf(next, 0)
        else:
            # Attempt to move p after next.
            moved = c.checkMoveWithParentWithWarning(p, next.parent(), True)
            if moved:
                dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
                p.moveAfter(next)
        # Patch by nh2: 0004-Add-bool-collapse_nodes_after_move-option.patch
        if c.collapse_nodes_after_move and moved and c.sparse_move and parent and not parent.isAncestorOf(p):
            # New in Leo 4.4.2: contract the old parent if it is no longer the parent of p.
            parent.contract()
        #@-<< Move p down & set moved if successful >>
        if moved:
            if inAtIgnoreRange and not p.inAtIgnoreRange():
                # The moved nodes have just become newly unignored.
                p.setDirty() # Mark descendent @thin nodes dirty.
            else: # No need to mark descendents dirty.
                dirtyVnodeList2 = p.setAllAncestorAtFileNodesDirty()
                dirtyVnodeList.extend(dirtyVnodeList2)
            c.setChanged(True)
            u.afterMoveNode(p, 'Move Down', undoData, dirtyVnodeList)
        c.redraw(p, setFocus=True)
        c.updateSyntaxColorer(p) # Moving can change syntax coloring.
    #@+node:ekr.20161021130640.184: *4* 'move-outline-left'
    @cmd('move-outline-left')
    def moveOutlineLeft(self, event=None):
        '''Move the selected node left if possible.'''
        c = self; u = c.undoer; p = c.p
        if not p: return
        if not c.canMoveOutlineLeft():
            if c.hoistStack: self.cantMoveMessage()
            c.treeFocusHelper()
            return
        if not p.hasParent():
            c.treeFocusHelper()
            return
        inAtIgnoreRange = p.inAtIgnoreRange()
        parent = p.parent()
        c.endEditing()
        undoData = u.beforeMoveNode(p)
        dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
        p.moveAfter(parent)
        if inAtIgnoreRange and not p.inAtIgnoreRange():
            # The moved nodes have just become newly unignored.
            p.setDirty() # Mark descendent @thin nodes dirty.
        else: # No need to mark descendents dirty.
            dirtyVnodeList2 = p.setAllAncestorAtFileNodesDirty()
            dirtyVnodeList.extend(dirtyVnodeList2)
        c.setChanged(True)
        u.afterMoveNode(p, 'Move Left', undoData, dirtyVnodeList)
        # Patch by nh2: 0004-Add-bool-collapse_nodes_after_move-option.patch
        if c.collapse_nodes_after_move and c.sparse_move: # New in Leo 4.4.2
            parent.contract()
        c.redraw_now(p, setFocus=True)
        c.recolor_now() # Moving can change syntax coloring.
    #@+node:ekr.20161021130640.185: *4* 'move-outline-right'
    @cmd('move-outline-right')
    def moveOutlineRight(self, event=None):
        '''Move the selected node right if possible.'''
        c = self; u = c.undoer; p = c.p
        if not p: return
        if not c.canMoveOutlineRight(): # 11/4/03: Support for hoist.
            if c.hoistStack: self.cantMoveMessage()
            c.treeFocusHelper()
            return
        back = p.back()
        if not back:
            c.treeFocusHelper()
            return
        if not c.checkMoveWithParentWithWarning(p, back, True):
            c.treeFocusHelper()
            return
        c.endEditing()
        undoData = u.beforeMoveNode(p)
        dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
        n = back.numberOfChildren()
        p.moveToNthChildOf(back, n)
        # Moving an outline right can never bring it outside the range of @ignore.
        dirtyVnodeList2 = p.setAllAncestorAtFileNodesDirty()
        dirtyVnodeList.extend(dirtyVnodeList2)
        c.setChanged(True)
        u.afterMoveNode(p, 'Move Right', undoData, dirtyVnodeList)
        # g.trace(p)
        c.redraw_now(p, setFocus=True)
        c.recolor_now()
    #@+node:ekr.20161021130640.186: *4* 'move-outline-up'
    @cmd('move-outline-up')
    def moveOutlineUp(self, event=None):
        '''Move the selected node up if possible.'''
        trace = False and not g.unitTesting
        c = self; u = c.undoer; p = c.p
        if not p: return
        if not c.canMoveOutlineUp(): # Support for hoist.
            if c.hoistStack: self.cantMoveMessage()
            c.treeFocusHelper()
            return
        back = p.visBack(c)
        if not back:
            if trace: g.trace('no visBack')
            return
        inAtIgnoreRange = p.inAtIgnoreRange()
        back2 = back.visBack(c)
        c.endEditing()
        undoData = u.beforeMoveNode(p)
        dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
        moved = False
        #@+<< Move p up >>
        #@+node:ekr.20161021130640.187: *5* << Move p up >>
        if trace:
            g.trace("visBack", back)
            g.trace("visBack2", back2)
            g.trace("back2.hasChildren", back2 and back2.hasChildren())
            g.trace("back2.isExpanded", back2 and back2.isExpanded())
        parent = p.parent()
        if not back2:
            if c.hoistStack: # hoist or chapter.
                limit, limitIsVisible = c.visLimit()
                assert limit
                if limitIsVisible:
                    # canMoveOutlineUp should have caught this.
                    g.trace('can not happen. In hoist')
                else:
                    # g.trace('chapter first child')
                    moved = True
                    p.moveToFirstChildOf(limit)
            else:
                # p will be the new root node
                p.moveToRoot(oldRoot=c.rootPosition())
                moved = True
        elif back2.hasChildren() and back2.isExpanded():
            if c.checkMoveWithParentWithWarning(p, back2, True):
                moved = True
                p.moveToNthChildOf(back2, 0)
        else:
            if c.checkMoveWithParentWithWarning(p, back2.parent(), True):
                moved = True
                p.moveAfter(back2)
        # Patch by nh2: 0004-Add-bool-collapse_nodes_after_move-option.patch
        if c.collapse_nodes_after_move and moved and c.sparse_move and parent and not parent.isAncestorOf(p):
            # New in Leo 4.4.2: contract the old parent if it is no longer the parent of p.
            parent.contract()
        #@-<< Move p up >>
        if moved:
            if inAtIgnoreRange and not p.inAtIgnoreRange():
                # The moved nodes have just become newly unignored.
                dirtyVnodeList2 = p.setDirty() # Mark descendent @thin nodes dirty.
            else: # No need to mark descendents dirty.
                dirtyVnodeList2 = p.setAllAncestorAtFileNodesDirty()
            dirtyVnodeList.extend(dirtyVnodeList2)
            c.setChanged(True)
            u.afterMoveNode(p, 'Move Right', undoData, dirtyVnodeList)
        c.redraw(p, setFocus=True)
        c.updateSyntaxColorer(p) # Moving can change syntax coloring.
    #@+node:ekr.20161021130640.180: *4* c.cantMoveMessage
    def cantMoveMessage(self):
        c = self; h = c.rootPosition().h
        kind = 'chapter' if h.startswith('@chapter') else 'hoist'
        g.warning("can't move node out of", kind)
    #@+node:ekr.20161021130640.118: *4* c.checkDrag
    def checkDrag(self, root, target):
        """Return False if target is any descendant of root."""
        c = self
        message = "Can not drag a node into its descendant tree."
        for z in root.subtree():
            if z == target:
                if g.app.unitTesting:
                    g.app.unitTestDict['checkMoveWithParentWithWarning'] = True
                else:
                    c.alert(message)
                return False
        return True
    #@+node:ekr.20161021130640.117: *4* c.checkMoveWithParentWithWarning
    def checkMoveWithParentWithWarning(self, root, parent, warningFlag):
        """Return False if root or any of root's descendents is a clone of
        parent or any of parents ancestors."""
        c = self
        message = "Illegal move or drag: no clone may contain a clone of itself"
        # g.trace("root",root,"parent",parent)
        clonedVnodes = {}
        for ancestor in parent.self_and_parents():
            if ancestor.isCloned():
                v = ancestor.v
                clonedVnodes[v] = v
        if not clonedVnodes:
            return True
        for p in root.self_and_subtree():
            if p.isCloned() and clonedVnodes.get(p.v):
                if g.app.unitTesting:
                    g.app.unitTestDict['checkMoveWithParentWithWarning'] = True
                elif warningFlag:
                    c.alert(message)
                return False
        return True
    #@+node:ekr.20161021130640.127: *3* Sort commands
    #@+node:ekr.20161021130640.129: *4* 'sort-children'
    # New in Leo 4.7 final: this method no longer supports
    # the 'cmp' keyword arg.

    @cmd('sort-children')
    def sortChildren(self, event=None, key=None, reverse=False):
        '''Sort the children of a node.'''
        c = self; p = c.p
        if p and p.hasChildren():
            c.sortSiblings(p=p.firstChild(), sortChildren=True, key=key, reverse=reverse)
    #@+node:ekr.20161021130640.130: *4* 'sort-siblings'
    # New in Leo 4.7 final: this method no longer supports
    # the 'cmp' keyword arg.

    @cmd('sort-siblings')
    def sortSiblings(self, event=None, key=None, p=None, sortChildren=False,
                      reverse=False):
        '''Sort the siblings of a node.'''
        c = self; u = c.undoer
        if not p : p = c.p
        if not p: return
        c.endEditing()
        undoType = 'Sort Children' if sortChildren else 'Sort Siblings'
        parent_v = p._parentVnode()
        parent = p.parent()
        oldChildren = parent_v.children[:]
        newChildren = parent_v.children[:]
        if key is None:

            def lowerKey(self):
                return (self.h.lower())

            key = lowerKey
        newChildren.sort(key=key, reverse=reverse)
        if oldChildren == newChildren:
            return
        # 2010/01/20. Fix bug 510148.
        c.setChanged(True)
        # g.trace(g.listToString(newChildren))
        bunch = u.beforeSort(p, undoType, oldChildren, newChildren, sortChildren)
        parent_v.children = newChildren
        if parent:
            dirtyVnodeList = parent.setAllAncestorAtFileNodesDirty()
        else:
            dirtyVnodeList = []
        u.afterSort(p, bunch, dirtyVnodeList)
        # Sorting destroys position p, and possibly the root position.
        p = c.setPositionAfterSort(sortChildren)
        c.redraw(p)
    #@+node:ekr.20161021130640.128: *4* c.setPositionAfterSort
    def setPositionAfterSort(self, sortChildren):
        c = self
        p = c.p
        p_v = p.v
        parent = p.parent()
        parent_v = p._parentVnode()
        if sortChildren:
            p = parent or c.rootPosition()
        else:
            if parent:
                p = parent.firstChild()
            else:
                p = leoNodes.Position(parent_v.children[0])
            while p and p.v != p_v:
                p.moveToNext()
            p = p or parent
        return p
    #@-others
#@+node:ekr.20161022115953.1: ** Toggle settings commands
if 0:
    #@+others
    #@+node:ekr.20161021130640.189: *3* 'toggle-sparse-move'
    @cmd('toggle-sparse-move')
    def toggleSparseMove(self, event=None):
        '''Toggle whether moves collapse the outline.'''
        c = self
        c.sparse_move = not c.sparse_move
        if not g.unitTesting:
            g.blue('sparse-move: %s' % c.sparse_move)
    #@-others
#@+node:ekr.20161021130640.213: ** Window commands
if 0:
    #@+others
    #@+node:ekr.20161021130640.214: *3* 'open-compare-window' (new command)
    @cmd('open-compare-window')
    def openCompareWindow(self, event=None):
        '''Open a dialog for comparing files and directories.'''
        c = self; frame = c.frame
        if not frame.comparePanel:
            frame.comparePanel = g.app.gui.createComparePanel(c)
        if frame.comparePanel:
            frame.comparePanel.bringToFront()
        else:
            g.warning('the', g.app.gui.guiName(),
                'gui does not support the compare window')
    #@+node:ekr.20161021130640.215: *3* 'open-python-window'
    @cmd('open-python-window')
    def openPythonWindow(self, event=None):
        '''Open Python's Idle debugger in a separate process.'''
        try:
            idlelib_path = imp.find_module('idlelib')[1]
        except ImportError:
            g.es_print('idlelib not found: can not open a Python window.')
            return
        idle = g.os_path_join(idlelib_path, 'idle.py')
        args = [sys.executable, idle]
        if 1: # Use present environment.
            os.spawnv(os.P_NOWAIT, sys.executable, args)
        else: # Use a pristine environment.
            os.spawnve(os.P_NOWAIT, sys.executable, args, os.environ)
    #@-others
#@+node:ekr.20161022113526.1: ** Utils for commands
if 0:
    #@+others
    #@+node:ekr.20161021130640.57: *3* c.goToLineNumber & goToScriptLineNumber
    def goToLineNumber(self, n):
        """
        Go to line n (zero-based) of a script.
        Called from g.handleScriptException.
        """
        # import leo.commands.gotoCommands as gotoCommands
        c = self
        c.gotoCommands.find_file_line(n)

    def goToScriptLineNumber(self, n, p):
        """
        Go to line n (zero-based) of a script.
        Called from g.handleScriptException.
        """
        # import leo.commands.gotoCommands as gotoCommands
        c = self
        c.gotoCommands.find_script_line(n, p)
    #@+node:ekr.20161021130640.101: *3* c.notValidInBatchMode
    def notValidInBatchMode(self, commandName):
        g.es('the', commandName, "command is not valid in batch mode")
    #@+node:ekr.20161021130640.212: *3* c.treeSelectHelper
    def treeSelectHelper(self, p):
        c = self
        if not p: p = c.p
        if p:
            # Do not call expandAllAncestors here.
            c.selectPosition(p)
            c.redraw_after_select(p)
        c.treeFocusHelper()
    #@+node:ekr.20161021130640.126: *3* c.validateOutline
    # Makes sure all nodes are valid.

    def validateOutline(self, event=None):
        c = self
        if not g.app.validate_outline:
            return True
        root = c.rootPosition()
        parent = c.nullPosition()
        if root:
            return root.validateOutlineWithParent(parent)
        else:
            return True
    #@+node:ekr.20161021130640.60: *3* c.writeScriptFile
    def writeScriptFile(self, script):
        trace = False and not g.unitTesting
        # Get the path to the file.
        c = self
        path = c.config.getString('script_file_path')
        if path:
            isAbsPath = os.path.isabs(path)
            driveSpec, path = os.path.splitdrive(path)
            parts = path.split('/')
            # xxx bad idea, loadDir is often read only!
            path = g.app.loadDir
            if isAbsPath:
                # make the first element absolute
                parts[0] = driveSpec + os.sep + parts[0]
            allParts = [path] + parts
            path = c.os_path_finalize_join(*allParts)
        else:
            path = c.os_path_finalize_join(
                g.app.homeLeoDir, 'scriptFile.py')
        if trace: g.trace(path)
        # Write the file.
        try:
            if g.isPython3:
                # Use the default encoding.
                f = open(path, encoding='utf-8', mode='w')
            else:
                f = open(path, 'w')
            s = script
            if not g.isPython3: # 2010/08/27
                s = g.toEncodedString(s, reportErrors=True)
            f.write(s)
            f.close()
        except Exception:
            g.es_exception()
            g.es("Failed to write script to %s" % path)
            # g.es("Check your configuration of script_file_path, currently %s" %
                # c.config.getString('script_file_path'))
            path = None
        return path
    #@+node:ekr.20161021130640.211: *3* c.xFocusHelper & initialFocusHelper
    def treeFocusHelper(self):
        c = self
        if c.stayInTreeAfterSelect:
            c.treeWantsFocus()
        else:
            c.bodyWantsFocus()

    def initialFocusHelper(self):
        c = self
        if c.outlineHasInitialFocus:
            c.treeWantsFocus()
        else:
            c.bodyWantsFocus()
    #@+node:ekr.20161021130640.138: *3* Check outline utils...
    # This code is no longer used by any Leo command,
    # but it will be retained for use of scripts.
    #@+node:ekr.20161021130640.139: *4* c.checkAllPythonCode
    def checkAllPythonCode(self, event=None, unittest=False, ignoreAtIgnore=True):
        '''Check all nodes in the selected tree for syntax and tab errors.'''
        c = self; count = 0; result = "ok"
        for p in c.all_unique_positions():
            count += 1
            if not unittest:
                #@+<< print dots >>
                #@+node:ekr.20161021130640.140: *5* << print dots >>
                if count % 100 == 0:
                    g.es('', '.', newline=False)
                if count % 2000 == 0:
                    g.enl()
                #@-<< print dots >>
            if g.scanForAtLanguage(c, p) == "python":
                if not g.scanForAtSettings(p) and (
                    not ignoreAtIgnore or not g.scanForAtIgnore(c, p)
                ):
                    try:
                        c.checkPythonNode(p, unittest)
                    except(SyntaxError, tokenize.TokenError, tabnanny.NannyNag):
                        result = "error" # Continue to check.
                    except Exception:
                        return "surprise" # abort
                    if unittest and result != "ok":
                        g.pr("Syntax error in %s" % p.cleanHeadString())
                        return result # End the unit test: it has failed.
        if not unittest:
            g.blue("check complete")
        return result
    #@+node:ekr.20161021130640.141: *4* c.checkPythonCode
    def checkPythonCode(self, event=None,
        unittest=False, ignoreAtIgnore=True,
        suppressErrors=False, checkOnSave=False
    ):
        '''Check the selected tree for syntax and tab errors.'''
        c = self; count = 0; result = "ok"
        if not unittest:
            g.es("checking Python code   ")
        for p in c.p.self_and_subtree():
            count += 1
            if not unittest and not checkOnSave:
                #@+<< print dots >>
                #@+node:ekr.20161021130640.142: *5* << print dots >>
                if count % 100 == 0:
                    g.es('', '.', newline=False)
                if count % 2000 == 0:
                    g.enl()
                #@-<< print dots >>
            if g.scanForAtLanguage(c, p) == "python":
                if not ignoreAtIgnore or not g.scanForAtIgnore(c, p):
                    try:
                        c.checkPythonNode(p, unittest, suppressErrors)
                    except(SyntaxError, tokenize.TokenError, tabnanny.NannyNag):
                        result = "error" # Continue to check.
                    except Exception:
                        return "surprise" # abort
        if not unittest:
            g.blue("check complete")
        # We _can_ return a result for unit tests because we aren't using doCommand.
        return result
    #@+node:ekr.20161021130640.143: *4* c.checkPythonNode
    def checkPythonNode(self, p, unittest=False, suppressErrors=False):
        c = self; h = p.h
        # Call getScript to ignore directives and section references.
        body = g.getScript(c, p.copy())
        if not body: return
        try:
            fn = '<node: %s>' % p.h
            if not g.isPython3:
                body = g.toEncodedString(body)
            compile(body + '\n', fn, 'exec')
            c.tabNannyNode(p, h, body, unittest, suppressErrors)
        except SyntaxError:
            if not suppressErrors:
                g.warning("Syntax error in: %s" % h)
                g.es_exception(full=False, color="black")
            if unittest: raise
        except Exception:
            g.es_print('unexpected exception')
            g.es_exception()
            if unittest: raise
    #@+node:ekr.20161021130640.144: *4* c.tabNannyNode
    # This code is based on tabnanny.check.

    def tabNannyNode(self, p, headline, body, unittest=False, suppressErrors=False):
        """Check indentation using tabnanny."""
        # c = self
        try:
            readline = g.ReadLinesClass(body).next
            tabnanny.process_tokens(tokenize.generate_tokens(readline))
        except IndentationError:
            junk, msg, junk = sys.exc_info()
            if not suppressErrors:
                g.warning("IndentationError in", headline)
                g.es('', msg)
            if unittest: raise
        except tokenize.TokenError:
            junk, msg, junk = sys.exc_info()
            if not suppressErrors:
                g.warning("TokenError in", headline)
                g.es('', msg)
            if unittest: raise
        except tabnanny.NannyNag:
            junk, nag, junk = sys.exc_info()
            if not suppressErrors:
                badline = nag.get_lineno()
                line = nag.get_line()
                message = nag.get_msg()
                g.warning("indentation error in", headline, "line", badline)
                g.es(message)
                line2 = repr(str(line))[1: -1]
                g.es("offending line:\n", line2)
            if unittest: raise
        except Exception:
            g.trace("unexpected exception")
            g.es_exception()
            if unittest: raise
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
