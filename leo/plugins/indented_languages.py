#@+leo-ver=5-thin
#@+node:ekr.20230917013414.1: * @file ../plugins/indented_languages.py
"""
A plugin that creates **study outlines** in which indentation replaces curly brackets.
"""
import re
from typing import Any
from leo.core import leoGlobals as g
### from leo.core.leoCommands import Commands as Cmdr
from leo.core.leoNodes import Position  ###, VNode

###
# from leo.plugins.importers.elisp import Elisp_Importer
# from leo.plugins.importers.python import Python_Importer
# from leo.plugins.importers.typescript import TS_Importer
# assert Elisp_Importer, Python_Importer, TS_Importer  ###

#@+others
#@+node:ekr.20230917084259.1: ** top-level
#@+node:ekr.20230917015308.1: *3* init (indented_languages.py)
def init() -> bool:
    """Return True if the plugin has loaded successfully."""
    # g.registerHandler('after-create-leo-frame', onCreate)
    # g.registerHandler('after-reading-external-file', onAfterRead)
    # g.registerHandler('before-writing-external-file', onBeforeWrite)
    return True
#@+node:ekr.20231022071443.1: *3* commands (indented_languages.py)
@g.command('import-to-indented-c')
def import_to_indented_c(event: Any) -> None:
    """The import-to-indented-c command."""
    c = event.get('c')
    if c:
        Indented_C(c).do_import()

@g.command('import-to-indented-elisp')
def import_to_indented_elisp(event: Any) -> None:
    """The import-to-indented-elisp command."""
    c = event.get('c')
    if c:
        Indented_Lisp(c).do_import()
        
@g.command('import-to-indented-typescript')
def import_to_indented_typescript(event: Any) -> None:
    """The import-to-indented-typescript command."""
    c = event.get('c')
    if c:
        Indented_TypeScript(c).do_import()


#@+node:ekr.20231022073438.1: **  class Indented_Importer
class Indented_Importer:
    """The base class for all indented importers."""
    
    ext: list[str] = None  # The file extension for the language.
    language: str = None  # The name of the language.
    
    def __init__(self, c):
        self.c = c

    #@+others
    #@+node:ekr.20231022073537.1: *3* Indented_Importer.do_import
    def do_import(self):
        """
        Base_Indented_Importer.do_import: Create a top-level node containing study outlines for all files in
        c.p and its descendants.
        
        Subclasses must define 
        """
        c, p = self.c, self.c.p
        ext = self.ext
        assert ext
        assert c  ###
        
        # Undoably create top-level organizer node
        
        if 0:
            seen: dict[str, bool] = {}
            for p2 in p.self_and_subtree():
                if p2.gnx not in seen:
                    seen [p2.gnx] = True
                    self.do_remove_brackets(p2)
        
    #@+node:ekr.20231022073306.4: *3* Indented_Importer.check_brackets
    # No need to worry about comments in guide lines.
    bracket_pat = re.compile(r'^\s*}.*?{\s*$')
    matched_bracket_pat = re.compile(r'{.*?}\s*')

    def check_brackets(self, guide_lines: list[str], p: Position) -> None:
        """
        Check that all lines contain at most one unmatched '{' or '}'.
        If '}' precedes '{' then only whitespace may appear before '}' and after '{'.
        Raise TypeError if there is a problem.
        """
        trace = False
        for i, line0 in enumerate(guide_lines):
            line = re.sub(self.matched_bracket_pat, '', line0)
            if trace and line != line0:
                g.trace(f"Sub0: Line {i:4}: {line0.strip()}")
                g.trace(f"Sub1: Line {i:4}: {line.strip()}")
            n1 = line.count('{')
            n2 = line.count('}')
            if n1 > 1 or n2 > 1:
                raise TypeError(f"Too many curly brackets in line {i:4}: {line.strip()}")
            if n1 == 1 and n2 == 1 and line.find('{') > line.find('}'):
                m = self.bracket_pat.match(line)
                if not m:
                    raise TypeError(
                        f"{p.h}: Too invalid curly brackets in line {i:4}: {line.strip()}")
                if trace:
                    g.trace(f"Good: Line {i:4}: {line.strip()}")
    #@-others
