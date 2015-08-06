#!/bin/sh
text=$(echo "show slave status\G" | mysql -u repl -p'SECRETPASS')
echo "$text" | grep -q "Waiting for master to send event" && exit 0
echo "$text" | grep -q "Checking master version" && exit 0
echo "$text" | grep -q "Reconnecting after a failed master event read" && exit 0
sleep 300
text=$(echo "show slave status\G" | mysql -u repl -p'SECRETPASS')
echo "$text" | grep -q "Waiting for master to send event" && exit 0
echo "$text" | grep -q "Checking master version" && exit 0
echo "$text" | grep -q "Reconnecting after a failed master event read" && exit 0
echo "MySQL replication failed" && exit 1
