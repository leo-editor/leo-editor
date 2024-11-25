
"""
leo/scripts/sphinx_build.py.

Invoke python/scripts/sphinx_build.exe
"""
import os
import subprocess
import sys

# Find python/Scripts/sphinx-build.exe.
python_folder = os.path.dirname(sys.executable)
script = os.path.normpath(os.path.join(
    python_folder, 'Scripts', 'sphinx-build.exe'))
assert os.path.exists(script), repr(script)

# Create a command that executes python/Scripts/sphinx-build.exe.
args_s = ' '.join(sys.argv[1:])
script_s = f'"{script}" {args_s}'
command = fr"python {script_s}"

# Print and execute the command!
print(f"sphinx_build.py: {command}\n")
subprocess.Popen(command, shell=True).communicate()
