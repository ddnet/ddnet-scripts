#!/bin/sh

# Build DDNet releases for all platforms

[ $# -ne 1 ] && echo "Usage: ./build.sh VERSION" && exit 1

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
  XZ_OPT=-9 tar cfJ DDNet-$VERSION.tar.xz DDNet-$VERSION
  mv DDNet-$VERSION.tar.xz $BUILDS
  rm -rf DDNet-$VERSION
}

build_macosx ()
{
  rm -rf macosx
  mkdir macosx
  cd macosx
  PATH=${PATH:+$PATH:}/home/deen/git/osxcross/target/bin
  eval `osxcross-conf`
  export OSXCROSS_OSX_VERSION_MIN=10.9
  cmake -DCMAKE_BUILD_TYPE=Release -DPREFER_BUNDLED_LIBS=ON -DCMAKE_TOOLCHAIN_FILE=cmake/toolchains/darwin.toolchain -DCMAKE_OSX_SYSROOT=/home/deen/git/osxcross/target/SDK/MacOSX10.13.sdk/ ../ddnet-master
  make -j2
  make package_default
  mv DDNet-*.dmg $BUILDS/DDNet-$VERSION-osx.dmg
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

  rm -rf ddnet-master
  unzip -q $WEBSITE/master.zip
  unzip -q $WEBSITE/libs.zip
  rm -rf ddnet-master/ddnet-libs
  mv ddnet-libs-master ddnet-master/ddnet-libs

  chroot . sh -c "cd ddnet-master && cmake -DCMAKE_BUILD_TYPE=Release -DPREFER_BUNDLED_LIBS=ON && make && make package_default"
  mv ddnet-master/DDNet-*.tar.xz $BUILDS/DDNet-$VERSION-linux_$PLATFORM.tar.xz

  rm -rf ddnet-master
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
  cmake -DCMAKE_BUILD_TYPE=Release -DPREFER_BUNDLED_LIBS=ON -DCMAKE_TOOLCHAIN_FILE=cmake/toolchains/mingw$PLATFORM.toolchain ../ddnet-master
  make package_default
  mv DDNet-*.zip $BUILDS/DDNet-$VERSION-win$PLATFORM.zip
  cd ..
  rm -rf win$PLATFORM
  unset PREFIX \
    TARGET_FAMILY TARGET_PLATFORM TARGET_ARCH
}

build_windows_videorecorder ()
{
  PLATFORM=$1

  rm -rf win$PLATFORM-videorecorder
  mkdir win$PLATFORM-videorecorder
  cd win$PLATFORM-videorecorder
  cmake -DVIDEORECORDER=ON -DAUTOUPDATE=OFF -DCMAKE_BUILD_TYPE=Release -DPREFER_BUNDLED_LIBS=ON -DCMAKE_TOOLCHAIN_FILE=cmake/toolchains/mingw$PLATFORM.toolchain ../ddnet-master
  make package_default
  unzip DDNet-$VERSION-win$PLATFORM.zip
  rm DDNet-$VERSION-win$PLATFORM.zip
  mv DDNet-$VERSION-win$PLATFORM DDNet-$VERSION-videorecorder-win$PLATFORM
  zip -9r DDNet-$VERSION-videorecorder-win$PLATFORM.zip DDNet-$VERSION-videorecorder-win$PLATFORM
  mv DDNet-$VERSION-videorecorder-win$PLATFORM.zip $BUILDS
  cd ..
  rm -rf win$PLATFORM-videorecorder
  unset PREFIX \
    TARGET_FAMILY TARGET_PLATFORM TARGET_ARCH
}

# Get the sources
cd $WEBSITE
rm -rf master.zip libs.zip
wget -nv -O master.zip https://github.com/ddnet/ddnet/archive/master.zip
wget -nv -O libs.zip https://github.com/ddnet/ddnet-libs/archive/master.zip
cd $BUILDDIR
rm -rf ddnet-master
unzip -q $WEBSITE/master.zip
cp -r ddnet-master DDNet-$VERSION
TIME_PREPARATION=$(($(date +%s) - $START_TIME))

build_source &

unzip -q $WEBSITE/libs.zip
rm -rf ddnet-master/ddnet-libs
mv ddnet-libs-master ddnet-master/ddnet-libs

build_macosx &> builds/mac.log &
build_linux x86_64 $BUILDDIR/debian6 &> builds/linux_x86_64.log &
CFLAGS=-m32 LDFLAGS=-m32 build_linux x86 $BUILDDIR/debian6_x86 &> builds/linux_x86.log &

TARGET_FAMILY=windows TARGET_PLATFORM=win64 TARGET_ARCH=amd64 \
  PREFIX=x86_64-w64-mingw32- PATH=/usr/x86_64-w64-mingw32/bin:$PATH \
  build_windows 64 &> builds/win64.log &

TARGET_FAMILY=windows TARGET_PLATFORM=win64 TARGET_ARCH=amd64 \
  PREFIX=x86_64-w64-mingw32- PATH=/usr/x86_64-w64-mingw32/bin:$PATH \
  build_windows_videorecorder 64 &> builds/win64-videorecorder.log &

TARGET_FAMILY=windows TARGET_PLATFORM=win32 TARGET_ARCH=ia32 \
  PREFIX=i686-w64-mingw32- PATH=/usr/i686-w64-mingw32/bin:$PATH \
  build_windows 32 &> builds/win32.log &

# Android
# TODO: Reenable with SDL2
#START_TIME=$(date +%s)
#cd $BUILDDIR/commandergenius/project/jni/application/teeworlds
#sed -e "s/YYYY/$VERSION/; s/XXXX/$NUMVERSION/" \
#  AndroidAppSettings.tmpl > AndroidAppSettings.cfg
#rm -rf src
#unzip -q $WEBSITE/master.zip
#mv ddnet-master src
#cp -r generated src/src/game/
#rm -rf AndroidData
#./AndroidPreBuild.sh
#
#cd $BUILDDIR/commandergenius
#./changeAppSettings.sh -a
#android update project -p project
#./build.sh
#{ jarsigner -verbose -keystore ~/.android/release.keystore -storepass $PASS \
#  -sigalg MD5withRSA -digestalg SHA1 \
#  project/bin/MainActivity-release-unsigned.apk androidreleasekey; } 2>/dev/null
#zipalign 4 project/bin/MainActivity-release-unsigned.apk \
#  project/bin/MainActivity-release.apk
#mv project/bin/MainActivity-release.apk $BUILDS/DDNet-${VERSION}.apk
#TIME_ANDROID=$(($(date +%s) - $START_TIME))

wait
rm -rf ddnet-master

rm -rf steam
mkdir steam
cd steam
unzip $BUILDS/DDNet-$VERSION-win64.zip
tar xvf $BUILDS/DDNet-$VERSION-linux_x86_64.tar.xz
7z x $BUILDS/DDNet-$VERSION-osx.dmg # might have problems with symlinks
mv DDNet-$VERSION-win64/data data
zip -9r DDNet-$VERSION-data.zip data
zip -9r DDNet-$VERSION-win64.zip data
rm -r DDNet-$VERSION-linux_x86_64/data
zip -9r DDNet-$VERSION-linux_x86_64.zip DDNet-$VERSION-linux_x86_64
rm -r DDNet-$VERSION-osx/DDNet.app/Contents/Resources/data DDNet-$VERSION-osx/DDNet-Server.app/Contents/Resources/data
zip -9r DDNet-$VERSION-linux_x86_64.zip DDNet-$VERSION-osx

NOW=$(date +'%F %R')
echo "Finished build of $VERSION at $NOW"
