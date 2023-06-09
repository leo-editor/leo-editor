#@+leo-ver=5-thin
#@+node:ekr.20171123135539.1: * @file ../commands/commanderEditCommands.py
"""Edit commands that used to be defined in leoCommands.py"""

#@+<< commanderEditCommands imports & annotations >>
#@+node:ekr.20220826084013.1: ** << commanderEditCommands imports & annotations >>
from __future__ import annotations
import re
from typing import Any, Optional, TYPE_CHECKING
from leo.core import leoGlobals as g

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent as Event
    from leo.core.leoNodes import Position
    Self = Cmdr  # For arguments to @g.commander_command.
#@-<< commanderEditCommands imports & annotations >>

#@+others
#@+node:ekr.20171123135625.34: ** c_ec.addComments
@g.commander_command('add-comments')
def addComments(self: Self, event: Event = None) -> None:
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
    c, p, u, w = self, self.p, self.undoer, self.frame.body.wrapper
    #
    # "Before" snapshot.
    bunch = u.beforeChangeBody(p)
    #
    # Make sure there is a selection.
    head, lines, tail, oldSel, oldYview = self.getBodyLines()
    if not lines:
        g.warning('no text selected')
        return
    #
    # The default language in effect at p.
    language = c.frame.body.colorizer.scanLanguageDirectives(p)
    if c.hasAmbiguousLanguage(p):
        language = c.getLanguageAtCursor(p, language)
    d1, d2, d3 = g.set_delims_from_language(language)
    d2 = d2 or ''
    d3 = d3 or ''
    if d1:
        openDelim, closeDelim = d1 + ' ', ''
    else:
        openDelim, closeDelim = d2 + ' ', ' ' + d3
    #
    # Calculate the result.
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
    #
    # Set p.b and w's text first.
    middle = ''.join(result)
    p.b = head + middle + tail  # Sets dirty and changed bits.
    w.setAllText(head + middle + tail)
    #
    # Calculate the proper selection range (i, j, ins).
    i = len(head)
    j = max(i, len(head) + len(middle) - 1)
    #
    # Set the selection range and scroll position.
    w.setSelectionRange(i, j, insert=j)
    w.setYScrollPosition(oldYview)
    #
    # "after" snapshot.
    u.afterChangeBody(p, 'Add Comments', bunch)
#@+node:ekr.20171123135625.16: ** c_ec.convertAllBlanks
@g.commander_command('convert-all-blanks')
def convertAllBlanks(self: Self, event: Event = None) -> None:
    """Convert all blanks to tabs in the selected outline."""
    c, u = self, self.undoer
    undoType = 'Convert All Blanks'
    current = c.p
    if g.app.batchMode:
        c.notValidInBatchMode(undoType)
        return
    d = c.scanAllDirectives(c.p)
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
            changed = False
            result = []
            text = p.v.b
            lines = text.split('\n')
            for line in lines:
                i, w = g.skip_leading_ws_with_indent(line, 0, tabWidth)
                s = g.computeLeadingWhitespace(
                    w, abs(tabWidth)) + line[i:]  # use positive width.
                if s != line:
                    changed = True
                result.append(s)
            if changed:
                count += 1
                p.setDirty()
                p.setBodyString('\n'.join(result))
                u.afterChangeNodeContents(p, undoType, innerUndoData)
    u.afterChangeGroup(current, undoType)
    if not g.unitTesting:
        # Must come before c.redraw().
        g.es("blanks converted to tabs in", count, "nodes")
#@+node:ekr.20171123135625.17: ** c_ec.convertAllTabs
@g.commander_command('convert-all-tabs')
def convertAllTabs(self: Self, event: Event = None) -> None:
    """Convert all tabs to blanks in the selected outline."""
    c = self
    u = c.undoer
    undoType = 'Convert All Tabs'
    current = c.p
    if g.app.batchMode:
        c.notValidInBatchMode(undoType)
        return
    theDict = c.scanAllDirectives(c.p)
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
            result = []
            changed = False
            text = p.v.b
            lines = text.split('\n')
            for line in lines:
                i, w = g.skip_leading_ws_with_indent(line, 0, tabWidth)
                s = g.computeLeadingWhitespace(
                    w, -abs(tabWidth)) + line[i:]  # use negative width.
                if s != line:
                    changed = True
                result.append(s)
            if changed:
                count += 1
                p.setDirty()
                p.setBodyString('\n'.join(result))
                u.afterChangeNodeContents(p, undoType, undoData)
    u.afterChangeGroup(current, undoType)
    if not g.unitTesting:
        g.es("tabs converted to blanks in", count, "nodes")
