#!/bin/sh
while true; do
  mv servers/$1.log servers/$1.log.old
  ASAN_OPTIONS=log_path=./ASAN:print_stacktrace=1:check_initialization_order=1:detect_leaks=1:halt_on_errors=0 ni -15 2 ./DDNet-Server-asan -f servers/$1.cfg
  sleep 1
done
