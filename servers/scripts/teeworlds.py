#!/usr/bin/env python2

#  A library to get the serverlist & information for Teeworlds servers
#  Copyright (C) 2011  m!nus <m1nus@online.de>
#
#  This software is provided 'as-is', without any express or implied
#  warranty.  In no event will the authors be held liable for any damages
#  arising from the use of this software.
#
#  Permission is granted to anyone to use this software for any purpose,
#  including commercial applications, and to alter it and redistribute it
#  freely, subject to the following restrictions:
#
#  1. The origin of this software must not be misrepresented; you must not
#     claim that you wrote the original software. If you use this software
#     in a product, an acknowledgment in the product documentation would be
#     appreciated but is not required.
#  2. Altered source versions must be plainly marked as such, and must not be
#     misrepresented as being the original software.
#  3. This notice may not be removed or altered from any source distribution.


from __future__ import print_function
import sys
import socket
import time
from random import randint
from struct import unpack
import select
import re

try:
    from importlib import reload
    import queue
except ImportError:
    import Queue as queue

if sys.version_info.major < 3:
    # UTF-8 is required as default encoding
    reload(sys)
    sys.setdefaultencoding('utf8')


def log(level, str):
  if level is 'debug': return
  print("[{0: <5}] {1}".format(level, str), file=sys.stderr)


def is_ipv6(address):
  if isinstance(address, tuple): address = address[0]
  return True if ':' in address else False

def intUnpack(n):
  print(n,file=sys.stderr)
  pSrc = n[0]
  Sign = (pSrc>>6)&1
  InOut = int(pSrc&0x3F)

  while True:
    if not pSrc&0x80:
      break
    pSrc = n[1]
    pInOut |= (pSrc&0x7F)<<(6)

    if not pSrc&0x80:
      break
    pSrc = n[2]
    pInOut |= (pSrc&0x7F)<<(6+7)

    if not pSrc&0x80:
      break
    pSrc = n[3]
    pInOut |= (pSrc&0x7F)<<(6+7+7)

    if not pSrc&0x80:
      break
    pSrc = n[4]
    pInOut |= (pSrc&0x7F)<<(6+7+7+7)
    break

  pSrc = n[5]
  pInOut ^= -Sign
  return pSrc

class MultiSocket(object):
  READ = 1
  WRITE = 2
  EXCEPTION = 4

  def __init__(self, timeout=None, interval=0, port=None):
    self.sockets = {}
    self.queue_out = queue.Queue()
    self.timeout = timeout
    self.interval = interval
    self.sockets[socket.AF_INET] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.SOL_UDP)
    self.sockets[socket.AF_INET].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #if port:
    #    original_port = port
    #    success = False
    #    while not success:
    #        try:
    #            self.sockets[socket.AF_INET].bind(('', port))
    #            success = True
    #        except socket.error as e:
    #            if e.errno != 98:
    #              raise
    #            port += 1
    #            if port > original_port + 9:
    #                raise
    self.has_ipv6 = socket.has_ipv6
    if self.has_ipv6:
      self.sockets[socket.AF_INET6] = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.SOL_UDP)
      self.sockets[socket.AF_INET6].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

  def select(self, type=None, timeout=None):
    timeout = self.timeout if timeout == None else timeout
    list_r = self.sockets.values() if (type&self.READ or type==None) else []
    list_w = self.sockets.values() if type&self.WRITE else []
    list_x = self.sockets.values() if type&self.EXCEPTION else []
    ret = select.select(list_r, list_w, list_x, timeout)
    if ret == ([], [], []):
      raise socket.timeout('select timed out')
    else:
      return ret

  def sendto(self, data, address):
    if is_ipv6(address):
      if not self.has_ipv6: return 0
      return self.sockets[socket.AF_INET6].sendto(data, address)
    else:
      return self.sockets[socket.AF_INET].sendto(data, address)

  def sendto_q(self, data, address, callback=None):
    self.queue_out.put((data, address, callback))

  def recvfrom(self, len):
    try:
      s = self.sockets.values()
      (r, w, x) = select.select(s, [], [], self.timeout)
      if not r and not w and not x:
        raise socket.timeout('select timed out')
      for sock in r:
        return sock.recvfrom(len)
    except socket.error as e:
      # Errno 10054 happens when we get ICMP port unreachable, we don't care about that
      if e.errno != 10054:
        raise
    # in case if error 10054 just retry
    # TODO: might reach maximum recursion
    return self.recvfrom(len)

  def process_queue(self, amount):
    for _ in range(amount):
      if not self.queue_out.empty():
        (data, address, callback) = self.queue_out.get()
        if self.sendto(data, address) == len(data):
          if hasattr(callback, '__call__'): callback(time.time())
        else:
          log('warning', 'failed to send whole packet, requeuing')
          self.queue_out.put((data, address, callback))


