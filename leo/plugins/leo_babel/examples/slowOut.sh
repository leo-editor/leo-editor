#@+leo-ver=5-thin
#@+node:bob.20170716135026.1: * @file examples/slowOut.sh
#@@language shell

for xxx in 1 2 3 4 5;
    do
        echo stdout $xxx
        if [[ ($xxx == 2) || ($xxx == 4) ]] ; then
            (>&2 echo stderr $xxx);
        fi
        sleep 3s
    done;
#@-leo
