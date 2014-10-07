import os
import sys
try:
    import readline
except ImportError:
    pass

overwrite_existing = '--force' in sys.argv

print("""
This script will install `commit-msg` and `pre-commit` hooks in
.../leo-editor/.git/hooks/ to manage Leo build numbers.

If you prefer, copy `commit-msg` and `pre-commit` from
.../leo-editor/leo/extensions/hooks/ to 
.../leo-editor/.git/hooks/ yourself.
""")

prompt = "Continue with installation? yes/N:"
if sys.version_info[0] > 2:
    ans = input(prompt)
else:
    ans = raw_input(prompt)

if ans != 'yes':
    print("Answer was not `yes`, aborting.")
    exit(10)

data = {}
path = os.path.dirname(__file__)
# check everything's going to work before doing anything
for hook in 'commit-msg', 'pre-commit':
    data[hook] = open(os.path.join(path, hook)).read()
    assert hook.strip(), "Emtpy hook file"
    rel_path = os.path.join(path, "..", "..", "..", ".git")
    assert os.path.exists(rel_path)
    rel_path = os.path.join(rel_path, 'hooks', hook)
    rel_path = os.path.abspath(rel_path)
    if os.path.exists(rel_path) and not overwrite_existing:
        print("'%s' already exists, aborting"%rel_path)
        print("Re-run with --force to overwrite existing hooks")
        exit(10)
    data[hook+"PATH"] = rel_path

# ok, now do things
for hook in 'commit-msg', 'pre-commit':
    open(data[hook+"PATH"], 'w').write(data[hook])
    os.chmod(data[hook+"PATH"], 0o744)
    print("Installed "+hook)