class Handler(object):
  def match(self, **kwargs):
    for name, value in kwargs.iteritems():
      if hasattr(self, name) and getattr(self, name) != value:
        return False
    return True

  def call(self, address, data):
    pass


class HandlerStorage(object):
  def __init__(self):
    self.handlers = []

  def add(self, handler):
    if isinstance(handler, list):
      self.handlers += handler
    else:
      self.handlers.append(handler)

  def remove(self, handler):
    if isinstance(handler, list):
      for item in handler:
        self.handlers.remove(item)
    else:
      self.handlers.remove(handler)

  def find(self, **kwargs):
    return [handler for handler in self.handlers if handler.match(**kwargs)]

  def __repr__(self):
    return str(self.handlers)


class MasterServer(Handler):
  _packet_count_request = 10*b'\xff' + b'cou2'
  _packet_count_response = 10*b'\xff' + b'siz2'
  _packet_list_request = 10*b'\xff' + b'req2'
  _packet_list_response = 10*b'\xff' + b'lis2'
  _serveraddr_size = 18

  def __init__(self, parent, address, name='none given'):
    self._parent = parent
    self._address = address
    self.address = ("[{host}]:{port}" if is_ipv6(address) else "{host}:{port}") \
          .format(host=address[0], port=address[1])
    #self.data = self._packet_list_response
    self.name = name
    self.latency = -1
    self.serverlist = ServerList()
    self.server_count = -1

  def request(self):
    self.request_time = time.time()
    self._parent.socket.sendto_q(10 * b'\xff' + b'req2', self._address, self.request_callback)
    self.server_count = 0

  def request_callback(self, request_time):
    self.request_time = request_time

  def add_from_serverlist(self, data):
    if len(data) % self._serveraddr_size != 0:
      raise Exception("Address packet's size not multiple of the server " + \
          "address struct's size: {datalen}%{addrsize}={modulo} data={data}" \
          .format(datalen=len(data), addrsize=self._serveraddr_size, \
              modulo=(len(data)%self._serveraddr_size), \
              data=' '.join([ "{0:2x}".format(ord(x)) for x in data ])))
    for i in xrange(0, len(data), self._serveraddr_size):
      if data[0:12] == b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff": # ::ffff:... == IPv4
        serverAddress = (socket.inet_ntoa(data[i+12:i+16]), unpack("!H", data[i+16:i+18])[0])
      else:
        # TODO: workaround for windows as inet_ntop doesn't exist there
        if sys.platform == "win32":
          log('warning', "Can't make IPv6 address on windows from binary: {0!r}".format(data[i:i+16]))
          continue
        serverAddress = (socket.inet_ntop(socket.AF_INET6, data[i:i+16]), unpack("!H", data[i+16:i+18])[0])
      server = Server(self._parent, serverAddress, master=self)
      server.request()
      self._parent.serverlist.add(server)
      self.serverlist.add(server)

  def call(self, address, data):
    count_header_len = len(self._packet_count_response)
    if data[0:count_header_len] == self._packet_count_response:
      self.latency = time.time() - self.request_time
      self.server_count += unpack('!H', data[count_header_len:count_header_len+2])[0]
    self.add_from_serverlist(data[len(self._packet_list_response):])

  def match(self, **kwargs):
    if not kwargs.has_key("address") or kwargs["address"] != self._address:
      return False
    if not kwargs.has_key("data") or kwargs["data"][0:len(self._packet_list_response)] != self._packet_list_response:
      return False
    return True

  def __repr__(self):
    return "<MasterServer name='{name}' address='{address}' servers='{servers}'>" \
      .format(name=self.name, address=self.address, servers=self.server_count)


