# Extra line, so perfect import will work.
try:
    import leo.core.leoGlobals as leo_g
    # leo_g.pr('IMPORT pyzo.util')
except Exception:
    leo_g = None
