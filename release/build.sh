#!/usr/bin/env zsh

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
  rm -rf macosx$1
  mkdir macosx$1
  cd macosx$1
  PATH=${PATH:+$PATH:}/home/deen/git/osxcross/target/bin
  eval `osxcross-conf`
  export OSXCROSS_OSX_VERSION_MIN=10.9
  cmake -DCMAKE_BUILD_TYPE=Release -DVIDEORECORDER=ON -DWEBSOCKETS=OFF -DPREFER_BUNDLED_LIBS=ON -DCMAKE_TOOLCHAIN_FILE=cmake/toolchains/darwin.toolchain -DCMAKE_OSX_SYSROOT=/home/deen/git/osxcross/target/SDK/MacOSX10.13.sdk/ ../ddnet-master
  make -j2
  make package_default
}

build_macosx_website ()
{
  build_macosx
  mv DDNet-*.dmg $BUILDS/DDNet-$VERSION-osx.dmg
  cd ..
  rm -rf macosx
}

build_macosx_steam ()
{
  build_macosx -steam
  mv DDNet-*.dmg ../DDNet-$VERSION-steam-osx.dmg
  cd ..
  rm -rf macosx-steam
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

  rm -rf ddnet-master ddnet-master-steam ddnet-libs-master
  unzip -q $WEBSITE/master.zip
  unzip -q $WEBSITE/libs.zip
  #mv ddnet-pr-ffmpeg2 ddnet-master
  rm -rf ddnet-master/ddnet-libs
  #mv ddnet-libs-pr-ffmpeg2 ddnet-master/ddnet-libs
  mv ddnet-libs-master ddnet-master/ddnet-libs
  cp -r ddnet-master ddnet-master-steam

  chroot . sh -c "cd ddnet-master && cmake -DCMAKE_BUILD_TYPE=Release -DVIDEORECORDER=ON -DWEBSOCKETS=OFF -DAUTOUPDATE=ON -DPREFER_BUNDLED_LIBS=ON && make package_default"
  chroot . sh -c "cd ddnet-master-steam && cmake -DCMAKE_BUILD_TYPE=Release -DVIDEORECORDER=ON -DWEBSOCKETS=OFF -DSTEAM=ON -DPREFER_BUNDLED_LIBS=ON && CXXFLAGS='-DPLATFORM_SUFFIX=\"-steam\"' CPPFLAGS='-DPLATFORM_SUFFIX=\"-steam\"' make -j2 package_default"
  mv ddnet-master/DDNet-*.tar.xz $BUILDS/DDNet-$VERSION-linux_$PLATFORM.tar.xz
  mv ddnet-master-steam/DDNet-*.tar.xz ../DDNet-$VERSION-steam-linux_$PLATFORM.tar.xz

  rm -rf ddnet-master ddnet-master-steam
  umount proc sys dev
  unset CFLAGS LDFLAGS PKG_CONFIG_PATH
}

# Windows
build_windows ()
{
  PLATFORM=$1
  BUILDOPTS=$2
  SUFFIX=$3
  DIR=win$PLATFORM$SUFFIX

  rm -rf $DIR
  mkdir $DIR
  cd $DIR
  cmake -DCMAKE_BUILD_TYPE=Release -DVIDEORECORDER=ON -DWEBSOCKETS=OFF -DPREFER_BUNDLED_LIBS=ON -DCMAKE_TOOLCHAIN_FILE=cmake/toolchains/mingw$PLATFORM.toolchain $BUILDOPTS ../ddnet-master
  make package_default
  unset PREFIX \
    TARGET_FAMILY TARGET_PLATFORM TARGET_ARCH
}

build_windows_website ()
{
  PLATFORM=$1
  build_windows $PLATFORM "-DAUTOUPDATE=ON"
  mv DDNet-*.zip $BUILDS/DDNet-$VERSION-win$PLATFORM.zip
  cd ..
  rm -rf win$PLATFORM
}

build_windows_steam ()
{
  PLATFORM=$1
  build_windows $PLATFORM "-DSTEAM=ON" "-steam"
  mv DDNet-*.zip ../DDNet-$VERSION-steam-win$PLATFORM.zip
  cd ..
  rm -rf win$PLATFORM-steam
}

# Get the sources
cd $WEBSITE
rm -rf master.zip libs.zip
#wget -nv -O master.zip https://github.com/def-/ddnet/archive/pr-ffmpeg2.zip
#wget -nv -O libs.zip https://github.com/ddnet/ddnet-libs/archive/pr-ffmpeg2.zip
wget -nv -O master.zip https://github.com/ddnet/ddnet/archive/master.zip
wget -nv -O libs.zip https://github.com/ddnet/ddnet-libs/archive/master.zip
cd $BUILDDIR
rm -rf ddnet-master
unzip -q $WEBSITE/master.zip
#mv ddnet-pr-ffmpeg2 ddnet-master
cp -r ddnet-master DDNet-$VERSION
TIME_PREPARATION=$(($(date +%s) - $START_TIME))

build_source &

