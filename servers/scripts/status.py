#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from ddnet import *
import json
from collections import OrderedDict

servers = OrderedDict([
    ("EUR", ("eur.ddnet.tw", "DDNet EUR"))
  , ("RUS", ("rus.ddnet.tw", "DDNet RUS"))
  , ("TUR", ("tur.ddnet.tw", "DDNet Turkey"))
  , ("IRN", ("irn.ddnet.tw", "DDNet Persian"))
  , ("CHL", ("chl.ddnet.tw", "DDNet Chile"))
  , ("BRA", ("bra.ddnet.tw", "DDNet Brazil"))
  #, ("ARG", ("arg.ddnet.tw", "DDNet Argentina"))
  , ("USA", ("usa.ddnet.tw", "DDNet USA"))
  , ("CAN", ("can.ddnet.tw", "DDNet CAN"))
  , ("CHN", ("chn.ddnet.tw", "DDNet CHN"))
  , ("JAP", ("jap.ddnet.tw", "DDNet Japan"))
  , ("KOR", ("kor.ddnet.tw", "DDNet Korea"))
  , ("SGP", ("sgp.ddnet.tw", "DDNet Singapore"))
  , ("ZAF", ("zaf.ddnet.tw", "DDNet South Africa"))
  #, ("IND", ("ind.ddnet.tw", "DDNet India"))
  ])

printStatus("DDraceNetwork", servers, json.load(open("/home/teeworlds/servers/serverlist.json"), object_pairs_hook=OrderedDict, object_hook=OrderedDict))

