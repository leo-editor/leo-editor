# @+leo-ver=5-thin
# @+node:ekr.20260604043712.1: * @file ../scripts/make_sphinx_docs.py
"""
make_sphinx_docs.py:  Regenerate the leo-editor/docs folder.

- Open LeoDocs.leo in Leo's bridge.
- Generate all intermediate files from @rst nodes in LeoDocs.leo.
- Run make-clean.
- Run make-html.
"""

# @+<< make_sphinx_docs: imports and annotations >>
# @+node:ekr.20260604045635.1: ** << make_sphinx_docs: imports and annotations >>
from datetime import datetime
import os
import re
from typing import Any, TYPE_CHECKING
from sphinx import __version__ as sphinx_version

import leo.core.leoBridge as leoBridge
from leo.core import leoGlobals as g  # g.app is None!

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
# @-<< make_sphinx_docs: imports and annotations >>

g.cls()
g_app: Any = None  # g.app, as defined in the bridge.

# @+others
# @+node:ekr.20260604044407.3: ** get_leo_version
conf_version_pat = re.compile(r"^version\s*=\s*\'([0-9]+\.[0-9]+\.[0-9]+)\'")


def get_leo_version(c: Cmdr) -> str:
    """Return the version in conf.py"""
    h = '@edit html/conf.py'
    p = g.findNodeAnywhere(c, h)
    assert p, h
    for line in g.splitLines(p.b):
        if m := conf_version_pat.match(line):
            return m.group(1).strip()
    return ''


# @+node:ekr.20260604044407.7: ** main
def main() -> None:
    """
    Make all html files using sphinx and copy the results to leo-editor/docs.
    """
    global g_app

    # First, open LeoDocs.leo in the bridge and define g.
    c = open_leo_docs()
    if not c:
        return

    finalize = g.os_path_finalize_join
    docs_path = html_path = finalize(g_app.loadDir, '..', '..', 'docs')
    if not os.path.exists(docs_path):
        print(f"Not found: {docs_path!r}")
        return
    docs_static_path = finalize(docs_path, '_static')
    if not os.path.exists(docs_static_path):
        print(f"Not found: {docs_static_path!r}")
        return

    ###
    # build_path = finalize(doc, 'html', '_build', 'html')
    # docs_path = finalize(docs)
    # docs_static_path = finalize(docs, '_static')
    # doc_static_path = finalize(doc, 'html', '_build', 'html', '_static')

    os.chdir(html_path)
    version = patch_home_page(c)
    if version:
        print(f"Found Leo version: {version}")
    else:
        print('no version in conf.py')
        return
    if 0:
        write_intermediate_files(c)
    if 0:
        make_html(html_path)
    print_git_status()


# @+node:ekr.20260604044407.5: ** make_html
def make_html(html_path: str) -> None:
    """
    Run make commands in the docs/html directory.
    """
    cwd = os.getcwd()
    assert cwd.lower() == html_path.lower(), (cwd, html_path)
    g.execute_shell_commands(
        [
            'make clean',  # Safest.
            'make html',
        ]
    )


# @+node:ekr.20260604050039.1: ** open_leo_docs
def open_leo_docs() -> Cmdr:
    """Open LeoDocs.leo using Leo's bridge."""
    global g_app

    path = g.os_path_finalize_join(__file__, '..', '..', 'doc', 'LeoDocs.leo')

    controller = leoBridge.controller(
        gui='nullGui',
        loadPlugins=False,
        readSettings=False,
        silent=False,
        verbose=True,
    )
    controller_g = controller.globals()
    if controller_g.app:
        g_app = controller_g.app
    else:
        print('Can not create Leo\'s bridge')
        return None
    if not g_app:
        print('Can not create g.app')
        return None
    c = controller.openLeoFile(path)
    if not c:
        print(f"Can not open: {path}")
    return c


# @+node:ekr.20260604044407.6: ** patch_home_page
date_pat = re.compile(r'^(.*?)(Last updated on\s*)(.+)(.*)$')
leo_version_pat = re.compile(r'^(.*?)Leo\s*([0-9]+\.[0-9]+\.[0-9]+)(.*)$')
sphinx_version_pat = re.compile(r'^(.*?)Sphinx\s*([0-9]+\.[0-9]+\.[0-9]+)(.*)$')


def patch_home_page(c: Cmdr) -> None:
    """
    Update (in *this*file) the "Last updated" and "Created using" fields in
    the node `@file ../../docs/index.html` or its descendants.
    """
    today = datetime.today()
    date = datetime.date(today).strftime("%B %d, %Y")  # Same as conf.py.
    leo_version = get_leo_version(c)

    def date_repl(m: re.Match) -> str:
        s = m.group(0)
        i, j = m.start(3), m.end(3)
        return s[:i] + date + s[j:]

    def leo_version_repl(m: re.Match) -> str:
        s = m.group(0)
        i, j = m.start(2), m.end(2)
        return s[:i] + leo_version + s[j:]

    def sphinx_version_repl(m: re.Match) -> str:
        s = m.group(0)
        i, j = m.start(2), m.end(2)
        return s[:i] + sphinx_version + s[j:]

    table = (
        (date_pat, date_repl),
        (leo_version_pat, leo_version_repl),
        (sphinx_version_pat, sphinx_version_repl),
    )
    h = '@file ../../docs/index.html'
    home_page = g.findNodeAnywhere(c, h)
    if not home_page:
        g.trace(f"Not found: {h!r}")
        return
    for p in home_page.self_and_subtree():
        old_lines = g.splitLines(p.b)
        new_lines = old_lines[:]
        for i, old_line in enumerate(old_lines):
            new_line = old_line
            for pattern, repl in table:
                new_line = re.sub(pattern, repl, new_line)
                if new_line != old_lines[i]:
                    print('')
                    print(f"Changed line {i:<2} of {p.h}")
                    print(new_line.rstrip())
                    new_lines[i] = old_lines[i] = new_line
        if new_lines != g.splitLines(p.b):
            p.b = ''.join(new_lines)
            print('')
            c.setChanged()
            home_page.setDirty()


# @+node:ekr.20260604044407.4: ** print_git_status
def print_git_status() -> None:
    """Report git status"""
    global g_app
    leo_path = g.os_path_finalize_join(g_app.loadDir, '..', '..')
    os.chdir(leo_path)
    print('')
    g.execute_shell_commands('git status')


# @+node:ekr.20260604044407.8: ** write_intermediate_files
def write_intermediate_files(c: Cmdr) -> bool:
    """Return True if the rst3 command wrote any intermediate files."""
    h = "Leo's Documentation"
    p = g.findTopLevelNode(c, h)
    if not p:
        g.es_print(f"Not found: {h!r}")
        return False
    c.selectPosition(p)
    n = c.rstCommands.rst3()
    if n == 0:
        g.es_print('No intermediate files changed', color='red')
    return n > 0


# @-others

if __name__ == '__main__':
    main()

# @@language python
# @-leo
