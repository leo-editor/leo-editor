# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20171123135539.1: * @file ../commands/commanderEditCommands.py
#@@first
"""Edit commands that used to be defined in leoCommands.py"""
import leo.core.leoGlobals as g
import re
#@+others
#@+node:ekr.20171123135625.34: ** c_ec.addComments
@g.commander_command('add-comments')
def addComments(self, event=None):
    #@+<< addComments docstring >>
    #@+node:ekr.20171123135625.35: *3* << addComments docstring >>
    #@@pagewidth 50
    """
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
    """
    #@-<< addComments docstring >>
    c = self; p = c.p
    head, lines, tail, oldSel, oldYview = self.getBodyLines()
    if not lines:
        g.warning('no text selected')
        return
    # The default language in effect at p.
    language = c.frame.body.colorizer.scanLanguageDirectives(p)
    if c.hasAmbiguousLanguage(p):
        language = c.getLanguageAtCursor(p, language)
    d1, d2, d3 = g.set_delims_from_language(language)
    d2 = d2 or ''; d3 = d3 or ''
    if d1:
        openDelim, closeDelim = d1 + ' ', ''
    else:
        openDelim, closeDelim = d2 + ' ', ' ' + d3
    # Comment out non-blank lines.
    indent = c.config.getBool('indent-added-comments', default=True)
    result = []
    for line in lines:
        if line.strip():
            i = g.skip_ws(line, 0)
            if indent:
                s = line[i:].replace('\n', '')
                result.append(line[0:i] + openDelim + s + closeDelim + '\n')
            else:
                s = line.replace('\n', '')
                result.append(openDelim + s + closeDelim + '\n')
        else:
            result.append(line)
    result = ''.join(result)
    c.updateBodyPane(
        head, result, tail, undoType='Add Comments', oldSel=None, oldYview=oldYview)
#@+node:ekr.20171123135625.3: ** c_ec.colorPanel
@g.commander_command('set-colors')
def colorPanel(self, event=None):
    """Open the color dialog."""
    c = self; frame = c.frame
    if not frame.colorPanel:
        frame.colorPanel = g.app.gui.createColorPanel(c)
    frame.colorPanel.bringToFront()
#@+node:ekr.20171123135625.16: ** c_ec.convertAllBlanks
@g.commander_command('convert-all-blanks')
def convertAllBlanks(self, event=None):
    """Convert all blanks to tabs in the selected outline."""
    c = self; u = c.undoer; undoType = 'Convert All Blanks'
    current = c.p
    if g.app.batchMode:
        c.notValidInBatchMode(undoType)
        return
    d = c.scanAllDirectives()
    tabWidth = d.get("tabwidth")
    count = 0
    u.beforeChangeGroup(current, undoType)
    for p in current.self_and_subtree():
        innerUndoData = u.beforeChangeNodeContents(p)
        if p == current:
            changed = c.convertBlanks(event)
            if changed:
                count += 1
        else:
            changed = False; result = []
            text = p.v.b
            lines = text.split('\n')
            for line in lines:
                i, w = g.skip_leading_ws_with_indent(line, 0, tabWidth)
                s = g.computeLeadingWhitespace(
                    w, abs(tabWidth)) + line[i:]  # use positive width.
                if s != line: changed = True
                result.append(s)
            if changed:
                count += 1
                p.setDirty()
                result = '\n'.join(result)
                p.setBodyString(result)
                u.afterChangeNodeContents(p, undoType, innerUndoData)
    u.afterChangeGroup(current, undoType)
    if not g.unitTesting:
        g.es("blanks converted to tabs in", count, "nodes")
            # Must come before c.redraw().
    if count > 0:
        c.redraw_after_icons_changed()
