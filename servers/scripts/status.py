#!/usr/bin/env python

from ddnet import *

serverAddresses = [
    ("185.37.147.11", 8303, "ddnet.tw") # Novice #1
  , ("185.37.147.11", 8304, "ddnet.tw") # Moderate #1
  , ("185.37.147.11", 8305, "ddnet.tw") # Brutal #1
  , ("185.37.147.11", 8306, "ddnet.tw") # Hitomi #1
  , ("185.37.147.11", 8308, "ddnet.tw") # Moderate #2
  , ("185.37.147.11", 8309, "ddnet.tw") # Moderate #3
  , ("185.37.147.11", 8311, "ddnet.tw") # Brutal #2
  , ("185.37.147.11", 8312, "ddnet.tw") # Novice #2
  , ("185.37.147.11", 8313, "ddnet.tw") # Brutal #3
  , ("185.37.147.11", 8314, "ddnet.tw") # Brutal #4
  , ("185.37.147.11", 8316, "ddnet.tw") # Hitomi #2
  , ("185.37.147.11", 8317, "ddnet.tw") # Oldschool #1
  , ("185.37.147.11", 8318, "ddnet.tw") # Oldschool #2
  , ("185.37.147.11", 8319, "ddnet.tw") # Oldschool #3
  , ("185.37.147.11", 8320, "ddnet.tw") # Oldschool #4
  , ("185.37.147.11", 8321, "ddnet.tw") # Solo #1
  , ("185.37.147.11", 8322, "ddnet.tw") # Bonus #1
  , ("185.37.147.11", 8323, "ddnet.tw") # Solo #2
  , ("185.37.147.11", 8324, "ddnet.tw") # Solo #3
  , ("185.37.147.11", 8326, "ddnet.tw") # Bonus #2
  , ("185.37.147.11", 8327, "ddnet.tw") # Bonus #3
  , ("185.37.147.11", 8330, "ddnet.tw") # Bonus #4
  , ("185.37.147.11", 8331, "ddnet.tw") # Bonus #5
  , ("185.37.147.11", 8332, "ddnet.tw") # Bonus #6
  , ("185.37.147.11", 8333, "ddnet.tw") # Bonus #7
  , ("185.37.147.11", 8334, "ddnet.tw") # Bonus #8
  , ("185.37.147.11", 8335, "ddnet.tw") # Bonus #9
  , ("185.37.147.11", 8336, "ddnet.tw") # Bonus #10
  , ("185.37.147.11", 8328, "ddnet.tw") # Bonus #11
  , ("185.37.147.11", 8307, "ddnet.tw") # Test #1
  , ("185.37.147.11", 8310, "ddnet.tw") # Test #2
  , ("185.37.147.11", 8315, "ddnet.tw") # Test #3
  , ("185.37.147.11", 8325, "ddnet.tw") # Nuclear Test #1

  , ("185.37.147.11", 8103, "ddnet.tw") # Block #1
  #, ("185.37.147.11", 8104, "ddnet.tw") # Block #2
  #, ("185.37.147.11", 8105, "ddnet.tw") # Block #3

  , ("185.37.147.11", 8201, "ddnet.tw") # iCTF #1
  , ("185.37.147.11", 8202, "ddnet.tw") # iCTF #2
  , ("185.37.147.11", 8203, "ddnet.tw") # iCTF #3
  , ("185.37.147.11", 8204, "ddnet.tw") # iCTF #4
  , ("185.37.147.11", 8205, "ddnet.tw") # iCTF #5
  , ("185.37.147.11", 8206, "ddnet.tw") # iCTF #6
  , ("185.37.147.11", 8207, "ddnet.tw") # iCTF #7
  , ("185.37.147.11", 8208, "ddnet.tw") # gCTF #1
  , ("185.37.147.11", 8209, "ddnet.tw") # gCTF #2

  , ("185.37.147.11", 8210, "ddnet.tw") # zCatch
  , ("185.37.147.11", 8211, "ddnet.tw") # Nano-League #1
  , ("185.37.147.11", 8212, "ddnet.tw") # Nano-League #1
  #, ("185.37.147.11", 8220, "ddnet.tw") # HTF
  #, ("185.37.147.11", 8230, "ddnet.tw") # Survival

  , ("185.37.147.11", 8241, "ddnet.tw") # Vanilla CTF #1
  , ("185.37.147.11", 8242, "ddnet.tw") # Vanilla CTF #2

  , ("176.31.125.151", 8303, "fra.ddnet.tw") # Novice #1
  , ("176.31.125.151", 8304, "fra.ddnet.tw") # Moderate #1
  , ("176.31.125.151", 8305, "fra.ddnet.tw") # Brutal #1
  , ("176.31.125.151", 8306, "fra.ddnet.tw") # Hitomi #1
  , ("176.31.125.151", 8308, "fra.ddnet.tw") # Moderate #2
  , ("176.31.125.151", 8309, "fra.ddnet.tw") # Moderate #3
  , ("176.31.125.151", 8311, "fra.ddnet.tw") # Brutal #2
  , ("176.31.125.151", 8312, "fra.ddnet.tw") # Novice #2
  , ("176.31.125.151", 8313, "fra.ddnet.tw") # Brutal #3
  , ("176.31.125.151", 8314, "fra.ddnet.tw") # Brutal #4
  , ("176.31.125.151", 8316, "fra.ddnet.tw") # Hitomi #2
  , ("176.31.125.151", 8317, "fra.ddnet.tw") # Oldschool #1
  , ("176.31.125.151", 8318, "fra.ddnet.tw") # Oldschool #2
  , ("176.31.125.151", 8319, "fra.ddnet.tw") # Oldschool #3
  , ("176.31.125.151", 8320, "fra.ddnet.tw") # Oldschool #4
  , ("176.31.125.151", 8321, "fra.ddnet.tw") # Solo #1
  , ("176.31.125.151", 8322, "fra.ddnet.tw") # Bonus #1
  , ("176.31.125.151", 8323, "fra.ddnet.tw") # Solo #2
  , ("176.31.125.151", 8324, "fra.ddnet.tw") # Solo #3
  , ("176.31.125.151", 8326, "fra.ddnet.tw") # Bonus #2
  , ("176.31.125.151", 8327, "fra.ddnet.tw") # Bonus #3
  , ("176.31.125.151", 8330, "fra.ddnet.tw") # Bonus #4
  , ("176.31.125.151", 8331, "fra.ddnet.tw") # Bonus #5
  , ("176.31.125.151", 8332, "fra.ddnet.tw") # Bonus #6
  , ("176.31.125.151", 8333, "fra.ddnet.tw") # Bonus #7
  , ("176.31.125.151", 8334, "fra.ddnet.tw") # Bonus #8
  , ("176.31.125.151", 8335, "fra.ddnet.tw") # Bonus #9
  , ("176.31.125.151", 8336, "fra.ddnet.tw") # Bonus #10

  , ("176.31.125.151", 8307, "fra.ddnet.tw") # Test

  , ("176.31.125.151", 8203, "fra.ddnet.tw") # Block #1
  , ("176.31.125.151", 8204, "fra.ddnet.tw") # Block #2
  , ("176.31.125.151", 8205, "fra.ddnet.tw") # Block #3

  , ("74.91.114.132", 8303, "usa.ddnet.tw") # Novice #1
  , ("74.91.114.132", 8304, "usa.ddnet.tw") # Moderate #1
  , ("74.91.114.132", 8305, "usa.ddnet.tw") # Brutal #1
  , ("74.91.114.132", 8306, "usa.ddnet.tw") # Hitomi #1
  , ("74.91.114.132", 8317, "usa.ddnet.tw") # Oldschool #1
  , ("74.91.114.132", 8321, "usa.ddnet.tw") # Solo #1

  , ("74.91.114.132", 8307, "usa.ddnet.tw") # Test

  , ("74.91.114.132", 8203, "usa.ddnet.tw") # Block #1
  , ("74.91.114.132", 8204, "usa.ddnet.tw") # Block #2
  , ("74.91.114.132", 8205, "usa.ddnet.tw") # Block #3

  , ("74.91.114.132", 8101, "usa.ddnet.tw") # iCTF #1
  , ("74.91.114.132", 8102, "usa.ddnet.tw") # iCTF #2
  , ("74.91.114.132", 8103, "usa.ddnet.tw") # iCTF #3
  , ("74.91.114.132", 8104, "usa.ddnet.tw") # iCTF #4

  , ("74.91.114.132", 8210, "usa.ddnet.tw") # zCatch #1
  , ("74.91.114.132", 8211, "usa.ddnet.tw") # zCatch #2
  , ("74.91.114.132", 8212, "usa.ddnet.tw") # zCatch #3
  #, ("74.91.114.132", 8220, "usa.ddnet.tw") # HTF
  #, ("74.91.114.132", 8230, "usa.ddnet.tw") # Survival
  , ("74.91.114.132", 8299, "usa.ddnet.tw") # Bomb Tag
  , ("74.91.114.132", 8250, "usa.ddnet.tw") # Monster

  , ("151.248.116.14", 8303, "rus.ddnet.tw") # Novice #1
  , ("151.248.116.14", 8304, "rus.ddnet.tw") # Moderate #1
  , ("151.248.116.14", 8305, "rus.ddnet.tw") # Brutal #1
  , ("151.248.116.14", 8306, "rus.ddnet.tw") # Hitomi #1
  , ("151.248.116.14", 8317, "rus.ddnet.tw") # Oldschool #1
  , ("151.248.116.14", 8321, "rus.ddnet.tw") # Solo #1
  , ("151.248.116.14", 8103, "rus.ddnet.tw") # Blocker

  , ("151.248.116.14", 8250, "rus.ddnet.tw") # Monster

  , ("112.124.108.6", 7303, "chn.ddnet.tw") # Novice #1
  , ("112.124.108.6", 7304, "chn.ddnet.tw") # Moderate #1
  , ("112.124.108.6", 7305, "chn.ddnet.tw") # Brutal #1
  , ("112.124.108.6", 7306, "chn.ddnet.tw") # Hitomi #1
  , ("112.124.108.6", 7317, "chn.ddnet.tw") # Oldschool #1
  , ("112.124.108.6", 7321, "chn.ddnet.tw") # Solo #1

  , ("190.114.253.157", 7303, "chl.ddnet.tw") # Novice #1
  , ("190.114.253.157", 7304, "chl.ddnet.tw") # Moderate #1
  , ("190.114.253.157", 7305, "chl.ddnet.tw") # Brutal #1
  , ("190.114.253.157", 7306, "chl.ddnet.tw") # Hitomi #1
  , ("190.114.253.157", 7308, "chl.ddnet.tw") # Moderate #2
  , ("190.114.253.157", 7309, "chl.ddnet.tw") # Moderate #3
  , ("190.114.253.157", 7311, "chl.ddnet.tw") # Brutal #2
  , ("190.114.253.157", 7317, "chl.ddnet.tw") # Oldschool #1
  , ("190.114.253.157", 7321, "chl.ddnet.tw") # Solo #1
  , ("190.114.253.157", 7322, "chl.ddnet.tw")
  , ("190.114.253.157", 7323, "chl.ddnet.tw")
  , ("190.114.253.157", 7324, "chl.ddnet.tw")
  , ("190.114.253.157", 7326, "chl.ddnet.tw")

  , ("190.114.253.157", 7203, "chl.ddnet.tw") # Block #1
  , ("190.114.253.157", 7204, "chl.ddnet.tw") # Block #2
  , ("190.114.253.157", 7205, "chl.ddnet.tw") # Block #3

  , ("190.114.253.157", 8101, "chl.ddnet.tw") # iCTF #1
  , ("190.114.253.157", 8102, "chl.ddnet.tw") # iCTF #2
  #, ("190.114.253.157", 8103, "chl.ddnet.tw") # iCTF #3
  #, ("190.114.253.157", 8104, "chl.ddnet.tw") # iCTF #4

  , ("190.114.253.157", 7210, "chl.ddnet.tw") # zCatch #1
  , ("190.114.253.157", 7211, "chl.ddnet.tw") # zCatch #2
  , ("190.114.253.157", 7212, "chl.ddnet.tw") # zCatch #3
  , ("190.114.253.157", 7220, "chl.ddnet.tw") # openFNG
  #, ("190.114.253.157", 8220, "chl.ddnet.tw") # HTF
  #, ("190.114.253.157", 8230, "chl.ddnet.tw") # Survival
  , ("190.114.253.157", 8299, "chl.ddnet.tw") # Bomb Tag

  , ("41.185.26.5", 7303, "zaf.ddnet.tw")
  , ("41.185.26.5", 7304, "zaf.ddnet.tw")
  , ("41.185.26.5", 7305, "zaf.ddnet.tw")
  , ("41.185.26.5", 7306, "zaf.ddnet.tw")
  , ("41.185.26.5", 7308, "zaf.ddnet.tw")
  , ("41.185.26.5", 7309, "zaf.ddnet.tw")
  , ("41.185.26.5", 7310, "zaf.ddnet.tw")
  , ("41.185.26.5", 7311, "zaf.ddnet.tw")
  , ("41.185.26.5", 7317, "zaf.ddnet.tw")
  , ("41.185.26.5", 7321, "zaf.ddnet.tw")
  , ("41.185.26.5", 7322, "zaf.ddnet.tw")
  , ("41.185.26.5", 7323, "zaf.ddnet.tw")
  , ("41.185.26.5", 7324, "zaf.ddnet.tw")
  , ("41.185.26.5", 7325, "zaf.ddnet.tw")

  , ("41.185.26.5", 7307, "zaf.ddnet.tw") # Test

  , ("41.185.26.5", 7210, "zaf.ddnet.tw") # zCatch
  , ("41.185.26.5", 7220, "zaf.ddnet.tw") # openFNG

  , ("94.182.162.155", 8303, "irn.ddnet.tw") # Novice #1
  , ("94.182.162.155", 8304, "irn.ddnet.tw") # Moderate #1
  , ("94.182.162.155", 8305, "irn.ddnet.tw") # Brutal #1
  , ("94.182.162.155", 8306, "irn.ddnet.tw") # Hitomi #1
  , ("94.182.162.155", 8317, "irn.ddnet.tw") # Oldschool #1
  #, ("94.182.162.155", 8321, "irn.ddnet.tw") # Solo #1

  , ("94.182.162.155", 8103, "irn.ddnet.tw") # Block #1
  , ("94.182.162.155", 7220, "irn.ddnet.tw") # openFNG

  #, ("94.182.162.155", 8204, "irn.ddnet.tw") # Block #2
  #, ("94.182.162.155", 8205, "irn.ddnet.tw") # Block #3
  #, ("94.182.162.155", 8206, "irn.ddnet.tw") # ADMIN #1
  #, ("94.182.162.155", 8207, "irn.ddnet.tw") # ADMIN #1

  #, ("94.182.162.155", 8101, "irn.ddnet.tw") # iCTF #1
  #, ("94.182.162.155", 8102, "irn.ddnet.tw") # iCTF #2
  ##, ("94.182.162.155", 8103, "irn.ddnet.tw") # iCTF #3
  ##, ("94.182.162.155", 8104, "irn.ddnet.tw") # iCTF #4

  #, ("94.182.162.155", 7210, "irn.ddnet.tw") # zCatch #1
  ##, ("94.182.162.155", 7211, "irn.ddnet.tw") # zCatch #2
  ##, ("94.182.162.155", 7212, "irn.ddnet.tw") # zCatch #3
  ##, ("94.182.162.155", 8220, "irn.ddnet.tw") # HTF
  ##, ("94.182.162.155", 8230, "irn.ddnet.tw") # Survival
  #, ("94.182.162.155", 8299, "irn.ddnet.tw") # Bomb Tag

  ]

servers = [
    ("ddnet.tw", "Network GER")
  , ("fra.ddnet.tw", "Network FRA")
  , ("usa.ddnet.tw", "Network USA")
  , ("rus.ddnet.tw", "Network RUS")
  , ("chn.ddnet.tw", "Network CHN")
  , ("chl.ddnet.tw", "Network Chile")
  , ("zaf.ddnet.tw", "Network South Africa")
  , ("irn.ddnet.tw", "Network Persian")
  ]

printStatus("DDraceNetwork", servers, serverAddresses)