class Server(Handler):
  _packet_request = 10*b'\xff' + b'gie3'
  _packet_response = 10*b'\xff' + b'inf3'


  def __init__(self, parent, address, master=None):
    self._address = address
    self.address = ("[{host}]:{port}" if is_ipv6(address) else "{host}:{port}") \
          .format(host=address[0], port=address[1])
    self._parent = parent
    self.master = master
    self.data = None
    self.packets_received = 0
    self.reset()

  def reset(self):
    self.latency = -1
    self.playerlist = PlayerList()
    self.version = None
    self.name = self.address
    self.map = None
    self.gametype = None
    self.password = None
    self.players = -1
    self.max_players = -1
    self.clients = -1
    self.max_clients = -1
    self.packets_received = 0

  def request(self):
    #log('debug', "Server-ping to " + self.address)
    self.token = chr(randint(1,255))
    self.data = self._packet_response + str(ord(self.token)) + b'\x00'
    self.request_time = time.time()
    self._parent.socket.sendto_q(self._packet_request + self.token, self._address, self.request_callback)
    self._parent.add_handler(self)

  def request_callback(self, request_time):
    self.request_time = request_time

  def call(self, address, data):
    #log('debug', "Server-callback hit from " + address)
    self.packets_received += 1
    self.parse(data[len(self.data):])

  def parse(self, data):
    self.latency = time.time() - self.request_time
    data = iter(data.split(b'\x00'))
    try:
      self.version = data.next().decode('utf8')
      self.name = data.next().decode('utf8')
      self.map = data.next().decode('utf8')
      self.gametype = data.next().decode('utf8')
      self.password = (data.next()=='1')
      self.players = int(data.next())
      self.max_players = int(data.next())
      self.clients = int(data.next())
      self.max_clients = int(data.next())
      for _ in range(self.clients):
        player = Player()
        try:
          player.name=data.next().decode('utf8')
        except:
          player.name=""
        try:
          player.clan=data.next().decode('utf8')
        except:
          player.clan=""
        try:
          player.country = int(data.next())
        except:
          player.country = 0
        try:
          player.score = int(data.next())
        except:
          player.country = 0
        player.playing = (data.next()=='1')
        player.server = self
        # Only one player with same name possible, ignore all others. There is
        # currently a bug on Chile where each packet is received 5 times.
        if not self.playerlist.contains(player.name):
          self.playerlist.add(player)
    except StopIteration:
      self.reset()
      # Ignore this as it is caused by rate limit of info packets
      #log('warning', 'unexpected end of data for server ' + str(self))
    for player in self.playerlist:
      self._parent.playerlist.add(player)

  def match(self, **kwargs):
    if not kwargs.has_key("address") or kwargs["address"] != self._address:
      return False
    if not kwargs.has_key("data") or kwargs["data"][0:len(self.data)] != self.data:
      return False
    return True

  def __repr__(self):
    return "<Server name='{name}' address='{address}'>" \
      .format(name=self.name, address=self.address)


