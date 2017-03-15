#!/bin/sh
PNG_DIR=/var/www/stats/server
RRD_DIR=/home/teeworlds/rrd
RRDTOOL=/opt/rrdtool-1.6.0/bin/rrdtool

net()
{
  $RRDTOOL graph $PNG_DIR/$1-net-$2.png --rigid --base 1000 \
    --width $3 --height $4 --logarithmic --units=si -a PNG \
    --vertical-label "Bytes/s" --start now-$2 \
    DEF:network_rx=$RRD_DIR/$1-net.rrd:network_rx:AVERAGE \
    DEF:network_tx=$RRD_DIR/$1-net.rrd:network_tx:AVERAGE \
    VDEF:network_rx_a=network_rx,AVERAGE \
    VDEF:network_rx_m=network_rx,MAXIMUM \
    VDEF:network_rx_c=network_rx,LAST \
    VDEF:network_rx_s=network_rx,TOTAL \
    VDEF:network_tx_a=network_tx,AVERAGE \
    VDEF:network_tx_m=network_tx,MAXIMUM \
    VDEF:network_tx_c=network_tx,LAST \
    VDEF:network_tx_s=network_tx,TOTAL \
    AREA:network_tx#fee8c8: \
    AREA:network_rx#e0e0e0: \
    LINE1:network_tx#e34a33:"out" \
    GPRINT:network_tx_a:"avg\: %6.2lf %sB" \
    GPRINT:network_tx_m:"max\: %6.2lf %sB" \
    GPRINT:network_tx_c:"cur\: %6.2lf %sB" \
    GPRINT:network_tx_s:"sum\: %6.2lf %sB\n" \
    LINE1:network_rx#636363:"in " \
    GPRINT:network_rx_a:"avg\: %6.2lf %sB" \
    GPRINT:network_rx_m:"max\: %6.2lf %sB" \
    GPRINT:network_rx_c:"cur\: %6.2lf %sB" \
    GPRINT:network_rx_s:"sum\: %6.2lf %sB\n"
}

packets()
{
  $RRDTOOL graph $PNG_DIR/$1-packets-$2.png --rigid --base 1000 \
    --width $3 --height $4 --logarithmic --units=si -a PNG \
    --vertical-label "Packets/s" --start now-$2 \
    DEF:packets_rx=$RRD_DIR/$1-net.rrd:packets_rx:AVERAGE \
    DEF:packets_tx=$RRD_DIR/$1-net.rrd:packets_tx:AVERAGE \
    VDEF:packets_rx_a=packets_rx,AVERAGE \
    VDEF:packets_rx_m=packets_rx,MAXIMUM \
    VDEF:packets_rx_c=packets_rx,LAST \
    VDEF:packets_rx_s=packets_rx,TOTAL \
    VDEF:packets_tx_a=packets_tx,AVERAGE \
    VDEF:packets_tx_m=packets_tx,MAXIMUM \
    VDEF:packets_tx_c=packets_tx,LAST \
    VDEF:packets_tx_s=packets_tx,TOTAL \
    AREA:packets_tx#fee8c8: \
    AREA:packets_rx#e0e0e0: \
    LINE1:packets_tx#e34a33:"out" \
    GPRINT:packets_tx_a:"avg\: %6.2lf %sp" \
    GPRINT:packets_tx_m:"max\: %6.2lf %sp" \
    GPRINT:packets_tx_c:"cur\: %6.2lf %sp" \
    GPRINT:packets_tx_s:"sum\: %6.2lf %sp\n" \
    LINE1:packets_rx#636363:"in " \
    GPRINT:packets_rx_a:"avg\: %6.2lf %sp" \
    GPRINT:packets_rx_m:"max\: %6.2lf %sp" \
    GPRINT:packets_rx_c:"cur\: %6.2lf %sp" \
    GPRINT:packets_rx_s:"sum\: %6.2lf %sp\n"
}

