# Reported paths

    dirs = [launchLeo, sys.executable, g.app.leoDir, g.app.loadDir, g.app.globalConfigDir, g.app.homeDir]

From Leo, launched from `leo-messages` from `pip install --editable`:

    C:/users/mattw/code/leo-editor/launchLeo.py
    c:\apps\miniconda3\envs\leo-dev\python.exe
    C:/users/mattw/code/leo-editor/leo
    C:/users/mattw/code/leo-editor/leo/core
    C:/users/mattw/code/leo-editor/leo/config
    C:/Users/mattw

From Leo in Admin CMD shell and no python on PATH:

    $ c:\apps\miniconda3\envs\leo-dev\python.exe leo-editor\launchLeo.py Leo-matt.leo

    Leo 5.8.1-b2 devel, build 20190216150955, Sat Feb 16 15:09:54 PST 2019
    ---
    C:/Users/mattw/code/leo-editor/launchLeo.py
    c:\apps\miniconda3\envs\leo-dev\python.exe
    C:/Users/mattw/code/leo-editor/leo
    C:/Users/mattw/code/leo-editor/leo/core
    C:/Users/mattw/code/leo-editor/leo/config
    C:/Users/mattw

From Leo in user CMD shell, conda environment, normal pip install

    C:/apps/miniconda3/envs/leo/lib/site-packages/launchLeo.py
    c:\apps\miniconda3\envs\leo\pythonw.exe
    C:/apps/miniconda3/envs/leo/lib/site-packages/leo
    C:/apps/miniconda3/envs/leo/lib/site-packages/leo/core
    C:/apps/miniconda3/envs/leo/lib/site-packages/leo/config
    C:/Users/mattw