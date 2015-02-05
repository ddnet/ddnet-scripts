import os, crc32, strutils

const
  baseDir = "/home/teeworlds/servers"
  mapdlDir = "/var/www-maps"

for kind, path in walkDir baseDir/"maps":
  if kind != pcFile:
    continue

  let (dir, name, ext) = splitFile(path)

  if ext != ".map":
    continue

  let
    sum = crc32FromFile(path).int64.toHex(8).toLower
    newName = name & "_" & sum & ext
    newPath = mapdlDir / newName
    tmpPath = newPath & ".tmp"

  if existsFile newPath:
    continue

  copyFile path, tmpPath
  moveFile tmpPath, newPath
