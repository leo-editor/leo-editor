# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20150514035813.1: * @file ../commands/editCommands.py
#@@first
"""Leo's general editing commands."""
#@+<< imports >>
#@+node:ekr.20150514050149.1: **  << imports >> (editCommands.py)
import os
import re
import leo.core.leoGlobals as g
from leo.commands.baseCommands import BaseEditCommandsClass as BaseEditCommandsClass
#@-<< imports >>

def cmd(name):
    """Command decorator for the EditCommandsClass class."""
    return g.new_cmd_decorator(name, ['c', 'editCommands',])

#@+others
#@+node:ekr.20180504180844.1: **  Top-level helper functions
#@+node:ekr.20180504180247.2: *3* find_next_trace
if_pat = re.compile(r'\n[ \t]*(if|elif)\s*trace\b.*:')
    # Will not find in comments, which is fine.
    
skip_pat = re.compile(r'=.*in g.app.debug')

def find_next_trace(ins, p):
    while p:
        ins = max(0, ins-1) # Back up over newline.
        s = p.b[ins:]
        m = re.search(skip_pat, s)
        if m:
            # Skip this node.
            g.es_print('Skipping', p.h)
        else:
            m = re.search(if_pat, s)
            if m:
                i = m.start()+1
                j = m.end()
                k = find_trace_block(i, j, s)
                i += ins
                k += ins
                return i, k, p
        p.moveToThreadNext()
        ins = 0
    return None, None, p
#@+node:ekr.20180504180247.3: *3* find_trace_block
def find_trace_block(i, j, s):
    """Find the statement or block starting at i."""
    assert s[i] != '\n'
    s = s[i:]
    lws = len(s) - len(s.lstrip())
    n = 1 # Number of lines to skip.
    lines = g.splitLines(s)
    for line in lines[1:]:
        lws2 = len(line) - len(line.lstrip())
        if lws2 <= lws:
            break
        n += 1
    assert n >= 1
    result_lines = lines[:n]
    return i + len(''.join(result_lines))
#@+node:ekr.20190926103141.1: *3* lineScrollHelper
# by Brian Theado.

def lineScrollHelper(c, prefix1, prefix2, suffix):
    w = c.frame.body.wrapper
    ins = w.getInsertPoint()
    c.inCommand = False
    c.executeMinibufferCommand(prefix1 + 'line' + suffix)
    ins2 = w.getInsertPoint()
    # If the cursor didn't change, then go to beginning/end of line
    if ins == ins2:
        c.executeMinibufferCommand(prefix2 + 'of-line' + suffix)
#@+node:ekr.20180504180134.1: ** @g.command('delete-trace-statements')
@g.command('delete-trace-statements')
def delete_trace_statements(event=None):
    """
    Delete all trace statements/blocks from c.p to the end of the outline.
    
    **Warning**: Use this command at your own risk.
    
    It can cause "if" and "else" clauses to become empty, resulting in
    syntax errors. Having said that, pyflakes & pylint will usually catch
    the problems.
    """
    c = event.get('c')
    if not c:
        return
    p = c.p
    ins = 0
    seen = []
    while True:
        i, k, p = find_next_trace(ins, p)
        if not p:
            g.es_print('done')
            return
        s = p.b
        if p.h not in seen:
            seen.append(p.h)
            g.es_print('Changed:', p.h)
        ins = 0 # Rescanning is essential.
        p.b = s[:i] + s[k:]
#@+node:ekr.20180210160930.1: ** @g.command('mark-first-parents')
@g.command('mark-first-parents')
def mark_first_parents(event):
    """Mark the node and all its parents."""
    c = event.get('c')
    changed = []
    if not c:
        return changed
    for parent in c.p.self_and_parents():
        if not parent.isMarked():
            parent.v.setMarked()
            parent.setAllAncestorAtFileNodesDirty()
            changed.append(parent.copy())
    if changed:
        # g.es("marked: " + ', '.join([z.h for z in changed]))
        c.setChanged()
        c.redraw()
    return changed
#@+node:ekr.20190926103245.1: ** @g.command('next-or-end-of-line')
# by Brian Theado.

@g.command('next-or-end-of-line')
def nextOrEndOfLine(event):
    lineScrollHelper(event['c'], 'next-', 'end-', '')

#@+node:ekr.20190926103246.2: ** @g.command('next-or-end-of-line-extend-selection')
# by Brian Theado.

@g.command('next-or-end-of-line-extend-selection')
def nextOrEndOfLineExtendSelection(event):
    lineScrollHelper(event['c'], 'next-', 'end-', '-extend-selection')

#@+node:ekr.20190926103246.1: ** @g.command('previous-or-beginning-of-line')
# by Brian Theado.

@g.command('previous-or-beginning-of-line')
def previousOrBeginningOfLine(event):
    lineScrollHelper(event['c'], 'previous-', 'beginning-', '')

#@+node:ekr.20190926103246.3: ** @g.command('previous-or-beginning-of-line-extend-selection')
# by Brian Theado.

@g.command('previous-or-beginning-of-line-extend-selection')
def previousOrBeginningOfLineExtendSelection(event):
    lineScrollHelper(event['c'], 'previous-', 'beginning-', '-extend-selection')
#@+node:ekr.20190323084957.1: ** @g.command('promote-bodies')
@g.command('promote-bodies')
def promoteBodies(event):
    """Copy the body text of all descendants to the parent's body text."""
    c = event.get('c')
    if not c:
        return
    p = c.p
    result = [p.b.rstrip()+'\n'] if p.b.strip() else []
    b = c.undoer.beforeChangeNodeContents(p)
    for child in p.subtree():
        h = child.h.strip()
        if child.b:
            body = '\n'.join(['  %s' % (z) for z in g.splitLines(child.b)])
            s = '- %s\n%s' % (h,body)
        else:
            s = '- %s' % h
        if s.strip():
            result.append(s.strip())
    if result:
        result.append('')
    p.b = '\n'.join(result)
    c.undoer.afterChangeNodeContents(p,'promote-bodies',b)
#@+node:ekr.20190323085410.1: ** @g.command('promote-headlines')
@g.command('promote-headlines')
def promoteHeadlines(event):
    """Copy the headlines of all descendants to the parent's body text."""
    c = event.get('c')
    if not c:
        return
    p = c.p
    b = c.undoer.beforeChangeNodeContents(p)
    result = '\n'.join([p.h.rstrip() for p in p.subtree()])
    if result:
        p.b = p.b.lstrip() + '\n' + result
        c.undoer.afterChangeNodeContents(p,'promote-headlines',b)
#@+node:ekr.20180504180647.1: ** @g.command('select-next-trace-statement')
@g.command('select-next-trace-statement')
def select_next_trace_statement(event=None):
    """Select the next statement/block enabled by `if trace...:`"""
    c = event.get('c')
    if not c:
        return
    w = c.frame.body.wrapper
    ins = w.getInsertPoint()
    i, k, p = find_next_trace(ins, c.p)
    if p:
        c.selectPosition(p)
        c.redraw()
        w.setSelectionRange(i, k, insert=k)
    else:
        g.es_print('done')
    c.bodyWantsFocus()
#@+node:ekr.20191010112910.1: ** @g.command('show-clone-ancestors')
@g.command('show-clone-ancestors')
def show_clone_ancestors(event=None):
    """Display links to all ancestor nodes of the node c.p."""
    c = event.get('c')
    if not c:
        return
    p = c.p
    g.es(f"Ancestors of '{p.h}':")
    for clone in c.all_positions():
        if clone.v == p.v:
            unl = clone.get_UNL(with_file=False, with_index=False)
            runl = " <- ".join(unl.split("-->")[::-1][1:])
                # reverse and drop first
            g.es("  ", newline = False)
            g.es_clickable_link(c, clone, 1, runl + "\n")
#@+node:ekr.20191007034723.1: ** @g.command('show-clone-parents')
@g.command('show-clone-parents')
def show_clones(event=None):
    """Display links to all parent nodes of the node c.p."""
    c = event.get('c')
    if not c:
        return
    seen = []
    for clone in c.vnode2allPositions(c.p.v):
        parent = clone.parent()
        if parent and parent not in seen:
            seen.append(parent)
            g.es_clickable_link(c, clone, 1, f"{parent.h} -> {clone.h}\n")
#@+node:ekr.20180210161001.1: ** @g.command('unmark-first-parents')
@g.command('unmark-first-parents')
def unmark_first_parents(event=None):
    """Mark the node and all its parents."""
    c = event.get('c')
    changed = []
    if not c:
        return changed
    for parent in c.p.self_and_parents():
        if parent.isMarked():
            parent.v.clearMarked()
            parent.setAllAncestorAtFileNodesDirty()
            changed.append(parent.copy())
    if changed:
        # g.es("unmarked: " + ', '.join([z.h for z in changed]))
        c.setChanged()
        c.redraw()
    return changed
