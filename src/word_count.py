# coding: utf-8
from __future__ import print_function
import pprint
import sys
import re
import subprocess
from collections import defaultdict, Counter


def is_match(regexes, filename):
    return any([bool(it.match(filename)) for it in regexes])


if __name__ == '__main__':
    args = sys.argv[1:]
    print('input file', args)
    regexes = [re.compile(it) for it in args]
    # Equal to list(map(re.compile, args))

    p = subprocess.Popen(['ls', '-m'], stdout=subprocess.PIPE)
    out, err = p.communicate()
    cnt = Counter()

    for item in out.split():
        item = item.decode('utf-8').strip(',')
        if is_match(regexes, str(item)):
            print('Read file:', item)
            with open(item, 'r') as f:
                words = re.findall(r'\w+', f.read())
                cnt += Counter(words)

    pprint.pprint(cnt.most_common(10))