unzip -q $WEBSITE/libs.zip
rm -rf ddnet-master/ddnet-libs
#mv ddnet-libs-pr-ffmpeg2 ddnet-master/ddnet-libs
mv ddnet-libs-master ddnet-master/ddnet-libs

build_macosx_website &> builds/mac.log &
CXXFLAGS='-DPLATFORM_SUFFIX=\"-steam\"' CPPFLAGS='-DPLATFORM_SUFFIX=\"-steam\"' build_macosx_steam &> builds/mac-steam.log &
build_linux x86_64 $BUILDDIR/debian6 &> builds/linux_x86_64.log &
CFLAGS=-m32 LDFLAGS=-m32 build_linux x86 $BUILDDIR/debian6_x86 &> builds/linux_x86.log &

(TARGET_FAMILY=windows TARGET_PLATFORM=win64 TARGET_ARCH=amd64 \
  PREFIX=x86_64-w64-mingw32- PATH=/usr/x86_64-w64-mingw32/bin:$PATH \
  build_windows_website 64

TARGET_FAMILY=windows TARGET_PLATFORM=win64 TARGET_ARCH=amd64 \
  PREFIX=x86_64-w64-mingw32- PATH=/usr/x86_64-w64-mingw32/bin:$PATH \
  CXXFLAGS='-DPLATFORM_SUFFIX=\"-steam\"' CPPFLAGS='-DPLATFORM_SUFFIX=\"-steam\"' \
  build_windows_steam 64) &> builds/win64.log &

(TARGET_FAMILY=windows TARGET_PLATFORM=win32 TARGET_ARCH=ia32 \
  PREFIX=i686-w64-mingw32- PATH=/usr/i686-w64-mingw32/bin:$PATH \
  build_windows_website 32

TARGET_FAMILY=windows TARGET_PLATFORM=win32 TARGET_ARCH=ia32 \
  PREFIX=i686-w64-mingw32- PATH=/usr/i686-w64-mingw32/bin:$PATH \
  CXXFLAGS='-DPLATFORM_SUFFIX=\"-steam\"' CPPFLAGS='-DPLATFORM_SUFFIX=\"-steam\"' \
  build_windows_steam 32) &> builds/win32.log &

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

rm -rf steam
mkdir steam
cd steam
mkdir ddnet

unzip ../DDNet-$VERSION-steam-win64.zip
mv DDNet-*-win64/data ddnet/data
zip -9r DDNet-$VERSION-data.zip ddnet
rm -r ddnet

mv DDNet-*-win64 ddnet
cp $BUILDDIR/steamworks/sdk/redistributable_bin/win64/steam_api64.dll ddnet/steam_api.dll
zip -9r DDNet-$VERSION-win64.zip ddnet
rm -r ddnet

unzip ../DDNet-$VERSION-steam-win32.zip
rm -r DDNet-*-win32/data
mv DDNet-*-win32 ddnet
cp $BUILDDIR/steamworks/sdk/redistributable_bin/steam_api.dll ddnet/steam_api.dll
zip -9r DDNet-$VERSION-win32.zip ddnet
rm -r ddnet

tar xvf ../DDNet-$VERSION-steam-linux_x86_64.tar.xz
rm -r DDNet-*-linux_x86_64/data
mv DDNet-*-linux_x86_64 ddnet
cp $BUILDDIR/ddnet-master/ddnet-libs/sdl/linux/lib64/libSDL2-2.0.so.0 ddnet
cp $BUILDDIR/steamworks/sdk/redistributable_bin/linux64/libsteam_api.so ddnet
zip -9r DDNet-$VERSION-linux_x86_64.zip ddnet
rm -r ddnet

tar xvf ../DDNet-$VERSION-steam-linux_x86.tar.xz
rm -r DDNet-*-linux_x86/data
mv DDNet-*-linux_x86 ddnet
cp $BUILDDIR/ddnet-master/ddnet-libs/sdl/linux/lib32/libSDL2-2.0.so.0 ddnet
cp $BUILDDIR/steamworks/sdk/redistributable_bin/linux32/libsteam_api.so ddnet
zip -9r DDNet-$VERSION-linux_x86.zip ddnet
rm -r ddnet

7z x ../DDNet-$VERSION-steam-osx.dmg
rm -r DDNet-*-osx/DDNet.app/Contents/Resources/data DDNet-*-osx/DDNet-Server.app/Contents/Resources/data
mkdir ddnet
mv DDNet-*-osx/DDNet.app/Contents/MacOS/DDNet DDNet-*-osx/DDNet-Server.app/Contents/MacOS/DDNet-Server* ddnet
mv DDNet-*-osx/DDNet.app/Contents/Frameworks .
cp -r DDNet-*-osx/DDNet-Server.app/Contents/Frameworks/* Frameworks
cp $BUILDDIR/steamworks/sdk/redistributable_bin/osx/libsteam_api.dylib Frameworks
zip -9r DDNet-$VERSION-osx.zip ddnet Frameworks
rm -r ddnet Frameworks DDNet-*-osx

rm -rf ddnet-master

NOW=$(date +'%F %R')
echo "Finished build of $VERSION at $NOW"
