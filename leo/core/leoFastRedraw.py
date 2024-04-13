#@+leo-ver=5-thin
#@+node:ekr.20181202062518.1: * @file leoFastRedraw.py
"""
Gui-independent fast-redraw code.

For an explanation, see this thread:
https://groups.google.com/forum/#!topic/leo-editor/hpHyHU2sWtM
"""
import difflib
import re
import time
from leo.core import leoGlobals as g

class FastRedraw:
    #@+others
    #@+node:ekr.20181202060924.4: ** LeoGui.dump_diff_op_codes
    def dump_diff_op_codes(self, a, b, op_codes):
        """Dump the opcodes returned by difflib.SequenceMatcher."""

        def summarize(aList):
            pat = re.compile(r'.*:.*:(.*)')
            return ', '.join([pat.match(z).group(1) for z in aList])

        for tag, i1, i2, j1, j2 in op_codes:
            if tag == 'equal':
                print(f"{tag:7} at {i1}:{i2} (both) ==> {summarize(b[j1:j2])!r}")
            elif tag == 'insert':
                print(f"{tag:7} at {i1}:{i2} (b)    ==> {summarize(b[j1:j2])!r}")
            elif tag == 'delete':
                print(f"{tag:7} at {i1}:{i2} (a)    ==> {summarize(a[i1:i2])!r}")
            elif tag == 'replace':
                print(f"{tag:7} at {i1}:{i2} (a)    ==> {summarize(a[i1:i2])!r}")
                print(f"{tag:7} at {i1}:{i2} (b)    ==> {summarize(b[j1:j2])!r}")
            else:
                print('unknown tag')
    #@+node:ekr.20181202060924.5: ** LeoGui.dump_opcodes
    def dump_opcodes(self, opcodes):
        """Dump the opcodes returned by app.peep_hole and app.make_redraw_list."""
        for z in opcodes:
            kind = z[0]
            if kind == 'replace':
                kind, i1, gnxs1, gnxs2 = z
                print(kind, i1)
                print("  a: [%s]" % ',\n    '.join(gnxs1))
                print("  b: [%s]" % ',\n    '.join(gnxs2))
            elif kind in ('delete', 'insert'):
                kind, i1, gnxs = z
                print(kind, i1)
                print("  [%s]" % ',\n    '.join(gnxs))
            else:
                print(z)
    #@+node:ekr.20181202060924.2: ** LeoGui.flatten_outline
    def flatten_outline(self, c):
        """Return a flat list of strings "level:gnx" for all *visible* positions."""
        trace = False and not g.unitTesting
        t1 = time.process_time()
        aList: list[str] = []
        for p in c.rootPosition().self_and_siblings():
            self.extend_flattened_outline(aList, p)
        if trace:
            t2 = time.process_time()
            print(f"app.flatten_outline: {len(aList)} entries {t2 - t1:6.4f} sec.")
        return aList

    def extend_flattened_outline(self, aList, p):
        """Add p and all p's visible descendants to aList."""
        # Padding the fields causes problems later.
        aList.append(f"{p.level()}:{p.gnx}:{p.h}\n")
        if p.isExpanded():
            for child in p.children():
                self.extend_flattened_outline(aList, child)
    #@+node:ekr.20181202060924.3: ** LeoGui.make_redraw_list
    def make_redraw_list(self, a, b):
        """
        Diff the a (old) and b (new) outline lists.
        Then optimize the diffs to create a redraw instruction list.
        """
        trace = False and not g.unitTesting
        if a == b:
            return []

        def gnxs(aList):
            """Return the gnx list. Do not try to remove this!"""
            return [z.strip() for z in aList]
        #@+others # Define local helpers
        #@-others
        d = difflib.SequenceMatcher(None, a, b)
        op_codes = list(d.get_opcodes())
        # dump_diff_op_codes(a, b, op_codes)
        #
        # Generate the instruction list, and verify the result.
        opcodes, result = [], []
        for tag, i1, i2, j1, j2 in op_codes:
            if tag == 'insert':
                opcodes.append(['insert', i1, gnxs(b[j1:j2])])
            elif tag == 'delete':
                opcodes.append(['delete', i1, gnxs(a[i1:i2])])
            elif tag == 'replace':
                opcodes.append(['replace', i1, gnxs(a[i1:i2]), gnxs(b[j1:j2])])
            result.extend(b[j1:j2])
        assert b == result, (a, b)
        #
        # Run the peephole.
        opcodes = self.peep_hole(opcodes)
        if trace:
            print('app.make_redraw_list: opcodes after peephole...')
            self.dump_opcodes(opcodes)
        return opcodes
    #@+node:ekr.20181202060924.6: ** LeoGui.peep_hole
    def peep_hole(self, opcodes):
        """Scan the list of opcodes, merging adjacent op-codes."""
        i, result = 0, []
        while i < len(opcodes):
            op0 = opcodes[i]
            if i == len(opcodes) - 1:
                result.append(op0)
                break
            op1 = opcodes[i + 1]
            kind0, kind1 = op0[0], op1[0]
            # Merge adjacent insert/delete opcodes with the same gnx.
            if (
                kind0 == 'insert' and kind1 == 'delete' or
                kind0 == 'delete' and kind1 == 'insert'
            ):
                kind0, index0, gnxs0 = op0
                kind1, index1, gnxs1 = op1
                if gnxs0[0] == gnxs1[0]:
                    result.append(['move', index0, index1, gnxs0, gnxs1])
                    i += 2  # Don't scan either op again!
                    break
            # The default is to retain the opcode.
            result.append(op0)
            i += 1
        return result
    #@-others

#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
