# requires python 3.5+
# for this style of subprocess.run()
import os
import leo
import leo.core.leoGlobals as g
import subprocess

sc_path = os.path.realpath(os.path.join(leo.__path__[0], 'scripts/win'))
elevate = os.path.join(sc_path, 'elevate.py')
register = os.path.join(sc_path, 'register-leo.leox')
unregister = os.path.join(sc_path, 'unregister-leo.leox')

g.es_print('--- Running elevate and register')
result = subprocess.run(['python', elevate, register], stdout=subprocess.PIPE)
g.es_print(result.stdout.decode('utf-8'))
g.es_print('---')
