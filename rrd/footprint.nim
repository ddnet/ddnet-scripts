import os, strutils, posix, strfmt
# CPU and memory usage of process, based on PROC(5) and
# http://stackoverflow.com/a/16736599
let
  pid = paramStr(1)
  # Clock ticks per second
  frequency = sysconf(SC_CLK_TCK)
  # Size of memory page in bytes
  pagesize  = sysconf(SC_PAGESIZE)

  uptime    = readFile("/proc/uptime").split[0].parseFloat
  fields    = readFile("/proc/" & pid & "/stat").split

  # Amount of time in user mode
  utime     = fields[13].parseInt
  # Amount of time in kernel mode
  stime     = fields[14].parseInt
  # Amount of children time in user mode
  cutime    = fields[15].parseInt
  # Amount of children time in kernel mode
  cstime    = fields[16].parseInt
  # Time process started after boot
  starttime = fields[21].parseInt

  # Resident Set Size: number of pages in memory
  rssmem    = fields[23].parseInt

  totaltime = utime + stime + cutime + cstime
  seconds   = uptime - (starttime / frequency)

  cpuusage  = 100 * (totaltime / frequency) / seconds
  memusage  = rssmem * pagesize / 1_000_000

echo interp"${cpuusage:.2f} % CPU ${memusage:.2f} MB Memory"