#@+node:ekr.20171123135625.17: ** c_ec.convertAllTabs
@g.commander_command('convert-all-tabs')
def convertAllTabs(self, event=None):
    """Convert all tabs to blanks in the selected outline."""
    c = self; u = c.undoer; undoType = 'Convert All Tabs'
    current = c.p
    if g.app.batchMode:
        c.notValidInBatchMode(undoType)
        return
    theDict = c.scanAllDirectives()
    tabWidth = theDict.get("tabwidth")
    count = 0
    u.beforeChangeGroup(current, undoType)
    for p in current.self_and_subtree():
        undoData = u.beforeChangeNodeContents(p)
        if p == current:
            changed = self.convertTabs(event)
            if changed:
                count += 1
        else:
            result = []; changed = False
            text = p.v.b
            lines = text.split('\n')
            for line in lines:
                i, w = g.skip_leading_ws_with_indent(line, 0, tabWidth)
                s = g.computeLeadingWhitespace(
                    w, -abs(tabWidth)) + line[i:]  # use negative width.
                if s != line: changed = True
                result.append(s)
            if changed:
                count += 1
                p.setDirty()
                result = '\n'.join(result)
                p.setBodyString(result)
                u.afterChangeNodeContents(p, undoType, undoData)
    u.afterChangeGroup(current, undoType)
    if not g.unitTesting:
        g.es("tabs converted to blanks in", count, "nodes")
    if count > 0:
        c.redraw_after_icons_changed()
#@+node:ekr.20171123135625.18: ** c_ec.convertBlanks
@g.commander_command('convert-blanks')
def convertBlanks(self, event=None):
    """Convert all blanks to tabs in the selected node."""
    c = self; changed = False
    head, lines, tail, oldSel, oldYview = c.getBodyLines(expandSelection=True)
    # Use the relative @tabwidth, not the global one.
    theDict = c.scanAllDirectives()
    tabWidth = theDict.get("tabwidth")
    if tabWidth:
        result = []
        for line in lines:
            s = g.optimizeLeadingWhitespace(line, abs(tabWidth))
                # Use positive width.
            if s != line: changed = True
            result.append(s)
        if changed:
            undoType = 'Convert Blanks'
            result = ''.join(result)
            oldSel = None
            c.updateBodyPane(head, result, tail, undoType, oldSel, oldYview)
                # Handles undo
    return changed
#@+node:ekr.20171123135625.19: ** c_ec.convertTabs
@g.commander_command('convert-tabs')
def convertTabs(self, event=None):
    """Convert all tabs to blanks in the selected node."""
    c = self; changed = False
    head, lines, tail, oldSel, oldYview = self.getBodyLines(expandSelection=True)
    # Use the relative @tabwidth, not the global one.
    theDict = c.scanAllDirectives()
    tabWidth = theDict.get("tabwidth")
    if tabWidth:
        result = []
        for line in lines:
            i, w = g.skip_leading_ws_with_indent(line, 0, tabWidth)
            s = g.computeLeadingWhitespace(w, -abs(tabWidth)) + line[i:]
                # use negative width.
            if s != line: changed = True
            result.append(s)
        if changed:
            undoType = 'Convert Tabs'
            result = ''.join(result)
            oldSel = None
            c.updateBodyPane(head, result, tail, undoType, oldSel, oldYview)
                # Handles undo
    return changed
#@+node:ekr.20171123135625.21: ** c_ec.dedentBody (unindent-region)
@g.commander_command('unindent-region')
def dedentBody(self, event=None):
    """Remove one tab's worth of indentation from all presently selected lines."""
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
        # Leo 5.6: preserve insert point.
        preserveSel = sel_1 == sel_2
        if preserveSel:
            ins = max(len(head), len(result[0]) - len(lines[0]) + ins)
            oldSel = ins, ins
        result = ''.join(result)
        c.updateBodyPane(head, result, tail, undoType, oldSel, oldYview, preserveSel)
#@+node:ekr.20171123135625.36: ** c_ec.deleteComments
@g.commander_command('delete-comments')
def deleteComments(self, event=None):
    #@+<< deleteComments docstring >>
    #@+node:ekr.20171123135625.37: *3* << deleteComments docstring >>
    #@@pagewidth 50
    """
    Removes one level of comment delimiters from all
    selected lines.  The applicable @language directive
    determines the comment delimiters to be removed.

    Removes single-line comments if possible; removes
    block comments for languages like html that lack
    single-line comments.

    *See also*: add-comments.
    """
    #@-<< deleteComments docstring >>
    c = self
    p = c.p
    head, lines, tail, oldSel, oldYview = self.getBodyLines()
    result = []
    if not lines:
        g.warning('no text selected')
        return
    # The default language in effect at p.
    language = c.frame.body.colorizer.scanLanguageDirectives(p)
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
                result.append(s[:i] + s[i + n1b :])
            elif g.match(s, i, d1):
                result.append(s[:i] + s[i + n1 :])
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
                result.append(s[:i] + s[first:last] + s[j + n3 :])
            else:
                result.append(s)
    result = ''.join(result)
    c.updateBodyPane(
        head, result, tail, undoType='Delete Comments', oldSel=None, oldYview=oldYview)
