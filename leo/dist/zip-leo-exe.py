"""Quick script to package up Leo.exe created by pyinstaller

    leo-editor/leo/dist - this script
    leo-editor/dist/leo - leo.exe with all dependencies
"""
import os
import shutil
from datetime import date
import leo.core.leoVersion as leov

here = os.path.abspath(os.path.dirname(__file__))
dist = os.path.join(here, "../../dist")

os.chdir(dist)
datestamp = date.today().isoformat()
shutil.make_archive(f"{leov.version}-{datestamp}", "zip", "leo")

print(f"Packaged {dist}/{leov.version}-{datestamp}.zip")
