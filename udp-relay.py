#!/usr/bin/env python
# Super simple script that listens to a local UDP port and relays all packets to an arbitrary remote host.
# Packets that the host sends back will also be relayed to the local UDP client.
# Works with Python 2 and 3

import sys, socket

num = 64

def fail(reason):
  sys.stderr.write(reason + '\n')
  sys.exit(1)

if len(sys.argv) != 2 or len(sys.argv[1].split(':')) != 3:
  fail('Usage: udp-relay.py localPort:remoteHost:remotePort')

localPort, remoteHost, remotePort = sys.argv[1].split(':')

try:
  localPort = int(localPort)
except:
  fail('Invalid port number: ' + str(localPort))
try:
  remotePort = int(remotePort)
except:
  fail('Invalid port number: ' + str(remotePort))

s = []
for i in range(num):
  port = localPort + i
  try:
    x = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    x.bind(('', port))
    s.append(x)
  except:
    fail('Failed to bind on port ' + str(port))

knownClient = None
knownServer = (remoteHost, remotePort)
sys.stderr.write('All set.\n')
while True:
  data, addr = s[0].recvfrom(32768)
  if knownClient is None:
    knownClient = addr
  if addr == knownClient:
      for i in range(num):
        s[i].sendto(data, knownServer)
  else:
    s[0].sendto(data, knownClient)