#@+node:ekr.20171123135625.18: ** c_ec.convertBlanks
@g.commander_command('convert-blanks')
def convertBlanks(self: Self, event: Event = None) -> bool:
    """
    Convert *all* blanks to tabs in the selected node.
    Return True if the the p.b was changed.
    """
    c, p, u, w = self, self.p, self.undoer, self.frame.body.wrapper
    #
    # "Before" snapshot.
    bunch = u.beforeChangeBody(p)
    oldYview = w.getYScrollPosition()
    w.selectAllText()
    head, lines, tail, oldSel, oldYview = c.getBodyLines()
    #
    # Use the relative @tabwidth, not the global one.
    d = c.scanAllDirectives(p)
    tabWidth = d.get("tabwidth")
    if not tabWidth:
        return False
    #
    # Calculate the result.
    changed, result = False, []
    for line in lines:
        s = g.optimizeLeadingWhitespace(line, abs(tabWidth))  # Use positive width.
        if s != line:
            changed = True
        result.append(s)
    if not changed:
        return False
    #
    # Set p.b and w's text first.
    middle = ''.join(result)
    p.b = head + middle + tail  # Sets dirty and changed bits.
    w.setAllText(head + middle + tail)
    #
    # Select all text and set scroll position.
    w.selectAllText()
    w.setYScrollPosition(oldYview)
    #
    # "after" snapshot.
    u.afterChangeBody(p, 'Indent Region', bunch)
    return True
#@+node:ekr.20171123135625.19: ** c_ec.convertTabs
@g.commander_command('convert-tabs')
def convertTabs(self: Self, event: Event = None) -> bool:
    """Convert all tabs to blanks in the selected node."""
    c, p, u, w = self, self.p, self.undoer, self.frame.body.wrapper
    #
    # "Before" snapshot.
    bunch = u.beforeChangeBody(p)
    #
    # Data...
    w.selectAllText()
    head, lines, tail, oldSel, oldYview = self.getBodyLines()
    # Use the relative @tabwidth, not the global one.
    theDict = c.scanAllDirectives(p)
    tabWidth = theDict.get("tabwidth")
    if not tabWidth:
        return False
    #
    # Calculate the result.
    changed, result = False, []
    for line in lines:
        i, width = g.skip_leading_ws_with_indent(line, 0, tabWidth)
        s = g.computeLeadingWhitespace(width, -abs(tabWidth)) + line[i:]  # use negative width.
        if s != line:
            changed = True
        result.append(s)
    if not changed:
        return False
    #
    # Set p.b and w's text first.
    middle = ''.join(result)
    p.b = head + middle + tail  # Sets dirty and changed bits.
    w.setAllText(head + middle + tail)
    #
    # Calculate the proper selection range (i, j, ins).
    i = len(head)
    j = max(i, len(head) + len(middle) - 1)
    #
    # Set the selection range and scroll position.
    w.setSelectionRange(i, j, insert=j)
    w.setYScrollPosition(oldYview)
    #
    # "after" snapshot.
    u.afterChangeBody(p, 'Add Comments', bunch)
    return True
#@+node:ekr.20171123135625.21: ** c_ec.dedentBody (unindent-region)
@g.commander_command('unindent-region')
def dedentBody(self: Self, event: Event = None) -> None:
    """Remove one tab's worth of indentation from all presently selected lines."""
    c, p, u, w = self, self.p, self.undoer, self.frame.body.wrapper
    #
    # Initial data.
    sel_1, sel_2 = w.getSelectionRange()
    tab_width = c.getTabWidth(c.p)
    head, lines, tail, oldSel, oldYview = self.getBodyLines()
    bunch = u.beforeChangeBody(p)
    #
    # Calculate the result.
    changed, result = False, []
    for line in lines:
        i, width = g.skip_leading_ws_with_indent(line, 0, tab_width)
        s = g.computeLeadingWhitespace(width - abs(tab_width), tab_width) + line[i:]
        if s != line:
            changed = True
        result.append(s)
    if not changed:
        return
    #
    # Set p.b and w's text first.
    middle = ''.join(result)
    all = head + middle + tail
    p.b = all  # Sets dirty and changed bits.
    w.setAllText(all)
    #
    # Calculate the proper selection range (i, j, ins).
    if sel_1 == sel_2:
        line = result[0]
        ins, width = g.skip_leading_ws_with_indent(line, 0, tab_width)
        i = j = len(head) + ins
    else:
        i = len(head)
        j = len(head) + len(middle)
        if middle.endswith('\n'):  # #1742.
            j -= 1
    #
    # Set the selection range and scroll position.
    w.setSelectionRange(i, j, insert=j)
    w.setYScrollPosition(oldYview)
    u.afterChangeBody(p, 'Unindent Region', bunch)
