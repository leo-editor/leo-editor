"""
check_leo_sync.py: Verify that LeoPyRef.leo is in sync with the plain
files it mirrors.

leo-editor's own source is tracked both as plain files (.py, .toml, .txt)
and as @file/@clean nodes inside leo/core/LeoPyRef.leo. A plain-file edit
that's never synced back into the outline (via refresh-from-disk) leaves
LeoPyRef.leo stale -- invisible to anyone not using the Leo GUI, until
someone next opens it there and gets a surprise (a resurrected stale node,
a missing file, or a spurious reindent).

This script opens LeoPyRef.leo headlessly and, for every @file/@clean node,
compares what AtFile would derive from the outline against the actual
mirrored file on disk, byte for byte. It exits nonzero (and lists every
mismatch) if anything is out of sync, so drift gets caught in CI instead
of by whoever next opens the outline in the GUI.

Usage:
    python -m leo.scripts.check_leo_sync
"""

import os
import sys

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

# cd to leo-editor, matching this directory's other scripts (flake8_leo.py etc).
leo_editor_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
os.chdir(leo_editor_dir)
sys.path.insert(0, leo_editor_dir)

from leo.core import leoBridge  # noqa: E402


def main() -> int:
    leo_path = os.path.join(leo_editor_dir, 'leo', 'core', 'LeoPyRef.leo')
    bridge = leoBridge.controller(
        gui='nullGui',
        loadPlugins=False,
        readSettings=False,
        silent=True,
        verbose=False,
    )
    c = bridge.openLeoFile(leo_path)
    at = c.atFileCommands

    missing: list[tuple[str, str]] = []
    out_of_sync: list[tuple[str, str, str]] = []
    checked = 0

    for p in c.all_positions():
        if not p.isAnyAtFileNode():
            continue
        h = p.h.strip()
        # @auto/@edit don't have a stable derived-string round-trip to compare.
        if h.startswith(('@auto', '@edit')):
            continue
        if not h.startswith(('@file', '@clean', '@thin', '@shadow', '@nosent')):
            continue
        full = c.fullPath(p)
        if not os.path.exists(full):
            missing.append((h, full))
            continue
        checked += 1
        use_sentinels = not h.startswith('@clean')
        try:
            derived = at.atFileToString(p.copy(), sentinels=use_sentinels)
        except Exception as e:  # pragma: no cover (defensive)
            out_of_sync.append((h, full, f'error deriving content: {e}'))
            continue
        with open(full, 'r', encoding='utf-8', errors='replace') as f:
            disk = f.read()
        if derived != disk:
            out_of_sync.append((h, full, 'content differs from what the outline would write'))

    print(f"checked {checked} @file/@clean nodes in {leo_path}")

    ok = True
    if missing:
        ok = False
        print(f"\n{len(missing)} node(s) reference a file that no longer exists on disk:")
        for h, full in missing:
            print(f"  MISSING: {h} -> {full}")
        print(
            "  (the file was likely renamed or deleted without updating the "
            "matching node's headline in LeoPyRef.leo)"
        )

    if out_of_sync:
        ok = False
        print(f"\n{len(out_of_sync)} node(s) are out of sync with their mirrored file:")
        for h, full, reason in out_of_sync:
            print(f"  DIFF: {h} -> {full} ({reason})")
        print(
            "  (re-sync via leoBridge: c.refreshFromDisk(p) for each node, "
            "then c.fileCommands.save() -- see the leo-editor skill)"
        )

    if ok:
        print("\nLeoPyRef.leo is in sync with all mirrored files.")
        return 0
    return 1


if __name__ == '__main__':
    sys.exit(main())