#@+node:ekr.20231022080007.1: ** class Indented_C
class Indented_C (Indented_Importer):
    """A class to support indented C files."""
    
    ext: list[str] = ['.c', '.cpp', '.cc']  
    language = 'c'

    #@+others
    #@+node:ekr.20231022080007.2: *3* Indented_C.do_remove_brackets (top level)
    def do_remove_brackets(self, indent: int, p: Position) -> None:
        """
        The top-level driver for each node.
        
        Using guide lines, remove most curly brackets from p.b.
        """
        contents = p.b
        if not contents.strip():
            # g.trace('Empty!', p.h)
            return
        lines = g.splitLines(contents)
        guide_lines = self.importer.make_guide_lines(lines)
        assert lines and len(lines) == len(guide_lines)

        # These may raise TypeError.
        self.check_brackets(guide_lines, p)
        self.check_indentation(indent, guide_lines, lines, p)
        self.remove_brackets(guide_lines, lines, p)
    #@+node:ekr.20231022080007.5: *4* Indented_C.remove_brackets
    curlies_pat = re.compile(r'{|}')
    close_curly_pat = re.compile(r'}')
    semicolon_pat = re.compile(r'}\s*;')

    def remove_brackets(self,
        guide_lines: list[str],
        lines: list[str],
        p: Position,
    ) -> None:
        """
        Remove curly brackets from p.b.
        Do not remove matching brackets if ';' follows the closing bracket.

        Raise TypeError if there is a problem.
        """

        tag=f"{g.my_name()}"

        # The stack contains tuples(curly_bracket, line_number, column_number) for each curly bracket.
        # Note: adding a 'level' entry to these tuples would be tricky.
        stack: list[tuple[str, int, int]] = []
        info: dict[tuple, tuple] = {}  # Keys and values are tuples, as above.

        # Pass 1: Create the info dict.
        level = 0  # To check for unmatched braces.
        for line_number, line in enumerate(guide_lines):
            last_column = 0
            for m in re.finditer(self.curlies_pat, line):
                curly = m.group(0)
                column_number = m.start()
                assert last_column == 0 or last_column < column_number, f"{tag} unexpected column"
                assert 0 <= column_number < len(line), f"{tag} column out of range"
                last_column = column_number
                # g.trace(f" {curly} level: {level} column: {column_number:3} line: {line_number:3} {line!r}")
                if curly == '{':
                    stack.append((curly, line_number, column_number))
                else:
                    assert curly == '}', f"{tag}: not }}"
                    assert stack, f"{tag}: stack underflow"
                    top = stack.pop()
                    top_curly, top_line_number, top_column_number = top
                    assert top_curly == '{', f"{tag} stack mismatch"
                    this_info = (curly, line_number, column_number)
                    info [top] = this_info
                    info [this_info] = top
                level += (1 if curly == '{' else -1)
        assert level == 0, f"{tag} unmatched brackets"

        # Pass 2: Make the substitutions when '}' is seen.
        result_lines = []  # Must be empty here.
        for line_number, line in enumerate(guide_lines):

            if '}' not in line:
                # No substitution is possible.
                result_lines.append(lines[line_number])
                continue

            # Don't make the substitution if '};' appears on the line.
            if self.semicolon_pat.search(line):
                # g.trace('Skip };', repr(line))
                result_lines.append(lines[line_number])
                continue

            for m in re.finditer(self.close_curly_pat, line):
                column_number = m.start()
                this_info = ('}', line_number, column_number)
                assert this_info in info, f"no matching info: {this_info}"
                match_curly, match_line, match_column = info [this_info]
                assert match_curly == '{', f"{tag}: wrong matching curly bracket"

                # Don't make the substitution if the match is on the same line.
                if match_line == line_number:
                    # g.trace('Same line', repr(line))
                    result_lines.append(lines[line_number])
                    break

                if 0:
                    print('')
                    print(f"{tag} Remove")
                    print(f"matching: {{ line: {match_line:3} column: {match_column:2} {guide_lines[match_line]!r}")
                    print(f"    this: }} line: {line_number:3} column: {column_number:2} {line!r}")

                # Replace the previous line in result_lines, *not* lines.
                s = result_lines[match_line]
                new_line = s[:match_column] + ' ' + s[match_column + 1:]
                result_lines[match_line] = new_line.rstrip() + '\n' if new_line.strip() else '\n'

                # Append this *real* line to result_lines.
                s = lines[line_number]
                this_line = s[:column_number] + ' ' + s[column_number + 1:]
                result_lines.append(this_line.rstrip() + '\n' if this_line.strip() else '\n')

        # Remove multiple blank lines. Some will be added later.
        new_result_lines: list[str] = []
        for i, line in enumerate(result_lines):
            if 0 < i - 1 < len(new_result_lines) and line == '\n' and new_result_lines[i-1] == '\n':
                pass
            else:
                new_result_lines.append(line)
        result_lines = new_result_lines

        # Add a header for traces.
        if 0:
            result_lines = [f"Node: {p.h}\n\n"] + result_lines
        # g.printObj(lines, f"lines: {p.h}")
        # g.printObj(guide_lines, f"guide_lines: {p.h}")
        # print(''.join(result_lines).rstrip() + '\n')
        # g.printObj(result_lines, tag=f"result_lines: {p.h}")
    #@-others