#@+node:ekr.20171123135625.36: ** c_ec.deleteComments
@g.commander_command('delete-comments')
def deleteComments(self: Self, event: Event = None) -> None:
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
    c, p, u, w = self, self.p, self.undoer, self.frame.body.wrapper
    #
    # "Before" snapshot.
    bunch = u.beforeChangeBody(p)
    #
    # Initial data.
    head, lines, tail, oldSel, oldYview = self.getBodyLines()
    if not lines:
        g.warning('no text selected')
        return
    # The default language in effect at p.
    language = c.frame.body.colorizer.scanLanguageDirectives(p)
    if c.hasAmbiguousLanguage(p):
        language = c.getLanguageAtCursor(p, language)
    d1, d2, d3 = g.set_delims_from_language(language)
    #
    # Calculate the result.
    changed, result = False, []
    if d1:
        # Remove the single-line comment delim in front of each line
        d1b = d1 + ' '
        n1, n1b = len(d1), len(d1b)
        for s in lines:
            i = g.skip_ws(s, 0)
            if g.match(s, i, d1b):
                result.append(s[:i] + s[i + n1b :])
                changed = True
            elif g.match(s, i, d1):
                result.append(s[:i] + s[i + n1 :])
                changed = True
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
                if g.match(s, first, ' '):
                    first += 1
                last = j
                if g.match(s, last - 1, ' '):
                    last -= 1
                result.append(s[:i] + s[first:last] + s[j + n3 :])
                changed = True
            else:
                result.append(s)
    if not changed:
        return
    #
    # Set p.b and w's text first.
    middle = ''.join(result)
    p.b = head + middle + tail  # Sets dirty and changed bits.
    w.setAllText(head + middle + tail)
    #
    # Set the selection range and scroll position.
    i = len(head)
    j = ins = max(i, len(head) + len(middle) - 1)
    w.setSelectionRange(i, j, insert=ins)
    w.setYScrollPosition(oldYview)
    #
    # "after" snapshot.
    u.afterChangeBody(p, 'Indent Region', bunch)
#@+node:ekr.20171123135625.54: ** c_ec.editHeadline (edit-headline)
@g.commander_command('edit-headline')
def editHeadline(self: Self, event: Event = None) -> tuple[Any, Any]:
    """
    Begin editing the headline of the selected node.

    This is just a wrapper around tree.editLabel.
    """
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
    return e, wrapper  # Neither of these is used by any caller.
#@+node:ekr.20171123135625.23: ** c_ec.extract & helpers
@g.commander_command('extract')
def extract(self: Self, event: Event = None) -> None:
    #@+<< docstring for extract command >>
    #@+node:ekr.20201113130021.1: *3* << docstring for extract command >>
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
    #@-<< docstring for extract command >>
    c, u, w = self, self.undoer, self.frame.body.wrapper
    undoType = 'Extract'
    # Set data.
    head, lines, tail, oldSel, oldYview = c.getBodyLines()
    if not lines:
        return  # Nothing selected.
    #
    # Remove leading whitespace.
    junk, ws = g.skip_leading_ws_with_indent(lines[0], 0, c.tab_width)
    lines = [g.removeLeadingWhitespace(s, ws, c.tab_width) for s in lines]
    h = lines[0].strip()
    ref_h = extractRef(c, h).strip()
    def_h = extractDef_find(c, lines)
    if ref_h:
        h, b, middle = ref_h, lines[1:], ' ' * ws + lines[0]  # By vitalije.
    elif def_h:
        h, b, middle = def_h, lines, ''
    else:
        h, b, middle = lines[0].strip(), lines[1:], ''
    #
    # Start the outer undo group.
    u.beforeChangeGroup(c.p, undoType)
    undoData = u.beforeInsertNode(c.p)
    p = createLastChildNode(c, c.p, h, ''.join(b))
    u.afterInsertNode(p, undoType, undoData)
    #
    # Start inner undo.
    if oldSel:
        i, j = oldSel
        w.setSelectionRange(i, j, insert=j)
    bunch = u.beforeChangeBody(c.p)  # Not p.
    #
    # Update the text and selection
    c.p.v.b = head + middle + tail  # Don't redraw.
    w.setAllText(head + middle + tail)
    i = len(head)
    j = max(i, len(head) + len(middle) - 1)
    w.setSelectionRange(i, j, insert=j)
    #
    # End the inner undo.
    u.afterChangeBody(c.p, undoType, bunch)
    #
    # Scroll as necessary.
    if oldYview:
        w.setYScrollPosition(oldYview)
    else:
        w.seeInsertPoint()
    #
    # Add the changes to the outer undo group.
    u.afterChangeGroup(c.p, undoType=undoType)
    p.parent().expand()
    c.redraw(p.parent())  # A bit more convenient than p.
    c.bodyWantsFocus()

