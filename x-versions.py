import semantic_version
print('=== Extracting semantic version from git tags ===')

# captured from `git tags > git-tags.txt`
tags='''4-11-a2 5.3 5.4 5.4-b1 5.4.1 5.5 5.5b1 5.6 5.6b1 5.7b1 Bug-135 Bug-149-stage-0-complete Fixed-bug-149 Leo-4-4-8-b1 Leo-4-5-b1 Leo-4-5-b2 Leo-4-5-b3 Leo-5.0-a1 Leo-5.0-a2 Leo-5.0-b1 Leo-5.0-b2 Leo-5.0-final Leo-5.1-b1 Leo-5.1-b2 Leo-5.1-final before-moving-parents-to-vnode before-open-with-work before-until-4-7-final before_unicode_mass_update breaks-auto-completer broke-abbrev last-good-commit last-good-vim last_working_recursive_import leo-4-10-b1 leo-4-10-final leo-4-11-a1 leo-4-11-b1 leo-4-11-final leo-4-4-8-b2 leo-4-4-8-b3 leo-4-4-8-final leo-4-4-8-rc1 leo-4-4-8-rc1-a leo-4-5-1-august-14-2008 leo-4-5-1-final leo-4-5-b4 leo-4-5-final leo-4-5-rc1 leo-4-5-rc2 leo-4-6-1-final-released leo-4-6-2 leo-4-6-b1 leo-4-6-b2 leo-4-6-rc1 leo-4-7-1-final leo-4-7-b1 leo-4-7-b2 leo-4-7-b2-as-released leo-4-7-b3 leo-4-7-final leo-4-7-rc1 leo-4-7-rc1-a leo-4-7-rc1-b leo-4-8-a1 leo-4-8-b1 leo-4-8-final leo-4-8-rc1 leo-4-9-b1 leo-4-9-b2 leo-4-9-b4 leo-4-9-final leo-4-9-rc1 leo-4-9-rc1-a leo-5.0-a1 old-rst-code-last-rev v5.2 v5.3'''.split()

valid = {}
skipped = []
for t in tags:
    try:
        tc = t
        if t.lower().startswith('leo-'): tc = t[4:]
        if t.lower().startswith('v'): tc = t[1:]
        v = semantic_version.Version.coerce(tc, partial=True)
        valid[t] = tc
    except ValueError:
        skipped.append(t)

print('\n--- PARSED ---\n')
longest = len(max(valid.keys(), key=len)) # length of longest element in list
for k,v in valid.items():
    print('{0:<{1}} -->\t{2}'.format(k,longest,v))

print('\n--- SKIPPED ---\n')
[print(x) for x in skipped]


def thankyou():
    print('''Thank you to:
    
    @Paolo_Bergantino, longest item in list:
        https://stackoverflow.com/questions/873327/pythons-most-efficient-way-to-choose-longest-string-in-list
    @EbraHim, use variable in format string:
        https://stackoverflow.com/questions/36962995/format-in-python-by-variable-length
    
    ''') 
# (c) 2018 Matt Wilkie, maphew@gmail.com
# License: X/MIT Open Source
