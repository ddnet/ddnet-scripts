#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from ddnet import *
import json
from collections import OrderedDict

servers = OrderedDict([
    ("GER", ("ger.ddnet.tw", "DDNet GER"))
  , ("RUS", ("rus.ddnet.tw", "DDNet RUS"))
  , ("CHL", ("chl.ddnet.tw", "DDNet Chile"))
  , ("USA", ("usa.ddnet.tw", "DDNet USA"))
  , ("ZAF", ("zaf.ddnet.tw", "DDNet South Africa"))
  , ("CHN", ("chn.ddnet.tw", "DDNet CHN"))
  ])

printStatus("DDraceNetwork", servers, json.load(open("/home/teeworlds/servers/serverlist.json"), object_pairs_hook=OrderedDict, object_hook=OrderedDict))
