import common, json, osproc, os, times, strutils, tables

type
  Data = object
    network_rx, network_tx: BiggestInt
    cpu, memory_used, memory_total, swap_used, swap_total: BiggestInt
    load: float

const freq = 30 # report new data to rrd every 30 seconds

var
  lastUpdated: BiggestInt = 0
  dataTable = initTable[string, Data]()
  count = 0
  countTable = initTable[string, int]()

proc rrdCreate(file, dataSources: string) =
  discard execCmd(rrdtool & " create " & file & " --step " & $freq & " " & dataSources &
    " RRA:AVERAGE:0.5:6:480 RRA:AVERAGE:0.5:42:480 RRA:AVERAGE:0.5:147:960")

proc rrdUpdate(file: string, values: varargs[string, `$`]) =
  var valuesString = ""
  for value in values:
    if valuesString.len > 0:
      valuesString.add ":"
    valuesString.add value
  discard execCmd(rrdtool & " update " & file & " N:" & valuesString)

proc updateServer(server: JsonNode) =
  let domain = server["type"].str

  for name, value in dataTable.mgetOrPut(domain, Data()).fieldPairs:
    when value is BiggestInt:
      value += server[name].num
    elif value is float:
      value += server[name].fnum
    else:
      error "Unhandled type in Data object"

  inc countTable.mgetOrPut(domain, 0)

  # Only save data if we got 30 values in the expected time span
  if count == freq and countTable[domain] == freq:
    let data = dataTable[domain]
    if data == Data():
      dataTable.del(domain)
      return
    else:
      dataTable[domain] = Data()

    let
      fileNet = (rrdDir / domain) & "-net.rrd"
      fileCpu = (rrdDir / domain) & "-cpu.rrd"
      fileMem = (rrdDir / domain) & "-mem.rrd"

    if not existsFile fileNet:
      fileNet.rrdCreate("DS:network_rx:GAUGE:60:0:U DS:network_tx:GAUGE:60:0:U")
    if not existsFile fileCpu:
      fileCpu.rrdCreate("DS:cpu:GAUGE:60:0:100 DS:load:GAUGE:60:0:U")
    if not existsFile fileMem:
      filemem.rrdCreate("DS:memory_used:GAUGE:60:0:U DS:memory_total:GAUGE:60:0:U DS:swap_used:GAUGE:60:0:U DS:swap_total:GAUGE:60:0:U")

    fileNet.rrdUpdate(data.network_rx div freq, data.network_tx div freq)
    fileCpu.rrdUpdate(min(data.cpu div freq, 100), data.load / freq)
    fileMem.rrdUpdate(data.memory_used div freq, data.memory_total div freq, data.swap_used div freq, data.swap_total div freq)

proc updateAllServers =
  let statsJson = parseFile statsJsonFile
  let newUpdated = parseBiggestInt statsJson["updated"].str

  if newUpdated <= lastUpdated:
    return

  inc count

  for server in statsJson["servers"]:
    try:
      updateServer(server)
    except:
      discard

  if count == freq:
    count = 0
    for val in countTable.mvalues:
      val = 0

while true:
  let startTime = epochTime()

  updateAllServers()

  sleep(int(epochTime() - startTime + 1) * 1000) # every second
