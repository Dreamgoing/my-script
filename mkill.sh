#!/bin/bash -e
echo "$1 $2 $*"
exec /usr/bin/python ./myscript/kill_process.py $*