#@+node:ekr.20171123135625.54: ** c_ec.editHeadline
@g.commander_command('edit-headline')
def editHeadline(self, event=None):
    """Begin editing the headline of the selected node."""
    c = self
    k, tree = c.k, c.frame.tree
    if g.app.batchMode:
        c.notValidInBatchMode("Edit Headline")
        return None, None
    e, wrapper = tree.editLabel(c.p)
    if k:
        # k.setDefaultInputState()
        k.setEditingState()
        k.showStateAndMode(w=wrapper)
    return e, wrapper
        # Neither of these is used by any caller.
#@+node:ekr.20171123135625.23: ** c_ec.extract & helpers
@g.commander_command('extract')
def extract(self, event=None):
    r"""
    Create child node from the selected body text.

    1. If the selection starts with a section reference, the section
       name becomes the child's headline. All following lines become
       the child's body text. The section reference line remains in
       the original body text.

    2. If the selection looks like a definition line (for the Python,
       JavaScript, CoffeeScript or Clojure languages) the
       class/function/method name becomes the child's headline and all
       selected lines become the child's body text.
       
       You may add additional regex patterns for definition lines using
       @data extract-patterns nodes. Each line of the body text should a
       valid regex pattern. Lines starting with # are comment lines. Use \#
       for patterns starting with #.

    3. Otherwise, the first line becomes the child's headline, and all
       selected lines become the child's body text.
    """
    c = self
    current = c.p  # Unchanging.
    u, undoType = c.undoer, 'Extract'
    head, lines, tail, oldSel, oldYview = c.getBodyLines()
    if not lines:
        return  # Nothing selected.
    # Remove leading whitespace.
    junk, ws = g.skip_leading_ws_with_indent(lines[0], 0, c.tab_width)
    lines = [g.removeLeadingWhitespace(s, ws, c.tab_width) for s in lines]
    h = lines[0].strip()
    ref_h = extractRef(c, h).strip()
    def_h = extractDef_find(c, lines)
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
    p = createLastChildNode(c, current, h, ''.join(b))
    u.afterInsertNode(p, undoType, undoData)
    c.updateBodyPane(head, middle, tail,
        undoType=undoType, oldSel=None, oldYview=oldYview)
    u.afterChangeGroup(current, undoType=undoType)
    p.parent().expand()
    c.redraw(p.parent())  # A bit more convenient than p.
    c.bodyWantsFocus()

# Compatibility

g.command_alias('extractSection', extract)
g.command_alias('extractPythonMethod', extract)
#@+node:ekr.20171123135625.20: *3* def createLastChildNode
def createLastChildNode(c, parent, headline, body):
    """A helper function for the three extract commands."""
    if body:
        body = body.rstrip()
    if not body:
        body = ""
    p = parent.insertAsLastChild()
    p.initHeadString(headline)
    p.setBodyString(body)
    p.setDirty()
    c.validateOutline()
    return p
#@+node:ekr.20171123135625.24: *3* def extractDef
extractDef_patterns = (
    re.compile(
    r'\((?:def|defn|defui|deftype|defrecord|defonce)\s+(\S+)'),  # clojure definition
    re.compile(r'^\s*(?:def|class)\s+(\w+)'),  # python definitions
    re.compile(r'^\bvar\s+(\w+)\s*=\s*function\b'),  # js function
    re.compile(r'^(?:export\s)?\s*function\s+(\w+)\s*\('),  # js function
    re.compile(r'\b(\w+)\s*:\s*function\s'),  # js function
    re.compile(r'\.(\w+)\s*=\s*function\b'),  # js function
    re.compile(r'(?:export\s)?\b(\w+)\s*=\s(?:=>|->)'),  # coffeescript function
    re.compile(
    r'(?:export\s)?\b(\w+)\s*=\s(?:\([^)]*\))\s*(?:=>|->)'),  # coffeescript function
    re.compile(r'\b(\w+)\s*:\s(?:=>|->)'),  # coffeescript function
    re.compile(r'\b(\w+)\s*:\s(?:\([^)]*\))\s*(?:=>|->)'),  # coffeescript function
)

