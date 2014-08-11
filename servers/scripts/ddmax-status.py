#!/usr/bin/env python

from ddnet import *

serverAddresses = [
    ("46.4.97.42", 8328, "ddracemax.info")
  , ("46.4.97.42", 8329, "ddracemax.info")
  , ("46.4.97.42", 8330, "ddracemax.info")
  , ("46.4.97.42", 8315, "ddracemax.info")
  , ("46.4.97.42", 8317, "ddracemax.info")
  , ("46.4.97.42", 8314, "ddracemax.info")
  , ("46.4.97.42", 8327, "ddracemax.info")
  , ("46.4.97.42", 8331, "ddracemax.info")
  , ("46.4.97.42", 8401, "ddracemax.info")
  , ("46.4.97.42", 8402, "ddracemax.info")
  , ("46.4.97.42", 8318, "ddracemax.info")
  , ("46.4.97.42", 8319, "ddracemax.info")
  , ("46.4.97.42", 8325, "ddracemax.info")
  , ("46.4.97.42", 8326, "ddracemax.info")
  , ("46.4.97.42", 8333, "ddracemax.info")
  , ("46.4.97.42", 8334, "ddracemax.info")
  , ("46.4.97.42", 8335, "ddracemax.info")

  , ("46.4.97.42", 8415, "ddracemax.info") # RacemaX

  , ("185.5.96.111", 8100, "185.5.96.111")
  , ("185.5.96.111", 8101, "185.5.96.111")
  , ("185.5.96.111", 8103, "185.5.96.111")
  , ("185.5.96.111", 8104, "185.5.96.111")
  ]

printStatus("DDracemaX", [("ddracemax.info", "DDracemaX")], serverAddresses, True)
