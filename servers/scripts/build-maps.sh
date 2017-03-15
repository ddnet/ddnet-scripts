#!/usr/bin/env zsh
mkdir -p /home/teeworlds/ddnet-maps
cd /home/teeworlds/ddnet-maps
rm -rf types

echo 'add_path $USERDIR\nadd_path $CURRENTDIR' > storage.cfg

for i in `cat ../servers/all-types`; do
  TYPEDIR=types/${i:l}
  echo "add_path $TYPEDIR" >> storage.cfg
  mkdir -p $TYPEDIR/maps
  grep "|" ../servers/$TYPEDIR/maps | cut -d"|" -f2 | while read j; do
    cp -- "../servers/maps/$j.map" $TYPEDIR/maps
    cp ../servers/$TYPEDIR/flexvotes.cfg $TYPEDIR
    grep -v "flexname.cfg" ../servers/$TYPEDIR/flexreset.cfg > $TYPEDIR/flexreset.cfg
    tail -n +5 ../servers/$TYPEDIR/votes.cfg > $TYPEDIR/votes.cfg
  done
done

git add * &>/dev/null
git commit -a -m "daily update" &>/dev/null
git push &>/dev/null
