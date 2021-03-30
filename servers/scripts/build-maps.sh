#!/usr/bin/env zsh

WORKDIR=~/ddnet-maps
COMPDIR=/var/www-maps/compilations

mkdir -p $WORKDIR
cd $WORKDIR
rm -rf types

echo 'add_path $USERDIR\nadd_path $DATADIR\nadd_path $CURRENTDIR' > storage.cfg

for i in $(cat ~/servers/all-types); do
  TYPEDIR=types/${i:l}
  echo "add_path $TYPEDIR" >> storage.cfg
  mkdir -p $TYPEDIR/maps
  cp ../servers/$TYPEDIR/flexvotes.cfg $TYPEDIR
  cp ../servers/$TYPEDIR/maps $TYPEDIR/maps.txt
  grep -v "flexname.cfg" ../servers/$TYPEDIR/flexreset.cfg > $TYPEDIR/flexreset.cfg
  cp ../servers/$TYPEDIR/votes.cfg $TYPEDIR/votes.cfg
  grep "|" ../servers/$TYPEDIR/maps | cut -d"|" -f2 | while read j; do
    chmod 644 -- "../servers/maps/$j.map"
    cp -- "../servers/maps/$j.map" $TYPEDIR/maps
  done
done

git pull &>/dev/null
git add * &>/dev/null
MAPS=$(git diff --name-status HEAD | grep '\.map')
if [ $? -eq 0 ]; then
  git commit -a -m "$(echo "$MAPS" | grep '\.map' | sed -e 's#^\(.\).*/maps/\(.*\).map.*$#\1 \2,#' | tr '\n' ' ' | head -c -2)" &>/dev/null
  git push &>/dev/null

  cd types
  for i in $(cat ~/servers/all-types); do
    TYPEDIR=${i:l}
    ZIPFILE=~/servers/${i:l}.zip
    zip -9rq $ZIPFILE $TYPEDIR
    mv $ZIPFILE $COMPDIR
  done
  cd ../..
  zip -9rq ~/servers/ddnet-maps.zip ddnet-maps -x '*.git*'
  mv ~/servers/ddnet-maps.zip $COMPDIR
fi

cd ~/servers
zip -9rq maps7.zip maps7
mv maps7.zip $COMPDIR
