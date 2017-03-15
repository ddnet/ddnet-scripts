#!/usr/bin/env zsh

for i in `cat ../servers/all-types`; do
  grep "|" ../servers/types/${i:l}/maps | while read j; do
    m=`echo "$j" | cut -d"|" -f2`
    grep -q -F "|$m|" releases || grep -q "|$m$" releases || ((nice -n19 ionice -c3 git log --diff-filter=A -- "maps/$m.map" | grep Date | sed -e "s/Date: *//" | sed -e "s/:[0-9]* [+-][0-9][0-9]00//" | tail -n 1 | tr '\n' '\t'; echo "$i\t$j") >> releases)
  done
done
sort -r releases > releases.$$.tmp
mv releases.$$.tmp releases