#@+node:ekr.20230917083456.1: ** class Indented_Lisp
class Indented_Lisp (Indented_Importer):
    """A class to support indented typescript files."""
    
    ext: list[str] = ['.el', ]  ### More???
    language = 'lisp'

    #@+others
    #@+node:ekr.20230917184608.1: *3* Indented_Lisp.do_remove_brackets (top level)
    def do_remove_brackets(self, indent: int, p: Position) -> None:
        """
        The top-level driver for each node.
        
        Using guide lines, remove most curly brackets from p.b.
        """
        contents = p.b
        if not contents.strip():
            # g.trace('Empty!', p.h)
            return
        lines = g.splitLines(contents)
        guide_lines = self.importer.make_guide_lines(lines)
        assert lines and len(lines) == len(guide_lines)

        # These may raise TypeError.
        self.check_brackets(guide_lines, p)
        self.check_indentation(indent, guide_lines, lines, p)
        self.remove_brackets(guide_lines, lines, p)
    #@+node:ekr.20230917185546.1: *4* IndentedTS.check_brackets
    # No need to worry about comments in guide lines.
    bracket_pat = re.compile(r'^\s*}.*?{\s*$')
    matched_bracket_pat = re.compile(r'{.*?}\s*')

    def check_brackets(self, guide_lines: list[str], p: Position) -> None:
        """
        Check that all lines contain at most one unmatched '{' or '}'.
        If '}' precedes '{' then only whitespace may appear before '}' and after '{'.
        Raise TypeError if there is a problem.
        """
        trace = False
        for i, line0 in enumerate(guide_lines):
            line = re.sub(self.matched_bracket_pat, '', line0)
            if trace and line != line0:
                g.trace(f"Sub0: Line {i:4}: {line0.strip()}")
                g.trace(f"Sub1: Line {i:4}: {line.strip()}")
            n1 = line.count('{')
            n2 = line.count('}')
            if n1 > 1 or n2 > 1:
                raise TypeError(f"Too many curly brackets in line {i:4}: {line.strip()}")
            if n1 == 1 and n2 == 1 and line.find('{') > line.find('}'):
                m = self.bracket_pat.match(line)
                if not m:
                    raise TypeError(
                        f"{p.h}: Too invalid curly brackets in line {i:4}: {line.strip()}")
                if trace:
                    g.trace(f"Good: Line {i:4}: {line.strip()}")
    #@+node:ekr.20230919030308.1: *4* IndentedTS.check_indentation
    curly_pat1, curly_pat2 = re.compile(r'{'), re.compile(r'}')
    paren_pat1, paren_pat2 = re.compile(r'\('), re.compile(r'\)')
    square_pat1, square_pat2 = re.compile(r'\['), re.compile(r'\]')

    def check_indentation(self,
        indent: int,
        guide_lines: list[str],
        lines: list[str],
        p: Position,
    ) -> None:
        """
        Check indentation and correct it if possible. Raise TypeError if not.
        
        Relax the checks for parenthesized lines.
        """
        print_header = True
        tag=f"{g.my_name()}"
        ws_char = ' ' if indent < 0 else '\t'
        ws_pat = re.compile(fr'^[{ws_char}]*')
        indent_s = ws_char * abs(indent)
        indent_n = len(indent_s)
        assert indent_n > 0, f"{tag}: bad indent_n: {indent_n} {indent_s!r}"

        # The main loop.
        curlies, squares, parens = 0, 0, 0
        for i, line in enumerate(guide_lines):
            strip_line = line.strip()
            # Check leading whitespace in *original* lines.
            if not parens and not squares and strip_line:
                original_line = lines[i]
                last_line = '' if i == 0 else lines[i-1].strip()
                m = ws_pat.match(original_line)
                assert m, f"{tag} check_indentation: ws_pat does not match"
                lws_s = m.group(0)
                lws = len(lws_s)
                lws_level, lws_remainder = divmod(lws, abs(indent))
                # Hacks to ignore special patterns.
                if (
                    strip_line.startswith(('/', '.', '?', ':', '(', '['))
                    or last_line.endswith(('=', '+'))
                    or '}' in line or '{' in line
                ):
                    ok = lws_remainder == 0
                else:
                    ok = lws_level == curlies
                if not ok:
                    if print_header:
                        print(f"\nNode {p.h}\n")
                        print_header = False
                    # g.trace(f"lws: {lws_level} rem: {lws_remainder} bracket level: {curlies}")
                    message = (
                        f"Bad indentation {lws_level:2} expected {curlies}:\n"
                        f"line {i:4}: {original_line!r}\n{' '*9}: {line!r}\n"
                    )
                    print(message)
                    if g.unitTesting:
                        raise TypeError(message)

            # Compute levels for the next line.
            for m in re.finditer(self.curly_pat1, line):
                curlies += 1
            for m in re.finditer(self.curly_pat2, line):
                curlies -= 1
            for m in re.finditer(self.paren_pat1, line):
                parens += 1
            for m in re.finditer(self.paren_pat2, line):
                parens -= 1
            for m in re.finditer(self.square_pat1, line):
                squares += 1
            for m in re.finditer(self.square_pat2, line):
                squares -= 1
    #@+node:ekr.20230919030850.1: *4* IndentedTS.remove_brackets
    curlies_pat = re.compile(r'{|}')
    close_curly_pat = re.compile(r'}')
    semicolon_pat = re.compile(r'}\s*;')

    def remove_brackets(self,
        guide_lines: list[str],
        lines: list[str],
        p: Position,
    ) -> None:
        """
        Remove curly brackets from p.b.
        Do not remove matching brackets if ';' follows the closing bracket.

        Raise TypeError if there is a problem.
        """

        tag=f"{g.my_name()}"

        # The stack contains tuples(curly_bracket, line_number, column_number) for each curly bracket.
        # Note: adding a 'level' entry to these tuples would be tricky.
        stack: list[tuple[str, int, int]] = []
        info: dict[tuple, tuple] = {}  # Keys and values are tuples, as above.

        # Pass 1: Create the info dict.
        level = 0  # To check for unmatched braces.
        for line_number, line in enumerate(guide_lines):
            last_column = 0
            for m in re.finditer(self.curlies_pat, line):
                curly = m.group(0)
                column_number = m.start()
                assert last_column == 0 or last_column < column_number, f"{tag} unexpected column"
                assert 0 <= column_number < len(line), f"{tag} column out of range"
                last_column = column_number
                # g.trace(f" {curly} level: {level} column: {column_number:3} line: {line_number:3} {line!r}")
                if curly == '{':
                    stack.append((curly, line_number, column_number))
                else:
                    assert curly == '}', f"{tag}: not }}"
                    assert stack, f"{tag}: stack underflow"
                    top = stack.pop()
                    top_curly, top_line_number, top_column_number = top
                    assert top_curly == '{', f"{tag} stack mismatch"
                    this_info = (curly, line_number, column_number)
                    info [top] = this_info
                    info [this_info] = top
                level += (1 if curly == '{' else -1)
        assert level == 0, f"{tag} unmatched brackets"

        # Pass 2: Make the substitutions when '}' is seen.
        result_lines = []  # Must be empty here.
        for line_number, line in enumerate(guide_lines):

            if '}' not in line:
                # No substitution is possible.
                result_lines.append(lines[line_number])
                continue

            # Don't make the substitution if '};' appears on the line.
            if self.semicolon_pat.search(line):
                # g.trace('Skip };', repr(line))
                result_lines.append(lines[line_number])
                continue

            for m in re.finditer(self.close_curly_pat, line):
                column_number = m.start()
                this_info = ('}', line_number, column_number)
                assert this_info in info, f"no matching info: {this_info}"
                match_curly, match_line, match_column = info [this_info]
                assert match_curly == '{', f"{tag}: wrong matching curly bracket"

                # Don't make the substitution if the match is on the same line.
                if match_line == line_number:
                    # g.trace('Same line', repr(line))
                    result_lines.append(lines[line_number])
                    break

                if 0:
                    print('')
                    print(f"{tag} Remove")
                    print(f"matching: {{ line: {match_line:3} column: {match_column:2} {guide_lines[match_line]!r}")
                    print(f"    this: }} line: {line_number:3} column: {column_number:2} {line!r}")

                # Replace the previous line in result_lines, *not* lines.
                s = result_lines[match_line]
                new_line = s[:match_column] + ' ' + s[match_column + 1:]
                result_lines[match_line] = new_line.rstrip() + '\n' if new_line.strip() else '\n'

                # Append this *real* line to result_lines.
                s = lines[line_number]
                this_line = s[:column_number] + ' ' + s[column_number + 1:]
                result_lines.append(this_line.rstrip() + '\n' if this_line.strip() else '\n')

        # Remove multiple blank lines. Some will be added later.
        new_result_lines: list[str] = []
        for i, line in enumerate(result_lines):
            if 0 < i - 1 < len(new_result_lines) and line == '\n' and new_result_lines[i-1] == '\n':
                pass
            else:
                new_result_lines.append(line)
        result_lines = new_result_lines

        # Add a header for traces.
        if 0:
            result_lines = [f"Node: {p.h}\n\n"] + result_lines
        # g.printObj(lines, f"lines: {p.h}")
        # g.printObj(guide_lines, f"guide_lines: {p.h}")
        # print(''.join(result_lines).rstrip() + '\n')
        # g.printObj(result_lines, tag=f"result_lines: {p.h}")
    #@-others
