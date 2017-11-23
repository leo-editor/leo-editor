# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20171123135539.1: * @file ../commands/commanderEditCommands.py
#@@first
'''Edit commands that used to be defined in leoCommands.py'''
import leo.core.leoGlobals as g
### import builtins
import os
# import re
### import sys
# import time

#@+others
#@+node:ekr.20171123135625.2: ** Edit top level
#@+node:ekr.20171123135625.3: *3* c.colorPanel
@g.commander_command('set-colors')
def colorPanel(self, event=None):
    '''Open the color dialog.'''
    c = self; frame = c.frame
    if not frame.colorPanel:
        frame.colorPanel = g.app.gui.createColorPanel(c)
    frame.colorPanel.bringToFront()
#@+node:ekr.20171123135625.9: *3* c.fontPanel
@g.commander_command('set-font')
def fontPanel(self, event=None):
    '''Open the font dialog.'''
    c = self; frame = c.frame
    if not frame.fontPanel:
        frame.fontPanel = g.app.gui.createFontPanel(c)
    frame.fontPanel.bringToFront()
#@+node:ekr.20171123135625.11: *3* c.preferences
@g.commander_command('settings')
def preferences(self, event=None):
    '''Handle the preferences command.'''
    c = self
    c.openLeoSettings()
#@+node:ekr.20171123135625.13: *3* c.writeScriptFile
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
#@+node:ekr.20171123135625.14: ** Edit Body submenu
#@+node:ekr.20171123135625.15: *3* c.findMatchingBracket
@g.commander_command('match-brackets')
@g.commander_command('select-to-matching-bracket')
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
#@+node:ekr.20171123135625.16: *3* c.convertAllBlanks
@g.commander_command('convert-all-blanks')
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
#@+node:ekr.20171123135625.17: *3* c.convertAllTabs
@g.commander_command('convert-all-tabs')
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
#@+node:ekr.20171123135625.18: *3* c.convertBlanks
@g.commander_command('convert-blanks')
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
#@+node:ekr.20171123135625.19: *3* c.convertTabs
@g.commander_command('convert-tabs')
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
#@+node:ekr.20171123135625.21: *3* c.dedentBody (unindent-region)
@g.commander_command('unindent-region')
def dedentBody(self, event=None):
    '''Remove one tab's worth of indentation from all presently selected lines.'''
    c, undoType = self, 'Unindent'
    w = c.frame.body.wrapper
    sel_1, sel_2 = w.getSelectionRange()
    ins = w.getInsertPoint()
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
        # Leo 5.6: preserve insert point.
        preserveSel = sel_1 == sel_2
        if preserveSel:
            ins = max(0, ins - abs(tab_width))
            oldSel = ins, ins
        c.updateBodyPane(head, result, tail, undoType, oldSel, oldYview, preserveSel)
#@+node:ekr.20171123135625.30: *3* c.indentBody (indent-region)
@g.commander_command('indent-region')
def indentBody(self, event=None):
    '''
    The indent-region command indents each line of the selected body text,
    or each line of a node if there is no selected text. The @tabwidth directive
    in effect determines amount of indentation. (not yet) A numeric argument
    specifies the column to indent to.
    '''
    c, undoType = self, 'Indent Region'
    w = c.frame.body.wrapper
    sel_1, sel_2 = w.getSelectionRange()
    ins = w.getInsertPoint()
    tab_width = c.getTabWidth(c.p)
    head, lines, tail, oldSel, oldYview = self.getBodyLines()
    changed, result = False, []
    for line in lines:
        i, width = g.skip_leading_ws_with_indent(line, 0, tab_width)
        s = g.computeLeadingWhitespace(width + abs(tab_width), tab_width) + line[i:]
        if s != line: changed = True
        result.append(s)
    if changed:
        # Leo 5.6: preserve insert point.
        preserveSel = sel_1 == sel_2
        if preserveSel:
            ins += tab_width
            oldSel = ins, ins
        result = ''.join(result)
        c.updateBodyPane(head, result, tail, undoType, oldSel, oldYview, preserveSel)
#@+node:ekr.20171123135625.38: *3* c.insertBodyTime, helpers and tests
@g.commander_command('insert-body-time')
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
#@+node:ekr.20171123135625.40: *3* c.reformatBody
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
#@+node:ekr.20171123135625.49: *3* c.unformatParagraph & helper
@g.commander_command('unformat-paragraph')
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
#@+node:ekr.20171123135625.50: *4* c.unreformat
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
#@+node:ekr.20171123135625.52: *3* justify-toggle-auto
@g.commander_command("justify-toggle-auto")
def justify_toggle_auto(self, event=None):
    c = self
    if c.editCommands.autojustify == 0:
        c.editCommands.autojustify = abs(c.config.getInt("autojustify") or 0)
        if c.editCommands.autojustify:
            g.es("Autojustify on, @int autojustify == %s" %
            c.editCommands.autojustify)
        else:
            g.es("Set @int autojustify in @settings")
    else:
        c.editCommands.autojustify = 0
        g.es("Autojustify off")
#@+node:ekr.20171123135625.53: ** Edit Headline submenu
#@+node:ekr.20171123135625.54: *3* c.editHeadline
@g.commander_command('edit-headline')
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
        # Neither of these is used by any caller.
#@+node:ekr.20171123135625.55: *3* c.toggleAngleBrackets
@g.commander_command('toggle-angle-brackets')
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
#@+node:ekr.20171123135625.27: ** c.extractSectionNames
@g.commander_command('extract-names')
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
#@+node:ekr.20171123135625.28: *3* c.findSectionName
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
#@-others
#@-leo