# Compatibility

g.command_alias('extractSection', extract)
g.command_alias('extractPythonMethod', extract)
#@+node:ekr.20171123135625.20: *3* def createLastChildNode
def createLastChildNode(c: Cmdr, parent: Position, headline: str, body: str) -> Position:
    """A helper function for the three extract commands."""
    # #1955: don't strip trailing lines.
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

def extractDef(c: Cmdr, s: str) -> str:
    """
    Return the defined function/method/class name if s
    looks like definition. Tries several different languages.
    """
    for pat in c.config.getData('extract-patterns') or []:
        try:
            pat = re.compile(pat)
            m = pat.search(s)
            if m:
                return m.group(1)
        except Exception:
            g.es_print('bad regex in @data extract-patterns', color='blue')
            g.es_print(pat)
    for pat in extractDef_patterns:
        m = pat.search(s)
        if m:
            return m.group(1)
    return ''
#@+node:ekr.20171123135625.26: *3* def extractDef_find
def extractDef_find(c: Cmdr, lines: list[str]) -> Optional[str]:
    for line in lines:
        def_h = extractDef(c, line.strip())
        if def_h:
            return def_h
    return None
#@+node:ekr.20171123135625.25: *3* def extractRef
def extractRef(c: Cmdr, s: str) -> str:
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
def extractSectionNames(self: Self, event: Event = None) -> None:
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
    found = False
    for s in lines:
        name = findSectionName(c, s)
        if name:
            if not found:
                u.beforeChangeGroup(current, undoType)  # first one!
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
def findSectionName(self: Self, s: str) -> Optional[str]:
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
def findMatchingBracket(self: Self, event: Event = None) -> None:
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
#@+node:ekr.20110402084740.14490: ** c_ec.goToNext/PrevHistory
@g.commander_command('goto-next-history-node')
def goToNextHistory(self: Self, event: Event = None) -> None:
    """Go to the next node in the history list."""
    c = self
    c.nodeHistory.goNext()

@g.commander_command('goto-prev-history-node')
def goToPrevHistory(self: Self, event: Event = None) -> None:
    """Go to the previous node in the history list."""
    c = self
    c.nodeHistory.goPrev()
#@+node:ekr.20171123135625.30: ** c_ec.alwaysIndentBody (always-indent-region)
@g.commander_command('always-indent-region')
def alwaysIndentBody(self: Self, event: Event = None) -> None:
    """
    The always-indent-region command indents each line of the selected body
    text. The @tabwidth directive in effect determines amount of
    indentation.
    """
    c, p, u, w = self, self.p, self.undoer, self.frame.body.wrapper
    #
    # #1801: Don't rely on bindings to ensure that we are editing the body.
    event_w = event and event.w
    if event_w != w:
        c.insertCharFromEvent(event)
        return
    #
    # "Before" snapshot.
    bunch = u.beforeChangeBody(p)
    #
    # Initial data.
    sel_1, sel_2 = w.getSelectionRange()
    tab_width = c.getTabWidth(p)
    head, lines, tail, oldSel, oldYview = self.getBodyLines()
    #
    # Calculate the result.
    changed, result = False, []
    for line in lines:
        if line.strip():
            i, width = g.skip_leading_ws_with_indent(line, 0, tab_width)
            s = g.computeLeadingWhitespace(width + abs(tab_width), tab_width) + line[i:]
            result.append(s)
            if s != line:
                changed = True
        else:
            result.append('\n')  # #2418
    if not changed:
        return
    #
    # Set p.b and w's text first.
    middle = ''.join(result)
    all = head + middle + tail
    p.b = all  # Sets dirty and changed bits.
    w.setAllText(all)
    #
    # Calculate the proper selection range (i, j, ins).
    if sel_1 == sel_2:
        line = result[0]
        i, width = g.skip_leading_ws_with_indent(line, 0, tab_width)
        i = j = len(head) + i
    else:
        i = len(head)
        j = len(head) + len(middle)
        if middle.endswith('\n'):  # #1742.
            j -= 1
    #
    # Set the selection range and scroll position.
    w.setSelectionRange(i, j, insert=j)
    w.setYScrollPosition(oldYview)
    #
    # "after" snapshot.
    u.afterChangeBody(p, 'Indent Region', bunch)