def extractDef(c, s):
    """
    Return the defined function/method/class name if s
    looks like definition. Tries several different languages.
    """
    for pat in c.config.getData('extract-patterns') or []:
        try:
            pat = re.compile(pat)
            m = pat.search(s)
            if m: return m.group(1)
        except Exception:
            g.es_print('bad regex in @data extract-patterns', color='blue')
            g.es_print(pat)
    for pat in extractDef_patterns:
        m = pat.search(s)
        if m: return m.group(1)
    return ''
#@+node:ekr.20171123135625.26: *3* def extractDef_find
def extractDef_find(c, lines):
    for line in lines:
        def_h = extractDef(c, line.strip())
        if def_h:
            return def_h
    return None
#@+node:ekr.20171123135625.25: *3* def extractRef
def extractRef(c, s):
    """Return s if it starts with a section name."""
    i = s.find('<<')
    j = s.find('>>')
    if -1 < i < j:
        return s
    i = s.find('@<')
    j = s.find('@>')
    if -1 < i < j:
        return s
    return ''
#@+node:ekr.20171123135625.27: ** c_ec.extractSectionNames & helper
@g.commander_command('extract-names')
def extractSectionNames(self, event=None):
    """
    Create child nodes for every section reference in the selected text.
    - The headline of each new child node is the section reference.
    - The body of each child node is empty.
    """
    c = self
    current = c.p
    u = c.undoer
    undoType = 'Extract Section Names'
    body = c.frame.body
    head, lines, tail, oldSel, oldYview = c.getBodyLines()
    if not lines:
        g.warning('No lines selected')
        return
    u.beforeChangeGroup(current, undoType)
    found = False
    for s in lines:
        name = findSectionName(c, s)
        if name:
            undoData = u.beforeInsertNode(current)
            p = createLastChildNode(c, current, name, None)
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
#@+node:ekr.20171123135625.28: *3* def findSectionName
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
        name = s[head1 : head2 + 2]
    return name
#@+node:ekr.20171123135625.15: ** c_ec.findMatchingBracket
@g.commander_command('match-brackets')
@g.commander_command('select-to-matching-bracket')
def findMatchingBracket(self, event=None):
    """Select the text between matching brackets."""
    c, p = self, self.p
    if g.app.batchMode:
        c.notValidInBatchMode("Match Brackets")
        return
    language = g.getLanguageAtPosition(c, p)
    if language == 'perl':
        g.es('match-brackets not supported for', language)
    else:
        g.MatchBrackets(c, p, language).run()
#@+node:ekr.20171123135625.9: ** c_ec.fontPanel
@g.commander_command('set-font')
def fontPanel(self, event=None):
    """Open the font dialog."""
    c = self; frame = c.frame
    if not frame.fontPanel:
        frame.fontPanel = g.app.gui.createFontPanel(c)
    frame.fontPanel.bringToFront()
#@+node:ekr.20110402084740.14490: ** c_ec.goToNext/PrevHistory
@g.commander_command('goto-next-history-node')
def goToNextHistory(self, event=None):
    """Go to the next node in the history list."""
    c = self
    c.nodeHistory.goNext()

@g.commander_command('goto-prev-history-node')
def goToPrevHistory(self, event=None):
    """Go to the previous node in the history list."""
    c = self
    c.nodeHistory.goPrev()
#@+node:ekr.20171123135625.30: ** c_ec.indentBody (indent-region)
@g.commander_command('indent-region')
def indentBody(self, event=None):
    """
    The indent-region command indents each line of the selected body text,
    or each line of a node if there is no selected text. The @tabwidth directive
    in effect determines amount of indentation. (not yet) A numeric argument
    specifies the column to indent to.
    """
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
#@+node:ekr.20171123135625.38: ** c_ec.insertBodyTime
@g.commander_command('insert-body-time')
def insertBodyTime(self, event=None):
    """Insert a time/date stamp at the cursor."""
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
#@+node:ekr.20171123135625.52: ** c_ec.justify-toggle-auto
@g.commander_command("justify-toggle-auto")
def justify_toggle_auto(self, event=None):
    c = self
    if c.editCommands.autojustify == 0:
        c.editCommands.autojustify = abs(c.config.getInt("autojustify") or 0)
        if c.editCommands.autojustify:
            g.es(f"Autojustify on, @int autojustify == {c.editCommands.autojustify}")
        else:
            g.es("Set @int autojustify in @settings")
    else:
        c.editCommands.autojustify = 0
        g.es("Autojustify off")
