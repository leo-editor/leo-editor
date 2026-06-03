# @+leo-ver=5-thin
# @+node:ekr.20240323050520.1: * @file ../scripts/beautify_all_leo.py
# @@language python

"""
beautify_all_leo.py: Beautify (almost) all of Leo's files.

Info item #3867 describes all of Leo's test scripts:
https://github.com/leo-editor/leo-editor/issues/2867

EKR's beautify-all-leo.cmd:
    cd {path-to-leo-editor}
    python -m leo.scripts.beautify_all_leo
"""

import os
import subprocess
import sys

print(os.path.basename(__file__))

# cd to leo-editor
leo_editor_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
os.chdir(leo_editor_dir)

# Define components of a single command.
toml_file = f"{leo_editor_dir}{os.sep}pyproject.toml"
assert os.path.exists(toml_file), toml_file
args = " ".join(
    (
        f"--config {toml_file}",
        # '--verbose',
    )
)
targets = (
    f"leo{os.sep}commands",
    f"leo{os.sep}core",
    f"leo{os.sep}external",
    f"leo{os.sep}modes",
    f"leo{os.sep}plugins",
    f"leo{os.sep}scripts",
    f"leo{os.sep}unittests",
)
# Use -m so that __name__ == '__main__'.
python = sys.executable
command = f"{python} -m ruff format {args} {' '.join(targets)}"
subprocess.Popen(command, shell=True).communicate()
# @-leo