#@+node:ekr.20210104123442.1: ** c_ec.indentBody (indent-region)
@g.commander_command('indent-region')
def indentBody(self: Self, event: Event = None) -> None:
    """
    The indent-region command indents each line of the selected body text.
    Unlike the always-indent-region command, this command inserts a tab
    (soft or hard) when there is no selected text.

    The @tabwidth directive in effect determines amount of indentation.
    """
    c, event_w, w = self, event and event.w, self.frame.body.wrapper
    # #1801: Don't rely on bindings to ensure that we are editing the body.
    if event_w != w:
        c.insertCharFromEvent(event)
        return
    # # 1739. Special case for a *plain* tab bound to indent-region.
    sel_1, sel_2 = w.getSelectionRange()
    if sel_1 == sel_2:
        char = getattr(event, 'char', None)
        stroke = getattr(event, 'stroke', None)
        if char == '\t' and stroke and stroke.isPlainKey():
            c.editCommands.selfInsertCommand(event)  # Handles undo.
            return
    c.alwaysIndentBody(event)
#@+node:ekr.20171123135625.38: ** c_ec.insertBodyTime
@g.commander_command('insert-body-time')
def insertBodyTime(self: Self, event: Event = None) -> None:
    """Insert a time/date stamp at the cursor."""
    c, p, u = self, self.p, self.undoer
    w = c.frame.body.wrapper
    undoType = 'Insert Body Time'
    if g.app.batchMode:
        c.notValidInBatchMode(undoType)
        return
    bunch = u.beforeChangeBody(p)
    w.deleteTextSelection()
    s = self.getTime(body=True)
    i = w.getInsertPoint()
    w.insert(i, s)
    p.v.b = w.getAllText()
    u.afterChangeBody(p, undoType, bunch)
#@+node:ekr.20171123135625.52: ** c_ec.justify-toggle-auto
@g.commander_command("justify-toggle-auto")
def justify_toggle_auto(self: Self, event: Event = None) -> None:
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
def line_to_headline(self: Self, event: Event = None) -> None:
    """
    Create child node from the selected line.

    Cut the selected line and make it the new node's headline
    """
    c, p, u, w = self, self.p, self.undoer, self.frame.body.wrapper
    undoType = 'line-to-headline'
    ins, s = w.getInsertPoint(), p.b
    i = g.find_line_start(s, ins)
    j = g.skip_line(s, i)
    line = s[i:j].strip()
    if not line:
        return
    u.beforeChangeGroup(p, undoType)
    #
    # Start outer undo.
    undoData = u.beforeInsertNode(p)
    p2 = p.insertAsLastChild()
    p2.h = line
    u.afterInsertNode(p2, undoType, undoData)
    #
    # "before" snapshot.
    bunch = u.beforeChangeBody(p)
    p.b = s[:i] + s[j:]
    w.setInsertPoint(i)
    p2.setDirty()
    c.setChanged()
    #
    # "after" snapshot.
    u.afterChangeBody(p, undoType, bunch)
    #
    # Finish outer undo.
    u.afterChangeGroup(p, undoType=undoType)
    p.expand()
    c.redraw(p)
    c.bodyWantsFocus()
#@+node:ekr.20171123135625.11: ** c_ec.preferences
@g.commander_command('settings')
def preferences(self: Self, event: Event = None) -> None:
    """Handle the preferences command."""
    c = self
    c.openLeoSettings()
