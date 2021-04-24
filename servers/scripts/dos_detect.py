#!/usr/bin/env python3
import os
import time
import collections

INTERVAL = 10

# Traffic class adapted from BotoX' ServerStatus: https://github.com/BotoX/ServerStatus
class Traffic:
    def __init__(self):
        self.rx = collections.deque(maxlen=10)
    def get(self):
        f = open('/proc/net/dev', 'r')
        net_dev = f.readlines()
        f.close()
        avgrx = 0

        for dev in net_dev[2:]:
            dev = dev.split(':')
            if dev[0].strip() == "lo" or dev[0].find("tun") > -1:
                continue
            dev = dev[1].split()
            avgrx += int(dev[0])

        self.rx.append(avgrx)
        avgrx = 0

        l = len(self.rx)
        for x in range(l - 1):
            avgrx += self.rx[x+1] - self.rx[x]

        avgrx = int(avgrx / l / INTERVAL)

        return avgrx

def main():
    traffic = Traffic()
    traffic.get()
    bad = collections.deque(maxlen=10)
    while True:
        netrx = traffic.get()
        ping = os.system("ping -c 1 master.ddnet.tw > /dev/null") == 0
        if netrx > 3_000_000 or not ping:
            bad.append(1)
        else:
            bad.append(0)
        if sum(bad) > 7:
            os.system("for i in /home/teeworlds/servers/servers/8*.fifo; do echo conn_timeout_protection 3600 > $i & done")
        time.sleep(INTERVAL)

if __name__ == '__main__':
    main()