#@+node:ekr.20190210095609.1: ** c_ec.line_to_headline
@g.commander_command('line-to-headline')
def line_to_headline(self, event=None):
    """
    Create child node from the selected line.
    
    Cut the selected line and make it the new node's headline
    """
    c, w = self, self.frame.body.wrapper
    p = c.p
    ins, s = w.getInsertPoint(), p.b
    u, undoType = c.undoer, 'Extract Line'
    i = g.find_line_start(s, ins)
    j = g.skip_line(s, i)
    line = s[i:j].strip()
    if not line:
        return
    u.beforeChangeGroup(p, undoType)
    undoData = u.beforeInsertNode(p)
    p2 = p.insertAsLastChild()
    p2.h = line
    u.afterInsertNode(p2, undoType, undoData)
    oldText = p.b
    p.b = s[:i] + s[j:]
    w.setInsertPoint(i)
    u.setUndoTypingParams(p, undoType, oldText=oldText, newText=p.b)
    p2.setDirty()
    c.setChanged()
    u.afterChangeGroup(p, undoType=undoType)
    c.redraw_after_icons_changed()
    p.expand()
    c.redraw(p)
    c.bodyWantsFocus()
#@+node:ekr.20171123135625.11: ** c_ec.preferences
@g.commander_command('settings')
def preferences(self, event=None):
    """Handle the preferences command."""
    c = self
    c.openLeoSettings()
#@+node:ekr.20171123135625.40: ** c_ec.reformatBody
@g.commander_command('reformat-body')
def reformatBody(self, event=None):
    """Reformat all paragraphs in the body."""
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
#@+node:ekr.20171123135625.41: ** c_ec.reformatParagraph & helpers
@g.commander_command('reformat-paragraph')
def reformatParagraph(self, event=None, undoType='Reformat Paragraph'):
    """
    Reformat a text paragraph

    Wraps the concatenated text to present page width setting. Leading tabs are
    sized to present tab width setting. First and second line of original text is
    used to determine leading whitespace in reformatted text. Hanging indentation
    is honored.

    Paragraph is bound by start of body, end of body and blank lines. Paragraph is
    selected by position of current insertion cursor.
    """
    c = self
    body = c.frame.body
    w = body.wrapper
    if g.app.batchMode:
        c.notValidInBatchMode("reformat-paragraph")
        return
    if w.hasSelection():
        i, j = w.getSelectionRange()
        w.setInsertPoint(i)
    oldSel, oldYview, original, pageWidth, tabWidth = rp_get_args(c)
    head, lines, tail = find_bound_paragraph(c)
    if lines:
        indents, leading_ws = rp_get_leading_ws(c, lines, tabWidth)
        result = rp_wrap_all_lines(c, indents, leading_ws, lines, pageWidth)
        rp_reformat(c, head, oldSel, oldYview, original, result, tail, undoType)
#@+node:ekr.20171123135625.43: *3* def ends_paragraph & single_line_paragraph
def ends_paragraph(s):
    """Return True if s is a blank line."""
    return not s.strip()

def single_line_paragraph(s):
    """Return True if s is a single-line paragraph."""
    return s.startswith('@') or s.strip() in ('"""', "'''")
#@+node:ekr.20171123135625.42: *3* def find_bound_paragraph
def find_bound_paragraph(c):
    """
    Return the lines of a paragraph to be reformatted.
    This is a convenience method for the reformat-paragraph command.
    """
    head, ins, tail = c.frame.body.getInsertLines()
    head_lines = g.splitLines(head)
    tail_lines = g.splitLines(tail)
    result = []
    insert_lines = g.splitLines(ins)
    para_lines = insert_lines + tail_lines
    # If the present line doesn't start a paragraph,
    # scan backward, adding trailing lines of head to ins.
    if insert_lines and not startsParagraph(insert_lines[0]):
        n = 0  # number of moved lines.
        for i, s in enumerate(reversed(head_lines)):
            if ends_paragraph(s) or single_line_paragraph(s):
                break
            elif startsParagraph(s):
                n += 1
                break
            else: n += 1
        if n > 0:
            para_lines = head_lines[-n :] + para_lines
            head_lines = head_lines[: -n]
    ended, started = False, False
    for i, s in enumerate(para_lines):
        if started:
            if ends_paragraph(s) or startsParagraph(s):
                ended = True
                break
            else:
                result.append(s)
        elif s.strip():
            result.append(s)
            started = True
            if ends_paragraph(s) or single_line_paragraph(s):
                i += 1
                ended = True
                break
        else:
            head_lines.append(s)
    if started:
        head = g.joinLines(head_lines)
        tail_lines = para_lines[i:] if ended else []
        tail = g.joinLines(tail_lines)
        return head, result, tail  # string, list, string
    return None, None, None
