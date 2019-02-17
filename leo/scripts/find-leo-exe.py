import os
import sys
print(sys.executable)

exe_dir = os.path.join(os.path.dirname(sys.executable), 'Scripts') 
matches = []
for s in os.listdir(exe_dir):
    if 'leo' in s:
        matches.append(s)
# TODO: figure out what scripts are called when on linux and mac

print(exe_dir)
print(matches)




#launchLeo = g.os_path_finalize_join(g.computeLeoDir(), '../launchLeo.py')
    # breaks when Leo installed under PYTHONHOME (ie: Lib/site-packages and Scripts)

#dirs = [launchLeo, sys.executable, g.app.leoDir, g.app.loadDir, g.app.globalConfigDir, g.app.homeDir]
#g.es_print('---')
#[g.es_print(x) for x in dirs]
# for d in dirs:
    # g.es_print(d, g.os_path_exists(d))

# if 'site-packages' in g.app.loadDir:
    # g.es_print('not running from source checkout')
    # script_dir = g.os_path_finalize_join(g.os_path_dirname(sys.executable), 'Scripts')
    # g.es_print(script_dir, g.os_path_exists(script_dir))
    # if g.os_path_exists(g.os_path_finalize_join(script_dir, 'leo.exe')):
        # g.es_print(g.os_path_finalize_join(script_dir, 'leo'))