#@+node:ekr.20171123135625.40: ** c_ec.reformatBody
@g.commander_command('reformat-body')
def reformatBody(self: Self, event: Event = None) -> None:
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
def reformatParagraph(self: Self, event: Event = None, undoType: str = 'Reformat Paragraph') -> None:
    """
    Reformat a text paragraph

    Wraps the concatenated text to present page width setting. Leading tabs are
    sized to present tab width setting. First and second line of original text is
    used to determine leading whitespace in reformatted text. Hanging indentation
    is honored.

    Paragraph is bound by start of body, end of body and blank lines. Paragraph is
    selected by position of current insertion cursor.
    """
    c, w = self, self.frame.body.wrapper
    if g.app.batchMode:
        c.notValidInBatchMode("reformat-paragraph")
        return
    # Set the insertion point for find_bound_paragraph.
    if w.hasSelection():
        i, j = w.getSelectionRange()
        w.setInsertPoint(i)
    head, lines, tail = find_bound_paragraph(c)
    if not lines:
        return
    oldSel, oldYview, original, pageWidth, tabWidth = rp_get_args(c)
    indents, leading_ws = rp_get_leading_ws(c, lines, tabWidth)
    result = rp_wrap_all_lines(c, indents, leading_ws, lines, pageWidth)
    rp_reformat(c, head, oldSel, oldYview, original, result, tail, undoType)
#@+node:ekr.20171123135625.43: *3* function: ends_paragraph & single_line_paragraph
def ends_paragraph(s: str) -> bool:
    """Return True if s is a blank line."""
    return not s.strip()

def single_line_paragraph(s: str) -> bool:
    """Return True if s is a single-line paragraph."""
    return s.startswith('@') or s.strip() in ('"""', "'''")
#@+node:ekr.20171123135625.42: *3* function: find_bound_paragraph
def find_bound_paragraph(c: Cmdr) -> tuple[str, list[str], str]:
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
        for s in reversed(head_lines):
            if ends_paragraph(s) or single_line_paragraph(s):
                break
            elif startsParagraph(s):
                n += 1
                break
            else:
                n += 1
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
        head = ''.join(head_lines)
        tail_lines = para_lines[i:] if ended else []
        tail = ''.join(tail_lines)
        return head, result, tail  # string, list, string
    return None, None, None
#@+node:ekr.20171123135625.45: *3* function: rp_get_args
def rp_get_args(c: Cmdr) -> tuple[int, int, str, int, int]:
    """Compute and return oldSel,oldYview,original,pageWidth,tabWidth."""
    body = c.frame.body
    w = body.wrapper
    d = c.scanAllDirectives(c.p)
    if c.editCommands.fillColumn > 0:
        pageWidth = c.editCommands.fillColumn
    else:
        pageWidth = d.get("pagewidth")
    tabWidth = d.get("tabwidth")
    original = w.getAllText()
    oldSel = w.getSelectionRange()
    oldYview = w.getYScrollPosition()
    return oldSel, oldYview, original, pageWidth, tabWidth
#@+node:ekr.20171123135625.46: *3* function: rp_get_leading_ws
def rp_get_leading_ws(c: Cmdr, lines: Any, tabWidth: Any) -> tuple[list[int], list[str]]:
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
#@+node:ekr.20171123135625.47: *3* function: rp_reformat
def rp_reformat(
    c: Cmdr,
    head: str,
    oldSel: Any,
    oldYview: Any,
    original: Any,
    result: str,
    tail: str,
    undoType: str,
) -> None:
    """Reformat the body and update the selection."""
    p, u, w = c.p, c.undoer, c.frame.body.wrapper
    s = head + result + tail
    changed = original != s
    bunch = u.beforeChangeBody(p)
    if changed:
        w.setAllText(s)  # Destroys coloring.
    #
    # #1748: Always advance to the next paragraph.
    i = len(head)
    j = max(i, len(head) + len(result) - 1)
    ins = j + 1
    while ins < len(s):
        i, j = g.getLine(s, ins)
        line = s[i:j]
        # It's annoying, imo, to treat @ lines differently.
        if line.isspace():
            ins = j + 1
        else:
            ins = i
            break
    ins = min(ins, len(s))
    w.setSelectionRange(ins, ins, insert=ins)
    #
    # Show more lines, if they exist.
    k = g.see_more_lines(s, ins, 4)
    p.v.insertSpot = ins
    w.see(k)  # New in 6.4. w.see works!
    if not changed:
        return
    #
    # Finish.
    p.v.b = s  # p.b would cause a redraw.
    u.afterChangeBody(p, undoType, bunch)
    w.setXScrollPosition(0)  # Never scroll horizontally.
