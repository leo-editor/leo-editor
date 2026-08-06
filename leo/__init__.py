# This file makes the leo directory a package.

# The function allows the following code to work::
#
#     import leo
#     leo.run()


def run(*args, **keys):  # pragma: no cover
    # import pdb; pdb = pdb.set_trace  # type: ignore[assignment]
    from leo.core import runLeo

    runLeo.run(*args, **keys)
