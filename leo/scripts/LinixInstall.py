#!/usr/bin/python

"""
A simple script to install Leo on Linux.

Contributed by David McNab <david@rebirthing.co.nz>
"""

import commands, os, sys  # commands module is for Unix only.

# We must be root to use this script.
if os.getuid() != 0:
    print("You need to run this install script as root")
    sys.exit(1)

# Create /usr/lib/leo and copy all files there.
print("***** Installing Leo to /usr/lib/leo...")
commands.getoutput("mkdir -p /usr/lib/leo")
commands.getoutput("cp -rp * /usr/lib/leo")

# Create user's 'leo' command script into /usr/bin/leo
print("***** Creating Leo startup script -> /usr/bin/leo")
fd = open("/usr/bin/leo", "w")
fd.write("""#!/usr/bin/python
import commands,sys
files = " ".join(sys.argv[1:])
print(commands.getoutput("python /usr/lib/leo/leo.py %s" % files))
""")
fd.close()
commands.getoutput("chmod 755 /usr/bin/leo")
print("***** Leo installed successfully - type 'leo filename.leo' to use it.")
