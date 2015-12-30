#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ddnet import *
import json
from collections import OrderedDict

servers = OrderedDict([
    ("GER", ("ger.ddnet.tw", "DDNet GER"))
  , ("RUS", ("rus.ddnet.tw", "DDNet RUS"))
  , ("USA", ("usa.ddnet.tw", "DDNet USA"))
  , ("CAN", ("can.ddnet.tw", "DDNet CAN"))
  , ("CHN", ("chn.ddnet.tw", "DDNet CHN"))
  , ("CHL", ("chl.ddnet.tw", "DDNet Chile"))
  , ("BRA", ("br.ddnet.tw",  "DDNet Brazil"))
  , ("ZAF", ("zaf.ddnet.tw", "DDNet South Africa"))
  #, ("IRN", ("irn.ddnet.tw", "DDNet Persian"))
  ])

printStatus("DDraceNetwork", servers, json.load(open("/home/teeworlds/servers/serverlist.json"), object_pairs_hook=OrderedDict, object_hook=OrderedDict))
