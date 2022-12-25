#!/usr/bin/env python3

import os
import sys
import time
from subprocess import Popen, PIPE, TimeoutExpired


def get_servers():
    HOME = os.getenv('HOME')
    with open(os.path.join(HOME, 'servers', 'all-locations')) as f:
        return ['ddnet.org'] + [s + '.ddnet.org' for s in f.readline().strip('\n').split()]

def main():
    if len(sys.argv) <= 1:
        print('No broadcast given.')
        exit(1)

    bc = 'broadcast "' + ' '.join(sys.argv[1:]).replace('\\', '\\\\').replace('"', '\\"') + '"'
    processes = []
    for srv in get_servers():
        p = Popen(['ssh', srv, 'cat > servers/servers/*.fifo', ], stdin=PIPE, stdout=sys.stdout, stderr=sys.stderr)
        p.stdin.write(bytes(bc, encoding='utf-8'))
        p.stdin.close()
        processes.append((srv, p))

    t0 = time.time()
    tend = t0 + 30
    failed = False

    for srv, p in processes:
        td = tend - time.time()
        if td < 0.2:
            td = 0.2
        try:
            if p.wait(td) != 0:
                failed = True
        except TimeoutExpired:
            p.kill()
            failed = True
        if failed:
            print('Error:', srv, 'is unreachable.')

    print('Done.')

main()
