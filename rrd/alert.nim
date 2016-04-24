import common, osproc, os, json, strutils

proc getLatestValues(file, time: string): seq[string] =
  let (output, errorCode) = execCmdEx(rrdtool & " fetch " & file & " AVERAGE -a -r 3min -s -3min")

  if errorCode != 0:
    raise newException(ValueError, "Error code " & $errorCode & " from rrdtool fetch")

  result = output.splitLines[^3].split(' ')

proc alert(title: string) =
  echo "DDNet server alert: ", title
  #var process = startProcess("/usr/bin/mail", args = ["-s", "DDNet server alert: " & title, "dennis@felsin9.de"])
  #process.inputStream.writeLine("More details at https://ddnet.tw/stats/server/")
  #process.inputStream.close()
  #discard process.waitForExit()
  #process.close()

if paramCount() != 1 or paramStr(1) notin ["1d", "7d", "49d"]:
  echo "alert [1d|7d|49d]"
  quit 1

let time = paramStr(1)

let statsJson = parseFile statsJsonFile
for server in statsJson["servers"]:
  let
    domain = server["type"].str
    fileNet = (rrdDir / domain) & "-net.rrd"
    fileCpu = (rrdDir / domain) & "-cpu.rrd"
    fileMem = (rrdDir / domain) & "-mem.rrd"

  if time == "1d":
    let
      values = fileNet.getLatestValues("3min")
      network_rx = values[1].parseFloat
      network_tx = values[2].parseFloat
    if network_rx + network_tx > 2_000_000:
      alert(server["name"].str & " network traffic over 2 MB/s for 3 min")

  if time == "1d":
    let
      values = fileMem.getLatestValues("3min")
      memUsed = values[1].parseFloat
      memTotal = values[2].parseFloat
      swapUsed = values[3].parseFloat
      swapTotal = values[4].parseFloat
    if memUsed + swapUsed > 0.9 * (memTotal + swapTotal):
      alert(server["name"].str & " memory and swap over 90% for 3 min")

  if time == "7d":
    let
      values = fileCpu.getLatestValues("21min")
      cpu = values[1].parseFloat
      load = values[2].parseFloat
    if cpu > 90.0:
      alert(server["name"].str & " CPU over 90% for 21 min")
    if load > 10.0:
      alert(server["name"].str & " Load over 10 for 21 min")

  if time == "49d":
    let
      values = fileNet.getLatestValues("4410")
    if values[1] == "-nan":
      alert(server["name"].str & " unreachable for 1 hour")
