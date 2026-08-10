"""
build_docs.py: Regenerate Leo's documentation from leo/doc/LeoDocs.leo.

Two-stage pipeline, both stages driven headlessly (no Leo GUI needed):

1. Run Leo's rst3 command over the LeoDocs.leo outline. This writes the
   reStructuredText intermediate files (leo/doc/html/*.html.txt and
   leo/doc/html/slides/**/*.html.txt) from the bodies of its @rst nodes.
   readSettings=True so the outline's own @settings tree is honored --
   in particular @bool rst3_call_docutils = False, which keeps this stage
   from invoking docutils itself; Sphinx does that in stage 2.
2. Run sphinx-build over leo/doc/html (using its conf.py/Makefile config)
   to turn those intermediates into final HTML.

Usage:
    python -m leo.scripts.build_docs [--out DIR]
"""

import argparse
import glob
import os
import shutil
import subprocess
import sys

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

leo_editor_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
os.chdir(leo_editor_dir)
sys.path.insert(0, leo_editor_dir)

from leo.core import leoBridge  # noqa: E402


def run_rst3() -> int:
    """Regenerate the .html.txt intermediates from LeoDocs.leo. Return the count written."""
    leo_path = os.path.join(leo_editor_dir, 'leo', 'doc', 'LeoDocs.leo')
    bridge = leoBridge.controller(
        gui='nullGui',
        loadPlugins=False,
        readSettings=True,
        silent=True,
        verbose=False,
    )
    c = bridge.openLeoFile(leo_path)
    # rst3() only searches the subtree of the current position (see
    # g.findRootsWithPredicate), and @rst trees are scattered across many
    # top-level nodes in LeoDocs.leo -- not gathered under one parent.
    # Run it once per top-level tree so every @rst node gets picked up.
    total = 0
    for p in c.rootPosition().self_and_siblings(copy=False):
        c.selectPosition(p)
        total += c.rstCommands.rst3()
    return total


def run_sphinx(out_dir: str) -> int:
    html_dir = os.path.join(leo_editor_dir, 'leo', 'doc', 'html')
    cmd = ['sphinx-build', '-b', 'html', html_dir, out_dir]
    print(' '.join(cmd))
    return subprocess.call(cmd)


def copy_home_page(out_dir: str) -> str:
    """Copy Leo's hand-maintained home page into the Sphinx output directory."""
    source = os.path.join(leo_editor_dir, 'docs', 'index.html')
    target = os.path.join(out_dir, 'index.html')
    shutil.copy2(source, target)
    return target


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--out',
        default=os.path.join(leo_editor_dir, 'leo', 'doc', 'html', '_build', 'html'),
        help='Directory to write the built HTML to.',
    )
    args = parser.parse_args()

    n = run_rst3()
    print(f"rst3: wrote {n} changed intermediate file(s)")
    # n only counts files that *changed*; on a no-op rebuild it's legitimately 0.
    # Check existence instead, as a sanity gate before handing off to sphinx-build.
    html_dir = os.path.join(leo_editor_dir, 'leo', 'doc', 'html')
    existing = glob.glob(os.path.join(html_dir, '*.html.txt'))
    if not existing:
        print("ERROR: no .html.txt intermediates found -- check LeoDocs.leo", file=sys.stderr)
        return 1

    rc = run_sphinx(args.out)
    if rc == 0:
        home_page = copy_home_page(args.out)
        if not os.path.isfile(home_page):
            print(f"ERROR: home page was not created: {home_page}", file=sys.stderr)
            return 1
        print(f"sphinx-build OK -> {args.out}")
    return rc


if __name__ == '__main__':
    sys.exit(main())
