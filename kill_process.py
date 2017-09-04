# coding=utf-8
# !/usr/bin/python
import os
import sys
import subprocess, signal

if __name__ == '__main__':
    p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    out, err = p.communicate()
    args = sys.argv[1:]
    print 'kill keyword: ', args
    for line in out.splitlines():
        if any([it in line for it in args]) and 'kill_process' not in line:
            print 'KILL: ', line
            pid = int(line.split(None, 1)[0])
            os.kill(pid, signal.SIGKILL)