#@+node:ekr.20171123135625.45: *3* def rp_get_args
def rp_get_args(c):
    """Compute and return oldSel,oldYview,original,pageWidth,tabWidth."""
    body = c.frame.body
    w = body.wrapper
    d = c.scanAllDirectives()
    if c.editCommands.fillColumn > 0:
        pageWidth = c.editCommands.fillColumn
    else:
        pageWidth = d.get("pagewidth")
    tabWidth = d.get("tabwidth")
    original = w.getAllText()
    oldSel = w.getSelectionRange()
    oldYview = w.getYScrollPosition()
    return oldSel, oldYview, original, pageWidth, tabWidth
#@+node:ekr.20171123135625.46: *3* def rp_get_leading_ws
def rp_get_leading_ws(c, lines, tabWidth):
    """Compute and return indents and leading_ws."""
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
#@+node:ekr.20171123135625.47: *3* def rp_reformat
def rp_reformat(c, head, oldSel, oldYview, original, result, tail, undoType):
    """Reformat the body and update the selection."""
    body = c.frame.body
    w = body.wrapper
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
        ins += 1  # Move past the selection.
        while ins < len(s):
            i, j = g.getLine(s, ins)
            line = s[i:j]
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
#@+node:ekr.20171123135625.48: *3* def rp_wrap_all_lines
def rp_wrap_all_lines(c, indents, leading_ws, lines, pageWidth):
    """Compute the result of wrapping all lines."""
    trailingNL = lines and lines[-1].endswith('\n')
    lines = [z[:-1] if z.endswith('\n') else z for z in lines]
    if lines:  # Bug fix: 2013/12/22.
        s = lines[0]
        if startsParagraph(s):
            # Adjust indents[1]
            # Similar to code in startsParagraph(s)
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
#@+node:ekr.20171123135625.44: *3* def startsParagraph
def startsParagraph(s):
    """Return True if line s starts a paragraph."""
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
    return val
#@+node:ekr.20171123135625.12: ** c_ec.show/hide/toggleInvisibles
@g.commander_command('hide-invisibles')
def hideInvisibles(self, event=None):
    """Hide invisible (whitespace) characters."""
    c = self
    showInvisiblesHelper(c, False)

@g.commander_command('show-invisibles')
def showInvisibles(self, event=None):
    """Show invisible (whitespace) characters."""
    c = self
    showInvisiblesHelper(c, True)

@g.commander_command('toggle-invisibles')
def toggleShowInvisibles(self, event=None):
    """Toggle showing of invisible (whitespace) characters."""
    c = self
    colorizer = c.frame.body.getColorizer()
    showInvisiblesHelper(c, not colorizer.showInvisibles)

def showInvisiblesHelper(c, val):
    frame = c.frame
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
    # #240: Set the status bits here.
    if hasattr(frame.body, 'set_invisibles'):
        frame.body.set_invisibles(c)
    c.frame.body.recolor(c.p)
#@+node:ekr.20171123135625.55: ** c_ec.toggleAngleBrackets
@g.commander_command('toggle-angle-brackets')
def toggleAngleBrackets(self, event=None):
    """Add or remove double angle brackets from the headline of the selected node."""
    c = self; p = c.p
    if g.app.batchMode:
        c.notValidInBatchMode("Toggle Angle Brackets")
        return
    c.endEditing()
    s = p.h.strip()
    # 2019/09/12: Guard against black.
    lt = "<<"
    rt = ">>"
    if s[0:2] == lt or s[-2:] == rt:
        if s[0:2] == "<<": s = s[2:]
        if s[-2:] == ">>": s = s[:-2]
        s = s.strip()
    else:
        s = g.angleBrackets(' ' + s + ' ')
    p.setHeadString(s)
    p.setDirty()  # #1449.
    c.setChanged()  # #1449.
    c.redrawAndEdit(p, selectAll=True)