class Server64(Handler):
  _packet_request = 10*b'\xff' + b'fstd'
  _packet_response = 10*b'\xff' + b'dtsf'


  def __init__(self, parent, address, master=None):
    self._address = address
    self.address = ("[{host}]:{port}" if is_ipv6(address) else "{host}:{port}") \
          .format(host=address[0], port=address[1])
    self._parent = parent
    self.master = master
    self.data = None
    self.reset()
    self.packets_received = 0

  def reset(self):
    self.latency = -1
    self.playerlist = PlayerList()
    self.version = None
    self.name = self.address
    self.map = None
    self.gametype = None
    self.password = None
    self.players = -1
    self.max_players = -1
    self.clients = -1
    self.max_clients = -1
    self.packets_received = 0

  def request(self):
    #log('debug', "Server-ping to " + self.address)
    self.token = chr(randint(1,255))
    self.data = self._packet_response + str(ord(self.token)) + b'\x00'
    self.request_time = time.time()
    self._parent.socket.sendto_q(self._packet_request + self.token, self._address, self.request_callback)
    self._parent.add_handler(self)

  def request_callback(self, request_time):
    self.request_time = request_time

  def call(self, address, data):
    #log('debug', "Server-callback hit from " + address)
    self.packets_received += 1
    self.parse(data[len(self.data):])

  def parse(self, data):
    self.latency = time.time() - self.request_time
    data = iter(data.split(b'\x00'))
    try:
      self.version = data.next().decode('utf8')
      self.name = data.next().decode('utf8')
      self.map = data.next().decode('utf8')
      self.gametype = data.next().decode('utf8')
      self.password = (data.next()=='1')
      self.players = int(data.next())
      self.max_players = int(data.next())
      self.clients = int(data.next())
      self.max_clients = int(data.next())

      if self.clients:
        n = data.next()
        offset = 0
        next = None

        if len(n) > 0:
          offset = ord(n[0])
          next = n[1:]

        nr = 24
        if (self.clients <= offset + 24):
          nr = self.clients - offset

        try:
          for _ in range(nr):
            player = Player()
            try:
              if not next:
                next = data.next()
              player.name=next.decode('utf8')
              next = None
            except:
              player.name=""
            try:
              player.clan=data.next().decode('utf8')
            except:
              player.clan=""
            try:
              player.country = int(data.next())
            except:
              player.country = 0
            try:
              player.score = int(data.next())
            except:
              player.score = 0
            player.playing = (data.next()=='1')
            player.server = self
            # Only one player with same name possible, ignore all others. There is
            # currently a bug on Chile where each packet is received 5 times.
            if not self.playerlist.contains(player.name):
              self.playerlist.add(player)
        except StopIteration:
          pass
    except StopIteration:
      self.reset()
      # Ignore this as it is caused by rate limit of info packets
      #log('warning', 'unexpected end of data for server ' + str(self))
    for player in self.playerlist:
      self._parent.playerlist.add(player)

  def match(self, **kwargs):
    if not kwargs.has_key("address") or kwargs["address"] != self._address:
      return False
    if not kwargs.has_key("data") or kwargs["data"][0:len(self.data)] != self.data:
      return False
    return True

  def __repr__(self):
    return "<Server name='{name}' address='{address}'>" \
      .format(name=self.name, address=self.address)


class Player(object):
  def __init__(self):
    self.name = ''
    self.clan = ''
    self.country = None
    self.score = None
    self.server = None
    self.playing = False

  def __repr__(self):
    return "<Player name='{name}'>".format(name=self.name)


class ServerList(object):
  def __init__(self):
    self.servers = []

  def add(self, server):
    if not isinstance(server, Server) and not isinstance(server, Server64):
      raise Exception('Trying to add non-Server object')
    self.servers.append(server)

  def find(self, name=None, gametype=None, maxping=None):
    output = ServerList()
    if name: name = re.compile(name, re.IGNORECASE)
    if gametype: gametype = re.compile(gametype, re.IGNORECASE)
    for server in self.servers:
      if (server.latency != -1) and \
        (name == None or  name.search(server.name)) and \
        (maxping == None or server.latency <= maxping) and \
        (gametype == None or gametype.search(server.gametype)):
        output.add(server)
    return output

  def sort(self, cmp=None, key=None, reverse=False):
    self.servers = sorted(self.servers, cmp, key, reverse)

  def reverse(self):
    self.players.reverse()

  def __iter__(self):
    return iter(self.servers)

  def __repr__(self):
    return str(self.servers)

  def __getitem__(self, i):
    return self.servers[i]

  def __setitem__(self, i, v):
    self.servers[i] = v