#@+node:ekr.20171123135625.48: *3* function: rp_wrap_all_lines
def rp_wrap_all_lines(
    c: Cmdr,
    indents: Any,
    leading_ws: Any,
    lines: list[str],
    pageWidth: int,
) -> str:
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
    result_list = g.wrap_lines(lines,
        pageWidth - indents[1],
        pageWidth - indents[0])
    # prefix with the leading whitespace, if any
    paddedResult = []
    paddedResult.append(leading_ws[0] + result_list[0])
    for line in result_list[1:]:
        paddedResult.append(leading_ws[1] + line)
    # Convert the result to a string.
    result = '\n'.join(paddedResult)
    if trailingNL:
        result = result + '\n'
    return result
#@+node:ekr.20171123135625.44: *3* function: startsParagraph
def startsParagraph(s: str) -> bool:
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
            (len(s) < 2 or s[2] in ' \t\n'))
    else:
        val = s.startswith('@') or s.startswith('-')
    return val
#@+node:ekr.20201124191844.1: ** c_ec.reformatSelection
@g.commander_command('reformat-selection')
def reformatSelection(self: Self, event: Event = None, undoType: str = 'Reformat Paragraph') -> None:
    """
    Reformat the selected text, as in reformat-paragraph, but without
    expanding the selection past the selected lines.
    """
    c, undoType = self, 'reformat-selection'
    p, u, w = c.p, c.undoer, c.frame.body.wrapper
    if g.app.batchMode:
        c.notValidInBatchMode(undoType)
        return
    bunch = u.beforeChangeBody(p)
    oldSel, oldYview, original, pageWidth, tabWidth = rp_get_args(c)
    head, middle, tail = c.frame.body.getSelectionLines()
    lines = g.splitLines(middle)
    if not lines:
        return
    indents, leading_ws = rp_get_leading_ws(c, lines, tabWidth)
    result = rp_wrap_all_lines(c, indents, leading_ws, lines, pageWidth)
    s = head + result + tail
    if s == original:
        return
    #
    # Update the text and the selection.
    w.setAllText(s)  # Destroys coloring.
    i = len(head)
    j = max(i, len(head) + len(result) - 1)
    j = min(j, len(s))
    w.setSelectionRange(i, j, insert=j)
    #
    # Finish.
    p.v.b = s  # p.b would cause a redraw.
    u.afterChangeBody(p, undoType, bunch)
    w.setXScrollPosition(0)  # Never scroll horizontally.
#@+node:ekr.20171123135625.12: ** c_ec.show/hide/toggleInvisibles
@g.commander_command('hide-invisibles')
def hideInvisibles(self: Self, event: Event = None) -> None:
    """Hide invisible (whitespace) characters."""
    c = self
    showInvisiblesHelper(c, False)

@g.commander_command('show-invisibles')
def showInvisibles(self: Self, event: Event = None) -> None:
    """Show invisible (whitespace) characters."""
    c = self
    showInvisiblesHelper(c, True)

@g.commander_command('toggle-invisibles')
def toggleShowInvisibles(self: Self, event: Event = None) -> None:
    """Toggle showing of invisible (whitespace) characters."""
    c = self
    colorizer = c.frame.body.getColorizer()
    showInvisiblesHelper(c, not colorizer.showInvisibles)

def showInvisiblesHelper(c: Cmdr, val: Any) -> None:
    frame = c.frame
    colorizer = frame.body.getColorizer()
    colorizer.showInvisibles = val
    colorizer.highlighter.showInvisibles = val
    # It is much easier to change the menu name here than in the menu updater.
    menu = frame.menu.getMenu("Edit")
    index = frame.menu.getMenuLabel(menu, 'Hide Invisibles' if val else 'Show Invisibles')
    if index is None:
        if val:
            frame.menu.setMenuLabel(menu, "Show Invisibles", "Hide Invisibles")
        else:
            frame.menu.setMenuLabel(menu, "Hide Invisibles", "Show Invisibles")
    # #240: Set the status bits here.
    if hasattr(frame.body, 'set_invisibles'):
        frame.body.set_invisibles(c)
    c.frame.body.recolor(c.p)
