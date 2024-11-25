
"""
leo/scripts/sphinx_build.py.

Invoke python/scripts/sphinx_build.exe
"""
g.cls()  ###
import os
import subprocess
import sys
from leo.core import leoGlobals as g

python_exe = sys.executable
python_folder = os.path.dirname(sys.executable)
# script = os.path.normpath(os.path.join(python_folder, 'Scripts', 'sphinx-build.exe'))
script = g.os_path_finalize_join(python_folder, 'Scripts', 'sphinx-build.exe')
assert os.path.exists(script), repr(script)

args = sys.argv
script_s = f'"{script}"'
command = fr"python {script_s}"
print(command, args)
### subprocess.Popen(command, shell=True).communicate()
