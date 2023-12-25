#@+leo-ver=5-thin
#@+node:ekr.20150514040138.1: * @file ../commands/helpCommands.py
"""Leo's help commands."""
#@+<< helpCommands imports & annotations >>
#@+node:ekr.20150514050337.1: ** << helpCommands imports & annotations >>
from __future__ import annotations
from collections.abc import Callable
import io
import re
import sys
import textwrap
from typing import TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.commands.baseCommands import BaseEditCommandsClass

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoGui import LeoKeyEvent as Event
#@-<< helpCommands imports & annotations >>

def cmd(name: str) -> Callable:
    """Command decorator for the helpCommands class."""
    return g.new_cmd_decorator(name, ['c', 'helpCommands',])

#@+others
#@+node:ekr.20160514121110.1: ** class HelpCommandsClass
class HelpCommandsClass(BaseEditCommandsClass):
    """A class containing Leo's help-for commands."""
    #@+others
    #@+node:ekr.20150514063305.373: *3* help
    @cmd('help')
    def help_command(self, event: Event = None) -> None:
        """Prints an introduction to Leo's help system."""
        #@+<< define rst_s >>
        #@+node:ekr.20150514063305.374: *4* << define rst_s >> (F1)
        #@@language rest

        rst_s = '''

        **Welcome to Leo's help system.**

        Alt-0 (vr-toggle) hides this help message.

        To learn about ``<Alt-X>`` commands, type::

            <Alt-X>help-for-minibuffer<Enter>

        To get a list of help topics, type::

            <Alt-X>help-<tab>

        For Leo commands (tab completion allowed), type::

            <Alt-X>help-for-command<Enter>
            <a Leo command name><Enter>

        To use Python's help system, type::

            <Alt-X>help-for-python<Enter>
            <a python symbol><Enter>

        For the command bound to a key, type::

            <Alt-X>help-for-keystroke<Enter><any key>

        '''
        #@-<< define rst_s >>
        self.c.putHelpFor(rst_s)
    #@+node:ekr.20150514063305.375: *3* helpForAbbreviations
    @cmd('help-for-abbreviations')
    def helpForAbbreviations(self, event: Event = None) -> None:
        """Prints a discussion of abbreviations."""
        #@+<< define s >>
        #@+node:ekr.20150514063305.376: *4* << define s >> (helpForAbbreviations)
        #@@language rest

        s = r'''\

        About Abbreviations
        -------------------

        Alt-0 (vr-toggle) hides this help message.

        Leo optionally expands abbreviations as you type.

        Abbreviations typically end with something like ";;" so they won't trigger
        by accident.

        You define abbreviations in @data abbreviations nodes or @data
        global-abbreviations nodes. None come predefined, but leoSettings.leo
        contains example abbreviations in the node::

            @@data abbreviations examples

        Abbreviations can simply be shortcuts::

            ncn;;=@nocolor

        Abbreviations can span multiple lines. Continued lines start with \\:, like
        this::

            form;;=<form action="main_submit" method="get" accept-charset="utf-8">
            \:<p><input type="submit" value="Continue &rarr;"></p>
            \:</form>\n

        Abbreviations can define templates in which <\|a-field-name\|> denotes a field
        to be filled in::

            input;;=<input type="text/submit/hidden/button"
            \:name="<|name|>"
            \:value="" id="<|id|>">\n

        Typing ",," after inserting a template selects the next field.

        Abbreviations can execute **abbreviation scripts**, delimited by {\|{ and
        }\|}::

            date;;={|{import time ; x=time.asctime()}|}
            ts;;={|{import time ; x=time.strftime("%Y%m%d%H%M%S")}|}

        For example, typing ts;; gives::

            20131009171117

        It's even possible to define a context in which abbreviation scripts execute.

        See leoSettings.leo for full details.

        '''
        #@-<< define s >>
        self.c.putHelpFor(s)
    #@+node:ekr.20150514063305.377: *3* helpForAutocompletion
    @cmd('help-for-autocompletion')
    def helpForAutocompletion(self, event: Event = None) -> None:
        """Prints a discussion of autocompletion."""
        #@+<< define s >>
        #@+node:ekr.20150514063305.378: *4* << define s >> (helpForAutocompletion)
        #@verbatim
        # @pagewidth 40
        #@@language rest

        s = '''

        About Autocompletion and Calltips
        ---------------------------------

        Alt-0 (vr-toggle) hides this help message.

        This documentation describes both
        autocompletion and calltips.

        Typing a period when @language python is
        in effect starts autocompletion. Typing
        '(' during autocompletion shows the
        calltip. Typing Return or Control-g
        (keyboard-quit) exits autocompletion or
        calltips.

        Autocompletion
        ==============

        Autocompletion shows what may follow a
        period in code. For example, after
        typing g. Leo will show a list of all
        the global functions in leoGlobals.py.
        Autocompletion works much like tab
        completion in the minibuffer. Unlike the
        minibuffer, the presently selected
        completion appears directly in the body
        pane.

        A leading period brings up 'Autocomplete
        Modules'. (The period goes away.) You
        can also get any module by typing its
        name. If more than 25 items would appear
        in the Autocompleter tab, Leo shows only
        the valid starting characters. At this
        point, typing an exclamation mark shows
        the complete list. Thereafter, typing
        further exclamation marks toggles
        between full and abbreviated modes.

        If x is a list 'x.!' shows all its
        elements, and if x is a Python
        dictionary, 'x.!' shows list(x.keys()).
        For example, 'sys.modules.!' Again,
        further exclamation marks toggles
        between full and abbreviated modes.

        During autocompletion, typing a question
        mark shows the docstring for the object.
        For example: 'g.app?' shows the
        docstring for g.app. This doesn't work
        (yet) directly for Python globals, but
        '__builtin__.f?' does. Example:
        '__builtin__.pow?' shows the docstring
        for pow.

        Autocompletion works in the Find tab;
        you can use <Tab> to cycle through the
        choices. The 'Completion' tab appears
        while you are doing this; the Find tab
        reappears once the completion is
        finished.

        Calltips
        ========

        Calltips appear after you type an open
        parenthesis in code. Calltips shows the
        expected arguments to a function or
        method. Calltips work for any Python
        function or method, including Python's
        global function. Examples:

        a) g.toUnicode(
           gives:
           g.toUnicode(s,encoding, reportErrors=False

        b) c.widgetWantsFocusNow
           gives:
           c.widgetWantsFocusNow(w

        c) reduce(
           gives:
           reduce(function, sequence[,initial]) -> value

        The calltips appear directly in the text
        and the argument list is highlighted so
        you can just type to replace it. The
        calltips appear also in the status line
        for reference after you have started to
        replace the args.

        Options
        =======

        Both autocompletion and calltips are
        initially enabled or disabled by the
        enable_autocompleter_initially and
        enable_calltips_initially settings in
        leoSettings.leo. You may enable or
        disable these features at any time with
        these commands: enable-autocompleter,
        enable-calltips, disable-autocompleter
        and disable-calltips. '''
        #@-<< define s >>
        self.c.putHelpFor(s)
    #@+node:ekr.20150514063305.379: *3* helpForBindings
    @cmd('help-for-bindings')
    def helpForBindings(self, event: Event = None) -> None:
        """Prints a discussion of keyboard bindings."""
        #@+<< define s >>
        #@+node:ekr.20150514063305.380: *4* << define s >> (helpForBindings)
        #@verbatim
        # @pagewidth 40
        #@@language rest

        s = '''

        About Key Bindings
        ------------------

        Alt-0 (vr-toggle) hides this help message.

        A shortcut specification has the form:

        command-name = shortcutSpecifier

        or

        command-name ! pane = shortcutSpecifier

        The first form creates a binding for all
        panes except the minibuffer. The second
        form creates a binding for one or more
        panes. The possible values for 'pane'
        are:

        ====    ===============
        pane    bound panes
        ====    ===============
        all     body,log,tree
        body    body
        log     log
        mini    minibuffer
        text    body,log
        tree    tree
        ====    ===============

        You may use None as the specifier.
        Otherwise, a shortcut specifier consists
        of a head followed by a tail. The head
        may be empty, or may be a concatenation
        of the following: (All entries in each
        row are equivalent)::

            Shift+ Shift-
            Alt+ or Alt-
            Control+, Control-, Ctrl+ or Ctrl-

        Notes:

        1. The case of plain letters is significant:
           a is not A.

        2. The Shift- (or Shift+) prefix can be
           applied *only* to letters or
           multi-letter tails. Leo will ignore
           (with a warning) the shift prefix
           applied to other single letters,
           e.g., Ctrl-Shift-(

        3. The case of letters prefixed by
           Ctrl-, Alt-, Key- or Shift- is *not*
           significant.

        The following table illustrates these
        rules. In each row, the first entry is
        the key (for k.bindingsDict) and the
        other entries are equivalents that the
        user may specify in leoSettings.leo::

            a, Key-a, Key-A
            A, Shift-A
            Alt-a, Alt-A
            Alt-A, Alt-Shift-a, Alt-Shift-A
            Ctrl-a, Ctrl-A
            Ctrl-A, Ctrl-Shift-a, Ctrl-Shift-A
            !, Key-!,Key-exclam,exclam

        '''
        #@-<< define s >>
        self.c.putHelpFor(s)
    #@+node:ekr.20150514063305.381: *3* helpForCommand & helpers
    @cmd('help-for-command')
    def helpForCommand(self, event: Event) -> None:
        """Prompts for a command name and prints the help message for that command."""
        c, k = self.c, self.c.k
        s = '''\
    Alt-0 (vr-toggle) hides this help message.

    Type the name of the command, followed by Return.
    '''
        c.putHelpFor(s)
        c.minibufferWantsFocusNow()
        k.fullCommand(event, help=True, helpHandler=self.helpForCommandFinisher)
    #@+node:ekr.20150514063305.382: *4* getBindingsForCommand
    def getBindingsForCommand(self, commandName: str) -> str:
        k = self.c.k
        data = []
        n1, n2 = 4, 20
        d = k.bindingsDict
        for stroke in sorted(d):
            assert g.isStroke(stroke), repr(stroke)
            aList = d.get(stroke, [])
            for bi in aList:
                if bi.commandName == commandName:
                    pane = '' if bi.pane == 'all' else f" {bi.pane}:"
                    s1 = pane
                    s2 = k.prettyPrintKey(stroke)
                    s3 = bi.commandName
                    n1 = max(n1, len(s1))
                    n2 = max(n2, len(s2))
                    data.append((s1, s2, s3),)
        data.sort(key=lambda x: x[1])
        return ','.join([f"{z1} {z2}" for z1, z2, z3 in data]).strip()
    #@+node:ekr.20150514063305.383: *4* helpForCommandFinisher
    def helpForCommandFinisher(self, commandName: str) -> None:
        c, s = self.c, None
        if commandName and commandName.startswith('help-for-'):
            # Execute the command itself.
            c.doCommandByName(commandName)
        else:
            if commandName:
                bindings = self.getBindingsForCommand(commandName)
                func = c.commandsDict.get(commandName)
                s = g.getDocStringForFunction(func)
                if s:
                    s = self.replaceBindingPatterns(s)
                else:
                    s = 'no docstring available'
                # Create the title.
                s2 = f"{commandName} ({bindings})" if bindings else commandName
                underline = '+' * len(s2)
                title = f"{s2}\n{underline}\n\n"
                if 1:  # 2015/03/24
                    s = title + textwrap.dedent(s)
                else:
                    # Fixes bug 618570:
                    s = title + ''.join([
                        line.lstrip() if line.strip() else '\n'
                            for line in g.splitLines(s)])
            else:
                #@+<< set s to about help-for-command >>
                #@+node:ekr.20150514063305.384: *5* << set s to about help-for-command >>
                s = '''\

                ++++++++++++++++++++++++
                About Leo's help command
                ++++++++++++++++++++++++

                Invoke Leo's help-for-command as follows::

                    <F1>
                    <Alt-X>help-for-command<return>

                Next, type the name of one of Leo's commands.
                You can use tab completion.  Examples::

                    <F1><tab>           shows all commands.
                    <F1>help-for<tab>   shows all help-for- commands.

                Here are the help-for commands::

                    help-for-abbreviations
                    help-for-autocompletion
                    help-for-bindings
                    help-for-command
                    help-for-debugging-commands
                    help-for-dynamic-abbreviations
                    help-for-find-commands
                    help-for-minibuffer
                    help-for-python
                    help-for-regular-expressions

                '''
                #@-<< set s to about help-for-command >>
            c.putHelpFor(s)
    #@+node:ekr.20150514063305.385: *4* replaceBindingPatterns
    def replaceBindingPatterns(self, s: str) -> str:
        """
        For each instance of the pattern !<command-name>! in s,
        replace the pattern by the key binding for command-name.
        """
        c = self.c
        pattern = re.compile(r'!<(.*)>!')
        while True:
            m = pattern.search(s, 0)
            if m is None:
                break
            name = m.group(1)
            junk, aList = c.config.getShortcut(name)
            for bi in aList:
                if bi.pane == 'all':
                    key = c.k.prettyPrintKey(bi.stroke.s)
                    break
            else:
                key = f"<Alt-X>{name}<Return>"
            s = s[: m.start()] + key + s[m.end() :]
        return s
    #@+node:ekr.20150514063305.386: *3* helpForCreatingExternalFiles
    @cmd('help-for-creating-external-files')
    def helpForCreatingExternalFiles(self, event: Event = None) -> None:
        """Prints a discussion of creating external files."""
        #@+<< define s >>
        #@+node:ekr.20150514063305.387: *4* << define s >> (helpForCreatingExternalFiles)
        #@@language rest

        s = r'''

        Creating External Files
        -------------------------

        This help discusses only @file nodes.
        For other ways of creating external files, see::

            https://leo-editor.github.io/leo-editor/tutorial-scripting.html or
            https://leo-editor.github.io/leo-editor/directives.html

        Leo creates external files in an unusual way.
        Please fee free to ask for help::

            https://groups.google.com/forum/#!forum/leo-editor or
            http://webchat.freenode.net/?channels=%23leo&uio=d4

        Overview
        ========

        Leo creates **external files** (files on your file system) from
        **@file nodes** and *all the descendants* of the @file node.
        Examples::

            @file spam.py
            @file ../foo.c
            @file ~/bar.py

        A single Leo outline may contain many @file nodes. As a result, Leo
        outlines function much like project files in other IDE's (Integrated
        development environments).

        Within an @file tree, simple text markup (discussed next) tells Leo how
        to create the external file from the @file node and its descendants.

        Markup
        ======

        Section references and the \\@all and \\@others directives tell
        Leo how to create external files.

        - A **section name** is any text of the form::

            <\\< any text >\\> (>> must not appear in "any text".)

        - A **section definition node** is any node whose headline starts with a section name.

        - A **section reference** is a section name that appears in body text.

        Leo creates external files containing \\@others directives by writing the
        *expansion* of the @file node. The **expansion** of *any* node is the
        node's body text after making these text **substitutions**:

        - Leo replaces \\@all by the *unexpanded* body text of *all* nodes.

        - Leo replaces \\@others with the *expansion* of all descendant nodes
          **except** section definition nodes. That's how \\@others got its name.

        - Leo replaces section references by the *expansion* of the body text of
          the corresponding section definition node.

        Whitespace is significant before \\@others and section references. Leo adds
        the leading whitespace appearing before each \\@others directive or section
        reference to every line of their expansion. As a result, Leo can generate
        external files even for Python.  The following cute trick works::

            if 1:
                <\\< a section >\\>
            if 0:
                \\@others

        **Notes**:

        - Any node may contain a single \\@others directive. No node may contain more
          than one \@others directive.

        - Nodes that *aren't* section definition nodes are included in the expansion
          of the *nearest* ancestor node containing an @others directive.

        **Example 1**: The body of the @file node for a typical Python module will
        look something like::

            '\\''A docstring.'\\''
            <\\< imports >\\>
            \@others
            if __name__ == '__main__':
                main()

        **Example 2**:  Here is a typical Python class definition in Leo::

            class MyClass:
                '\\''A docstring.'\\''
                \@others

        \@first and @last
        =================

        The @first directive forces lines to appear before the first sentinel of a
        external file. For example::

            @first #! /usr/bin/env python

        Similarly, @last forces lines to appear after the last sentinel.

        \\@path
        =======

        Rather than specifying long paths in @file nodes, you can specify a path in
        an ancestor @path node.

        For example, suppose three nodes have the following headlines::

            @path a
                @path b
                    @file c/d.py

        The @file node creates the file a/b/c/d.py

        Within @path and @<file> paths, {{exp}} gets evaluated with the following
        predefined symbols: c, g, p, os and sys.  For example::

            @file {{os.path.abspath(os.curdir)}}/abc.py

        '''
        #@-<< define s >>
        s = s.replace('\\', '')
        self.c.putHelpFor(s)
    #@+node:ekr.20150514063305.388: *3* helpForDebuggingCommands
    @cmd('help-for-debugging-commands')
    def helpForDebuggingCommands(self, event: Event = None) -> None:
        """Prints a discussion of of Leo's debugging commands."""
        #@+<< define s >>
        #@+node:ekr.20150514063305.389: *4* << define s >> (helpForDebuggingCommands)
        #@verbatim
        # @pagewidth 40
        #@@language rest

        s = '''

        About Debugging Commands
        ------------------------

        Alt-0 (vr-toggle) hides this help message.

        The following commands are useful for debugging::

            debug:               Start an external debugger in another process.
            dump-node:           Dump c.p.v, including gnx, uA's, etc.
            gc-collect-garbage:  Invoke the garbage collector.
            gc-dump-all-objects: Print a summary of all Python objects.
            gc-show-summary:     Print a brief summary of Python objects.
            pdb:                 Start Python's debugger.
            show-focus:          Print information about the requested focus.
            show-stats:          Print statistics about existing Python objects.

        Leo's --trace command-line arg can enable traces.
        '''
        #@-<< define s >>
        self.c.putHelpFor(s)
    #@+node:ekr.20150514063305.390: *3* helpForDragAndDrop
    @cmd('help-for-drag-and-drop')
    def helpForDragAndDrop(self, event: Event = None) -> None:
        """Prints a discussion of of Leo's drag-and-drop commands."""
        #@+<< define s >>
        #@+node:ekr.20150514063305.391: *4* << define s >> (helpForDragAndDrop
        #@verbatim
        # @pagewidth 40
        #@@language rest

        s = '''

        About Drag and Drop
        ===================

        Nodes
        -----

        You may drag nodes from within a Leo outline or between Leo outlines,
        including nodes from separately running copies of Leo.

        To drag, click and hold on a headline and drag it over another headline.
        Control-drags create clones; regular drags move the node.

        Files
        -----

        You may also drag one or more files from a file folder over a headline.

        For text files, Leo will create @auto, @edit or @file nodes as appropriate.

        Dragging .leo files from a file folder to a Leo outline works like the
        open-outline command. Control-dragging .leo files copies all nodes of the
        .leo file to the receiving outline, under a single node called::

            From <name of .leo file>

        '''
        #@-<< define s >>
        self.c.putHelpFor(s)
    #@+node:ekr.20150514063305.392: *3* helpForDynamicAbbreviations
    @cmd('help-for-dynamic-abbreviations')
    def helpForDynamicAbbreviations(self, event: Event = None) -> None:
        """Prints a discussion of abbreviations."""
        #@+<< define s >>
        #@+node:ekr.20150514063305.393: *4* << define s >> (helpForDynamicAbbreviations)
        #@@language rest

        s = '''

        About Dynamic Abbreviations
        ---------------------------

        Alt-0 (vr-toggle) hides this help message.

        .. Description taken from http://www.emacswiki.org/emacs/DynamicAbbreviations

        A dynamic abbreviation (dabbrev) is like a normal abbreviation except:

        - You do not have to define it(!)
        - You expand it with Alt-/ (dabbrev-expand) or Alt-Ctrl-/ (dabbrev-completion)

        For example, suppose the text aLongIvarName appears anywhere in the
        outline. To type this name again type::

            aLong<Alt-/>

        You will see a list of possible completions in the log pane.

        Alt-Ctrl-/ (dabbrev-completion) inserts the longest prefix of all
        completions immediately.  For instance, suppose the following appear in text::

            aVeryLongIvarName
            aVeryLongMethodName

        Typing::

            aVery<Alt-Ctrl-/>

        will immediately extend the typing to::

            aVeryLong

        '''
        #@-<< define s >>
        self.c.putHelpFor(s)
    #@+node:ekr.20150514063305.394: *3* helpForFindCommands
    @cmd('help-for-find-commands')
    def helpForFindCommands(self, event: Event = None) -> None:
        """Prints a discussion of of Leo's find commands."""
        #@+<< define s >>
        #@+node:ekr.20150514063305.395: *4* << define s >> (help-for-find-commands)
        #@@language rest

        s = '''

        Finding & replacing text
        ------------------------

        Alt-0 (vr-toggle) hides this help message.

        **Ctrl-F** (start-search) shows the Find pane
        and puts focus in the find box.

        Enter the find text and the replacement text if desired::

            Tab switches focus from widget to widget.
            Return executes the find-next command.

        When Leo selects the found text you can do::

            Ctrl-equal (replace)
            Ctrl-minus (replace-then-find)
            F3 (find-next)
            F2 (find-previous)
            Ctrl-G (keyboard-quit)
            anything else :-)

        You can Leo's commands toggle check boxes and radio buttons.
        These commands are listed in the Search menu.

        You can execute these commands (and see their key bindings)
        using the minibuffer::

            <Alt-X>tog<tab>f<tab>   or
            <Alt-X>set<tab>f<tab>

        Incremental searching
        ---------------------

        Incremental search is done only from the minibuffer::

            Alt-I (isearch forward)
            Alt-R (isearch backward)
            BackSpace retracts the search
            All other characters extend the search

        During an incremental search::

            Enter or Ctrl-G stops the search.
            Alt-S finds the search string again.
            Alt-R ditto for reverse searches.
        '''
        #@-<< define s >>
        self.c.putHelpFor(s)
    #@+node:ekr.20150628161341.1: *3* helpForKeystroke
    @cmd('help-for-keystroke')
    def helpForKeystroke(self, event: Event) -> None:
        """Prompts for any key and prints the bindings for that key."""
        c, k = self.c, self.c.k
        state_name = 'help-for-keystroke'
        state = k.getState(state_name)
        if state == 0:
            k.setLabelBlue('Enter any key: ')
            k.setState(state_name, 1, self.helpForKeystroke)
            c.minibufferWantsFocus()
        else:
            d = k.bindingsDict
            k.clearState()
            result = []
            for bi in d.get(event.stroke, []):  # a list of BindingInfo objects.
                pane, cmd = bi.pane, bi.commandName
                result.append(cmd if pane == 'all' else f"{pane}: {cmd}")
            s = f"{event.stroke.s}: {','.join(result)}"
            k.showStateAndMode()
            c.frame.putStatusLine(s, bg='blue', fg='white')
            c.bodyWantsFocus()
    #@+node:ekr.20150514063305.396: *3* helpForMinibuffer
    @cmd('help-for-minibuffer')
    def helpForMinibuffer(self, event: Event = None) -> None:
        """Print a messages telling you how to get started with Leo."""
        # A bug in Leo: triple quotes puts indentation before each line.
        c = self.c
        #@+<< define s >>
        #@+node:ekr.20150514063305.397: *4* << define s >> (helpForMinibuffer)
        #@@language rest

        s = '''\

        About the Minibuffer
        --------------------

        Alt-0 (vr-toggle) hides this help message.

        The mini-buffer is intended to be like the Emacs buffer:

        full-command: (default shortcut: Alt-x) Puts the focus in the minibuffer. Type a
        full command name, then hit <Return> to execute the command. Tab completion
        works, but not yet for file names.

        quick-command-mode (default shortcut: Alt-x). Like Emacs Control-C. This mode is
        defined in leoSettings.leo. It is useful for commonly-used commands.

        universal-argument (default shortcut: Alt-u). Like Emacs Ctrl-u. Adds a repeat
        count for later command. Ctrl-u 999 a adds 999 a's. Many features remain
        unfinished.

        keyboard-quit (default shortcut: Ctrl-g) Exits any minibuffer mode and puts
        the focus in the body pane.

        Use the help-for-command command to see documentation for a particular command.
        '''
        #@-<< define s >>
        c.putHelpFor(s)
    #@+node:ekr.20150514063305.398: *3* helpForRegularExpressions
    @cmd('help-for-regular-expressions')
    def helpForRegularExpressions(self, event: Event = None) -> None:
        """Prints a discussion of of Leo's find commands."""
        #@+<< define s >>
        #@+node:ekr.20150514063305.399: *4* << define s >> (helpForRegularExpressions)
        #@@language rest

        # Using raw string is essential.

        s = r'''

        About regular expressions
        -------------------------

        Alt-0 (vr-toggle) hides this help message.

        Python's regular expressions, http://docs.python.org/library/re.html,
        are valid in find patterns::

            .               Matches any character (including newline if DOTALL flag specified).
            ^               Matches start of the string (of every line in MULTILINE mode).
            $               Matches end of the string (of every line in MULTILINE mode).
            *               0 or more of preceding regular expression (as many as possible).
            +               1 or more of preceding regular expression (as many as possible).
            ?               0 or 1 occurrence of preceding regular expression.
            *?, +?, ??      Same as *, + and ? but matches as few characters as possible.
            {m,n}           Matches from m to n repetitions of preceding RE.
            {m,n}?          Same as {m,n}, but attempting to match as few repetitions as possible.
            [ ]             Defines character set: e.g. '[a-zA-Z]' to match all letters (see also \w \S).
            [^ ]            Defines complemented character set: matches if char is NOT in set.
            \               Escapes special chars '*?+&$|()' and introduces special sequences (see below).
                            If not using a raw string, write as '\\' in the pattern string.
            \\              Matches a literal '\'.
            |               Specifies alternative: 'foo|bar' matches 'foo' or 'bar'.
            (...)           Matches any RE inside (), and delimits a group.
            (?:...)         Matches RE inside (), but doesn't delimit a group.
            (?P<name>...)   Matches any RE inside (), and delimits a named group.
                            r'(?P<id>[a-zA-Z_]\w*)' defines a group named id.
            (?P=name)       Matches whatever text was matched by the earlier group named name.
            (?=...)         Matches if ... matches next, but doesn't consume any of the string
                            'Isaac (?=Asimov)' matches 'Isaac' only if followed by 'Asimov'.
            (?!...)         Matches if ... doesn't match next. Negative of (?=...).
            (?<=...)        Matches if the current position in the string is preceded by a match
                            for ... that ends at the current position.
                            This is called a positive lookbehind assertion.
            (?<!...)        Matches if the current position in the string is not preceded by a match for ...
                            This is called a negative lookbehind assertion.
            (?(group)A|B)   Group is either a numeric group ID or a group name defined with (?Pgroup...)
                            earlier in the expression.
                            If the specified group matched, the regular expression pattern A will be tested
                            against the string; if the group didn't match, the pattern B will be used instead.
            (?#...)         A comment; ignored.
            (?letters)      Each letter is in 'ilmsux' and sets the corresponding flag.
                            re.I, re.L, re.M, re.S, re.U, re.X.
            \number         Matches content of the group of the same number.
            \A              Matches only at the start of the string.
            \b              Empty str at beginning or end of word:
                            '\bis\b' matches 'is', but not 'his'.
            \B              Empty str NOT at beginning or end of word.
            \d              Any decimal digit:          [0-9]
            \D              Any non-decimal digit char  [^0-9]).
            \s              Any whitespace char         [ \t\n\r\f\v]
            \S              Any non-whitespace char     [^ \t\n\r\f\v]
            \w              Any alphaNumeric char (depends on LOCALE flag).
            \W              Any non-alphaNumeric char (depends on LOCALE flag).
            \Z              Matches only at the end of the string.

        '''
        #@-<< define s >>
        self.c.putHelpFor(s)
    #@+node:ekr.20150514063305.400: *3* helpForScripting
    @cmd('help-for-scripting')
    def helpForScripting(self, event: Event = None) -> None:
        """Prints a discussion of Leo scripting."""
        #@+<< define s >>
        #@+node:ekr.20150514063305.401: *4* << define s >> (helpForScripting)
        #@@language rest

        s = '''

        Summary of Leo Scripting
        -------------------------

        Overview
        ========

        Any Leo node may contain a Python script.

        Ctrl-B (execute-script) executes the body text of the presently selected node.

        execute-script creates the script using @others and section references:
        **you can create complex scripts from a node and its descendants.**

        As discussed below, execute-script predefines three variables: c, g and p.
        Using these variables, scripts may easily do any of the following:

        - Gain access to all data contained in any Leo outline.
        - Traverse the data in any outline.
        - Use utility classes and function in the leo.core.leoGlobals module.
        - Execute any code in Leo's own code base.

        *Tip*: use Alt-1 (toggle-autocompleter) and Alt-2 (toggle-calltips) as aids to memory and to speed typing.

        Predefined symbols
        ==================

        The execute-script command predefines three variables::

            c: The commander of the present outline.
            g: The leo.core.leoGlobals module.
            p: The presently selected position, c.p.

        Commands class
        ==============

        A commander is an instance of the Commands class in leo.core.leoCommands.
        A commander represents all outline data and most of Leo's source code.
        Here are the most important ivars of the Commands class::

            c.frame         c's outer frame, a LeoFrame instance.
            c.user_dict     a temporary dict for use of scripts and plugins.
            c.redraw()
            c.positionExists(p)

        Here is a partial list of the **official ivars** of any commander c:

            c.frame                 The frame containing the log,body,tree, etc.
            c.frame.body            The body pane.
            c.frame.body.widget     The gui widget for the body pane.
            c.frame.body.wrapper    The high level interface for the body widget.
            c.frame.iconBar         The icon bar.
            c.frame.log             The log pane.
            c.frame.log.widget      The gui widget for the log pane.
            c.frame.log.wrapper     The high-level interface for the log pane.
            c.frame.tree            The tree pane.

        VNode class
        ===========

        All data in Leo outlines resides in vnodes.
        All clones of the same node share the same VNode.
        Here are the most important ivars and properties of the VNode class::

            v.b: v's body text.
            v.h: v's headline text.
            v.u: v.unknownAttributes, a persistent Python dictionary.

        v.u (uA's or unknownAttributes or userAttributes) allow plugins or scripts
        to associate persistent data with vnodes. For details see the section about
        userAttributes in the Customizing Leo chapter.

        Position class
        ==============

        A position represents the state of a traversal of an outline.
        Because of clones, the same VNode may appear multiple times during a traversal.

        Properties of the position class::

            p.b: same as p.v.b.
            p.h: same as p.v.h.
            p.u: same as p.v.u.

        Getter methods of the position class::

            p.back()
            p.children()
            p.firstChild()
            p.hasBack()
            p.hasChildren()
            p.hasNext()
            p.hasParent()
            p.hasThreadBack()
            p.hasThreadNext()
            p.isAncestorOf(p2)
            p.isAnyAtFileNode()
            p.isAt...Node()
            p.isCloned()
            p.isDirty()
            p.isExpanded()
            p.isMarked()
            p.isRoot()
            p.isVisible()
            p.lastChild()
            p.level()
            p.next()
            p.nodeAfterTree()
            p.nthChild()
            p.numberOfChildren()
            p.parent()
            p.parents()
            p.threadBack()
            p.threadNext()
            p.visBack()
            p.visNext()

        Setter methods of the position class::

            p.setDirty()
            p.setMarked()

        Methods that operate on nodes::

            p.clone()
            p.contract()
            p.doDelete(new_position)
            p.expand()
            p.insertAfter()
            p.insertAsNthChild(n)
            p.insertBefore()
            p.moveAfter(p2)
            p.moveToFirstChildOf(parent,n)
            p.moveToLastChildOf(parent,n)
            p.moveToNthChildOf(parent,n)
            p.moveToRoot()

        The following position methods move positions *themselves*: they change the
        node to which a position refers. They do *not* change outline structure in
        any way! Use these when generators are not flexible enough::

            p.moveToBack()
            p.moveToFirstChild()
            p.moveToLastChild()
            p.moveToLastNode()
            p.moveToNext()
            p.moveToNodeAfterTree(p2)
            p.moveToNthChild(n))
            p.moveToParent()
            p.moveToThreadBack()
            p.moveToThreadNext()
            p.moveToVisBack(c)
            p.moveToVisNext(c)

        Generators
        ==========

        The following Python generators return positions::

            c.all_positions()
            c.all_unique_positions()
            p.children()
            p.parents()
            p.self_and_parents()
            p.self_and_siblings()
            p.following_siblings()
            p.subtree()
            p.self_and_subtree()

        The leo.core.leoGlobals module
        ==============================

        **g vars**::

            g.app
            g.app.gui
            g.app.windowlist
            g.unitTesting
            g.user_dict  # a temporary dict for use of scripts and plugins.

        **g decorator**::

            @g.command(command-name)

        **g functions** (the most interesting: there are many more in leoGlobals.py)::

            g.angleBrackets()
            g.app.commanders()
            g.app.gui.guiName()
            g.es(*args,**keys)
            g.es_print(*args,**keys)
            g.es_exception()
            g.getScript(c,p,
                useSelectedText=True,
                forcePythonSentinels=True,
                useSentinels=True)
            g.openWithFileName(fileName, old_c=None, gui=None)
            g.os_path_... # Wrappers for os.path methods.
            g.pdb(message='')
            g.toEncodedString(s,encoding='utf-8',reportErrors=False)
            g.toUnicode(s, encoding='utf-8',reportErrors=False)
            g.trace(*args,**keys)
            g.warning(*args,**keys)

        '''
        #@-<< define s >>
        self.c.putHelpFor(s)
    #@+node:ekr.20170823084423.1: *3* helpForSettings
    @cmd('help-for-settings')
    def helpForSettings(self, event: Event = None) -> None:
        """Prints a discussion of of Leo's find commands."""
        #@+<< define s >>
        #@+node:ekr.20170823084456.1: *4* << define s >> (helpForSettings)
        #@@language rest

        # Using raw string is essential.

        s = r'''

        About settings
        ---------------

        **@settings trees** specify settings. The headline of each node indicates
        its type. The body text of most nodes contain comments. However, the body
        text of \@data, \@font, \@item and \@shortcuts nodes may contain data. For
        more information about the format of \@settings trees, see leoSettings.leo.

        leoSettings.leo is Leo's main settings file. myLeoSettings.leo contains
        your personal settings. Settings in myLeoSettings.leo override the settings
        in leoSettings.leo. Put myLeoSettings.leo in your home `~` directory or in
        the `~/.leo` directory. Any other .leo file may contain an \@settings tree.
        Such settings apply only to that file.

        '''
        #@-<< define s >>
        self.c.putHelpFor(s)
    #@+node:ekr.20230306104232.1: *3* help.showColorSettings
    @cmd('show-color-settings')
    def showColorSettings(self, event: Event = None) -> None:
        """
        Print the value of all @color settings.

        The following shows where the each setting comes from:

        -     leoSettings.leo,
        -  @  @button, @command, @mode.
        - [D] default settings.
        - [F] indicates the file being loaded,
        - [M] myLeoSettings.leo,
        - [T] theme .leo file.
        """
        self.c.config.printColorSettings()
    #@+node:ekr.20230306104131.1: *3* help.showFontSettings
    @cmd('show-font-settings')
    def showFontSettings(self, event: Event = None) -> None:
        """
        Print the value of every @font setting.

        The following shows where the each setting comes from:

        -     leoSettings.leo,
        -  @  @button, @command, @mode.
        - [D] default settings.
        - [F] indicates the file being loaded,
        - [M] myLeoSettings.leo,
        - [T] theme .leo file.
        """
        self.c.config.printFontSettings()
    #@+node:ekr.20150514063305.402: *3* help.showSettings
    @cmd('show-settings')
    def showSettings(self, event: Event = None) -> None:
        """
        Print the value of every setting, except key bindings, commands, and
        open-with tables.

        The following shows where the each setting comes from:

        -     leoSettings.leo,
        -  @  @button, @command, @mode.
        - [D] default settings.
        - [F] indicates the file being loaded,
        - [M] myLeoSettings.leo,
        - [T] theme .leo file.
        """
        self.c.config.printSettings()
    #@+node:ekr.20190831025811.1: *3* help.showSettingsOutline
    @cmd('show-settings-outline')
    def showSettingsOutline(self, event: Event = None) -> None:
        """
        Create and open an outline, summarizing all presently active settings.

        The outline retains the organization of all active settings files.

        See #852: https://github.com/leo-editor/leo-editor/issues/852
        """

        self.c.config.createActivesSettingsOutline()
    #@+node:ekr.20150514063305.403: *3* pythonHelp
    @cmd('help-for-python')
    def pythonHelp(self, event: Event = None) -> None:
        """Prompt for a arg for Python's help function, and put it to the VR pane."""
        c, k = self.c, self.c.k
        c.minibufferWantsFocus()
        k.setLabelBlue('Python help: ')
        k.get1Arg(event, handler=self.pythonHelp1)

    def pythonHelp1(self, event: Event) -> str:
        c, k = self.c, self.c.k
        k.clearState()
        k.resetLabel()
        s = k.arg.strip()
        if not s:
            return ''
        old = sys.stdout
        try:
            sys.stdout = io.StringIO()
            #  If the argument is a string, the string is looked up as a name...
            # and a help page is printed on the console.
            help(str(s))
            s2 = sys.stdout.getvalue()  # #2165
        finally:
            sys.stdout = old
        if not s2:
            return ''
        # Send it to the vr pane as a <pre> block
        s2 = '<pre>' + s2 + '</pre>'
        c.putHelpFor(s2)
        return s2  # For unit tests.
    #@-others
#@-others
#@-leo