#@+node:ekr.20171123135625.55: ** c_ec.toggleAngleBrackets
@g.commander_command('toggle-angle-brackets')
def toggleAngleBrackets(self: Self, event: Event = None) -> None:
    """Add or remove double angle brackets from the headline of the selected node."""
    c, p = self, self.p
    if g.app.batchMode:
        c.notValidInBatchMode("Toggle Angle Brackets")
        return
    c.endEditing()
    s = p.h.strip()
    # 2019/09/12: Guard against black.
    lt = "<<"
    rt = ">>"
    if s[0:2] == lt or s[-2:] == rt:
        if s[0:2] == "<<":
            s = s[2:]
        if s[-2:] == ">>":
            s = s[:-2]
        s = s.strip()
    else:
        s = g.angleBrackets(' ' + s + ' ')
    p.setHeadString(s)
    p.setDirty()  # #1449.
    c.setChanged()  # #1449.
    c.redrawAndEdit(p, selectAll=True)
#@+node:ekr.20171123135625.49: ** c_ec.unformatParagraph & helper
@g.commander_command('unformat-paragraph')
def unformatParagraph(self: Self, event: Event = None, undoType: str = 'Unformat Paragraph') -> None:
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
#@+node:ekr.20171123135625.50: *3* function: unreformat
def unreformat(
    c: Cmdr,
    head: str,
    oldSel: Any,
    oldYview: Any,
    original: str,
    result: str,
    tail: str,
    undoType: str,
) -> None:
    """unformat the body and update the selection."""
    p, u, w = c.p, c.undoer, c.frame.body.wrapper
    s = head + result + tail
    ins = max(len(head), len(head) + len(result) - 1)
    bunch = u.beforeChangeBody(p)
    w.setAllText(s)  # Destroys coloring.
    changed = original != s
    if changed:
        p.v.b = w.getAllText()
        u.afterChangeBody(p, undoType, bunch)
    # Advance to the next paragraph.
    ins += 1  # Move past the selection.
    while ins < len(s):
        i, j = g.getLine(s, ins)
        line = s[i:j]
        if line.isspace():
            ins = j + 1
        else:
            ins = i
            break
    c.recolor()  # Required.
    w.setSelectionRange(ins, ins, insert=ins)
    # More useful than for reformat-paragraph.
    w.see(ins)
    # Make sure we never scroll horizontally.
    w.setXScrollPosition(0)
#@+node:ekr.20180410054716.1: ** c_ec: insert-jupyter-toc & insert-markdown-toc
@g.commander_command('insert-jupyter-toc')
def insertJupyterTOC(self: Self, event: Event = None) -> None:
    """
    Insert a Jupyter table of contents at the cursor,
    replacing any selected text.
    """
    insert_toc(c=self, kind='jupyter')

@g.commander_command('insert-markdown-toc')
def insertMarkdownTOC(self: Self, event: Event = None) -> None:
    """
    Insert a Markdown table of contents at the cursor,
    replacing any selected text.
    """
    insert_toc(c=self, kind='markdown')
#@+node:ekr.20180410074238.1: *3* insert_toc
def insert_toc(c: Cmdr, kind: str) -> None:
    """Insert a table of contents at the cursor."""
    p, u = c.p, c.undoer
    w = c.frame.body.wrapper
    undoType = f"Insert {kind.capitalize()} TOC"
    if g.app.batchMode:
        c.notValidInBatchMode(undoType)
        return
    bunch = u.beforeChangeBody(p)
    w.deleteTextSelection()
    s = make_toc(c, kind=kind, root=c.p)
    i = w.getInsertPoint()
    w.insert(i, s)
    p.v.b = w.getAllText()
    u.afterChangeBody(p, undoType, bunch)
#@+node:ekr.20180410054926.1: *3* make_toc
def make_toc(c: Cmdr, kind: str, root: Position) -> str:
    """Return the toc for root.b as a list of lines."""

    def cell_type(p: Position) -> str:
        language = g.getLanguageAtPosition(c, p)
        return 'markdown' if language in ('jupyter', 'markdown') else 'python'

    def clean_headline(s: str) -> str:
        # Surprisingly tricky. This could remove too much, but better to be safe.
        aList = [ch for ch in s if ch in '-: ' or ch.isalnum()]
        return ''.join(aList).rstrip('-').strip()

    result: list[str] = []
    stack: list[int] = []
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
