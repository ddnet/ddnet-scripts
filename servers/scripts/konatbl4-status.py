#!/usr/bin/env python2

from ddnet import *

serverAddresses = [
    ("62.173.150.210", 8303, "ddrace.tk")
  , ("62.173.150.210", 8304, "ddrace.tk")
  , ("62.173.150.210", 8305, "ddrace.tk")
  , ("62.173.150.210", 8306, "ddrace.tk")
  ]

printStatus("KOnATbl4", [], serverAddresses, True)
