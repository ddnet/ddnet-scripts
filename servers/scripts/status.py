#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from ddnet import *
import json
from collections import OrderedDict

servers = OrderedDict([
    ("EUR", ("eur.ddnet.org", "DDNet EUR"))
  , ("RUS", ("rus.ddnet.org", "DDNet RUS"))
  , ("TUR", ("tur.ddnet.org", "DDNet Turkey"))
  , ("IRN", ("irn.ddnet.org", "DDNet Persian"))
  , ("CHL", ("chl.ddnet.org", "DDNet Chile"))
  , ("BRA", ("bra.ddnet.org", "DDNet Brazil"))
  , ("ARG", ("arg.ddnet.org", "DDNet Argentina"))
  #, ("MEX", ("mex.ddnet.org", "DDNet Mexico"))
  , ("USA", ("usa.ddnet.org", "DDNet USA"))
  , ("CAN", ("can.ddnet.org", "DDNet CAN"))
  , ("CHN", ("chn.ddnet.org", "DDNet CHN"))
  , ("JAP", ("jap.ddnet.org", "DDNet Japan"))
  , ("KOR", ("kor.ddnet.org", "DDNet Korea"))
  , ("SGP", ("sgp.ddnet.org", "DDNet Singapore"))
  , ("IND", ("ind.ddnet.org", "DDNet India"))
  , ("AUS", ("aus.ddnet.org", "DDNet Australia"))
  , ("ZAF", ("zaf.ddnet.org", "DDNet South Africa"))
  ])

printStatus("DDraceNetwork", servers, json.load(open("/home/teeworlds/servers/serverlist.json"), object_pairs_hook=OrderedDict, object_hook=OrderedDict))

