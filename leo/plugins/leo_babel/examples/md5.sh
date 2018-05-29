#@+leo-ver=5-thin
#@+node:bob.20170830131933.1: * @file md5.sh
#@@language shell

for fpn in "$@" ; do
    md5sum $fpn
done
#@-leo
