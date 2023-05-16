#@+leo-ver=5-thin
#@+node:ekr.20200316100818.1: * @file ../plugins/importers/rust.py
"""The @auto importer for rust."""
import re
from leo.core.leoCommands import Commands as Cmdr
from leo.core.leoNodes import Position
from leo.plugins.importers.linescanner import Importer
#@+others
#@+node:ekr.20200316101240.2: ** class Rust_Importer(Importer)
class Rust_Importer(Importer):

    language = 'rust'

    if 0:
        def __init__(self, c: Cmdr) -> None:
            """rust_Importer.__init__"""
            # Init the base class.
            super().__init__(c, language='rust')

    #@+others
    #@+node:ekr.20200317114526.1: *3* rust_i.compute_headline
    func_pattern = re.compile(r'\s*(pub )?\s*(enum|fn|impl|mod|struct|trait)\b(.*)')
    arg_pat = re.compile(r'(\(.*?\))')
    type_pat = re.compile(r'(\s*->.*)')
    life_pat = re.compile(r'(\<.*\>)')
    body_pat = re.compile(r'(\{.*\})')

    def compute_headline(self, s: str) -> str:
        """
        Remove argument list and return value.
        """
        s = s.strip()
        m = self.func_pattern.match(s)
        if not m:  # pragma: no cover (defensive)
            return s
        g1 = m.group(1) or ''
        g2 = m.group(2) or ''
        head = f"{g1} {g2}".strip()
        # Remove the argument list and return value.
        tail = m.group(3) or ''.strip()
        tail = re.sub(self.arg_pat, '', tail, count=1)
        tail = re.sub(self.type_pat, '', tail, count=1)
        tail = re.sub(self.body_pat, '', tail, count=1)
        # Clean lifetime specs except for impl.
        if not head.startswith('impl'):
            tail = re.sub(self.life_pat, '', tail, count=1)
        # Remove trailing '(' or '{'
        tail = tail.strip()
        while tail.endswith(('{', '(', ',', ')')):
            tail = tail[:-1].rstrip()
        # Remove trailing '>' sometimes.
        while '<' not in tail and tail.endswith('>'):  # pragma: no cover (missing test)
            tail = tail[:-1].rstrip()
        return f"{head} {tail}".strip().replace('  ', ' ')
    #@-others
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for rust."""
    Rust_Importer(c).import_from_string(parent, s)

importer_dict = {
    'extensions': ['.rs',],
    'func': do_import,
}
#@@language python
#@@tabwidth -4
#@-leo