#@+node:ekr.20231022073306.1: ** class Indented_TypeScript
class Indented_TypeScript (Indented_Importer):
    """A class to support indented typescript files."""
    
    ext = ['.ts']
    language = 'typescript'

    #@+others
    #@+node:ekr.20231022073306.3: *3* Indented_TS.do_remove_brackets (top level)
    def do_remove_brackets(self, indent: int, p: Position) -> None:
        """
        The top-level driver for each node.
        
        Using guide lines, remove most curly brackets from p.b.
        """
        contents = p.b
        if not contents.strip():
            # g.trace('Empty!', p.h)
            return
        lines = g.splitLines(contents)
        guide_lines = self.importer.make_guide_lines(lines)
        assert lines and len(lines) == len(guide_lines)

        # These may raise TypeError.
        self.check_brackets(guide_lines, p)
        self.check_indentation(indent, guide_lines, lines, p)
        self.remove_brackets(guide_lines, lines, p)
    #@+node:ekr.20231022073306.6: *3* IndentedTS.remove_brackets
    curlies_pat = re.compile(r'{|}')
    close_curly_pat = re.compile(r'}')
    semicolon_pat = re.compile(r'}\s*;')

    def remove_brackets(self,
        guide_lines: list[str],
        lines: list[str],
        p: Position,
    ) -> None:
        """
        Remove curly brackets from p.b.
        Do not remove matching brackets if ';' follows the closing bracket.

        Raise TypeError if there is a problem.
        """

        tag=f"{g.my_name()}"

        # The stack contains tuples(curly_bracket, line_number, column_number) for each curly bracket.
        # Note: adding a 'level' entry to these tuples would be tricky.
        stack: list[tuple[str, int, int]] = []
        info: dict[tuple, tuple] = {}  # Keys and values are tuples, as above.

        # Pass 1: Create the info dict.
        level = 0  # To check for unmatched braces.
        for line_number, line in enumerate(guide_lines):
            last_column = 0
            for m in re.finditer(self.curlies_pat, line):
                curly = m.group(0)
                column_number = m.start()
                assert last_column == 0 or last_column < column_number, f"{tag} unexpected column"
                assert 0 <= column_number < len(line), f"{tag} column out of range"
                last_column = column_number
                # g.trace(f" {curly} level: {level} column: {column_number:3} line: {line_number:3} {line!r}")
                if curly == '{':
                    stack.append((curly, line_number, column_number))
                else:
                    assert curly == '}', f"{tag}: not }}"
                    assert stack, f"{tag}: stack underflow"
                    top = stack.pop()
                    top_curly, top_line_number, top_column_number = top
                    assert top_curly == '{', f"{tag} stack mismatch"
                    this_info = (curly, line_number, column_number)
                    info [top] = this_info
                    info [this_info] = top
                level += (1 if curly == '{' else -1)
        assert level == 0, f"{tag} unmatched brackets"

        # Pass 2: Make the substitutions when '}' is seen.
        result_lines = []  # Must be empty here.
        for line_number, line in enumerate(guide_lines):

            if '}' not in line:
                # No substitution is possible.
                result_lines.append(lines[line_number])
                continue

            # Don't make the substitution if '};' appears on the line.
            if self.semicolon_pat.search(line):
                # g.trace('Skip };', repr(line))
                result_lines.append(lines[line_number])
                continue

            for m in re.finditer(self.close_curly_pat, line):
                column_number = m.start()
                this_info = ('}', line_number, column_number)
                assert this_info in info, f"no matching info: {this_info}"
                match_curly, match_line, match_column = info [this_info]
                assert match_curly == '{', f"{tag}: wrong matching curly bracket"

                # Don't make the substitution if the match is on the same line.
                if match_line == line_number:
                    # g.trace('Same line', repr(line))
                    result_lines.append(lines[line_number])
                    break

                if 0:
                    print('')
                    print(f"{tag} Remove")
                    print(f"matching: {{ line: {match_line:3} column: {match_column:2} {guide_lines[match_line]!r}")
                    print(f"    this: }} line: {line_number:3} column: {column_number:2} {line!r}")

                # Replace the previous line in result_lines, *not* lines.
                s = result_lines[match_line]
                new_line = s[:match_column] + ' ' + s[match_column + 1:]
                result_lines[match_line] = new_line.rstrip() + '\n' if new_line.strip() else '\n'

                # Append this *real* line to result_lines.
                s = lines[line_number]
                this_line = s[:column_number] + ' ' + s[column_number + 1:]
                result_lines.append(this_line.rstrip() + '\n' if this_line.strip() else '\n')

        # Remove multiple blank lines. Some will be added later.
        new_result_lines: list[str] = []
        for i, line in enumerate(result_lines):
            if 0 < i - 1 < len(new_result_lines) and line == '\n' and new_result_lines[i-1] == '\n':
                pass
            else:
                new_result_lines.append(line)
        result_lines = new_result_lines

        # Add a header for traces.
        if 0:
            result_lines = [f"Node: {p.h}\n\n"] + result_lines
        # g.printObj(lines, f"lines: {p.h}")
        # g.printObj(guide_lines, f"guide_lines: {p.h}")
        # print(''.join(result_lines).rstrip() + '\n')
        # g.printObj(result_lines, tag=f"result_lines: {p.h}")
    #@-others
#@-others
#@-leo
