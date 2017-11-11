''' setuptools_scm module isn't documented in a way I understand,
particularly with regard to version number formatting. Let's explore
and see what we can learn..
'''
import setuptools_scm as scm

print("Default:\t{}\n".format(scm.get_version()))

scm_version_options = {
    'write_to_template': '{tag}',
    'write_to' : 'leo/version.py' # feasible for core/leoVersion to use this?
    }

for s in ['guess-next-dev','post-release']:
    scm.version_scheme = s
    print("{}:\t{}".format(s, scm.get_version()))

  

'''
    what would you want it to look like? Something like:

    Leo 5.6.dev131+g9cdc1356, branch = master
    build 20171031115424, Tue Oct 31 11:54:24 CDT 2017

Build # looks redundant, it's just a compressed time stamp right?
I actually don't want anything, other than to have the same number reported by Leo as is used on PyPi.

'''