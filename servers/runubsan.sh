#!/bin/sh
while true; do
  mv servers/$1.log servers/$1.log.old
  UBSAN_OPTIONS=log_path=./UBSAN:print_stacktrace=1 ni -15 2 ./DDNet-Server-ubsan -f servers/$1.cfg
  sleep 1
done
