import strutils, strfmt, algorithm

var mappings: array[0x80, seq[int]]
var confusables: array[0x80, seq[int]]

for line in "confusables.txt".lines:
  let fields = line.split(" ;\t")
  if fields.len < 3 or not fields[2].startsWith("MA"):
    continue

  var smaller = fields[0].parseHexInt

  if fields[1].count(' ') > 0:
    var s = fields[1].split(' ').map(parseHexInt)
    if smaller < 0x80:
      mappings[smaller] = s

for line in "confusables.txt".lines:
  let fields = line.split(" ;\t")

  if fields.len < 3 or not fields[2].startsWith("MA"):
    continue

  var smaller = fields[0].parseHexInt
  var bigger: int

  block outer:
    if fields[1].count(' ') > 0:
      var s = fields[1].split(' ').map(parseHexInt)
      for key, mapping in mappings:
        if s == mapping and smaller != key:
          bigger = key
          break outer
      continue
    else:
      bigger = fields[1].parseHexInt

  if bigger < smaller:
    swap bigger, smaller

  if smaller >= 0x80:
    continue

  if confusables[smaller].isNil:
    confusables[smaller] = @[]

  confusables[smaller].add(bigger)

for smaller, confs in confusables.mpairs:
  if confs.isNil:
    #echo smaller.toHex(4), " ", char(smaller)
    continue

  stdout.writefmt "\tcase 0x{:04X}: return ", smaller
  confs.sort(cmp)
  for i, bigger in confs:
    if i > 0:
      stdout.write " || "
    stdout.writefmt "bigger == 0x{:04X}", bigger
  stdout.writeln ";"
