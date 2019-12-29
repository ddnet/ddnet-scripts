#!/bin/sh

# Build DDNet7 server releases for all platforms

[ $# -ne 1 ] && echo "Usage: ./build7.sh VERSION" && exit 1

START_TIME=$(date +%s)
renice -n 19 -p $$ > /dev/null
ionice -n 3 -p $$

unset CC
unset CXX
PATH=$PATH:/usr/local/bin:/opt/android-sdk/build-tools/23.0.3:/opt/android-sdk/tools:/opt/android-ndk:/opt/android-sdk/platform-tools
BUILDDIR=/home/deen/isos/ddnet
BUILDS=$BUILDDIR/builds
WEBSITE=/var/www/felsing.ath.cx/htdocs/dennis
PASS="$(cat pass)"

set -ex

VERSION=$1
NUMVERSION=$(python -c "try:
  s = \"$VERSION\".split('.')
  t = s[2] if len(s) > 2 else '0'
  print(s[0].zfill(2) + s[1] + t)
except:
  print('0000')")

NOW=$(date +'%F %R')
echo "Starting build of $VERSION at $NOW"

build_source ()
{
  XZ_OPT=-9 tar cfJ DDNet7-Server-$VERSION.tar.xz DDNet7-Server-$VERSION
  mv DDNet7-Server-$VERSION.tar.xz $BUILDS
  rm -rf DDNet7-Server-$VERSION
}

build_macosx ()
{
  rm -rf macosx
  mkdir macosx
  cd macosx
  PATH=${PATH:+$PATH:}/home/deen/git/osxcross/target/bin
  cmake -DCMAKE_BUILD_TYPE=Release -DCLIENT=OFF -DPREFER_BUNDLED_LIBS=ON -DCMAKE_TOOLCHAIN_FILE=cmake/toolchains/darwin.toolchain -DCMAKE_OSX_SYSROOT=/home/deen/git/osxcross/target/SDK/MacOSX10.11.sdk/ ../ddnet7-master
  make DDNet7-Server
  make package_default
  mv DDNet7-Server-*.dmg $BUILDS/DDNet7-Server-$VERSION-osx.dmg
  cd ..
  rm -rf macosx
}

build_linux ()
{
  PLATFORM=$1
  DIR=$2

  cd $DIR
  umount proc sys dev 2> /dev/null || true
  mount -t proc proc proc/
  mount -t sysfs sys sys/
  mount -o bind /dev dev/

  rm -rf ddnet7-master
  unzip -q $WEBSITE/master.zip

  chroot . sh -c "cd ddnet7-master && cmake -DCMAKE_BUILD_TYPE=Release -DCLIENT=OFF -DPREFER_BUNDLED_LIBS=ON && make DDNet7-Server && make package_default"
  mv ddnet7-master/DDNet7-Server-*.tar.xz $BUILDS/DDNet7-Server-$VERSION-linux_$PLATFORM.tar.xz

  rm -rf ddnet7-master
  umount proc sys dev
  unset CFLAGS LDFLAGS PKG_CONFIG_PATH
}

# Windows
build_windows ()
{
  PLATFORM=$1

  rm -rf win$PLATFORM
  mkdir win$PLATFORM
  cd win$PLATFORM
  cmake -DCMAKE_BUILD_TYPE=Release -DCLIENT=OFF -DPREFER_BUNDLED_LIBS=ON -DCMAKE_TOOLCHAIN_FILE=cmake/toolchains/mingw$PLATFORM.toolchain ../ddnet7-master
  make DDNet7-Server
  make package_default
  mv DDNet7-Server-*.zip $BUILDS/DDNet7-Server-$VERSION-win$PLATFORM.zip
  cd ..
  rm -rf win$PLATFORM
  unset PREFIX \
    TARGET_FAMILY TARGET_PLATFORM TARGET_ARCH
}

# Get the sources
cd $WEBSITE
rm -rf master.zip
wget -nv -O master.zip https://github.com/ddnet/ddnet7/archive/master.zip
cd $BUILDDIR
rm -rf ddnet7-master
unzip -q $WEBSITE/master.zip
cp -r ddnet7-master DDNet7-Server-$VERSION
TIME_PREPARATION=$(($(date +%s) - $START_TIME))

build_source &

build_macosx &> builds/mac.log &
build_linux x86_64 $BUILDDIR/debian6 &> builds/linux_x86_64.log &
CFLAGS=-m32 LDFLAGS=-m32 build_linux x86 $BUILDDIR/debian6_x86 &> builds/linux_x86.log &

TARGET_FAMILY=windows TARGET_PLATFORM=win64 TARGET_ARCH=amd64 \
  PREFIX=x86_64-w64-mingw32- PATH=/usr/x86_64-w64-mingw32/bin:$PATH \
  build_windows 64 &> builds/win64.log &

TARGET_FAMILY=windows TARGET_PLATFORM=win32 TARGET_ARCH=ia32 \
  PREFIX=i686-w64-mingw32- PATH=/usr/i686-w64-mingw32/bin:$PATH \
  build_windows 32 &> builds/win32.log &

wait
rm -rf ddnet7-master

NOW=$(date +'%F %R')
echo "Finished build of $VERSION at $NOW"
