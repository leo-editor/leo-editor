# @+leo-ver=5-thin
# @+node:ekr.20260604043712.1: * @file ../scripts/make_sphinx_docs.py
"""
make_sphinx_docs.py:  Regenerate the leo-editor/docs folder.

- Open LeoDocs.leo in Leo's bridge.
- Generate all intermediate files from @rst nodes in LeoDocs.leo.
- Run make-clean.
- Run make-html.
"""

# @@language python

# @+<< make_sphinx_docs: imports and annotations >>
# @+node:ekr.20260604045635.1: ** << make_sphinx_docs: imports and annotations >>
from datetime import datetime

# import glob
import os
import re

# import shutil
from typing import Any, TYPE_CHECKING
from sphinx import __version__ as sphinx_version

import leo.core.leoBridge as leoBridge
from leo.core import leoGlobals as leo_g

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
# @-<< make_sphinx_docs: imports and annotations >>

leo_g.cls()

g: Any = None  # The bridge's g defines g.app.

# @+others
# @+node:ekr.20260604044407.3: ** get_leo_version
conf_version_pat = re.compile(r"version\s*= '([0-9]+\.[0-9]+\.[0-9]+)'")


def get_leo_version(c: Cmdr) -> str:
    """Return the version in conf.py"""
    h = '@edit html/conf.py'
    p = g.findNodeAnywhere(c, h)
    assert p, h
    for m in conf_version_pat.finditer(p.b):
        version = m.group(1)
        if version:
            return version
    assert False, 'no version in conf.py'


# @+node:ekr.20260604044407.7: ** main
def main() -> None:
    """
    Make all html files using sphinx and copy the results to leo-editor/docs.
    """
    g = leo_g
    finalize = g.os_path_finalize_join
    join = os.path.join

    # Base paths. Not finalized.
    docs = join(g.app.loadDir, '..', '..', 'docs')
    doc = join(g.app.loadDir, '..', 'doc')

    # We will cd to the html path.
    html_path = finalize(doc, 'html')

    # We will copy all files from build_path to docs_path.
    build_path = finalize(doc, 'html', '_build', 'html')
    docs_path = finalize(docs)

    # We will copy the static folder from doc/html/_build/html/_static to docs.
    # We *must* use the _build-related path to update sphinx .css files.
    docs_static_path = finalize(docs, '_static')
    ### doc_static_path = finalize(doc, 'html', '_build', 'html', '_static')

    # Step 2: Make sure all paths exist.
    paths = (build_path, docs_path, docs_static_path, html_path)
    fails = [z for z in paths if not g.os_path_exists(z)]
    if fails:
        g.printObj(fails, tag='run: Missing paths...')
        return
    c = open_leo_docs()
    if not c:
        return
    os.chdir(html_path)
    patch_home_page(c)
    write_intermediate_files(c)
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
    global g
    path = leo_g.os_path_finalize_join(__file__, '..', '..', 'doc', 'LeoDocs.leo')

    controller = leoBridge.controller(
        gui='nullGui',
        loadPlugins=False,
        readSettings=False,
        silent=False,
        verbose=True,
    )
    g = controller.globals()
    c = controller.openLeoFile(path)
    if not c:
        print("Can not open: {path}")
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
    leo_path = g.os_path_finalize_join(g.app.loadDir, '..', '..')
    os.chdir(leo_path)
    print('')
    g.execute_shell_commands('git status')


# @+node:ekr.20260604044407.8: ** write_intermediate_files
def write_intermediate_files(c: Cmdr) -> bool:
    """Return True if the rst3 command wrote any intermediate files."""
    g = leo_g
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
# @-leo
