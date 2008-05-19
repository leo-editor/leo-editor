# This file makes the leo directory a package.

# The function allows the following code to work::
#
#     import leo
#     leo.run()

def run(*args,**keys):
    import pdb ; pdb = pdb.set_trace
    import leo.core.runLeo as runLeo
    runLeo.run(*args,**keys)