class PlayerList(object):
  def __init__(self):
    self.players = []

  def add(self, player):
    if not isinstance(player, Player):
      raise Exception('Trying to add non-Player-object')
    self.players.append(player)

  def contains(self, name=None):
    for player in self.players:
      if name == player.name:
        return True
    return False

  def find(self, name=None, clan=None, country=None, playing=None, server=None):
    output = PlayerList()
    if name: name = re.compile(name, re.IGNORECASE)
    if clan: clan = re.compile(clan, re.IGNORECASE)
    for player in self.players:
      if (name == None or name.search(player.name)) and \
        (clan == None or clan.search(player.clan)) and \
        (country == None or player.country == country) and \
        (server == None or player.server == server) and \
        (playing == None or player.playing == playing):
        output.add(player)
    return output

  def sort(self, cmp=None, key=None, reverse=False):
    self.players = sorted(self.players, cmp, key, reverse)

  def reverse(self):
    self.players.reverse()

  def __iter__(self):
    return iter(self.players)

  def __repr__(self):
    return str(self.players)


class Teeworlds(object):
  def __init__(self, timeout=5):
    #self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #self.socket.setblocking(0)
    #self._socket.settimeout(2)
    self.timeout = timeout
    self.handlers = HandlerStorage()
    self.serverlist = ServerList()
    self.playerlist = PlayerList()
    self.masterlist = []
    self.socket = MultiSocket(timeout=0.001, port=6990)

  def query_masters(self):
    masters = ["master{0}.teeworlds.com".format(i) for i in range(2, 4+1)]
    for mastername in masters:
      # resolves host and picks the first address
      try:
        info = socket.getaddrinfo(mastername, 8300, 0, socket.SOCK_DGRAM)
      except socket.gaierror as e:
        log('warning', 'getaddrinfo failed: ' + str(e))
        continue
      else:
        master_addr = info[0][4]
        log('debug', "requesting " + mastername + " " + str(master_addr))
        master = MasterServer(self, master_addr, mastername.partition(".")[0])
        master.request()
        self.add_handler(master)
        self.masterlist.append(master)

  def run_loop(self):
    start_time = time.time()
    last_send = 0
    while True:
      try:
        #(data, address) = self.socket.recvfrom(1492)
        #log('debug', "received data from socket: byteslen=" + str(len(data)) + " bytes=" + ' '.join([ "{0:2x}".format(ord(x)) for x in data[0:20] ]))
        #for handler in self.handlers.find(data=data, address=address):
        # log('debug', "calling handler " + repr(handler) + "with address=" + str(address))
        # handler.call(address, data)
        #self.socket.process_queue()
        (r, w, x) = self.socket.select(MultiSocket.READ | MultiSocket.WRITE)
        cur_time = time.time()
        if w and cur_time > last_send + 0.005:
          last_send = cur_time
          self.socket.process_queue(1)
        if not r:
          if cur_time > start_time + self.timeout:
            break
          time.sleep(0.010)
        else:
          for sock in r:
            try:
              (data, address) = sock.recvfrom(1492)
              log('debug', "received data from socket: byteslen=" + str(len(data)) + " bytes=" + ' '.join([ "{0:2x}".format(ord(x)) for x in data[0:20] ]))
              for handler in self.handlers.find(data=data, address=address):
                log('debug', "calling handler " + repr(handler) + " with address=" + str(address))
                handler.call(address, data)
            except socket.error as e:
              # Errno 10054 happens when we get ICMP port unreachable, we don't care about that
              if e.errno != 10054:
                raise
      except socket.timeout:
        break

  def add_handler(self, handler):
    # improve this
    if not isinstance(handler, Handler):
      raise Exception('Expecting instance of class Handler')
    self.handlers.add(handler)


if __name__ == "__main__":
  tw = Teeworlds(timeout=2)
  tw.query_masters()
  tw.run_loop()
  servers = tw.serverlist.find(name="^C", gametype="CTF", maxping=0.1)
  servers.sort(key=lambda s: s.latency)
  for server in servers:
      print("{server: <64} [{gametype: ^16}] on {master}: {clients: >2}/{max_clients: >2} - {latency: >4.0f} ms" \
      .format(server=server.name, gametype=server.gametype, master=server.master.name, clients=server.clients, \
          max_clients=server.max_clients, latency=server.latency*1000))
