#!/bin/sh

cd /home/teeworlds/servers

update()
{
  type=`grep "console: executing 'types/.*/flexname.cfg'" servers/$1.log | tail -n 1 | sed -e "s#.*console: executing 'types/\(.*\)/flexname.cfg'#\1#"`
  sleep 0.2
  echo "exec types/$type/flexname.cfg" > servers/$1.fifo
}

for i in `cat all-servers`; do
  update $i &
done
