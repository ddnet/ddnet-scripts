#!/usr/bin/env zsh
# To be run at 23:05
cd /home/teeworlds/servers
cat > scripts/print.sh << EOF
#!/usr/bin/env zsh
echo "broadcast \"Advent of DDNet Day 24: Snow Problem (Moderate)\"" > /home/teeworlds/servers/servers/*fifo
sleep 7
echo "broadcast \"Finish 1 map a day to participate, see DDNet.org!\"" > /home/teeworlds/servers/servers/*fifo
EOF
./git-update-files-only.sh &
sleep 55m
echo "Moderate|3|Snow Problem|Soapy Sandwich" >> advent
