#!/usr/bin/env zsh

function mcp {
  cp $1 $2.$$.tmp && mv $2.$$.tmp $2
}

set -e -x
setopt extended_glob
OLD_VERSION=$1
VERSION=$2
renice -n 19 -p $$
ionice -c 3 -p $$

unzip /var/www/downloads/DDNet-$OLD_VERSION-win32.zip
unzip /var/www/downloads/DDNet-$OLD_VERSION-win64.zip
tar xvf /var/www/downloads/DDNet-$OLD_VERSION-linux_x86.tar.xz
tar xvf /var/www/downloads/DDNet-$OLD_VERSION-linux_x86_64.tar.xz
unzip /var/www/downloads/DDNet-$VERSION-win32.zip
unzip /var/www/downloads/DDNet-$VERSION-win64.zip
tar xvf /var/www/downloads/DDNet-$VERSION-linux_x86.tar.xz
tar xvf /var/www/downloads/DDNet-$VERSION-linux_x86_64.tar.xz

./diff_update.py $OLD_VERSION $VERSION

mv data data.old
mv DDNet-$VERSION-win64/data data
mv DDNet-$VERSION-win64/license.txt .
mv DDNet-$VERSION-win64/storage.cfg .
mv DDNet-$VERSION-win64/config_directory.bat .
mv DDNet-$VERSION-win64/config_directory.sh .
rm -r data.old

for i in DDNet-$VERSION-win32/*.{exe,dll}; do mcp $i ${i:r:t}-win32.${i:e}; done
for i in DDNet-$VERSION-win64/*.{exe,dll}; do mcp $i ${i:r:t}-win64.${i:e}; done
for i in DDNet-$VERSION-linux_x86/{DDNet,DDNet-Server}; do mcp $i ${i:r:t}-linux-x86; done
if ls DDNet-$VERSION-linux_x86/*.so 2>&1 > /dev/null; then
  for i in DDNet-$VERSION-linux_x86/*.so; do mcp $i ${i:r:t}-linux-x86.so; done
fi
for i in DDNet-$VERSION-linux_x86_64/{DDNet,DDNet-Server}; do mcp $i ${i:r:t}-linux-x86_64; done
if ls DDNet-$VERSION-linux_x86_64/*.so 2>&1 > /dev/null; then
  for i in DDNet-$VERSION-linux_x86_64/*.so; do mcp $i ${i:r:t}-linux-x86_64.so; done
fi

cp update.json update.json.old && mv update.json.new update.json

rm -r DDNet-$OLD_VERSION-*
rm -r DDNet-$VERSION-*

cd /var/www/downloads
rm -f DDNet-latest-win32.zip DDNet-latest-win64.zip DDNet-latest-linux_x86_64.tar.xz DDNet-latest-linux_x86.tar.xz DDNet-latest-macos.dmg
ln -s DDNet-$VERSION-win32.zip DDNet-latest-win32.zip
ln -s DDNet-$VERSION-win64.zip DDNet-latest-win64.zip
ln -s DDNet-$VERSION-linux_x86_64.tar.xz DDNet-latest-linux_x86_64.tar.xz
ln -s DDNet-$VERSION-linux_x86.tar.xz DDNet-latest-linux_x86.tar.xz
ln -s DDNet-$VERSION-macos.dmg DDNet-latest-macos.dmg

(sha256sum DDNet-*~*latest(.) GraphicsTools-* > sha256sums.$$.tmp
mv sha256sums.$$.tmp sha256sums.txt) &
(md5sum DDNet-*~*latest(.) GraphicsTools-* > md5sums.$$.tmp
mv md5sums.$$.tmp md5sums.txt) &
