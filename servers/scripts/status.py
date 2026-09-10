#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from ddnet import *
import sys
import json
from collections import OrderedDict

sys.stdout.reconfigure(encoding='utf-8')

servers = OrderedDict([
    ("EUR", ("eur.ddnet.org", "DDNet EUR"))
  #, ("UKR", ("ukr.ddnet.org", "DDNet UKR"))
  , ("RUS", ("rus.ddnet.org", "DDNet RUS"))
  , ("TUR", ("tur.ddnet.org", "DDNet Türkiye"))
  #, ("BHR", ("bhr.ddnet.org", "DDNet Bahrain"))
  , ("IRN", ("irn.ddnet.org", "DDNet Persian"))
  , ("CHL", ("chl.ddnet.org", "DDNet Chile"))
  , ("BRA", ("bra.ddnet.org", "DDNet Brazil"))
  , ("ARG", ("arg.ddnet.org", "DDNet Argentina"))
  #, ("PER", ("per.ddnet.org", "DDNet Peru"))
  , ("USA", ("usa.ddnet.org", "DDNet USA"))
  , ("CHN", ("chn.ddnet.org", "DDNet CHN"))
  , ("TWN", ("twn.ddnet.org", "DDNet Taiwan"))
  #, ("JAP", ("jap.ddnet.org", "DDNet Japan"))
  , ("KOR", ("kor.ddnet.org", "DDNet Korea"))
  , ("SGP", ("sgp.ddnet.org", "DDNet Singapore"))
  , ("IND", ("ind.ddnet.org", "DDNet India"))
  , ("AUS", ("aus.ddnet.org", "DDNet Australia"))
  , ("ZAF", ("zaf.ddnet.org", "DDNet South Africa"))
  ])

communities = json.load(open("/home/httpmaster/communities-generated-backcompat.json"), object_pairs_hook=OrderedDict, object_hook=OrderedDict)
ddnet_community = None
for community in communities:
    if community["id"] == "ddnet":
        if ddnet_community is not None:
            raise RuntimeError("duplicate ddnet community")
        ddnet_community = community
if ddnet_community is None:
    raise RuntimeError("ddnet community not found")

servers_order_index = {server: i for i, server in enumerate(servers)}
ddnet_community["icon"]["servers"].sort(
    key=lambda s: servers_order_index.get(s.get("name"), float("inf"))
)

types_order_index = {typ: i for i, typ in enumerate(["Tutorial", "DDNet", "Test", "Block", "FNG", "iCTF", "Vanilla", "Infection", "TSmash", "Foot", "Monster", "TeeWare", "xPanic", "zCatch"])}
for community in ddnet_community["icon"]["servers"]:
    sorted_items = sorted(
        community["servers"].items(),
        key=lambda item: types_order_index.get(item[0], float("inf"))
    )
    community["servers"] = OrderedDict(sorted_items)

printStatus("DDraceNetwork", servers, ddnet_community["icon"]["servers"])
