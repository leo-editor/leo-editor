# @+leo-ver=5-thin
# @+node:ekr.20260604043712.1: * @file ../scripts/make_sphinx_docs.py
"""
make_sphinx_docs.py:  Regenerate the leo-editor/docs folder.

- Open LeoDocs.leo in Leo's bridge.
- Generate all intermediate files from @rst nodes in LeoDocs.leo.
- Patch index.html.
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


def get_leo_version(conf_path: str) -> str:
    """Return the version in conf.py"""
    try:
        with open(conf_path, 'rb') as f:
            s = g.toUnicode(f.read())
        for line in g.splitLines(s):
            if m := conf_version_pat.match(line):
                return m.group(1).strip()
        return ''
    except Exception:
        return ''


# @+node:ekr.20260604044407.7: ** main
def main() -> None:
    """
    Make all html files using sphinx and copy the results to leo-editor/docs.
    """
    # Open LeoDocs.leo in the bridge and set g_app global.
    c = open_leo_docs()
    if not c:
        return

    # Compute paths.
    finalize = g.os_path_finalize_join
    docs_path = html_path = finalize(g_app.loadDir, '..', '..', 'docs')
    if not os.path.exists(docs_path):
        print(f"Not found: {docs_path!r}")
        return
    docs_static_path = finalize(docs_path, '_static')
    if not os.path.exists(docs_static_path):
        print(f"Not found: {docs_static_path!r}")
        return
    conf_path = finalize(docs_path, 'html', 'conf.py')
    if not os.path.exists(conf_path):
        print(f"Not found: {conf_path!r}")
        return

    # Get version from
    os.chdir(html_path)
    if version := get_leo_version(conf_path):
        print(f"Found Leo version: {version}")
    else:
        print(f"no version in {conf_path}")
        return
    patch_home_page(c, docs_path, version)
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


def patch_home_page(c: Cmdr, docs_path: str, version: str) -> None:
    """
    Update (in *this*file) the "Last updated" and "Created using" fields in
    the node `@file ../../docs/index.html` or its descendants.
    """
    today = datetime.today()
    date = datetime.date(today).strftime("%B %d, %Y")  # Same as conf.py.

    def date_repl(m: re.Match) -> str:
        s = m.group(0)
        i, j = m.start(3), m.end(3)
        return s[:i] + date + s[j:]

    def leo_version_repl(m: re.Match) -> str:
        s = m.group(0)
        i, j = m.start(2), m.end(2)
        return s[:i] + version + s[j:]

    def sphinx_version_repl(m: re.Match) -> str:
        s = m.group(0)
        i, j = m.start(2), m.end(2)
        return s[:i] + sphinx_version + s[j:]

    table = (
        (date_pat, date_repl),
        (leo_version_pat, leo_version_repl),
        (sphinx_version_pat, sphinx_version_repl),
    )

    # Perform the substitutions directly in index.html.
    index_path = g.os_path_finalize_join(docs_path, 'index.html')
    try:
        with open(index_path, 'r+') as f:
            s = g.toUnicode(f.read())
            old_lines = g.splitLines(s)
            new_lines = old_lines[:]
            for i, line in enumerate(g.splitLines(s)):
                for pattern, repl in table:
                    line = re.sub(pattern, repl, line)
                    if line != old_lines[i]:
                        print('')
                        print(f"Changed line {i:<2} of index.html")
                        print('old:', old_lines[i].rstrip())
                        print('new:', line.rstrip())
                        break
            if False and new_lines != old_lines:  ###
                f.seek(0)
                f.write(''.join(new_lines))
                f.truncate()
    except Exception:
        g.es_exception()


# @+node:ekr.20260604044407.4: ** print_git_status
def print_git_status() -> None:
    """Report git status"""
    leo_path = g.os_path_finalize_join(g_app.loadDir, '..', '..')
    os.chdir(leo_path)
    print('')
    print('git status')
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