#@+node:ekr.20160514100029.1: ** class EditCommandsClass
class EditCommandsClass(BaseEditCommandsClass):
    """Editing commands with little or no state."""
    # pylint: disable=eval-used
    #@+others
    #@+node:ekr.20150514063305.116: *3* ec.__init__
    def __init__(self, c):
        """Ctor for EditCommandsClass class."""
        # pylint: disable=super-init-not-called
        self.c = c
        self.ccolumn = '0' # For comment column functions.
        self.cursorStack = []
            # Values are tuples, (i, j, ins)
        self.extendMode = False # True: all cursor move commands extend the selection.
        self.fillPrefix = '' # For fill prefix functions.
        self.fillColumn = 0 # For line centering.
            # Set by the set-fill-column command.
            # If zero, @pagewidth value is used.
        self.moveSpotNode = None # A VNode.
        self.moveSpot = None # For retaining preferred column when moving up or down.
        self.moveCol = None # For retaining preferred column when moving up or down.
        self.sampleWidget = None # Created later.
        self.swapSpots = []
        self._useRegex = False # For replace-string
        self.w = None # For use by state handlers.
        # Settings...
        cf = c.config
        self.autocompleteBrackets = cf.getBool('autocomplete-brackets')
        if cf.getBool('auto-justify-on-at-start'):
            self.autojustify = abs(cf.getInt('auto-justify') or 0)
        else:
            self.autojustify = 0
        self.bracketsFlashBg = cf.getColor('flash-brackets-background-color')
        self.bracketsFlashCount = cf.getInt('flash-brackets-count')
        self.bracketsFlashDelay = cf.getInt('flash-brackets-delay')
        self.bracketsFlashFg = cf.getColor('flash-brackets-foreground-color')
        self.flashMatchingBrackets = cf.getBool('flash-matching-brackets')
        self.smartAutoIndent = cf.getBool('smart-auto-indent')
        self.openBracketsList = cf.getString('open-flash-brackets') or '([{'
        self.closeBracketsList = cf.getString('close-flash-brackets') or ')]}'
        self.initBracketMatcher(c)
    #@+node:ekr.20150514063305.190: *3* ec.cache
    @cmd('clear-all-caches')
    @cmd('clear-cache')
    def clearAllCaches(self, event=None):
        """Clear all of Leo's file caches."""
        g.app.global_cacher.clear()
        g.app.commander_cacher.clear()
        
    @cmd('dump-caches')
    def dumpCaches(self, event=None):
        """Dump, all of Leo's file caches."""
        g.app.global_cacher.dump()
        g.app.commander_cacher.dump()
    #@+node:ekr.20150514063305.118: *3* ec.doNothing
    @cmd('do-nothing')
    def doNothing(self, event):
        """A placeholder command, useful for testing bindings."""
        pass
    #@+node:ekr.20150514063305.278: *3* ec.insertFileName
    @cmd('insert-file-name')
    def insertFileName(self, event=None):
        """
        Prompt for a file name, then insert it at the cursor position.
        This operation is undoable if done in the body pane.

        The initial path is made by concatenating path_for_p() and the selected
        text, if there is any, or any path like text immediately preceding the
        cursor.
        """
        c = self.c
        w = self.editWidget(event)
        if w:

            def callback(arg, w=w):
                i = w.getSelectionRange()[0]
                w.deleteTextSelection()
                w.insert(i, arg)
                if g.app.gui.widget_name(w) == 'body':
                    c.frame.body.onBodyChanged(undoType='Typing')

            # see if the widget already contains the start of a path
            start_text = w.getSelectedText()
            if not start_text:  # look at text preceeding insert point
                start_text = w.getAllText()[:w.getInsertPoint()]
                if start_text:
                    # make non-path characters whitespace
                    start_text = ''.join(i if i not in '\'"`()[]{}<>!|*,@#$&' else ' '
                                         for i in start_text)
                    if start_text[-1].isspace():  # use node path if nothing typed
                        start_text = ''
                    else:
                        start_text = start_text.rsplit(None, 1)[-1]
                        # set selection range so w.deleteTextSelection() works in the callback
                        w.setSelectionRange(
                            w.getInsertPoint()-len(start_text), w.getInsertPoint())

            c.k.functionTail = g.os_path_finalize_join(self.path_for_p(c, c.p), start_text or '')
            c.k.getFileName(event, callback=callback)
    #@+node:ekr.20150514063305.279: *3* ec.insertHeadlineTime
    @cmd('insert-headline-time')
    def insertHeadlineTime(self, event=None):
        """Insert a date/time stamp in the headline of the selected node."""
        frame = self
        c, p = frame.c, self.c.p
        if g.app.batchMode:
            c.notValidInBatchMode("Insert Headline Time")
            return
        w = c.frame.tree.edit_widget(p)
            # 2015/06/09: Fix bug 131: Insert time in headline now inserts time in body
            # Get the wrapper from the tree itself.
            # Do *not* set w = self.editWidget!
        if w:
            # Fix bug https://bugs.launchpad.net/leo-editor/+bug/1185933
            # insert-headline-time should insert at cursor.
            # Note: The command must be bound to a key for this to work.
            ins = w.getInsertPoint()
            s = c.getTime(body=False)
            w.insert(ins, s)
        else:
            c.endEditing()
            time = c.getTime(body=False)
            s = p.h.rstrip()
            if s:
                p.h = ' '.join([s, time])
            else:
                p.h = time
            c.redrawAndEdit(p, selectAll=True)
    #@+node:tbrown.20151118134307.1: *3* ec.path_for_p
    def path_for_p(self, c, p):
        """path_for_p - return the filesystem path (directory) containing
        node `p`.

        FIXME: this general purpose code should be somewhere else, and there
        may already be functions that do some of the work, although perhaps
        without handling so many corner cases (@auto-my-custom-type etc.)

        :param outline c: outline containing p
        :param position p: position to locate
        :return: path
        :rtype: str
        """

        def atfile(p):
            """return True if p is an @<file> node *of any kind*"""
            word0 = p.h.split()[0]
            return (
                word0 in g.app.atFileNames|set(['@auto']) or
                word0.startswith('@auto-')
            )

        aList = g.get_directives_dict_list(p)
        path = c.scanAtPathDirectives(aList)
        while c.positionExists(p):
            if atfile(p):  # see if it's a @<file> node of some sort
                nodepath = p.h.split(None, 1)[-1]
                nodepath = g.os_path_join(path, nodepath)
                if not g.os_path_isdir(nodepath):  # remove filename
                    nodepath = g.os_path_dirname(nodepath)
                if g.os_path_isdir(nodepath):  # append if it's a directory
                    path = nodepath
                break
            p.moveToParent()

        return path
    #@+node:ekr.20150514063305.347: *3* ec.tabify & untabify
    @cmd('tabify')
    def tabify(self, event):
        """Convert 4 spaces to tabs in the selected text."""
        self.tabifyHelper(event, which='tabify')

    @cmd('untabify')
    def untabify(self, event):
        """Convert tabs to 4 spaces in the selected text."""
        self.tabifyHelper(event, which='untabify')

    def tabifyHelper(self, event, which):
        w = self.editWidget(event)
        if not w or not w.hasSelection():
            return
        self.beginCommand(w, undoType=which)
        i, end = w.getSelectionRange()
        txt = w.getSelectedText()
        if which == 'tabify':
            pattern = re.compile(r' {4,4}') # Huh?
            ntxt = pattern.sub('\t', txt)
        else:
            pattern = re.compile(r'\t')
            ntxt = pattern.sub('    ', txt)
        w.delete(i, end)
        w.insert(i, ntxt)
        n = i + len(ntxt)
        w.setSelectionRange(n, n, insert=n)
        self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.191: *3* ec: capitalization & case
    #@+node:ekr.20150514063305.192: *4* ec.capitalizeWord & up/downCaseWord
    @cmd('capitalize-word')
    def capitalizeWord(self, event):
        """Capitalize the word at the cursor."""
        self.capitalizeHelper(event, 'cap', 'capitalize-word')

    @cmd('downcase-word')
    def downCaseWord(self, event):
        """Convert all characters of the word at the cursor to lower case."""
        self.capitalizeHelper(event, 'low', 'downcase-word')

    @cmd('upcase-word')
    def upCaseWord(self, event):
        """Convert all characters of the word at the cursor to UPPER CASE."""
        self.capitalizeHelper(event, 'up', 'upcase-word')
    #@+node:ekr.20150514063305.194: *4* ec.capitalizeHelper
    def capitalizeHelper(self, event, which, undoType):
        w = self.editWidget(event)
        if not w:
            return
        s = w.getAllText()
        ins = w.getInsertPoint()
        i, j = g.getWord(s, ins)
        word = s[i: j]
        if not word.strip():
            return
        self.beginCommand(w, undoType=undoType)
        if which == 'cap': word2 = word.capitalize()
        elif which == 'low': word2 = word.lower()
        elif which == 'up': word2 = word.upper()
        else: g.trace('can not happen: which = %s' % s(which))
        changed = word != word2
        if changed:
            w.delete(i, j)
            w.insert(i, word2)
            w.setSelectionRange(ins, ins, insert=ins)
        self.endCommand(changed=changed, setLabel=True)
    #@+node:ekr.20150514063305.195: *3* ec: clicks and focus
    #@+node:ekr.20150514063305.196: *4* ec.activate-x-menu & activateMenu
    @cmd('activate-cmds-menu')
    def activateCmdsMenu(self, event=None):
        """Activate Leo's Cmnds menu."""
        self.activateMenu('Cmds')

    @cmd('activate-edit-menu')
    def activateEditMenu(self, event=None):
        """Activate Leo's Edit menu."""
        self.activateMenu('Edit')

    @cmd('activate-file-menu')
    def activateFileMenu(self, event=None):
        """Activate Leo's File menu."""
        self.activateMenu('File')

    @cmd('activate-help-menu')
    def activateHelpMenu(self, event=None):
        """Activate Leo's Help menu."""
        self.activateMenu('Help')

    @cmd('activate-outline-menu')
    def activateOutlineMenu(self, event=None):
        """Activate Leo's Outline menu."""
        self.activateMenu('Outline')

    @cmd('activate-plugins-menu')
    def activatePluginsMenu(self, event=None):
        """Activate Leo's Plugins menu."""
        self.activateMenu('Plugins')

    @cmd('activate-window-menu')
    def activateWindowMenu(self, event=None):
        """Activate Leo's Window menu."""
        self.activateMenu('Window')

    def activateMenu(self, menuName):
        c = self.c
        c.frame.menu.activateMenu(menuName)
    #@+node:ekr.20150514063305.199: *4* ec.focusTo...
    @cmd('focus-to-body')
    def focusToBody(self, event=None):
        """Put the keyboard focus in Leo's body pane."""
        c, k = self.c, self.c.k
        c.bodyWantsFocus()
        if k:
            k.setDefaultInputState()
            k.showStateAndMode()

    @cmd('focus-to-log')
    def focusToLog(self, event=None):
        """Put the keyboard focus in Leo's log pane."""
        self.c.logWantsFocus()

    @cmd('focus-to-minibuffer')
    def focusToMinibuffer(self, event=None):
        """Put the keyboard focus in Leo's minibuffer."""
        self.c.minibufferWantsFocus()

    @cmd('focus-to-tree')
    def focusToTree(self, event=None):
        """Put the keyboard focus in Leo's outline pane."""
        self.c.treeWantsFocus()
    #@+node:ekr.20150514063305.201: *4* ec.clicks in the icon box
    # These call the actual event handlers so as to trigger hooks.

    @cmd('ctrl-click-icon')
    def ctrlClickIconBox(self, event=None):
        """Simulate a ctrl-click in the icon box of the presently selected node."""
        c = self.c
        c.frame.tree.OnIconCtrlClick(c.p)
            # Calls the base LeoTree method.

    @cmd('click-icon-box')
    def clickIconBox(self, event=None):
        """Simulate a click in the icon box of the presently selected node."""
        c = self.c
        c.frame.tree.onIconBoxClick(event, p=c.p)

    @cmd('double-click-icon-box')
    def doubleClickIconBox(self, event=None):
        """Simulate a double-click in the icon box of the presently selected node."""
        c = self.c
        c.frame.tree.onIconBoxDoubleClick(event, p=c.p)

    @cmd('right-click-icon')
    def rightClickIconBox(self, event=None):
        """Simulate a right click in the icon box of the presently selected node."""
        c = self.c
        c.frame.tree.onIconBoxRightClick(event, p=c.p)
    #@+node:ekr.20150514063305.202: *4* ec.clickClickBox
    @cmd('click-click-box')
    def clickClickBox(self, event=None):
        """
        Simulate a click in the click box (+- box) of the presently selected node.

        Call the actual event handlers so as to trigger hooks.
        """
        c = self.c
        c.frame.tree.onClickBoxClick(event, p=c.p)
    #@+node:ekr.20150514063305.207: *3* ec: comment column
    #@+node:ekr.20150514063305.208: *4* ec.setCommentColumn
    @cmd('set-comment-column')
    def setCommentColumn(self, event):
        """Set the comment column for the indent-to-comment-column command."""
        w = self.editWidget(event)
        if w:
            s = w.getAllText()
            ins = w.getInsertPoint()
            row, col = g.convertPythonIndexToRowCol(s, ins)
            self.ccolumn = col
    #@+node:ekr.20150514063305.209: *4* ec.indentToCommentColumn
    @cmd('indent-to-comment-column')
    def indentToCommentColumn(self, event):
        """
        Insert whitespace to indent the line containing the insert point to the
        comment column.
        """
        w = self.editWidget(event)
        if not w:
            return
        self.beginCommand(w, undoType='indent-to-comment-column')
        s = w.getAllText()
        ins = w.getInsertPoint()
        i, j = g.getLine(s, ins)
        line = s[i: j]
        c1 = int(self.ccolumn)
        line2 = ' ' * c1 + line.lstrip()
        if line2 != line:
            w.delete(i, j)
            w.insert(i, line2)
        w.setInsertPoint(i + c1)
        self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.214: *3* ec: fill column and centering
    #@+at
    # 
    # These methods are currently just used in tandem to center the line or
    # region within the fill column. for example, dependent upon the fill column, this text:
    # 
    # cats
    # raaaaaaaaaaaats
    # mats
    # zaaaaaaaaap
    # 
    # may look like
    # 
    #                                  cats
    #                            raaaaaaaaaaaats
    #                                  mats
    #                              zaaaaaaaaap
    # 
    # after an center-region command via Alt-x.
    #@+node:ekr.20150514063305.215: *4* ec.centerLine
    @cmd('center-line')
    def centerLine(self, event):
        """Centers line within current fill column"""
        c, k, w = self.c, self.c.k, self.editWidget(event)
        if not w:
            return
        if self.fillColumn > 0:
            fillColumn = self.fillColumn
        else:
            d = c.scanAllDirectives()
            fillColumn = d.get("pagewidth")
        s = w.getAllText()
        i, j = g.getLine(s, w.getInsertPoint())
        line = s[i: j].strip()
        if not line or len(line) >= fillColumn:
            return
        self.beginCommand(w, undoType='center-line')
        n = (fillColumn - len(line)) / 2
        ws = ' ' * n
        k = g.skip_ws(s, i)
        if k > i: w.delete(i, k - i)
        w.insert(i, ws)
        self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.216: *4* ec.setFillColumn
    @cmd('set-fill-column')
    def setFillColumn(self, event):
        """Set the fill column used by the center-line and center-region commands."""
        k = self.c.k
        self.w = self.editWidget(event)
        if self.w:
            k.setLabelBlue('Set Fill Column: ')
            k.get1Arg(event, handler=self.setFillColumn1)

    def setFillColumn1(self, event):
        c, k, w = self.c, self.c.k, self.w
        k.clearState()
        try:
            # Bug fix: 2011/05/23: set the fillColumn ivar!
            self.fillColumn = n = int(k.arg)
            k.setLabelGrey('fill column is: %d' % n)
            k.commandName = 'set-fill-column %d' % n
        except ValueError:
            k.resetLabel()
        c.widgetWantsFocus(w)
    #@+node:ekr.20150514063305.217: *4* ec.centerRegion
    @cmd('center-region')
    def centerRegion(self, event):
        """Centers the selected text within the fill column"""
        c, k, w = self.c, self.c.k, self.editWidget(event)
        if not w:
            return
        s = w.getAllText()
        sel_1, sel_2 = w.getSelectionRange()
        ind, junk = g.getLine(s, sel_1)
        junk, end = g.getLine(s, sel_2)
        if self.fillColumn > 0:
            fillColumn = self.fillColumn
        else:
            d = c.scanAllDirectives()
            fillColumn = d.get("pagewidth")
        self.beginCommand(w, undoType='center-region')
        inserted = 0
        while ind < end:
            s = w.getAllText()
            i, j = g.getLine(s, ind)
            line = s[i: j].strip()
            if len(line) >= fillColumn:
                ind = j
            else:
                n = int((fillColumn - len(line)) / 2)
                inserted += n
                k = g.skip_ws(s, i)
                if k > i: w.delete(i, k - i)
                w.insert(i, ' ' * n)
                ind = j + n - (k - i)
        w.setSelectionRange(sel_1, sel_2 + inserted)
        self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.218: *4* ec.setFillPrefix
    @cmd('set-fill-prefix')
    def setFillPrefix(self, event):
        """Make the selected text the fill prefix."""
        w = self.editWidget(event)
        if w:
            s = w.getAllText()
            i, j = w.getSelectionRange()
            self.fillPrefix = s[i: j]
    #@+node:ekr.20150514063305.219: *4* ec._addPrefix
    def _addPrefix(self, ntxt):
        ntxt = ntxt.split('.')
        ntxt = map(lambda a: self.fillPrefix + a, ntxt)
        ntxt = '.'.join(ntxt)
        return ntxt
    #@+node:ekr.20150514063305.220: *3* ec: find quick support
    #@+node:ekr.20150514063305.221: *4* ec.backward/findCharacter & helper
    @cmd('backward-find-character')
    def backwardFindCharacter(self, event):
        """Search backwards for a character."""
        return self.findCharacterHelper(event, backward=True, extend=False)

    @cmd('backward-find-character-extend-selection')
    def backwardFindCharacterExtendSelection(self, event):
        """Search backward for a character, extending the selection."""
        return self.findCharacterHelper(event, backward=True, extend=True)

    @cmd('find-character')
    def findCharacter(self, event):
        """Search for a character."""
        return self.findCharacterHelper(event, backward=False, extend=False)

    @cmd('find-character-extend-selection')
    def findCharacterExtendSelection(self, event):
        """Search for a character, extending the selection."""
        return self.findCharacterHelper(event, backward=False, extend=True)
    #@+node:ekr.20150514063305.222: *5* ec.findCharacterHelper
    def findCharacterHelper(self, event, backward, extend):
        """Put the cursor at the next occurance of a character on a line."""
        k = self.c.k
        self.w = self.editWidget(event)
        if not self.w:
            return
        self.event = event
        self.backward = backward
        self.extend = extend or self.extendMode # Bug fix: 2010/01/19
        self.insert = self.w.getInsertPoint()
        s = '%s character%s: ' % (
            'Backward find' if backward else 'Find',
            ' & extend' if extend else '')
        k.setLabelBlue(s)
        # Get the arg without touching the focus.
        k.getArg(event, handler=self.findCharacter1, oneCharacter=True, useMinibuffer=False)

    def findCharacter1(self, event):
        k = self.c.k
        event, w = self.event, self.w
        backward = self.backward
        extend = self.extend or self.extendMode
        ch = k.arg
        s = w.getAllText()
        ins = w.toPythonIndex(self.insert)
        i = ins + -1 if backward else + 1 # skip the present character.
        if backward:
            start = 0
            j = s.rfind(ch, start, max(start, i)) # Skip the character at the cursor.
            if j > -1: self.moveToHelper(event, j, extend)
        else:
            end = len(s)
            j = s.find(ch, min(i, end), end) # Skip the character at the cursor.
            if j > -1: self.moveToHelper(event, j, extend)
        k.resetLabel()
        k.clearState()
    #@+node:ekr.20150514063305.223: *4* ec.findWord and FindWordOnLine & helper
    @cmd('find-word')
    def findWord(self, event):
        """Put the cursor at the next word that starts with a character."""
        return self.findWordHelper(event, oneLine=False)

    @cmd('find-word-in-line')
    def findWordInLine(self, event):
        """Put the cursor at the next word (on a line) that starts with a character."""
        return self.findWordHelper(event, oneLine=True)
    #@+node:ekr.20150514063305.224: *5* ec.findWordHelper
    def findWordHelper(self, event, oneLine):
        k = self.c.k
        self.w = self.editWidget(event)
        if self.w:
            self.oneLineFlag = oneLine
            k.setLabelBlue('Find word %sstarting with: ' % (
                'in line ' if oneLine else ''))
            k.get1Arg(event, handler=self.findWord1, oneCharacter=True)

    def findWord1(self, event):
        c, k = self.c, self.c.k
        ch = k.arg
        if ch:
            w = self.w
            i = w.getInsertPoint()
            s = w.getAllText()
            end = len(s)
            if self.oneLineFlag:
                end = s.find('\n', i) # Limit searches to this line.
                if end == -1: end = len(s)
            while i < end:
                i = s.find(ch, i + 1, end) # Ensure progress and i > 0.
                if i == -1:
                    break
                elif not g.isWordChar(s[i - 1]):
                    w.setSelectionRange(i, i, insert=i)
                    break
        k.resetLabel()
        k.clearState()
        c.widgetWantsFocus(w)
    #@+node:ekr.20150514063305.225: *3* ec: goto node
    #@+node:ekr.20170411065920.1: *4* ec.gotoAnyClone
    @cmd('goto-any-clone')
    def gotoAnyClone(self, event=None):
        """Select then next cloned node, regardless of whether c.p is a clone."""
        c = self.c
        p = c.p.threadNext()
        while p:
            if p.isCloned():
                c.selectPosition(p)
                return
            p.moveToThreadNext()
        g.es('no clones found after', c.p.h)
    #@+node:ekr.20150514063305.226: *4* ec.gotoCharacter
    @cmd('goto-char')
    def gotoCharacter(self, event):
        """Put the cursor at the n'th character of the buffer."""
        k = self.c.k
        self.w = self.editWidget(event)
        if self.w:
            k.setLabelBlue("Goto n'th character: ")
            k.get1Arg(event, handler=self.gotoCharacter1)

    def gotoCharacter1(self, event):
        c, k = self.c, self.c.k
        n = k.arg
        w = self.w
        ok = False
        if n.isdigit():
            n = int(n)
            if n >= 0:
                w.setInsertPoint(n)
                w.seeInsertPoint()
                ok = True
        if not ok:
            g.warning('goto-char takes non-negative integer argument')
        k.resetLabel()
        k.clearState()
        c.widgetWantsFocus(w)
    #@+node:ekr.20150514063305.227: *4* ec.gotoGlobalLine
    @cmd('goto-global-line')
    def gotoGlobalLine(self, event):
        """
        Put the cursor at the line in the *outline* corresponding to the line
        with the given line number *in the external file*.

        For external files containing sentinels, there may be *several* lines
        in the file that correspond to the same line in the outline.

        An Easter Egg: <Alt-x>number invokes this code.
        """
        # Improved docstring for #253: Goto Global line (Alt-G) is inconsistent.
        # https://github.com/leo-editor/leo-editor/issues/253
        k = self.c.k
        self.w = self.editWidget(event)
        if self.w:
            k.setLabelBlue('Goto global line: ')
            k.get1Arg(event, handler=self.gotoGlobalLine1)

    def gotoGlobalLine1(self, event):
        c, k = self.c, self.c.k
        n = k.arg
        k.resetLabel()
        k.clearState()
        if n.isdigit():
            # Very important: n is one-based.
            c.gotoCommands.find_file_line(n=int(n))
    #@+node:ekr.20150514063305.228: *4* ec.gotoLine
    @cmd('goto-line')
    def gotoLine(self, event):
        """Put the cursor at the n'th line of the buffer."""
        k = self.c.k
        self.w = self.editWidget(event)
        if self.w:
            k.setLabelBlue('Goto line: ')
            k.get1Arg(event, handler=self.gotoLine1)

    def gotoLine1(self, event):
        c, k = self.c, self.c.k
        n, w = k.arg, self.w
        if n.isdigit():
            n = int(n)
            s = w.getAllText()
            i = g.convertRowColToPythonIndex(s, n-1, 0)
            w.setInsertPoint(i)
            w.seeInsertPoint()
        k.resetLabel()
        k.clearState()
        c.widgetWantsFocus(w)
    #@+node:ekr.20150514063305.229: *3* ec: icons
    #@+at
    # 
    # To do:
    # 
    # - Define standard icons in a subfolder of Icons folder?
    # - Tree control recomputes height of each line.
    #@+node:ekr.20150514063305.230: *4* ec. Helpers
    #@+node:ekr.20150514063305.231: *5* ec.appendImageDictToList
    def appendImageDictToList(self, aList, path, xoffset, **kargs):
        c = self.c
        relPath = path  # for finding icon on load in different environment
        path = g.app.gui.getImageFinder(path)
        # pylint: disable=unpacking-non-sequence
        image, image_height = g.app.gui.getTreeImage(c, path)
        if not image:
            g.es('can not load image:', path)
            return xoffset
        if image_height is None:
            yoffset = 0
        else:
            yoffset = 0 # (c.frame.tree.line_height-image_height)/2
            # TNB: I suspect this is being done again in the drawing code
        newEntry = {
            'type': 'file',
            'file': path,
            'relPath': relPath,
            'where': 'beforeHeadline',
            'yoffset': yoffset, 'xoffset': xoffset, 'xpad': 1, # -2,
            'on': 'VNode',
        }
        newEntry.update(kargs) # may switch 'on' to 'VNode'
        aList.append(newEntry)
        xoffset += 2
        return xoffset
    #@+node:ekr.20150514063305.232: *5* ec.dHash
    def dHash(self, d):
        """Hash a dictionary"""
        return ''.join(['%s%s' % (str(k), str(d[k])) for k in sorted(d)])
    #@+node:ekr.20150514063305.233: *5* ec.getIconList
    def getIconList(self, p):
        """Return list of icons for position p, call setIconList to apply changes"""
        fromVnode = []
        if hasattr(p.v, 'unknownAttributes'):
            fromVnode = [dict(i) for i in p.v.u.get('icons', [])]
            for i in fromVnode: i['on'] = 'VNode'
        return fromVnode
    #@+node:ekr.20150514063305.234: *5* ec.setIconList & helpers
    def setIconList(self, p, l, setDirty=True):
        """Set list of icons for position p to l"""
        current = self.getIconList(p)
        if not l and not current: return # nothing to do
        lHash = ''.join([self.dHash(i) for i in l])
        cHash = ''.join([self.dHash(i) for i in current])
        if lHash == cHash:
            # no difference between original and current list of dictionaries
            return
        self._setIconListHelper(p, l, p.v, setDirty)
    #@+node:ekr.20150514063305.235: *6* ec._setIconListHelper
    def _setIconListHelper(self, p, subl, uaLoc, setDirty):
        """icon setting code common between v and t nodes

        p - postion
        subl - list of icons for the v or t node
        uaLoc - the v or t node
        """
        if subl: # Update the uA.
            if not hasattr(uaLoc, 'unknownAttributes'):
                uaLoc.unknownAttributes = {}
            uaLoc.unknownAttributes['icons'] = list(subl)
            # g.es((p.h,uaLoc.unknownAttributes['icons']))
            uaLoc._p_changed = 1
            if setDirty:
                p.setDirty()
        else: # delete the uA.
            if hasattr(uaLoc, 'unknownAttributes'):
                if 'icons' in uaLoc.unknownAttributes:
                    del uaLoc.unknownAttributes['icons']
                    uaLoc._p_changed = 1
                    if setDirty:
                        p.setDirty()
    #@+node:ekr.20150514063305.236: *4* ec.deleteFirstIcon
    @cmd('delete-first-icon')
    def deleteFirstIcon(self, event=None):
        """Delete the first icon in the selected node's icon list."""
        c = self.c
        aList = self.getIconList(c.p)
        if aList:
            self.setIconList(c.p, aList[1:])
            c.setChanged(True)
            c.redraw_after_icons_changed()
    #@+node:ekr.20150514063305.237: *4* ec.deleteIconByName
    def deleteIconByName(self, t, name, relPath): # t not used.
        """for use by the right-click remove icon callback"""
        c, p = self.c, self.c.p
        aList = self.getIconList(p)
        if not aList:
            return
        basePath = g.os_path_finalize_join(g.app.loadDir, "..", "Icons") # #1341.
        absRelPath = g.os_path_finalize_join(basePath, relPath) # #1341
        name = g.os_path_finalize(name) # #1341
        newList = []
        for d in aList:
            name2 = d.get('file')
            name2 = g.os_path_finalize(name2) # #1341
            name2rel = d.get('relPath')
            if not (name == name2 or absRelPath == name2 or relPath == name2rel):
                newList.append(d)
        if len(newList) != len(aList):
            self.setIconList(p, newList)
            c.setChanged(True)
            c.redraw_after_icons_changed()
        else:
            g.trace('not found', name)
    #@+node:ekr.20150514063305.238: *4* ec.deleteLastIcon
    @cmd('delete-last-icon')
    def deleteLastIcon(self, event=None):
        """Delete the first icon in the selected node's icon list."""
        c = self.c
        aList = self.getIconList(c.p)
        if aList:
            self.setIconList(c.p, aList[: -1])
            c.setChanged(True)
            c.redraw_after_icons_changed()
    #@+node:ekr.20150514063305.239: *4* ec.deleteNodeIcons
    @cmd('delete-node-icons')
    def deleteNodeIcons(self, event=None, p=None):
        """Delete all of the selected node's icons."""
        c = self.c
        p = p or c.p
        if p.u:
            p.v._p_changed = 1
            self.setIconList(p, [])
            p.setDirty()
            c.setChanged(True)
            c.redraw_after_icons_changed()
    #@+node:ekr.20150514063305.240: *4* ec.insertIcon
    @cmd('insert-icon')
    def insertIcon(self, event=None):
        """Prompt for an icon, and insert it into the node's icon list."""
        c, p = self.c, self.c.p
        iconDir = g.os_path_finalize_join(g.app.loadDir, "..", "Icons")
        os.chdir(iconDir)
        paths = g.app.gui.runOpenFileDialog(c,
            title='Get Icons',
            filetypes=[('All files', '*'), ('Gif', '*.gif'), ('Bitmap', '*.bmp'), ('Icon', '*.ico'),],
            defaultextension=None,
            multiple=True)
        if not paths: return
        aList = []
        xoffset = 2
        for path in paths:
            xoffset = self.appendImageDictToList(aList, path, xoffset)
        aList2 = self.getIconList(p)
        aList2.extend(aList)
        self.setIconList(p, aList2)
        c.setChanged(True)
        c.redraw_after_icons_changed()
    #@+node:ekr.20150514063305.241: *4* ec.insertIconFromFile
    def insertIconFromFile(self, path, p=None, pos=None, **kargs):
        c = self.c
        if not p: p = c.p
        aList = []
        xoffset = 2
        xoffset = self.appendImageDictToList(aList, path, xoffset, **kargs)
        aList2 = self.getIconList(p)
        if pos is None: pos = len(aList2)
        aList2.insert(pos, aList[0])
        self.setIconList(p, aList2)
        c.setChanged(True)
        c.redraw_after_icons_changed()
    #@+node:ekr.20150514063305.242: *3* ec: indent
    #@+node:ekr.20150514063305.243: *4* ec.deleteIndentation
    @cmd('delete-indentation')
    def deleteIndentation(self, event):
        """Delete indentation in the presently line."""
        w = self.editWidget(event)
        if not w:
            return
        s = w.getAllText()
        ins = w.getInsertPoint()
        i, j = g.getLine(s, ins)
        line = s[i: j]
        line2 = s[i: j].lstrip()
        delta = len(line) - len(line2)
        if delta:
            self.beginCommand(w, undoType='delete-indentation')
            w.delete(i, j)
            w.insert(i, line2)
            ins -= delta
            w.setSelectionRange(ins, ins, insert=ins)
            self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.244: *4* ec.indentRelative
    @cmd('indent-relative')
    def indentRelative(self, event):
        """
        The indent-relative command indents at the point based on the previous
        line (actually, the last non-empty line.) It inserts whitespace at the
        point, moving point, until it is underneath an indentation point in the
        previous line.

        An indentation point is the end of a sequence of whitespace or the end of
        the line. If the point is farther right than any indentation point in the
        previous line, the whitespace before point is deleted and the first
        indentation point then applicable is used. If no indentation point is
        applicable even then whitespace equivalent to a single tab is inserted.
        """
        c = self.c
        undoType = 'indent-relative'
        w = self.editWidget(event)
        if not w:
            return
        s = w.getAllText()
        ins = w.getInsertPoint()
        oldSel = w.getSelectionRange()
        oldYview = w.getYScrollPosition()
        # Find the previous non-blank line
        i, j = g.getLine(s, ins)
        while 1:
            if i <= 0: return
            i, j = g.getLine(s, i - 1)
            line = s[i: j]
            if line.strip(): break
        self.beginCommand(w, undoType=undoType)
        try:
            k = g.skip_ws(s, i)
            ws = s[i: k]
            i2, j2 = g.getLine(s, ins)
            k = g.skip_ws(s, i2)
            line = ws + s[k: j2]
            w.delete(i2, j2)
            w.insert(i2, line)
            w.setInsertPoint(i2 + len(ws))
            c.frame.body.onBodyChanged(undoType, oldSel=oldSel, oldText=s, oldYview=oldYview)
        finally:
            self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.245: *3* ec: info
    #@+node:ekr.20150514063305.247: *4* ec.lineNumber
    @cmd('line-number')
    def lineNumber(self, event):
        """Print the line and column number and percentage of insert point."""
        k = self.c.k
        w = self.editWidget(event)
        if not w:
            return
        s = w.getAllText()
        i = w.getInsertPoint()
        row, col = g.convertPythonIndexToRowCol(s, i)
        percent = int((i * 100) / len(s))
        k.setLabelGrey(
            'char: %s row: %d col: %d pos: %d (%d%% of %d)' % (
                repr(s[i]), row, col, i, percent, len(s)))
    #@+node:ekr.20150514063305.248: *4* ec.k.viewLossage
    @cmd('view-lossage')
    def viewLossage(self, event):
        """Put the Emacs-lossage in the minibuffer label."""
        k = self.c.k
        g.es('lossage...')
        aList = g.app.lossage
        aList.reverse()
        for data in aList:
            ch, stroke = data
            g.es('', k.prettyPrintKey(stroke))
    #@+node:ekr.20150514063305.249: *4* ec.whatLine
    @cmd('what-line')
    def whatLine(self, event):
        """Print the line number of the line containing the cursor."""
        k = self.c.k
        w = self.editWidget(event)
        if w:
            s = w.getAllText()
            i = w.getInsertPoint()
            row, col = g.convertPythonIndexToRowCol(s, i)
            k.keyboardQuit()
            k.setStatusLabel("Line %s" % row)
    #@+node:ekr.20150514063305.250: *3* ec: insert & delete
    #@+node:ekr.20150514063305.251: *4* ec.addSpace/TabToLines & removeSpace/TabFromLines & helper
    @cmd('add-space-to-lines')
    def addSpaceToLines(self, event):
        """Add a space to start of all lines, or all selected lines."""
        self.addRemoveHelper(event, ch=' ', add=True, undoType='add-space-to-lines')

    @cmd('add-tab-to-lines')
    def addTabToLines(self, event):
        """Add a tab to start of all lines, or all selected lines."""
        self.addRemoveHelper(event, ch='\t', add=True, undoType='add-tab-to-lines')

    @cmd('remove-space-from-lines')
    def removeSpaceFromLines(self, event):
        """Remove a space from start of all lines, or all selected lines."""
        self.addRemoveHelper(event, ch=' ', add=False, undoType='remove-space-from-lines')

    @cmd('remove-tab-from-lines')
    def removeTabFromLines(self, event):
        """Remove a tab from start of all lines, or all selected lines."""
        self.addRemoveHelper(event, ch='\t', add=False, undoType='remove-tab-from-lines')
    #@+node:ekr.20150514063305.252: *5* ec.addRemoveHelper
    def addRemoveHelper(self, event, ch, add, undoType):
        c = self.c
        w = self.editWidget(event)
        if not w:
            return
        if w.hasSelection(): s = w.getSelectedText()
        else: s = w.getAllText()
        if not s:
            return
        # Insert or delete spaces instead of tabs when negative tab width is in effect.
        d = c.scanAllDirectives()
        width = d.get('tabwidth')
        if ch == '\t' and width < 0: ch = ' ' * abs(width)
        self.beginCommand(w, undoType=undoType)
        lines = g.splitLines(s)
        if add:
            result = [ch + line for line in lines]
        else:
            result = [line[len(ch):] if line.startswith(ch) else line for line in lines]
        result = ''.join(result)
        if w.hasSelection():
            i, j = w.getSelectionRange()
            w.delete(i, j)
            w.insert(i, result)
            w.setSelectionRange(i, i + len(result))
        else:
            w.setAllText(result)
            w.setSelectionRange(0, len(s))
        self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.253: *4* ec.backwardDeleteCharacter
    @cmd('backward-delete-char')
    def backwardDeleteCharacter(self, event=None):
        """Delete the character to the left of the cursor."""
        c = self.c
        w = self.editWidget(event)
        if not w:
            return
        wname = c.widget_name(w)
        ins = w.getInsertPoint()
        i, j = w.getSelectionRange()
        if wname.startswith('body'):
            self.beginCommand(w)
            try:
                tab_width = c.getTabWidth(c.p)
                changed = True
                if i != j:
                    w.delete(i, j)
                    w.setSelectionRange(i, i, insert=i)
                elif i == 0:
                    changed = False
                elif tab_width > 0:
                    w.delete(ins - 1)
                    w.setSelectionRange(ins - 1, ins - 1, insert=ins - 1)
                else:
                    #@+<< backspace with negative tab_width >>
                    #@+node:ekr.20150514063305.254: *5* << backspace with negative tab_width >>
                    s = prev = w.getAllText()
                    ins = w.getInsertPoint()
                    i, j = g.getLine(s, ins)
                    s = prev = s[i: ins]
                    n = len(prev)
                    abs_width = abs(tab_width)
                    # Delete up to this many spaces.
                    n2 = (n % abs_width) or abs_width
                    n2 = min(n, n2)
                    count = 0
                    while n2 > 0:
                        n2 -= 1
                        ch = prev[n - count - 1]
                        if ch != ' ': break
                        else: count += 1
                    # Make sure we actually delete something.
                    i = ins - (max(1, count))
                    w.delete(i, ins)
                    w.setSelectionRange(i, i, insert=i)
                    #@-<< backspace with negative tab_width >>
            finally:
                self.endCommand(changed=changed, setLabel=False)
                    # Necessary to make text changes stick.
        else:
            # No undo in this widget.
            # Make sure we actually delete something if we can.
            s = w.getAllText()
            if i != j:
                j = max(i, min(j, len(s)))
                w.delete(i, j)
                w.setSelectionRange(i, i, insert=i)
            elif ins != 0:
                # Do nothing at the start of the headline.
                w.delete(ins - 1)
                ins = ins - 1
                w.setSelectionRange(ins, ins, insert=ins)
    #@+node:ekr.20150514063305.255: *4* ec.cleanAllLines (changed)
    @cmd('clean-all-lines')
    def cleanAllLines(self, event):
        """Clean all lines in the selected tree."""
        c = self.c
        u = c.undoer
        w = c.frame.body.wrapper
        if not w: return
        tag = 'clean-all-lines'
        u.beforeChangeGroup(c.p, tag)
        n = 0
        for p in c.p.self_and_subtree():
            lines = []
            for line in g.splitLines(p.b):
                if line.rstrip():
                    lines.append(line.rstrip())
                if line.endswith('\n'):
                    lines.append('\n')
            s2 = ''.join(lines)
            if s2 != p.b:
                print(p.h)
                bunch = u.beforeChangeNodeContents(p)
                p.b = s2
                p.setDirty() # Was p.v.setDirty.
                n += 1
                u.afterChangeNodeContents(p, tag, bunch)
        u.afterChangeGroup(c.p, tag)
        c.redraw_after_icons_changed()
        g.es('cleaned %s nodes' % n)
    #@+node:ekr.20150514063305.256: *4* ec.cleanLines
    @cmd('clean-lines')
    def cleanLines(self, event):
        """Removes trailing whitespace from all lines, preserving newlines.
        """
        w = self.editWidget(event)
        if not w:
            return
        if w.hasSelection():
            s = w.getSelectedText()
        else:
            s = w.getAllText()
        lines = []
        for line in g.splitlines(s):
            if line.rstrip():
                lines.append(line.rstrip())
            if line.endswith('\n'):
                lines.append('\n')
        result = ''.join(lines)
        if s != result:
            self.beginCommand(w, undoType='clean-lines')
            if w.hasSelection():
                i, j = w.getSelectionRange()
                w.delete(i, j)
                w.insert(i, result)
                w.setSelectionRange(i, j + len(result))
            else:
                i = w.getInsertPoint()
                w.delete(0, 'end')
                w.insert(0, result)
                w.setInsertPoint(i)
            self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.257: *4* ec.clearSelectedText
    @cmd('clear-selected-text')
    def clearSelectedText(self, event):
        """Delete the selected text."""
        w = self.editWidget(event)
        if not w: return
        i, j = w.getSelectionRange()
        if i == j: return
        self.beginCommand(w, undoType='clear-selected-text')
        w.delete(i, j)
        w.setInsertPoint(i)
        self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.258: *4* ec.delete-word & backward-delete-word
    @cmd('delete-word')
    def deleteWord(self, event=None):
        """Delete the word at the cursor."""
        self.deleteWordHelper(event, forward=True)

    @cmd('backward-delete-word')
    def backwardDeleteWord(self, event=None):
        """Delete the word in front of the cursor."""
        self.deleteWordHelper(event, forward=False)
    # Patch by NH2.

    @cmd('delete-word-smart')
    def deleteWordSmart(self, event=None):
        """Delete the word at the cursor, treating whitespace
        and symbols smartly."""
        self.deleteWordHelper(event, forward=True, smart=True)

    @cmd('backward-delete-word-smart')
    def backwardDeleteWordSmart(self, event=None):
        """Delete the word in front of the cursor, treating whitespace
        and symbols smartly."""
        self.deleteWordHelper(event, forward=False, smart=True)

    def deleteWordHelper(self, event, forward, smart=False):
        # c = self.c
        w = self.editWidget(event)
        if not w:
            return
        self.beginCommand(w, undoType="delete-word")
        if w.hasSelection():
            from_pos, to_pos = w.getSelectionRange()
        else:
            from_pos = w.getInsertPoint()
            self.moveWordHelper(event, extend=False, forward=forward, smart=smart)
            to_pos = w.getInsertPoint()
        # For Tk GUI, make sure to_pos > from_pos
        if from_pos > to_pos:
            from_pos, to_pos = to_pos, from_pos
        w.delete(from_pos, to_pos)
        self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.259: *4* ec.deleteNextChar
    @cmd('delete-char')
    def deleteNextChar(self, event):
        """Delete the character to the right of the cursor."""
        w = self.editWidget(event)
        if not w: return
        s = w.getAllText()
        i, j = w.getSelectionRange()
        self.beginCommand(w, undoType='delete-char')
        changed = True
        if i != j:
            w.delete(i, j)
            w.setInsertPoint(i)
        elif j < len(s):
            w.delete(i)
            w.setInsertPoint(i)
        else:
            changed = False
        self.endCommand(changed=changed, setLabel=False)
    #@+node:ekr.20150514063305.260: *4* ec.deleteSpaces
    @cmd('delete-spaces')
    def deleteSpaces(self, event, insertspace=False):
        """Delete all whitespace surrounding the cursor."""
        w = self.editWidget(event)
        if not w:
            return
        undoType = 'insert-space' if insertspace else 'delete-spaces'
        s = w.getAllText()
        ins = w.getInsertPoint()
        i, j = g.getLine(s, ins)
        w1 = ins - 1
        while w1 >= i and s[w1].isspace():
            w1 -= 1
        w1 += 1
        w2 = ins
        while w2 <= j and s[w2].isspace():
            w2 += 1
        spaces = s[w1: w2]
        if spaces:
            self.beginCommand(w, undoType=undoType)
            if insertspace: s = s[: w1] + ' ' + s[w2:]
            else: s = s[: w1] + s[w2:]
            w.setAllText(s)
            w.setInsertPoint(w1)
            self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.261: *4* ec.insertHardTab
    @cmd('insert-hard-tab')
    def insertHardTab(self, event):
        """Insert one hard tab."""
        c = self.c
        w = self.editWidget(event)
        if not w:
            return
        if not g.isTextWrapper(w):
            return
        name = c.widget_name(w)
        if name.startswith('head'):
            return
        ins = w.getInsertPoint()
        self.beginCommand(w, undoType='insert-hard-tab')
        w.insert(ins, '\t')
        ins += 1
        w.setSelectionRange(ins, ins, insert=ins)
        self.endCommand()
    #@+node:ekr.20150514063305.262: *4* ec.insertNewLine
    @cmd('insert-newline')
    def insertNewLine(self, event):
        """Insert a newline at the cursor."""
        self.insertNewlineBase(event)

    insertNewline = insertNewLine

    def insertNewlineBase(self, event):
        """A helper that can be monkey-patched by tables.py plugin."""
        # Note: insertNewlineHelper already exists.
        c, k = self.c, self.c.k
        w = self.editWidget(event)
        if not w:
            return
        if not g.isTextWrapper(w):
            return
        name = c.widget_name(w)
        if name.startswith('head'):
            return
        oldSel = w.getSelectionRange()
        self.beginCommand(w, undoType='newline')
        self.insertNewlineHelper(w=w, oldSel=oldSel, undoType=None)
        k.setInputState('insert')
        k.showStateAndMode()
        self.endCommand()
    #@+node:ekr.20150514063305.263: *4* ec.insertNewLineAndTab
    @cmd('newline-and-indent')
    def insertNewLineAndTab(self, event):
        """Insert a newline and tab at the cursor."""
        c, k = self.c, self.c.k
        p = c.p
        w = self.editWidget(event)
        if not w:
            return
        if not g.isTextWrapper(w):
            return
        name = c.widget_name(w)
        if name.startswith('head'):
            return
        self.beginCommand(w, undoType='insert-newline-and-indent')
        oldSel = w.getSelectionRange()
        self.insertNewlineHelper(w=w, oldSel=oldSel, undoType=None)
        self.updateTab(p, w, smartTab=False)
        k.setInputState('insert')
        k.showStateAndMode()
        self.endCommand(changed=True, setLabel=False)
    #@+node:ekr.20150514063305.264: *4* ec.insertParentheses
    @cmd('insert-parentheses')
    def insertParentheses(self, event):
        """Insert () at the cursor."""
        w = self.editWidget(event)
        if w:
            self.beginCommand(w, undoType='insert-parenthesis')
            i = w.getInsertPoint()
            w.insert(i, '()')
            w.setInsertPoint(i + 1)
            self.endCommand(changed=True, setLabel=False)
    #@+node:ekr.20150514063305.265: *4* ec.insertSoftTab
    @cmd('insert-soft-tab')
    def insertSoftTab(self, event):
        """Insert spaces equivalent to one tab."""
        c = self.c
        w = self.editWidget(event)
        if not w:
            return
        if not g.isTextWrapper(w):
            return
        name = c.widget_name(w)
        if name.startswith('head'): return
        tab_width = abs(c.getTabWidth(c.p))
        ins = w.getInsertPoint()
        self.beginCommand(w, undoType='insert-soft-tab')
        w.insert(ins, ' ' * tab_width)
        ins += tab_width
        w.setSelectionRange(ins, ins, insert=ins)
        self.endCommand()
    #@+node:ekr.20150514063305.266: *4* ec.removeBlankLines
    @cmd('remove-blank-lines')
    def removeBlankLines(self, event):
        """
        Remove lines containing nothing but whitespace.

        Select all lines if there is no existing selection.
        """
        c = self.c
        w = self.editWidget(event)
        expandSelection = not w.hasSelection()
        head, lines, tail, oldSel, oldYview = c.getBodyLines(expandSelection=expandSelection)
        changed, result = False, []
        for line in lines:
            if line.strip():
                result.append(line)
            else:
                changed = True
        result = ''.join(result)
        if changed:
            oldSel, undoType = None, 'remove-blank-lines'
            c.updateBodyPane(head, result, tail, undoType, oldSel, oldYview)
    #@+node:ekr.20150514063305.267: *4* ec.replaceCurrentCharacter
    @cmd('replace-current-character')
    def replaceCurrentCharacter(self, event):
        """Replace the current character with the next character typed."""
        k = self.c.k
        self.w = self.editWidget(event)
        if self.w:
            k.setLabelBlue('Replace Character: ')
            k.get1Arg(event, handler=self.replaceCurrentCharacter1)

    def replaceCurrentCharacter1(self, event):
        c, k, w = self.c, self.c.k, self.w
        ch = k.arg
        if ch:
            i, j = w.getSelectionRange()
            if i > j: i, j = j, i
            # Use raw insert/delete to retain the coloring.
            if i == j:
                i = max(0, i - 1)
                w.delete(i)
            else:
                w.delete(i, j)
            w.insert(i, ch)
            w.setInsertPoint(i + 1)
        k.clearState()
        k.resetLabel()
        k.showStateAndMode()
        c.widgetWantsFocus(w)
    #@+node:ekr.20150514063305.268: *4* ec.selfInsertCommand, helpers
    # @cmd('self-insert-command')
    def selfInsertCommand(self, event, action='insert'):
        """
        Insert a character in the body pane.

        This is the default binding for all keys in the body pane.
        It handles undo, bodykey events, tabs, back-spaces and bracket matching.
        """
        c, p = self.c, self.c.p
        w = self.editWidget(event)
        if not w:
            return
        #@+<< set local vars >>
        #@+node:ekr.20150514063305.269: *5* << set local vars >> (selfInsertCommand)
        stroke = event.stroke if event else None
        ch = event.char if event else ''
        if ch == 'Return':
            ch = '\n' # This fixes the MacOS return bug.
        if ch == 'Tab':
            ch = '\t'
        name = c.widget_name(w)
        oldSel = w.getSelectionRange() if name.startswith('body') else (None, None)
        oldText = p.b if name.startswith('body') else ''
        undoType = 'Typing'
        brackets = self.openBracketsList + self.closeBracketsList
        inBrackets = ch and g.checkUnicode(ch) in brackets
        #@-<< set local vars >>
        assert g.isStrokeOrNone(stroke)
        if g.doHook("bodykey1", c=c, p=p, ch=ch, oldSel=oldSel, undoType=undoType):
            return
        if ch == '\t':
            self.updateTab(p, w)
        elif ch == '\b':
            # This is correct: we only come here if there no bindngs for this key.
            self.backwardDeleteCharacter(event)
        elif ch in ('\r', '\n'):
            ch = '\n'
            self.insertNewlineHelper(w, oldSel, undoType)
        elif ch in '\'"' and c.config.getBool('smart-quotes'):
            self.doSmartQuote(action, ch, oldSel, w)
        elif inBrackets and self.autocompleteBrackets:
            self.updateAutomatchBracket(p, w, ch, oldSel)
        elif ch:
            # Null chars must not delete the selection.
            self.doPlainChar(action, ch, event, inBrackets, oldSel, stroke, w)
        else:
            return
        # Set the column for up and down keys.
        spot = w.getInsertPoint()
        c.editCommands.setMoveCol(w, spot)
        # Update the text and handle undo.
        newText = w.getAllText()
        changed = newText != oldText
        if changed:
            c.frame.body.onBodyChanged(undoType=undoType,
                oldSel=oldSel, oldText=oldText, oldYview=None)
        g.doHook("bodykey2", c=c, p=p, ch=ch, oldSel=oldSel, undoType=undoType)
    #@+node:ekr.20160924135613.1: *5* ec.doPlainChar
    def doPlainChar(self, action, ch, event, inBrackets, oldSel, stroke, w):
        c, p = self.c, self.c.p
        isPlain = stroke.find('Alt') == -1 and stroke.find('Ctrl') == -1
        i, j = oldSel
        if i > j: i, j = j, i
        # Use raw insert/delete to retain the coloring.
        if i != j: w.delete(i, j)
        elif action == 'overwrite': w.delete(i)
        if isPlain:
            ins = w.getInsertPoint()
            if self.autojustify > 0 and not inBrackets:
                # Support #14: auto-justify body text.
                s = w.getAllText()
                i = g.skip_to_start_of_line(s, ins)
                i, j = g.getLine(s, i)
                # Only insert a newline at the end of a line.
                if j - i >= self.autojustify and (ins >= len(s) or s[ins] == '\n'):
                    # Find the start of the word.
                    n = 0
                    ins -= 1
                    while ins-1 > 0 and g.isWordChar(s[ins-1]):
                        n += 1
                        ins -= 1
                    sins = ins  # start of insert, to collect trailing whitespace
                    while sins > 0 and s[sins-1] in (' \t'):
                        sins -= 1
                    oldSel = (sins, ins)
                    self.insertNewlineHelper(w, oldSel, undoType=None)
                    ins = w.getInsertPoint()
                    ins += (n+1)
            w.insert(ins, ch)
            w.setInsertPoint(ins + 1)
        else:
            g.app.gui.insertKeyEvent(event, i)
        if inBrackets and self.flashMatchingBrackets:
            self.flashMatchingBracketsHelper(c, ch, i, p, w)
    #@+node:ekr.20150514063305.270: *5* ec.doPlainTab
    def doPlainTab(self, s, i, tab_width, w):
        """Insert spaces equivalent to one tab."""
        start, end = g.getLine(s, i)
        s2 = s[start: i]
        width = g.computeWidth(s2, tab_width)
        if tab_width > 0:
            w.insert(i, '\t')
            ins = i + 1
        else:
            n = abs(tab_width) - (width % abs(tab_width))
            w.insert(i, ' ' * n)
            ins = i + n
        w.setSelectionRange(ins, ins, insert=ins)
    #@+node:ekr.20180806045802.1: *5* ec.doSmartQuote
    def doSmartQuote(self, action, ch, oldSel, w):
        """Convert a straight quote to a curly quote, depending on context."""
        i, j = oldSel
        if i > j:
            i, j = j, i
        # Use raw insert/delete to retain the coloring.
        if i != j:
            w.delete(i, j)
        elif action == 'overwrite':
            w.delete(i)
        ins = w.getInsertPoint()
        # Pick the correct curly quote.
        s = w.getAllText() or ""
        i2 = g.skip_to_start_of_line(s, max(0,ins-1))
        open_curly = ins == i2 or ins > i2 and s[ins-1] in ' \t'
            # not s[ins-1].isalnum()
        if open_curly:
            ch = '‘' if ch == "'" else "“"
        else:
            ch = '’' if ch == "'" else "”"
        w.insert(ins, ch)
        w.setInsertPoint(ins + 1)
    #@+node:ekr.20150514063305.271: *5* ec.flashCharacter
    def flashCharacter(self, w, i):
        """Flash the character at position i of widget w."""
        bg = self.bracketsFlashBg or 'DodgerBlue1'
        fg = self.bracketsFlashFg or 'white'
        flashes = self.bracketsFlashCount or 3
        delay = self.bracketsFlashDelay or 75
        w.flashCharacter(i, bg, fg, flashes, delay)
    #@+node:ekr.20150514063305.272: *5* ec.flashMatchingBracketsHelper
    def flashMatchingBracketsHelper(self, c, ch, i, p, w):
        """Flash matching brackets at char ch at position i at widget w."""
        d = {}
        if ch in self.openBracketsList:
            for z in range(len(self.openBracketsList)):
                d[self.openBracketsList[z]] = self.closeBracketsList[z]
            # reverse = False # Search forward
        else:
            for z in range(len(self.openBracketsList)):
                d[self.closeBracketsList[z]] = self.openBracketsList[z]
            # reverse = True # Search backward
        s = w.getAllText()
        # A partial fix for bug 127: Bracket matching is buggy.
        language = g.getLanguageAtPosition(c, p)
        if language ==  'perl':
            return
        j = g.MatchBrackets(c, p, language).find_matching_bracket(ch, s, i)
        if j is not None:
            self.flashCharacter(w, j)
    #@+node:ekr.20150514063305.273: *5* ec.initBracketMatcher
    def initBracketMatcher(self, c):
        """Init the bracket matching code."""
        if len(self.openBracketsList) != len(self.closeBracketsList):
            g.es_print('bad open/close_flash_brackets setting: using defaults')
            self.openBracketsList = '([{'
            self.closeBracketsList = ')]}'
    #@+node:ekr.20150514063305.274: *5* ec.insertNewlineHelper
    def insertNewlineHelper(self, w, oldSel, undoType):

        c, p = self.c, self.c.p
        i, j = oldSel
        ch = '\n'
        if i != j:
            # No auto-indent if there is selected text.
            w.delete(i, j)
            w.insert(i, ch)
            w.setInsertPoint(i + 1)
        else:
            w.insert(i, ch)
            w.setInsertPoint(i + 1)
            if (c.autoindent_in_nocolor or
                (c.frame.body.colorizer.useSyntaxColoring(p) and
                undoType != "Change")
            ):
                # No auto-indent if in @nocolor mode or after a Change command.
                self.updateAutoIndent(p, w)
        w.seeInsertPoint()
    #@+node:ekr.20150514063305.275: *5* ec.updateAutoIndent
    def updateAutoIndent(self, p, w):
        """Handle auto indentation."""
        c = self.c
        tab_width = c.getTabWidth(p)
        # Get the previous line.
        s = w.getAllText()
        ins = w.getInsertPoint()
        i = g.skip_to_start_of_line(s, ins)
        i, j = g.getLine(s, i - 1)
        s = s[i: j - 1]
        # Add the leading whitespace to the present line.
        junk, width = g.skip_leading_ws_with_indent(s, 0, tab_width)
        if s and s[-1] == ':':
            # For Python: increase auto-indent after colons.
            if g.findLanguageDirectives(c, p) == 'python':
                width += abs(tab_width)
        if self.smartAutoIndent:
            # Determine if prev line has unclosed parens/brackets/braces
            bracketWidths = [width]
            tabex = 0
            for i, ch in enumerate(s):
                if ch == '\t':
                    tabex += tab_width - 1
                if ch in '([{':
                    bracketWidths.append(i + tabex + 1)
                elif ch in '}])' and len(bracketWidths) > 1:
                    bracketWidths.pop()
            width = bracketWidths.pop()
        ws = g.computeLeadingWhitespace(width, tab_width)
        if ws:
            i = w.getInsertPoint()
            w.insert(i, ws)
            w.setInsertPoint(i + len(ws))
            w.seeInsertPoint()
                # 2011/10/02: Fix cursor-movement bug.
    #@+node:ekr.20150514063305.276: *5* ec.updateAutomatchBracket
    def updateAutomatchBracket(self, p, w, ch, oldSel):

        c = self.c
        d = c.scanAllDirectives(p)
        i, j = oldSel
        language = d.get('language')
        s = w.getAllText()
        if ch in ('(', '[', '{',):
            automatch = language not in ('plain',)
            if automatch:
                ch = ch + {'(': ')', '[': ']', '{': '}'}.get(ch)
            if i != j: w.delete(i, j)
            w.insert(i, ch)
            if automatch:
                ins = w.getInsertPoint()
                w.setInsertPoint(ins - 1)
        else:
            ins = w.getInsertPoint()
            ch2 = s[ins] if ins < len(s) else ''
            if ch2 in (')', ']', '}'):
                ins = w.getInsertPoint()
                w.setInsertPoint(ins + 1)
            else:
                if i != j: w.delete(i, j)
                w.insert(i, ch)
                w.setInsertPoint(i + 1)
    #@+node:ekr.20150514063305.277: *5* ec.updateTab
    def updateTab(self, p, w, smartTab=True):
        """Add spaces equivalent to a tab."""
        c = self.c
        i, j = w.getSelectionRange()
            # Returns insert point if no selection, with i <= j.
        if i != j:
            # w.delete(i,j)
            c.indentBody()
        else:
            tab_width = c.getTabWidth(p)
            # Get the preceeding characters.
            s = w.getAllText()
            start, end = g.getLine(s, i)
            after = s[i: end]
            if after.endswith('\n'): after = after[: -1]
            # Only do smart tab at the start of a blank line.
            doSmartTab = (smartTab and c.smart_tab and i == start)
                # Truly at the start of the line.
                # and not after # Nothing *at all* after the cursor.
            if doSmartTab:
                self.updateAutoIndent(p, w)
                # Add a tab if otherwise nothing would happen.
                if s == w.getAllText():
                    self.doPlainTab(s, i, tab_width, w)
            else:
                self.doPlainTab(s, i, tab_width, w)
    #@+node:ekr.20150514063305.280: *3* ec: lines
    #@+node:ekr.20150514063305.281: *4* ec.flushLines (doesn't work)
    @cmd('flush-lines')
    def flushLines(self, event):
        """
        Delete each line that contains a match for regexp, operating on the
        text after point.

        In Transient Mark mode, if the region is active, the command operates
        on the region instead.
        """
        k = self.c.k
        k.setLabelBlue('Flush lines regexp: ')
        k.get1Arg(event, handler=self.flushLines1)

    def flushLines1(self, event):
        k = self.c.k
        k.clearState()
        k.resetLabel()
        self.linesHelper(event, k.arg, 'flush')
        k.commandName = 'flush-lines %s' % k.arg
    #@+node:ekr.20150514063305.282: *4* ec.keepLines (doesn't work)
    @cmd('keep-lines')
    def keepLines(self, event):
        """
        Delete each line that does not contain a match for regexp, operating on
        the text after point.

        In Transient Mark mode, if the region is active, the command operates
        on the region instead.
        """
        k = self.c.k
        k.setLabelBlue('Keep lines regexp: ')
        k.get1Arg(event, handler=self.keepLines1)

    def keepLines1(self, event):
        k = self.c.k
        k.clearState()
        k.resetLabel()
        self.linesHelper(event, k.arg, 'keep')
        k.commandName = 'keep-lines %s' % k.arg
    #@+node:ekr.20150514063305.283: *4* ec.linesHelper
    def linesHelper(self, event, pattern, which):
        w = self.editWidget(event)
        if not w:
            return
        self.beginCommand(w, undoType=which + '-lines')
        if w.hasSelection():
            i, end = w.getSelectionRange()
        else:
            i = w.getInsertPoint()
            end = 'end'
        txt = w.get(i, end)
        tlines = txt.splitlines(True)
        keeplines = list(tlines) if which == 'flush' else []
        try:
            regex = re.compile(pattern)
            for n, z in enumerate(tlines):
                f = regex.findall(z)
                if which == 'flush' and f:
                    keeplines[n] = None
                elif f:
                    keeplines.append(z)
        except Exception:
            return
        if which == 'flush':
            keeplines = [x for x in keeplines if x is not None]
        w.delete(i, end)
        w.insert(i, ''.join(keeplines))
        w.setInsertPoint(i)
        self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.284: *4* ec.splitLine
    @cmd('split-line')
    def splitLine(self, event):
        """Split a line at the cursor position."""
        w = self.editWidget(event)
        if w:
            self.beginCommand(w, undoType='split-line')
            s = w.getAllText()
            ins = w.getInsertPoint()
            w.setAllText(s[: ins] + '\n' + s[ins:])
            w.setInsertPoint(ins + 1)
            self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.285: *3* ec: move cursor
    #@+node:ekr.20150514063305.286: *4* ec. helpers
    #@+node:ekr.20150514063305.287: *5* ec.extendHelper
    def extendHelper(self, w, extend, spot, upOrDown=False):
        """
        Handle the details of extending the selection.
        This method is called for all cursor moves.

        extend: Clear the selection unless this is True.
        spot:   The *new* insert point.
        """
        c, p = self.c, self.c.p
        extend = extend or self.extendMode
        ins = w.getInsertPoint()
        i, j = w.getSelectionRange()
        # Reset the move spot if needed.
        if self.moveSpot is None or p.v != self.moveSpotNode:
            self.setMoveCol(w, ins if extend else spot) # sets self.moveSpot.
        elif extend:
            # 2011/05/20: Fix bug 622819
            # Ctrl-Shift movement is incorrect when there is an unexpected selection.
            if i == j:
                self.setMoveCol(w, ins) # sets self.moveSpot.
            elif self.moveSpot in (i, j) and self.moveSpot != ins:
                # The bug fix, part 1.
                pass
            else:
                # The bug fix, part 2.
                # Set the moveCol to the *not* insert point.
                if ins == i: k = j
                elif ins == j: k = i
                else: k = ins
                self.setMoveCol(w, k) # sets self.moveSpot.
        else:
            if upOrDown:
                s = w.getAllText()
                i2, j2 = g.getLine(s, spot)
                line = s[i2: j2]
                row, col = g.convertPythonIndexToRowCol(s, spot)
                if True: # was j2 < len(s)-1:
                    n = min(self.moveCol, max(0, len(line) - 1))
                else:
                    n = min(self.moveCol, max(0, len(line))) # A tricky boundary.
                spot = g.convertRowColToPythonIndex(s, row, n)
            else: # Plain move forward or back.
                self.setMoveCol(w, spot) # sets self.moveSpot.
        if extend:
            if spot < self.moveSpot:
                w.setSelectionRange(spot, self.moveSpot, insert=spot)
            else:
                w.setSelectionRange(self.moveSpot, spot, insert=spot)
        else:
            w.setSelectionRange(spot, spot, insert=spot)
        w.seeInsertPoint()
        c.frame.updateStatusLine()
    #@+node:ekr.20150514063305.288: *5* ec.moveToHelper
    def moveToHelper(self, event, spot, extend):
        """
        Common helper method for commands the move the cursor
        in a way that can be described by a Tk Text expression.
        """
        c, k = self.c, self.c.k
        w = self.editWidget(event)
        if not w: return
        c.widgetWantsFocusNow(w)
        # Put the request in the proper range.
        if c.widget_name(w).startswith('mini'):
            i, j = k.getEditableTextRange()
            if spot < i: spot = i
            elif spot > j: spot = j
        self.extendHelper(w, extend, spot, upOrDown=False)
    #@+node:ekr.20150514063305.305: *5* ec.moveWithinLineHelper
    def moveWithinLineHelper(self, event, spot, extend):
        w = self.editWidget(event)
        if not w:
            return
        # Bug fix: 2012/02/28: don't use the Qt end-line logic:
        # it apparently does not work for wrapped lines.
        spots = ('end-line', 'finish-line', 'start-line')
        if hasattr(w, 'leoMoveCursorHelper') and spot not in spots:
            extend = extend or self.extendMode
            w.leoMoveCursorHelper(kind=spot, extend=extend)
        else:
            s = w.getAllText()
            ins = w.getInsertPoint()
            i, j = g.getLine(s, ins)
            line = s[i:j]
            if spot == 'begin-line': # was 'start-line'
                self.moveToHelper(event, i, extend=extend)
            elif spot == 'end-line':
                # Bug fix: 2011/11/13: Significant in external tests.
                if g.match(s, j - 1, '\n') and i != j: j -= 1
                self.moveToHelper(event, j, extend=extend)
            elif spot == 'finish-line':
                if not line.isspace():
                    if g.match(s, j - 1, '\n'): j -= 1
                    while j >= 0 and s[j].isspace():
                        j -= 1
                self.moveToHelper(event, j, extend=extend)
            elif spot == 'start-line': # new
                if not line.isspace():
                    while i < j and s[i].isspace():
                        i += 1
                self.moveToHelper(event, i, extend=extend)
            else:
                g.trace('can not happen: bad spot: %s' % spot)
    #@+node:ekr.20150514063305.317: *5* ec.moveWordHelper
    def moveWordHelper(self, event, extend, forward, end=False, smart=False):
        """
        Move the cursor to the next/previous word.
        The cursor is placed at the start of the word unless end=True
        """
        c = self.c
        w = self.editWidget(event)
        if not w:
            return
        c.widgetWantsFocusNow(w)
        s = w.getAllText()
        n = len(s)
        i = w.getInsertPoint()
        # pylint: disable=anomalous-backslash-in-string
        alphanumeric_re = re.compile("\w")
        whitespace_re = re.compile("\s")
        simple_whitespace_re = re.compile("[ \t]")
        #@+others
        #@+node:ekr.20150514063305.318: *6* ec.moveWordHelper functions
        def is_alphanumeric(c):
            return alphanumeric_re.match(c) is not None

        def is_whitespace(c):
            return whitespace_re.match(c) is not None

        def is_simple_whitespace(c):
            return simple_whitespace_re.match(c) is not None

        def is_line_break(c):
            return is_whitespace(c) and not is_simple_whitespace(c)

        def is_special(c):
            return not is_alphanumeric(c) and not is_whitespace(c)

        def seek_until_changed(i, match_function, step):
            while 0 <= i < n and match_function(s[i]):
                i += step
            return i

        def seek_word_end(i):
            return seek_until_changed(i, is_alphanumeric, 1)

        def seek_word_start(i):
            return seek_until_changed(i, is_alphanumeric, -1)

        def seek_simple_whitespace_end(i):
            return seek_until_changed(i, is_simple_whitespace, 1)

        def seek_simple_whitespace_start(i):
            return seek_until_changed(i, is_simple_whitespace, -1)

        def seek_special_end(i):
            return seek_until_changed(i, is_special, 1)

        def seek_special_start(i):
            return seek_until_changed(i, is_special, -1)
        #@-others
        if smart:
            if forward:
                if 0 <= i < n:
                    if is_alphanumeric(s[i]):
                        i = seek_word_end(i)
                        i = seek_simple_whitespace_end(i)
                    elif is_simple_whitespace(s[i]):
                        i = seek_simple_whitespace_end(i)
                    elif is_special(s[i]):
                        i = seek_special_end(i)
                        i = seek_simple_whitespace_end(i)
                    else:
                        i += 1 # e.g. for newlines
            else:
                i -= 1 # Shift cursor temporarily by -1 to get easy read access to the prev. char
                if 0 <= i < n:
                    if is_alphanumeric(s[i]):
                        i = seek_word_start(i)
                        # Do not seek further whitespace here
                    elif is_simple_whitespace(s[i]):
                        i = seek_simple_whitespace_start(i)
                    elif is_special(s[i]):
                        i = seek_special_start(i)
                        # Do not seek further whitespace here
                    else:
                        i -= 1 # e.g. for newlines
                i += 1
        else:
            if forward:
                # Unlike backward-word moves, there are two options...
                if end:
                    while 0 <= i < n and not g.isWordChar(s[i]):
                        i += 1
                    while 0 <= i < n and g.isWordChar(s[i]):
                        i += 1
                else:
                    while 0 <= i < n and g.isWordChar(s[i]):
                        i += 1
                    while 0 <= i < n and not g.isWordChar(s[i]):
                        i += 1
            else:
                i -= 1
                while 0 <= i < n and not g.isWordChar(s[i]):
                    i -= 1
                while 0 <= i < n and g.isWordChar(s[i]):
                    i -= 1
                i += 1 # 2015/04/30
        self.moveToHelper(event, i, extend)
    #@+node:ekr.20150514063305.289: *5* ec.setMoveCol
    def setMoveCol(self, w, spot):
        """Set the column to which an up or down arrow will attempt to move."""
        p = self.c.p
        i, row, col = w.toPythonIndexRowCol(spot)
        self.moveSpot = i
        self.moveCol = col
        self.moveSpotNode = p.v
    #@+node:ekr.20150514063305.290: *4* ec.backToHome/ExtendSelection
    @cmd('back-to-home')
    def backToHome(self, event, extend=False):
        """
        Smart home:
        Position the point at the first non-blank character on the line,
        or the start of the line if already there.
        """
        w = self.editWidget(event)
        if not w: return
        s = w.getAllText()
        ins = w.getInsertPoint()
        if s:
            i, j = g.getLine(s, ins)
            i1 = i
            while i < j and s[i] in (' \t'):
                i += 1
            if i == ins:
                i = i1
            self.moveToHelper(event, i, extend=extend)

    @cmd('back-to-home-extend-selection')
    def backToHomeExtendSelection(self, event):
        self.backToHome(event, extend=True)
    #@+node:ekr.20150514063305.291: *4* ec.backToIndentation
    @cmd('back-to-indentation')
    def backToIndentation(self, event):
        """Position the point at the first non-blank character on the line."""
        w = self.editWidget(event)
        if not w:
            return
        s = w.getAllText()
        ins = w.getInsertPoint()
        i, j = g.getLine(s, ins)
        while i < j and s[i] in (' \t'):
            i += 1
        self.moveToHelper(event, i, extend=False)
    #@+node:ekr.20150514063305.316: *4* ec.backward*/ExtendSelection
    @cmd('back-word')
    def backwardWord(self, event):
        """Move the cursor to the previous word."""
        self.moveWordHelper(event, extend=False, forward=False)

    @cmd('back-word-extend-selection')
    def backwardWordExtendSelection(self, event):
        """Extend the selection by moving the cursor to the previous word."""
        self.moveWordHelper(event, extend=True, forward=False)

    @cmd('back-word-smart')
    def backwardWordSmart(self, event):
        """Move the cursor to the beginning of the current or the end of the previous word."""
        self.moveWordHelper(event, extend=False, forward=False, smart=True)

    @cmd('back-word-smart-extend-selection')
    def backwardWordSmartExtendSelection(self, event):
        """Extend the selection by moving the cursor to the beginning of the current
        or the end of the previous word."""
        self.moveWordHelper(event, extend=True, forward=False, smart=True)

    #@+node:ekr.20170707072347.1: *4* ec.beginningOfLine/ExtendSelection
    @cmd('beginning-of-line')
    def beginningOfLine(self, event):
        """Move the cursor to the first character of the line."""
        self.moveWithinLineHelper(event, 'begin-line', extend=False)

    @cmd('beginning-of-line-extend-selection')
    def beginningOfLineExtendSelection(self, event):
        """
        Extend the selection by moving the cursor to the first character of the
        line.
        """
        self.moveWithinLineHelper(event, 'begin-line', extend=True)
    #@+node:ekr.20150514063305.292: *4* ec.between lines & helper
    @cmd('next-line')
    def nextLine(self, event):
        """Move the cursor down, extending the selection if in extend mode."""
        self.moveUpOrDownHelper(event, 'down', extend=False)

    @cmd('next-line-extend-selection')
    def nextLineExtendSelection(self, event):
        """Extend the selection by moving the cursor down."""
        self.moveUpOrDownHelper(event, 'down', extend=True)

    @cmd('previous-line')
    def prevLine(self, event):
        """Move the cursor up, extending the selection if in extend mode."""
        self.moveUpOrDownHelper(event, 'up', extend=False)

    @cmd('previous-line-extend-selection')
    def prevLineExtendSelection(self, event):
        """Extend the selection by moving the cursor up."""
        self.moveUpOrDownHelper(event, 'up', extend=True)
    #@+node:ekr.20150514063305.293: *5* ec.moveUpOrDownHelper
    def moveUpOrDownHelper(self, event, direction, extend):

        w = self.editWidget(event)
        if not w:
            return
        ins = w.getInsertPoint()
        s = w.getAllText()
        w.seeInsertPoint()
        if hasattr(w, 'leoMoveCursorHelper'):
            extend = extend or self.extendMode
            w.leoMoveCursorHelper(kind=direction, extend=extend)
        else:
            # Find the start of the next/prev line.
            row, col = g.convertPythonIndexToRowCol(s, ins)
            i, j = g.getLine(s, ins)
            if direction == 'down':
                i2, j2 = g.getLine(s, j)
            else:
                i2, j2 = g.getLine(s, i - 1)
            # The spot is the start of the line plus the column index.
            n = max(0, j2 - i2 - 1) # The length of the new line.
            col2 = min(col, n)
            spot = i2 + col2
            self.extendHelper(w, extend, spot, upOrDown=True)
    #@+node:ekr.20150514063305.294: *4* ec.buffers & helper
    @cmd('beginning-of-buffer')
    def beginningOfBuffer(self, event):
        """Move the cursor to the start of the body text."""
        self.moveToBufferHelper(event, 'home', extend=False)

    @cmd('beginning-of-buffer-extend-selection')
    def beginningOfBufferExtendSelection(self, event):
        """Extend the text selection by moving the cursor to the start of the body text."""
        self.moveToBufferHelper(event, 'home', extend=True)

    @cmd('end-of-buffer')
    def endOfBuffer(self, event):
        """Move the cursor to the end of the body text."""
        self.moveToBufferHelper(event, 'end', extend=False)

    @cmd('end-of-buffer-extend-selection')
    def endOfBufferExtendSelection(self, event):
        """Extend the text selection by moving the cursor to the end of the body text."""
        self.moveToBufferHelper(event, 'end', extend=True)
    #@+node:ekr.20150514063305.295: *5* ec.moveToBufferHelper
    def moveToBufferHelper(self, event, spot, extend):
        w = self.editWidget(event)
        if not w:
            return
        if hasattr(w, 'leoMoveCursorHelper'):
            extend = extend or self.extendMode
            w.leoMoveCursorHelper(kind=spot, extend=extend)
        else:
            if spot == 'home':
                self.moveToHelper(event, 0, extend=extend)
            elif spot == 'end':
                s = w.getAllText()
                self.moveToHelper(event, len(s), extend=extend)
            else:
                g.trace('can not happen: bad spot', spot)
    #@+node:ekr.20150514063305.296: *4* ec.characters & helper
    @cmd('back-char')
    def backCharacter(self, event):
        """Move the cursor back one character, extending the selection if in extend mode."""
        self.moveToCharacterHelper(event, 'left', extend=False)

    @cmd('back-char-extend-selection')
    def backCharacterExtendSelection(self, event):
        """Extend the selection by moving the cursor back one character."""
        self.moveToCharacterHelper(event, 'left', extend=True)

    @cmd('forward-char')
    def forwardCharacter(self, event):
        """Move the cursor forward one character, extending the selection if in extend mode."""
        self.moveToCharacterHelper(event, 'right', extend=False)

    @cmd('forward-char-extend-selection')
    def forwardCharacterExtendSelection(self, event):
        """Extend the selection by moving the cursor forward one character."""
        self.moveToCharacterHelper(event, 'right', extend=True)
    #@+node:ekr.20150514063305.297: *5* ec.moveToCharacterHelper
    def moveToCharacterHelper(self, event, spot, extend):
        w = self.editWidget(event)
        if not w:
            return
        if hasattr(w, 'leoMoveCursorHelper'):
            extend = extend or self.extendMode
            w.leoMoveCursorHelper(kind=spot, extend=extend)
        else:
            i = w.getInsertPoint()
            if spot == 'left':
                i = max(0, i - 1)
                self.moveToHelper(event, i, extend=extend)
            elif spot == 'right':
                i = min(i + 1, len(w.getAllText()))
                self.moveToHelper(event, i, extend=extend)
            else:
                g.trace('can not happen: bad spot: %s' % spot)
    #@+node:ekr.20150514063305.298: *4* ec.clear/set/ToggleExtendMode
    @cmd('clear-extend-mode')
    def clearExtendMode(self, event):
        """Turn off extend mode: cursor movement commands do not extend the selection."""
        self.extendModeHelper(event, False)

    @cmd('set-extend-mode')
    def setExtendMode(self, event):
        """Turn on extend mode: cursor movement commands do extend the selection."""
        self.extendModeHelper(event, True)

    @cmd('toggle-extend-mode')
    def toggleExtendMode(self, event):
        """Toggle extend mode, i.e., toggle whether cursor movement commands extend the selections."""
        self.extendModeHelper(event, not self.extendMode)

    def extendModeHelper(self, event, val):
        c = self.c
        w = self.editWidget(event)
        if w:
            self.extendMode = val
            if not g.unitTesting:
                # g.red('extend mode','on' if val else 'off'))
                c.k.showStateAndMode()
            c.widgetWantsFocusNow(w)
    #@+node:ekr.20170707072524.1: *4* ec.endOfLine/ExtendSelection
    @cmd('end-of-line')
    def endOfLine(self, event):
        """Move the cursor to the last character of the line."""
        self.moveWithinLineHelper(event, 'end-line', extend=False)

    @cmd('end-of-line-extend-selection')
    def endOfLineExtendSelection(self, event):
        """Extend the selection by moving the cursor to the last character of the line."""
        self.moveWithinLineHelper(event, 'end-line', extend=True)
    #@+node:ekr.20150514063305.299: *4* ec.exchangePointMark
    @cmd('exchange-point-mark')
    def exchangePointMark(self, event):
        """
        Exchange the point (insert point) with the mark (the other end of the
        selected text).
        """
        c = self.c
        w = self.editWidget(event)
        if not w:
            return
        if hasattr(w, 'leoMoveCursorHelper'):
            w.leoMoveCursorHelper(kind='exchange', extend=False)
        else:
            c.widgetWantsFocusNow(w)
            i, j = w.getSelectionRange(sort=False)
            if i == j: return
            ins = w.getInsertPoint()
            ins = j if ins == i else i
            w.setInsertPoint(ins)
            w.setSelectionRange(i, j, insert=None)
    #@+node:ekr.20150514063305.300: *4* ec.extend-to-line
    @cmd('extend-to-line')
    def extendToLine(self, event):
        """Select the line at the cursor."""
        w = self.editWidget(event)
        if not w:
            return
        s = w.getAllText()
        n = len(s)
        i = w.getInsertPoint()
        while 0 <= i < n and not s[i] == '\n':
            i -= 1
        i += 1
        i1 = i
        while 0 <= i < n and not s[i] == '\n':
            i += 1
        w.setSelectionRange(i1, i)
    #@+node:ekr.20150514063305.301: *4* ec.extend-to-sentence
    @cmd('extend-to-sentence')
    def extendToSentence(self, event):
        """Select the line at the cursor."""
        w = self.editWidget(event)
        if not w:
            return
        s = w.getAllText()
        n = len(s)
        i = w.getInsertPoint()
        i2 = 1 + s.find('.', i)
        if i2 == -1: i2 = n
        i1 = 1 + s.rfind('.', 0, i2 - 1)
        w.setSelectionRange(i1, i2)
    #@+node:ekr.20150514063305.302: *4* ec.extend-to-word
    @cmd('extend-to-word')
    def extendToWord(self, event, select=True, w=None):
        """Compute the word at the cursor. Select it if select arg is True."""
        if not w:
            w = self.editWidget(event)
        if not w:
            return 0, 0
        s = w.getAllText()
        n = len(s)
        i = i1 = w.getInsertPoint()
        # Find a word char on the present line if one isn't at the cursor.
        if not (0 <= i < n and g.isWordChar(s[i])):
            # First, look forward
            while i < n and not g.isWordChar(s[i]) and s[i] != '\n':
                i += 1
            # Next, look backward.
            if not (0 <= i < n and g.isWordChar(s[i])):
                i = i1 - 1 if (i >= n or s[i] == '\n') else i1
                while i >= 0 and not g.isWordChar(s[i]) and s[i] != '\n':
                    i -= 1
        # Make sure s[i] is a word char.
        if 0 <= i < n and g.isWordChar(s[i]):
            # Find the start of the word.
            while 0 <= i < n and g.isWordChar(s[i]):
                i -= 1
            i += 1
            i1 = i
            # Find the end of the word.
            while 0 <= i < n and g.isWordChar(s[i]):
                i += 1
            if select:
                w.setSelectionRange(i1, i)
            return i1, i
        return 0, 0
    #@+node:ekr.20170707072837.1: *4* ec.finishOfLine/ExtendSelection
    @cmd('finish-of-line')
    def finishOfLine(self, event):
        """Move the cursor to the last character of the line."""
        self.moveWithinLineHelper(event, 'finish-line', extend=False)

    @cmd('finish-of-line-extend-selection')
    def finishOfLineExtendSelection(self, event):
        """Extend the selection by moving the cursor to the last character of the line."""
        self.moveWithinLineHelper(event, 'finish-line', extend=True)
    #@+node:ekr.20170707160947.1: *4* ec.forward*/ExtendSelection
    @cmd('forward-end-word')
    def forwardEndWord(self, event): # New in Leo 4.4.2
        """Move the cursor to the next word."""
        self.moveWordHelper(event, extend=False, forward=True, end=True)

    @cmd('forward-end-word-extend-selection')
    def forwardEndWordExtendSelection(self, event): # New in Leo 4.4.2
        """Extend the selection by moving the cursor to the next word."""
        self.moveWordHelper(event, extend=True, forward=True, end=True)

    @cmd('forward-word')
    def forwardWord(self, event):
        """Move the cursor to the next word."""
        self.moveWordHelper(event, extend=False, forward=True)

    @cmd('forward-word-extend-selection')
    def forwardWordExtendSelection(self, event):
        """Extend the selection by moving the cursor to the end of the next word."""
        self.moveWordHelper(event, extend=True, forward=True)

    @cmd('forward-word-smart')
    def forwardWordSmart(self, event):
        """Move the cursor to the end of the current or the beginning of the next word."""
        self.moveWordHelper(event, extend=False, forward=True, smart=True)

    @cmd('forward-word-smart-extend-selection')
    def forwardWordSmartExtendSelection(self, event):
        """Extend the selection by moving the cursor to the end of the current
        or the beginning of the next word."""
        self.moveWordHelper(event, extend=True, forward=True, smart=True)
    #@+node:ekr.20150514063305.303: *4* ec.movePastClose & helper
    @cmd('move-past-close')
    def movePastClose(self, event):
        """Move the cursor past the closing parenthesis."""
        self.movePastCloseHelper(event, extend=False)

    @cmd('move-past-close-extend-selection')
    def movePastCloseExtendSelection(self, event):
        """Extend the selection by moving the cursor past the closing parenthesis."""
        self.movePastCloseHelper(event, extend=True)
    #@+node:ekr.20150514063305.304: *5* ec.movePastCloseHelper
    def movePastCloseHelper(self, event, extend):
        c = self.c
        w = self.editWidget(event)
        if not w:
            return
        c.widgetWantsFocusNow(w)
        s = w.getAllText()
        ins = w.getInsertPoint()
        # Scan backwards for i,j.
        i = ins
        while i >= 0 and s[i] != '\n':
            if s[i] == '(': break
            i -= 1
        else: return
        j = ins
        while j >= 0 and s[j] != '\n':
            if s[j] == '(': break
            j -= 1
        if i < j: return
        # Scan forward for i2,j2.
        i2 = ins
        while i2 < len(s) and s[i2] != '\n':
            if s[i2] == ')': break
            i2 += 1
        else: return
        j2 = ins
        while j2 < len(s) and s[j2] != '\n':
            if s[j2] == ')': break
            j2 += 1
        if i2 > j2: return
        self.moveToHelper(event, i2 + 1, extend)
    #@+node:ekr.20150514063305.306: *4* ec.pages & helper
    @cmd('back-page')
    def backPage(self, event):
        """Move the cursor back one page,
        extending the selection if in extend mode."""
        self.movePageHelper(event, kind='back', extend=False)

    @cmd('back-page-extend-selection')
    def backPageExtendSelection(self, event):
        """Extend the selection by moving the cursor back one page."""
        self.movePageHelper(event, kind='back', extend=True)

    @cmd('forward-page')
    def forwardPage(self, event):
        """Move the cursor forward one page,
        extending the selection if in extend mode."""
        self.movePageHelper(event, kind='forward', extend=False)

    @cmd('forward-page-extend-selection')
    def forwardPageExtendSelection(self, event):
        """Extend the selection by moving the cursor forward one page."""
        self.movePageHelper(event, kind='forward', extend=True)
    #@+node:ekr.20150514063305.307: *5* ec.movePageHelper
    def movePageHelper(self, event, kind, extend): # kind in back/forward.
        """Move the cursor up/down one page, possibly extending the selection."""
        w = self.editWidget(event)
        if not w:
            return
        linesPerPage = 15 # To do.
        if hasattr(w, 'leoMoveCursorHelper'):
            extend = extend or self.extendMode
            w.leoMoveCursorHelper(
                kind='page-down' if kind == 'forward' else 'page-up',
                extend=extend, linesPerPage=linesPerPage)
            # w.seeInsertPoint()
            # c.frame.updateStatusLine()
            # w.rememberSelectionAndScroll()
        else:
            ins = w.getInsertPoint()
            s = w.getAllText()
            lines = g.splitLines(s)
            row, col = g.convertPythonIndexToRowCol(s, ins)
            row2 = max(0, row - linesPerPage) if kind == 'back' else min(row + linesPerPage, len(lines) - 1)
            if row == row2: return
            spot = g.convertRowColToPythonIndex(s, row2, col, lines=lines)
            self.extendHelper(w, extend, spot, upOrDown=True)
    #@+node:ekr.20150514063305.308: *4* ec.paragraphs & helpers
    @cmd('back-paragraph')
    def backwardParagraph(self, event):
        """Move the cursor to the previous paragraph."""
        self.backwardParagraphHelper(event, extend=False)

    @cmd('back-paragraph-extend-selection')
    def backwardParagraphExtendSelection(self, event):
        """Extend the selection by moving the cursor to the previous paragraph."""
        self.backwardParagraphHelper(event, extend=True)

    @cmd('forward-paragraph')
    def forwardParagraph(self, event):
        """Move the cursor to the next paragraph."""
        self.forwardParagraphHelper(event, extend=False)

    @cmd('forward-paragraph-extend-selection')
    def forwardParagraphExtendSelection(self, event):
        """Extend the selection by moving the cursor to the next paragraph."""
        self.forwardParagraphHelper(event, extend=True)
    #@+node:ekr.20150514063305.309: *5* ec.backwardParagraphHelper
    def backwardParagraphHelper(self, event, extend):
        w = self.editWidget(event)
        if not w:
            return
        s = w.getAllText()
        i, j = w.getSelectionRange()
        # A hack for wx gui: set the insertion point to the end of the selection range.
        if g.app.unitTesting:
            w.setInsertPoint(j)
        i, j = g.getLine(s, j)
        line = s[i: j]
        if line.strip():
            # Find the start of the present paragraph.
            while i > 0:
                i, j = g.getLine(s, i - 1)
                line = s[i: j]
                if not line.strip(): break
        # Find the end of the previous paragraph.
        while i > 0:
            i, j = g.getLine(s, i - 1)
            line = s[i: j]
            if line.strip():
                i = j - 1
                break
        self.moveToHelper(event, i, extend)
    #@+node:ekr.20150514063305.310: *5* ec.forwardParagraphHelper
    def forwardParagraphHelper(self, event, extend):
        w = self.editWidget(event)
        if not w: return
        s = w.getAllText()
        ins = w.getInsertPoint()
        i, j = g.getLine(s, ins)
        line = s[i: j]
        if line.strip(): # Skip past the present paragraph.
            self.selectParagraphHelper(w, i)
            i, j = w.getSelectionRange()
            j += 1
        # Skip to the next non-blank line.
        i = j
        while j < len(s):
            i, j = g.getLine(s, j)
            line = s[i: j]
            if line.strip(): break
        w.setInsertPoint(ins) # Restore the original insert point.
        self.moveToHelper(event, i, extend)
    #@+node:ekr.20170707093335.1: *4* ec.pushCursor and popCursor
    @cmd('pop-cursor')
    def popCursor(self, event=None):
        """Restore the node, selection range and insert point from the stack."""
        c = self.c
        w = self.editWidget(event)
        if w and self.cursorStack:
            p, i, j, ins = self.cursorStack.pop()
            if c.positionExists(p):
                c.selectPosition(p)
                c.redraw()
                w.setSelectionRange(i, j, insert=ins)
                c.bodyWantsFocus()
            else:
                g.es('invalid position', c.p.h)
        elif not w:
            g.es('no stacked cursor', color='blue')

    @cmd('push-cursor')
    def pushCursor(self, event=None):
        """Push the selection range and insert point on the stack."""
        c = self.c
        w = self.editWidget(event)
        if w:
            p = c.p.copy()
            i, j = w.getSelectionRange()
            ins = w.getInsertPoint()
            self.cursorStack.append((p, i, j, ins),)
        else:
            g.es('cursor not pushed', color='blue')
    #@+node:ekr.20150514063305.311: *4* ec.selectAllText
    @cmd('select-all')
    def selectAllText(self, event):
        """Select all text."""
        k = self.c.k
        w = self.editWidget(event)
        if not w: return
        # Bug fix 2013/12/13: Special case the minibuffer.
        if w == k.w:
            k.selectAll()
        elif w and g.isTextWrapper(w):
            w.selectAllText()
    #@+node:ekr.20150514063305.312: *4* ec.sentences & helpers
    @cmd('back-sentence')
    def backSentence(self, event):
        """Move the cursor to the previous sentence."""
        self.backSentenceHelper(event, extend=False)

    @cmd('back-sentence-extend-selection')
    def backSentenceExtendSelection(self, event):
        """Extend the selection by moving the cursor to the previous sentence."""
        self.backSentenceHelper(event, extend=True)

    @cmd('forward-sentence')
    def forwardSentence(self, event):
        """Move the cursor to the next sentence."""
        self.forwardSentenceHelper(event, extend=False)

    @cmd('forward-sentence-extend-selection')
    def forwardSentenceExtendSelection(self, event):
        """Extend the selection by moving the cursor to the next sentence."""
        self.forwardSentenceHelper(event, extend=True)
    #@+node:ekr.20150514063305.313: *5* ec.backSentenceHelper
    def backSentenceHelper(self, event, extend):
        c = self.c
        w = self.editWidget(event)
        if not w:
            return
        c.widgetWantsFocusNow(w)
        s = w.getAllText()
        ins = w.getInsertPoint()
        # Find the starting point of the scan.
        i = ins
        i -= 1 # Ensure some progress.
        if i < 0:
            return
        # Tricky.
        if s[i] == '.':
            i -= 1
        while i >= 0 and s[i] in ' \n':
            i -= 1
        if i >= ins:
            i -= 1
        if i >= len(s):
            i -= 1
        if i <= 0:
            return
        if s[i] == '.':
            i -= 1
        # Scan backwards to the end of the paragraph.
        # Stop at empty lines.
        # Skip periods within words.
        # Stop at sentences ending in non-periods.
        end = False
        while not end and i >= 0:
            progress = i
            if s[i] == '.':
                # Skip periods surrounded by letters/numbers
                if i > 0 and s[i - 1].isalnum() and s[i + 1].isalnum():
                    i -= 1
                else:
                    i += 1
                    while i < len(s) and s[i] in ' \n':
                        i += 1
                    i -= 1
                    break
            elif s[i] == '\n':
                j = i - 1
                while j >= 0:
                    if s[j] == '\n':
                        # Don't include first newline.
                        end = True
                        break # found blank line.
                    elif s[j] == ' ':
                        j -= 1
                    else:
                        i -= 1
                        break # no blank line found.
                else:
                    # No blank line found.
                    i -= 1
            else:
                i -= 1
            assert end or progress > i
        i += 1
        if i < ins:
            self.moveToHelper(event, i, extend)
    #@+node:ekr.20150514063305.314: *5* ec.forwardSentenceHelper
    def forwardSentenceHelper(self, event, extend):
        c = self.c
        w = self.editWidget(event)
        if not w:
            return
        c.widgetWantsFocusNow(w)
        s = w.getAllText()
        ins = w.getInsertPoint()
        if ins >= len(s):
            return
        # Find the starting point of the scan.
        i = ins
        if i + 1 < len(s) and s[i + 1] == '.':
            i += 1
        if s[i] == '.':
            i += 1
        else:
            while i < len(s) and s[i] in ' \n':
                i += 1
            i -= 1
        if i <= ins:
            i += 1
        if i >= len(s):
            return
        # Scan forward to the end of the paragraph.
        # Stop at empty lines.
        # Skip periods within words.
        # Stop at sentences ending in non-periods.
        end = False
        while not end and i < len(s):
            progress = i
            if s[i] == '.':
                # Skip periods surrounded by letters/numbers
                if 0 < i < len(s) and s[i - 1].isalnum() and s[i + 1].isalnum():
                    i += 1
                else:
                    i += 1
                    break # Include the paragraph.
            elif s[i] == '\n':
                j = i + 1
                while j < len(s):
                    if s[j] == '\n':
                        # Don't include first newline.
                        end = True
                        break # found blank line.
                    elif s[j] == ' ':
                        j += 1
                    else:
                        i += 1
                        break # no blank line found.
                else:
                    # No blank line found.
                    i += 1
            else:
                i += 1
            assert end or progress < i
        i = min(i, len(s))
        if i > ins:
            self.moveToHelper(event, i, extend)
    #@+node:ekr.20170707072644.1: *4* ec.startOfLine/ExtendSelection
    @cmd('start-of-line')
    def startOfLine(self, event):
        """Move the cursor to first non-blank character of the line."""
        self.moveWithinLineHelper(event, 'start-line', extend=False)

    @cmd('start-of-line-extend-selection')
    def startOfLineExtendSelection(self, event):
        """
        Extend the selection by moving the cursor to first non-blank character
        of the line.
        """
        self.moveWithinLineHelper(event, 'start-line', extend=True)
    #@+node:ekr.20150514063305.319: *3* ec: paragraph
    #@+node:ekr.20150514063305.320: *4* ec.backwardKillParagraph
    @cmd('backward-kill-paragraph')
    def backwardKillParagraph(self, event):
        """Kill the previous paragraph."""
        c = self.c
        w = self.editWidget(event)
        if not w:
            return
        self.beginCommand(w, undoType='backward-kill-paragraph')
        try:
            self.backwardParagraphHelper(event, extend=True)
            i, j = w.getSelectionRange()
            if i > 0: i = min(i + 1, j)
            c.killBufferCommands.kill(event, i, j,
                                      force=True, # Use i, j without change.
                                      undoType=None)
            w.setSelectionRange(i, i, insert=i)
        finally:
            self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.321: *4* ec.fillRegion
    @cmd('fill-region')
    def fillRegion(self, event):
        """Fill all paragraphs in the selected text."""
        c, p = self.c, self.c.p
        undoType = 'fill-region'
        w = self.editWidget(event)
        i, j = w.getSelectionRange()
        c.undoer.beforeChangeGroup(p, undoType)
        while 1:
            progress = w.getInsertPoint()
            c.reformatParagraph(event, undoType='reformat-paragraph')
            ins = w.getInsertPoint()
            s = w.getAllText()
            w.setInsertPoint(ins)
            if progress >= ins or ins >= j or ins >= len(s):
                break
        c.undoer.afterChangeGroup(p, undoType)
    #@+node:ekr.20150514063305.322: *4* ec.fillRegionAsParagraph
    @cmd('fill-region-as-paragraph')
    def fillRegionAsParagraph(self, event):
        """Fill the selected text."""
        w = self.editWidget(event)
        if not w or not self._chckSel(event):
            return
        self.beginCommand(w, undoType='fill-region-as-paragraph')
        self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.323: *4* ec.fillParagraph
    @cmd('fill-paragraph')
    def fillParagraph(self, event):
        """Fill the selected paragraph"""
        w = self.editWidget(event)
        if w:
            # Clear the selection range.
            i, j = w.getSelectionRange()
            w.setSelectionRange(i, i, insert=i)
            self.c.reformatParagraph(event)
    #@+node:ekr.20150514063305.324: *4* ec.killParagraph
    @cmd('kill-paragraph')
    def killParagraph(self, event):
        """Kill the present paragraph."""
        c = self.c
        w = self.editWidget(event)
        if not w:
            return
        self.beginCommand(w, undoType='kill-paragraph')
        try:
            self.extendToParagraph(event)
            i, j = w.getSelectionRange()
            c.killBufferCommands.kill(event, i, j,
                                      force=True, # Use i, j without change.
                                      undoType=None)
            w.setSelectionRange(i, i, insert=i)
        finally:
            self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.325: *4* ec.extend-to-paragraph & helper
    @cmd('extend-to-paragraph')
    def extendToParagraph(self, event):
        """Select the paragraph surrounding the cursor."""
        w = self.editWidget(event)
        if not w: return
        s = w.getAllText()
        ins = w.getInsertPoint()
        i, j = g.getLine(s, ins)
        line = s[i: j]
        # Find the start of the paragraph.
        if line.strip(): # Search backward.
            while i > 0:
                i2, j2 = g.getLine(s, i - 1)
                line = s[i2: j2]
                if line.strip(): i = i2
                else: break # Use the previous line.
        else: # Search forward.
            while j < len(s):
                i, j = g.getLine(s, j)
                line = s[i: j]
                if line.strip(): break
            else: return
        # Select from i to the end of the paragraph.
        self.selectParagraphHelper(w, i)
    #@+node:ekr.20150514063305.326: *5* ec.selectParagraphHelper
    def selectParagraphHelper(self, w, start):
        """Select from start to the end of the paragraph."""
        s = w.getAllText()
        i1, j = g.getLine(s, start)
        while j < len(s):
            i, j2 = g.getLine(s, j)
            line = s[i: j2]
            if line.strip(): j = j2
            else: break
        j = max(start, j - 1)
        w.setSelectionRange(i1, j, insert=j)
    #@+node:ekr.20150514063305.327: *3* ec: region
    #@+node:ekr.20150514063305.328: *4* ec.tabIndentRegion (indent-rigidly)
    @cmd('indent-rigidly')
    def tabIndentRegion(self, event):
        """Insert a hard tab at the start of each line of the selected text."""
        w = self.editWidget(event)
        if not w or not self._chckSel(event):
            return
        self.beginCommand(w, undoType='indent-rigidly')
        s = w.getAllText()
        i1, j1 = w.getSelectionRange()
        i, junk = g.getLine(s, i1)
        junk, j = g.getLine(s, j1)
        lines = g.splitlines(s[i: j])
        n = len(lines)
        lines = g.joinLines(['\t' + line for line in lines])
        s = s[: i] + lines + s[j:]
        w.setAllText(s)
        # Retain original row/col selection.
        w.setSelectionRange(i1, j1 + n, insert=j1 + n)
        self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.329: *4* ec.countRegion
    @cmd('count-region')
    def countRegion(self, event):
        """Print the number of lines and characters in the selected text."""
        k = self.c.k
        w = self.editWidget(event)
        if not w:
            return
        txt = w.getSelectedText()
        lines = 1
        chars = 0
        for z in txt:
            if z == '\n': lines += 1
            else: chars += 1
        k.setLabelGrey('Region has %s lines, %s character%s' % (
            lines, chars, '' if chars == 1 else 's'))
    #@+node:ekr.20150514063305.330: *4* ec.moveLinesDown
    @cmd('move-lines-down')
    def moveLinesDown(self, event):
        """
        Move all lines containing any selected text down one line,
        moving to the next node if the lines are the last lines of the body.
        """
        c = self.c
        w = self.editWidget(event)
        if not w:
            return
        s = w.getAllText()
        sel_1, sel_2 = w.getSelectionRange()
        insert_pt = w.getInsertPoint()
        i, junk = g.getLine(s, sel_1)
        i2, j = g.getLine(s, sel_2)
        lines = s[i: j]
        # Select from start of the first line to the *start* of the last line.
        # This prevents selection creep.
        self.beginCommand(w, undoType='move-lines-down')
        try:
            next_i, next_j = g.getLine(s, j) # 2011/04/01: was j+1
            next_line = s[next_i: next_j]
            n2 = next_j - next_i
            if j < len(s):
                w.delete(i, next_j)
                if next_line.endswith('\n'):
                    # Simply swap positions with next line
                    new_lines = next_line + lines
                else:
                    # Last line of the body to be moved up doesn't end in a newline
                    # while we have to remove the newline from the line above moving down.
                    new_lines = next_line + '\n' + lines[: -1]
                    n2 += 1
                w.insert(i, new_lines)
                w.setSelectionRange(sel_1 + n2, sel_2 + n2, insert=insert_pt + n2)
            else:
                # Leo 5.6: insert a blank line before the selected lines.
                w.insert(i, '\n')
                w.setSelectionRange(sel_1 + 1, sel_2 + 1, insert=insert_pt + 1)
            # Fix bug 799695: colorizer bug after move-lines-up into a docstring
            c.recolor()
        finally:
            self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.331: *4* ec.moveLinesUp
    @cmd('move-lines-up')
    def moveLinesUp(self, event):
        """
        Move all lines containing any selected text up one line,
        moving to the previous node as needed.
        """
        c = self.c
        w = self.editWidget(event)
        if not w:
            return
        s = w.getAllText()
        sel_1, sel_2 = w.getSelectionRange()
        insert_pt = w.getInsertPoint() # 2011/04/01
        i, junk = g.getLine(s, sel_1)
        i2, j = g.getLine(s, sel_2)
        lines = s[i: j]
        self.beginCommand(w, undoType='move-lines-up')
        try:
            prev_i, prev_j = g.getLine(s, i - 1)
            prev_line = s[prev_i: prev_j]
            n2 = prev_j - prev_i
            if i > 0:
                w.delete(prev_i, j)
                if lines.endswith('\n'):
                    # Simply swap positions with next line
                    new_lines = lines + prev_line
                else:
                    # Lines to be moved up don't end in a newline while the
                    # previous line going down needs its newline taken off.
                    new_lines = lines + '\n' + prev_line[: -1]
                w.insert(prev_i, new_lines)
                w.setSelectionRange(sel_1 - n2, sel_2 - n2, insert=insert_pt - n2)
            else:
                # Leo 5.6: Insert a blank line after the line.
                w.insert(j, '\n')
                w.setSelectionRange(sel_1, sel_2, insert=sel_1)
            # Fix bug 799695: colorizer bug after move-lines-up into a docstring
            c.recolor()
        finally:
            self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.332: *4* ec.reverseRegion
    @cmd('reverse-region')
    def reverseRegion(self, event):
        """Reverse the order of lines in the selected text."""
        w = self.editWidget(event)
        if not w or not self._chckSel(event):
            return
        self.beginCommand(w, undoType='reverse-region')
        s = w.getAllText()
        i1, j1 = w.getSelectionRange()
        i, junk = g.getLine(s, i1)
        junk, j = g.getLine(s, j1)
        txt = s[i: j]
        aList = txt.split('\n')
        aList.reverse()
        txt = '\n'.join(aList) + '\n'
        w.setAllText(s[: i1] + txt + s[j1:])
        ins = i1 + len(txt) - 1
        w.setSelectionRange(ins, ins, insert=ins)
        self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.333: *4* ec.up/downCaseRegion & helper
    @cmd('downcase-region')
    def downCaseRegion(self, event):
        """Convert all characters in the selected text to lower case."""
        self.caseHelper(event, 'low', 'downcase-region')

    @cmd('toggle-case-region')
    def toggleCaseRegion(self, event):
        """Toggle the case of all characters in the selected text."""
        self.caseHelper(event, 'toggle', 'toggle-case-region')

    @cmd('upcase-region')
    def upCaseRegion(self, event):
        """Convert all characters in the selected text to UPPER CASE."""
        self.caseHelper(event, 'up', 'upcase-region')

    def caseHelper(self, event, way, undoType):
        w = self.editWidget(event)
        if not w or not w.hasSelection():
            return
        self.beginCommand(w, undoType=undoType)
        s = w.getAllText()
        i, j = w.getSelectionRange()
        ins = w.getInsertPoint()
        s2 = s[i: j]
        if way == 'low':
            sel = s2.lower()
        elif way == 'up':
            sel = s2.upper()
        else:
            assert way == 'toggle'
            sel = s2.swapcase()
        s2 = s[: i] + sel + s[j:]
        changed = s2 != s
        if changed:
            w.setAllText(s2)
            w.setSelectionRange(i, j, insert=ins)
        self.endCommand(changed=changed, setLabel=True)
    #@+node:ekr.20150514063305.334: *3* ec: scrolling
    #@+node:ekr.20150514063305.335: *4* ec.scrollUp/Down & helper
    @cmd('scroll-down-half-page')
    def scrollDownHalfPage(self, event):
        """Scroll the presently selected pane down one line."""
        self.scrollHelper(event, 'down', 'half-page')

    @cmd('scroll-down-line')
    def scrollDownLine(self, event):
        """Scroll the presently selected pane down one line."""
        self.scrollHelper(event, 'down', 'line')

    @cmd('scroll-down-page')
    def scrollDownPage(self, event):
        """Scroll the presently selected pane down one page."""
        self.scrollHelper(event, 'down', 'page')

    @cmd('scroll-up-half-page')
    def scrollUpHalfPage(self, event):
        """Scroll the presently selected pane down one line."""
        self.scrollHelper(event, 'up', 'half-page')

    @cmd('scroll-up-line')
    def scrollUpLine(self, event):
        """Scroll the presently selected pane up one page."""
        self.scrollHelper(event, 'up', 'line')

    @cmd('scroll-up-page')
    def scrollUpPage(self, event):
        """Scroll the presently selected pane up one page."""
        self.scrollHelper(event, 'up', 'page')
    #@+node:ekr.20150514063305.336: *5* ec.scrollHelper
    def scrollHelper(self, event, direction, distance):
        """
        Scroll the present pane up or down one page
        kind is in ('up/down-half-page/line/page)
        """
        w = event and event.w
        if w and hasattr(w, 'scrollDelegate'):
            kind = direction + '-' + distance
            w.scrollDelegate(kind)
    #@+node:ekr.20150514063305.337: *4* ec.scrollOutlineUp/Down/Line/Page
    @cmd('scroll-outline-down-line')
    def scrollOutlineDownLine(self, event=None):
        """Scroll the outline pane down one line."""
        tree = self.c.frame.tree
        if hasattr(tree, 'scrollDelegate'):
            tree.scrollDelegate('down-line')
        elif hasattr(tree.canvas, 'leo_treeBar'):
            a, b = tree.canvas.leo_treeBar.get()
            if b < 1.0: tree.canvas.yview_scroll(1, "unit")

    @cmd('scroll-outline-down-page')
    def scrollOutlineDownPage(self, event=None):
        """Scroll the outline pane down one page."""
        tree = self.c.frame.tree
        if hasattr(tree, 'scrollDelegate'):
            tree.scrollDelegate('down-page')
        elif hasattr(tree.canvas, 'leo_treeBar'):
            a, b = tree.canvas.leo_treeBar.get()
            if b < 1.0: tree.canvas.yview_scroll(1, "page")

    @cmd('scroll-outline-up-line')
    def scrollOutlineUpLine(self, event=None):
        """Scroll the outline pane up one line."""
        tree = self.c.frame.tree
        if hasattr(tree, 'scrollDelegate'):
            tree.scrollDelegate('up-line')
        elif hasattr(tree.canvas, 'leo_treeBar'):
            a, b = tree.canvas.leo_treeBar.get()
            if a > 0.0: tree.canvas.yview_scroll(-1, "unit")

    @cmd('scroll-outline-up-page')
    def scrollOutlineUpPage(self, event=None):
        """Scroll the outline pane up one page."""
        tree = self.c.frame.tree
        if hasattr(tree, 'scrollDelegate'):
            tree.scrollDelegate('up-page')
        elif hasattr(tree.canvas, 'leo_treeBar'):
            a, b = tree.canvas.leo_treeBar.get()
            if a > 0.0: tree.canvas.yview_scroll(-1, "page")
    #@+node:ekr.20150514063305.338: *4* ec.scrollOutlineLeftRight
    @cmd('scroll-outline-left')
    def scrollOutlineLeft(self, event=None):
        """Scroll the outline left."""
        tree = self.c.frame.tree
        if hasattr(tree, 'scrollDelegate'):
            tree.scrollDelegate('left')
        elif hasattr(tree.canvas, 'xview_scroll'):
            tree.canvas.xview_scroll(1, "unit")

    @cmd('scroll-outline-right')
    def scrollOutlineRight(self, event=None):
        """Scroll the outline left."""
        tree = self.c.frame.tree
        if hasattr(tree, 'scrollDelegate'):
            tree.scrollDelegate('right')
        elif hasattr(tree.canvas, 'xview_scroll'):
            tree.canvas.xview_scroll(-1, "unit")
    #@+node:ekr.20150514063305.339: *3* ec: sort
    #@+at
    # XEmacs provides several commands for sorting text in a buffer.  All
    # operate on the contents of the region (the text between point and the
    # mark).  They divide the text of the region into many "sort records",
    # identify a "sort key" for each record, and then reorder the records
    # using the order determined by the sort keys.  The records are ordered so
    # that their keys are in alphabetical order, or, for numerical sorting, in
    # numerical order.  In alphabetical sorting, all upper-case letters `A'
    # through `Z' come before lower-case `a', in accordance with the ASCII
    # character sequence.
    # 
    #    The sort commands differ in how they divide the text into sort
    # records and in which part of each record they use as the sort key.
    # Most of the commands make each line a separate sort record, but some
    # commands use paragraphs or pages as sort records.  Most of the sort
    # commands use each entire sort record as its own sort key, but some use
    # only a portion of the record as the sort key.
    # 
    # `M-x sort-lines'
    #      Divide the region into lines and sort by comparing the entire text
    #      of a line.  A prefix argument means sort in descending order.
    # 
    # `M-x sort-paragraphs'
    #      Divide the region into paragraphs and sort by comparing the entire
    #      text of a paragraph (except for leading blank lines).  A prefix
    #      argument means sort in descending order.
    # 
    # `M-x sort-pages'
    #      Divide the region into pages and sort by comparing the entire text
    #      of a page (except for leading blank lines).  A prefix argument
    #      means sort in descending order.
    # 
    # `M-x sort-fields'
    #      Divide the region into lines and sort by comparing the contents of
    #      one field in each line.  Fields are defined as separated by
    #      whitespace, so the first run of consecutive non-whitespace
    #      characters in a line constitutes field 1, the second such run
    #      constitutes field 2, etc.
    # 
    #      You specify which field to sort by with a numeric argument: 1 to
    #      sort by field 1, etc.  A negative argument means sort in descending
    #      order.  Thus, minus 2 means sort by field 2 in reverse-alphabetical
    #      order.
    # 
    # `M-x sort-numeric-fields'
    #      Like `M-x sort-fields', except the specified field is converted to
    #      a number for each line and the numbers are compared.  `10' comes
    #      before `2' when considered as text, but after it when considered
    #      as a number.
    # 
    # `M-x sort-columns'
    #      Like `M-x sort-fields', except that the text within each line used
    #      for comparison comes from a fixed range of columns.  An explanation
    #      is given below.
    # 
    #    For example, if the buffer contains:
    # 
    #      On systems where clash detection (locking of files being edited) is
    #      implemented, XEmacs also checks the first time you modify a buffer
    #      whether the file has changed on disk since it was last visited or
    #      saved.  If it has, you are asked to confirm that you want to change
    #      the buffer.
    # 
    # then if you apply `M-x sort-lines' to the entire buffer you get:
    # 
    #      On systems where clash detection (locking of files being edited) is
    #      implemented, XEmacs also checks the first time you modify a buffer
    #      saved.  If it has, you are asked to confirm that you want to change
    #      the buffer.
    #      whether the file has changed on disk since it was last visited or
    # 
    # where the upper case `O' comes before all lower case letters.  If you
    # apply instead `C-u 2 M-x sort-fields' you get:
    # 
    #      saved.  If it has, you are asked to confirm that you want to change
    #      implemented, XEmacs also checks the first time you modify a buffer
    #      the buffer.
    #      On systems where clash detection (locking of files being edited) is
    #      whether the file has changed on disk since it was last visited or
    # 
    # where the sort keys were `If', `XEmacs', `buffer', `systems', and `the'.
    # 
    #    `M-x sort-columns' requires more explanation.  You specify the
    # columns by putting point at one of the columns and the mark at the other
    # column.  Because this means you cannot put point or the mark at the
    # beginning of the first line to sort, this command uses an unusual
    # definition of `region': all of the line point is in is considered part
    # of the region, and so is all of the line the mark is in.
    # 
    #    For example, to sort a table by information found in columns 10 to
    # 15, you could put the mark on column 10 in the first line of the table,
    # and point on column 15 in the last line of the table, and then use this
    # command.  Or you could put the mark on column 15 in the first line and
    # point on column 10 in the last line.
    # 
    #    This can be thought of as sorting the rectangle specified by point
    # and the mark, except that the text on each line to the left or right of
    # the rectangle moves along with the text inside the rectangle.  *Note
    # Rectangles::.
    #@+node:ekr.20150514063305.340: *4* ec.sortLines commands
    @cmd('reverse-sort-lines-ignoring-case')
    def reverseSortLinesIgnoringCase(self, event):
        """Sort the selected lines in reverse order, ignoring case."""
        return self.sortLines(event, ignoreCase=True, reverse=True)

    @cmd('reverse-sort-lines')
    def reverseSortLines(self, event):
        """Sort the selected lines in reverse order."""
        return self.sortLines(event, reverse=True)

    @cmd('sort-lines-ignoring-case')
    def sortLinesIgnoringCase(self, event):
        """Sort the selected lines, ignoring case."""
        return self.sortLines(event, ignoreCase=True)

    @cmd('sort-lines')
    def sortLines(self, event, ignoreCase=False, reverse=False):
        """Sort the selected lines."""
        w = self.editWidget(event)
        if not self._chckSel(event):
            return
        undoType = 'reverse-sort-lines' if reverse else 'sort-lines'
        self.beginCommand(w, undoType=undoType)
        try:
            s = w.getAllText()
            sel1, sel2 = w.getSelectionRange()
            ins = w.getInsertPoint()
            i, junk = g.getLine(s, sel1)
            junk, j = g.getLine(s, sel2)
            s2 = s[i: j]
            if not s2.endswith('\n'): s2 = s2 + '\n'
            aList = g.splitLines(s2)

            def lower(s):
                return s.lower() if ignoreCase else s

            aList.sort(key=lower)
                # key is a function that extracts args.
            if reverse:
                aList.reverse()
            s = g.joinLines(aList)
            w.delete(i, j)
            w.insert(i, s)
            w.setSelectionRange(sel1, sel2, insert=ins)
        finally:
            self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.341: *4* ec.sortColumns
    @cmd('sort-columns')
    def sortColumns(self, event):
        """
        Sort lines of selected text using only lines in the given columns to do
        the comparison.
        """
        w = self.editWidget(event)
        if not self._chckSel(event):
            return
        self.beginCommand(w, undoType='sort-columns')
        try:
            s = w.getAllText()
            sel_1, sel_2 = w.getSelectionRange()
            sint1, sint2 = g.convertPythonIndexToRowCol(s, sel_1)
            sint3, sint4 = g.convertPythonIndexToRowCol(s, sel_2)
            sint1 += 1
            sint3 += 1
            i, junk = g.getLine(s, sel_1)
            junk, j = g.getLine(s, sel_2)
            txt = s[i: j]
            columns = [w.get('%s.%s' % (z, sint2), '%s.%s' % (z, sint4))
                for z in range(sint1, sint3 + 1)]
            aList = g.splitLines(txt)
            zlist = list(zip(columns, aList))
            zlist.sort()
            s = g.joinLines([z[1] for z in zlist])
            w.delete(i, j)
            w.insert(i, s)
            w.setSelectionRange(sel_1, sel_1 + len(s), insert=sel_1 + len(s))
        finally:
            self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.342: *4* ec.sortFields
    @cmd('sort-fields')
    def sortFields(self, event, which=None):
        """
        Divide the selected text into lines and sort by comparing the contents
        of one field in each line. Fields are defined as separated by
        whitespace, so the first run of consecutive non-whitespace characters
        in a line constitutes field 1, the second such run constitutes field 2,
        etc.

        You specify which field to sort by with a numeric argument: 1 to sort
        by field 1, etc. A negative argument means sort in descending order.
        Thus, minus 2 means sort by field 2 in reverse-alphabetical order.
         """
        w = self.editWidget(event)
        if not w or not self._chckSel(event):
            return
        self.beginCommand(w, undoType='sort-fields')
        s = w.getAllText()
        ins = w.getInsertPoint()
        r1, r2, r3, r4 = self.getRectanglePoints(w)
        i, junk = g.getLine(s, r1)
        junk, j = g.getLine(s, r4)
        txt = s[i: j] # bug reported by pychecker.
        txt = txt.split('\n')
        fields = []
        fn = r'\w+'
        frx = re.compile(fn)
        for line in txt:
            f = frx.findall(line)
            if not which:
                fields.append(f[0])
            else:
                i = int(which)
                if len(f) < i: return
                i = i - 1
                fields.append(f[i])
        nz = sorted(zip(fields, txt))
        w.delete(i, j)
        int1 = i
        for z in nz:
            w.insert('%s.0' % int1, '%s\n' % z[1])
            int1 = int1 + 1
        w.setInsertPoint(ins)
        self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.343: *3* ec: swap/transpose
    #@+node:ekr.20150514063305.344: *4* ec.transposeLines
    @cmd('transpose-lines')
    def transposeLines(self, event):
        """Transpose the line containing the cursor with the preceding line."""
        w = self.editWidget(event)
        if not w:
            return
        ins = w.getInsertPoint()
        s = w.getAllText()
        if not s.strip():
            return
        i, j = g.getLine(s, ins)
        line1 = s[i: j]
        self.beginCommand(w, undoType='transpose-lines')
        if i == 0: # Transpose the next line.
            i2, j2 = g.getLine(s, j + 1)
            line2 = s[i2: j2]
            w.delete(0, j2)
            w.insert(0, line2 + line1)
            w.setInsertPoint(j2 - 1)
        else: # Transpose the previous line.
            i2, j2 = g.getLine(s, i - 1)
            line2 = s[i2: j2]
            w.delete(i2, j)
            w.insert(i2, line1 + line2)
            w.setInsertPoint(j - 1)
        self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.345: *4* ec.transposeWords
    @cmd('transpose-words')
    def transposeWords(self, event):
        """
        Transpose the word before the cursor with the word after the cursor
        Punctuation between words does not move. For example, ‘FOO, BAR’
        transposes into ‘BAR, FOO’.
        """
        w = self.editWidget(event)
        if not w: return
        self.beginCommand(w, undoType='transpose-words')
        s = w.getAllText()
        i1, j1 = self.extendToWord(event, select=False)
        s1 = s[i1: j1]
        if i1 > j1: i1, j1 = j1, i1
        # Search for the next word.
        k = j1 + 1
        while k < len(s) and s[k] != '\n' and not g.isWordChar1(s[k]):
            k += 1
        changed = k < len(s)
        if changed:
            ws = s[j1: k]
            w.setInsertPoint(k + 1)
            i2, j2 = self.extendToWord(event, select=False)
            s2 = s[i2: j2]
            s3 = s[: i1] + s2 + ws + s1 + s[j2:]
            w.setAllText(s3)
            w.setSelectionRange(j1, j1, insert=j1)
        self.endCommand(changed=changed, setLabel=True)
    #@+node:ekr.20150514063305.346: *4* ec.swapCharacters & transeposeCharacters
    @cmd('transpose-chars')
    def transposeCharacters(self, event):
        """Swap the characters at the cursor."""
        w = self.editWidget(event)
        if not w:
            return
        self.beginCommand(w, undoType='swap-characters')
        s = w.getAllText()
        i = w.getInsertPoint()
        if 0 < i < len(s):
            w.setAllText(s[: i - 1] + s[i] + s[i - 1] + s[i + 1:])
            w.setSelectionRange(i, i, insert=i)
        self.endCommand(changed=True, setLabel=True)

    swapCharacters = transposeCharacters
    #@+node:ekr.20150514063305.348: *3* ec: uA's
    #@+node:ekr.20150514063305.349: *4* ec.clearNodeUas & clearAllUas (changed)
    @cmd('clear-node-uas')
    def clearNodeUas(self, event=None):
        """Clear the uA's in the selected VNode."""
        c = self.c
        p = c and c.p
        if p and p.v.u:
            p.v.u = {}
            # #1276.
            p.setDirty() # was p.v.setDirty.
            c.setChanged()
            c.redraw()
            
    @cmd('clear-all-uas')
    def clearAllUas(self, event=None):
        """Clear all uAs in the entire outline."""
        c = self.c
        # #1276.
        changed = False
        for p in self.c.all_unique_positions():
            if p.v.u:
                p.v.u = {}
                p.setDirty() # was p.v.setDirty.
                changed = True
        if changed:
            c.setChanged()
            c.redraw()
    #@+node:ekr.20150514063305.350: *4* ec.showUas & showAllUas
    @cmd('show-all-uas')
    def showAllUas(self, event=None):
        """Print all uA's in the outline."""
        g.es_print('Dump of uAs...')
        for v in self.c.all_unique_nodes():
            if v.u:
                self.showNodeUas(v=v)

    @cmd('show-node-uas')
    def showNodeUas(self, event=None, v=None):
        """Print the uA's in the selected node."""
        c = self.c
        if v:
            d, h = v.u, v.h
        else:
            d, h = c.p.v.u, c.p.h
        g.es_print(h)
        g.es_print(g.objToString(d))
    #@+node:ekr.20150514063305.351: *4* ec.setUa
    @cmd('set-ua')
    def setUa(self, event):
        """Prompt for the name and value of a uA, then set the uA in the present node."""
        k = self.c.k
        self.w = self.editWidget(event)
        if self.w:
            k.setLabelBlue('Set uA: ')
            k.get1Arg(event, handler=self.setUa1)

    def setUa1(self, event):
        k = self.c.k
        self.uaName = k.arg
        s = 'Set uA: %s To: ' % (self.uaName)
        k.setLabelBlue(s)
        k.getNextArg(self.setUa2)

    def setUa2(self, event):
        c, k = self.c, self.c.k
        val = k.arg
        d = c.p.v.u
        d[self.uaName] = val
        self.showNodeUas()
        k.clearState()
        k.resetLabel()
        k.showStateAndMode()
    #@-others
#@-others
#@-leo