#@+node:ekr.20171123135625.49: ** c_ec.unformatParagraph & helper
@g.commander_command('unformat-paragraph')
def unformatParagraph(self, event=None, undoType='Unformat Paragraph'):
    """
    Unformat a text paragraph. Removes all extra whitespace in a paragraph.

    Paragraph is bound by start of body, end of body and blank lines. Paragraph is
    selected by position of current insertion cursor.
    """
    c = self
    body = c.frame.body
    w = body.wrapper
    if g.app.batchMode:
        c.notValidInBatchMode("unformat-paragraph")
        return
    if w.hasSelection():
        i, j = w.getSelectionRange()
        w.setInsertPoint(i)
    oldSel, oldYview, original, pageWidth, tabWidth = rp_get_args(c)
    head, lines, tail = find_bound_paragraph(c)
    if lines:
        result = ' '.join([z.strip() for z in lines]) + '\n'
        unreformat(c, head, oldSel, oldYview, original, result, tail, undoType)
#@+node:ekr.20171123135625.50: *3* def.unreformat
def unreformat(c, head, oldSel, oldYview, original, result, tail, undoType):
    """unformat the body and update the selection."""
    body = c.frame.body
    w = body.wrapper
    # This destroys recoloring.
    junk, ins = body.setSelectionAreas(head, result, tail)
    changed = original != head + result + tail
    if changed:
        body.onBodyChanged(undoType, oldSel=oldSel, oldYview=oldYview)
    # Advance to the next paragraph.
    s = w.getAllText()
    ins += 1  # Move past the selection.
    while ins < len(s):
        i, j = g.getLine(s, ins)
        line = s[i:j]
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
#@+node:ekr.20180410054716.1: ** c_ec: insert-jupyter-toc & insert-markdown-toc
@g.commander_command('insert-jupyter-toc')
def insertJupyterTOC(self, event=None):
    """
    Insert a Jupyter table of contents at the cursor,
    replacing any selected text.
    """
    insert_toc(c=self, kind='jupyter')

@g.commander_command('insert-markdown-toc')
def insertMarkdownTOC(self, event=None):
    """
    Insert a Markdown table of contents at the cursor,
    replacing any selected text.
    """
    insert_toc(c=self, kind='markdown')
#@+node:ekr.20180410074238.1: *3* insert_toc
def insert_toc(c, kind):
    """Insert a table of contents at the cursor."""
    undoType = f"Insert {kind.capitalize()} TOC"
    w = c.frame.body.wrapper
    if g.app.batchMode:
        c.notValidInBatchMode(undoType)
        return
    oldSel = w.getSelectionRange()
    w.deleteTextSelection()
    s = make_toc(c, kind=kind, root=c.p)
    i = w.getInsertPoint()
    w.insert(i, s)
    c.frame.body.onBodyChanged(undoType, oldSel=oldSel)
#@+node:ekr.20180410054926.1: *3* make_toc
def make_toc(c, kind, root):
    """Return the toc for root.b as a list of lines."""

    def cell_type(p):
        language = g.getLanguageAtPosition(c, p)
        return 'markdown' if language in ('jupyter', 'markdown') else 'python'

    def clean_headline(s):
        # Surprisingly tricky. This could remove too much, but better to be safe.
        aList = [ch for ch in s if ch in '-: ' or ch.isalnum()]
        return ''.join(aList).rstrip('-').strip()

    result, stack = [], []
    for p in root.subtree():
        if cell_type(p) == 'markdown':
            level = p.level() - root.level()
            if len(stack) < level:
                stack.append(1)
            else:
                stack = stack[:level]
            n = stack[-1]
            stack[-1] = n + 1
            # Use bullets
            title = clean_headline(p.h)
            url = clean_headline(p.h.replace(' ', '-'))
            if kind == 'markdown':
                url = url.lower()
            line = f"{' ' * 4 * (level - 1)}- [{title}](#{url})\n"
            result.append(line)
    if result:
        result.append('\n')
    return ''.join(result)
#@-others
#@-leo
