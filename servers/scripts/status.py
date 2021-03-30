#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from ddnet import *
import json
from collections import OrderedDict

servers = OrderedDict([
    ("GER", ("ger.ddnet.tw", "DDNet GER"))
  , ("POL", ("pol.ddnet.tw", "DDNet POL"))
  , ("RUS", ("rus.ddnet.tw", "DDNet RUS"))
  , ("IRN", ("irn.ddnet.tw", "DDNet Persian"))
  #, ("KSA", ("ksa.ddnet.tw", "DDNet KSA"))
  , ("CHL", ("chl.ddnet.tw", "DDNet Chile"))
  , ("BRA", ("bra.ddnet.tw", "DDNet Brazil"))
  , ("ARG", ("arg.ddnet.tw", "DDNet Argentina"))
  #, ("COL", ("col.ddnet.tw", "DDNet Colombia"))
  #, ("CRI", ("cri.ddnet.tw", "DDNet Costa Rica"))
  , ("USA", ("usa.ddnet.tw", "DDNet USA"))
  , ("CAN", ("can.ddnet.tw", "DDNet CAN"))
  , ("CHN", ("chn.ddnet.tw", "DDNet CHN"))
  , ("KOR", ("kor.ddnet.tw", "DDNet Korea"))
  #, ("JAP", ("jap.ddnet.tw", "DDNet Japan"))
  , ("SGP", ("sgp.ddnet.tw", "DDNet Singapore"))
  , ("ZAF", ("zaf.ddnet.tw", "DDNet South Africa"))
  #, ("AUS", ("aus.ddnet.tw", "DDNet AUS"))
  ])

printStatus("DDraceNetwork", servers, json.load(open("/home/teeworlds/servers/serverlist.json"), object_pairs_hook=OrderedDict, object_hook=OrderedDict))