cpu()
{
  $RRDTOOL graph $PNG_DIR/$1-cpu-$2.png --rigid --lower-limit -100 --upper-limit 100 \
    --width $3 --height $4 -a PNG \
    --vertical-label "%" --start now-$2 \
    DEF:cpu=$RRD_DIR/$1-cpu.rrd:cpu:AVERAGE \
    DEF:load_raw=$RRD_DIR/$1-cpu.rrd:load:AVERAGE \
    CDEF:load=load_raw,UN,0,load_raw,IF \
    VDEF:cpu_a=cpu,AVERAGE \
    VDEF:cpu_m=cpu,MAXIMUM \
    VDEF:cpu_c=cpu,LAST \
    VDEF:load_a=load,AVERAGE \
    VDEF:load_m=load,MAXIMUM \
    VDEF:load_c=load,LAST \
    CDEF:load0=load,1,LT,load,1,IF \
    CDEF:load1=load0,1,LT,0,load,2,LT,load,1,-,1,IF,IF \
    CDEF:load2=load1,1,LT,0,load,3,LT,load,2,-,1,IF,IF \
    CDEF:load3=load2,1,LT,0,load,4,LT,load,3,-,1,IF,IF \
    CDEF:load4=load3,1,LT,0,load,4,-,IF \
    CDEF:cload4=load4,load_m,/,-100,\* \
    CDEF:cload3=load3,load_m,/,-100,\* \
    CDEF:cload2=load2,load_m,/,-100,\* \
    CDEF:cload1=load1,load_m,/,-100,\* \
    CDEF:cload0=load0,load_m,/,-100,\* \
    CDEF:cload=load_raw,load_m,/,-100,\* \
    AREA:cpu#e0e0e0: \
    LINE1:cpu#636363:"cpu" \
    GPRINT:cpu_a:"avg\: %5.0lf %%" \
    GPRINT:cpu_m:"max\: %5.0lf %%" \
    GPRINT:cpu_c:"cur\: %5.0lf %%\n" \
    COMMENT:"load\:" \
    AREA:cload0#00FFFF80:"0..1      " \
    AREA:cload1#00D00080:"1..2      ":STACK \
    AREA:cload2#FFD00080:"2..3      ":STACK \
    AREA:cload3#FF000080:"3..4      ":STACK \
    AREA:cload4#FF00FF80:"> 4\n":STACK \
    LINE:cload#636363:"" \
    GPRINT:load_a:"       avg\: %7.2lf" \
    GPRINT:load_m:"max\: %7.2lf" \
    GPRINT:load_c:"cur\: %7.2lf\n"
}

mem()
{
  $RRDTOOL graph $PNG_DIR/$1-mem-$2.png --rigid --base 1000 \
    --width $3 --height $4 -a PNG \
    --vertical-label "Bytes" --start now-$2 \
    DEF:memory_used_raw=$RRD_DIR/$1-mem.rrd:memory_used:AVERAGE \
    DEF:memory_total_raw=$RRD_DIR/$1-mem.rrd:memory_total:AVERAGE \
    DEF:swap_used_raw=$RRD_DIR/$1-mem.rrd:swap_used:AVERAGE \
    DEF:swap_total_raw=$RRD_DIR/$1-mem.rrd:swap_total:AVERAGE \
    CDEF:memory_used=memory_used_raw,1000,\* \
    CDEF:memory_free=memory_total_raw,1000,\*,memory_used,- \
    CDEF:swap_used=swap_used_raw,1000,\* \
    CDEF:swap_free=swap_total_raw,1000,\*,swap_used,- \
    CDEF:swap_used_neg=swap_used,-1,\* \
    CDEF:swap_free_neg=swap_free,-1,\* \
    VDEF:memory_used_a=memory_used,AVERAGE \
    VDEF:memory_used_m=memory_used,MAXIMUM \
    VDEF:memory_used_c=memory_used,LAST \
    VDEF:swap_used_a=swap_used,AVERAGE \
    VDEF:swap_used_m=swap_used,MAXIMUM \
    VDEF:swap_used_c=swap_used,LAST \
    AREA:memory_used#aa000080:"Used memory" \
    GPRINT:memory_used_a:"avg\: %8.2lf %sB" \
    GPRINT:memory_used_m:"max\: %8.2lf %sB" \
    GPRINT:memory_used_c:"cur\: %8.2lf %sB\n" \
    AREA:memory_free#00aa0080:"Free memory\n":STACK \
    LINE:memory_used#aa0000: \
    AREA:swap_used_neg#80000080:"Used swap  " \
    GPRINT:swap_used_a:"avg\: %8.2lf %sB" \
    GPRINT:swap_used_m:"max\: %8.2lf %sB" \
    GPRINT:swap_used_c:"cur\: %8.2lf %sB\n" \
    AREA:swap_free_neg#00800080:"Free swap\n":STACK \
    LINE:swap_used_neg#aa0000:
}

if [ "$1" = "49d" ]; then
  WIDTH=935
  HEIGHT=100
else
  WIDTH=419
  HEIGHT=150
fi

grep ', "type": ' /var/www/status/json/stats.json | sed -e 's/.*, "type": "\([a-z\.]*\)", "host": .*/\1/' | while read LINE; do
  for graph in net packets cpu mem; do
    $graph $LINE $1 $WIDTH $HEIGHT > /dev/null
  done
done
