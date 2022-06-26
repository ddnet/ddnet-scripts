#!/usr/bin/env zsh

# Build DDNet releases for all platforms
# Prerequisites:
# pacman -S mingw-w64-binutils mingw-w64-gcc mingw-w64-crt mingw-w64-headers mingw-w64-winpthreads openssl-1.0
# https://github.com/tpoechtrager/osxcross build osxcross and its compiler-rt.sh (don't forget to install)
# https://github.com/mozilla/libdmg-hfsplus build and install
# steamworks sdk

[ $# -ne 1 ] && echo "Usage: ./build.sh VERSION" && exit 1

renice -n 19 -p $$ > /dev/null
ionice -n 3 -p $$

unset CC
unset CXX
CXXFLAGS_STEAM="-DDDNET_CHECKSUM_SALT=$(cat steam_salt)"
CXXFLAGS_WEB="-DDDNET_CHECKSUM_SALT=$(cat web_salt)"
PATH=$PATH:/usr/local/bin:/opt/android-sdk/build-tools/23.0.3:/opt/android-sdk/tools:/opt/android-ndk:/opt/android-sdk/platform-tools
BUILDDIR=/home/deen/isos/ddnet
BUILDS=$BUILDDIR/builds

set -ex

# Flags to pass to cmake when building a regular website build, Steam build is
# always without autoupdater and without update info. For nightlies and RCs use:
# UPDATE_FLAGS="-DAUTOUPDATE=OFF -DINFORM_UPDATE=OFF" UPDATE_FLAGS_MACOS=-DINFORM_UPDATE=OFF
UPDATE_FLAGS="${UPDATE_FLAGS:--DAUTOUPDATE=ON}"
UPDATE_FLAGS_MACOS="${UPDATE_FLAGS_MACOS:-}"

MAIN_REPO_USER="${MAIN_REPO_USER:-ddnet}"
MAIN_REPO_NAME="${MAIN_REPO_NAME:-ddnet}"
MAIN_REPO_BRANCH="${MAIN_REPO_BRANCH:-master}"

LIBS_REPO_USER="${LIBS_REPO_USER:-ddnet}"
LIBS_REPO_NAME="${LIBS_REPO_NAME:-ddnet-libs}"
LIBS_REPO_BRANCH="${LIBS_REPO_BRANCH:-master}"

VERSION=$1
NOW=$(date +'%F %R')
echo "Starting build of $VERSION at $NOW"

build_source ()
{
  XZ_OPT=-9 tar cfJ DDNet-$VERSION.tar.xz DDNet-$VERSION
  mv DDNet-$VERSION.tar.xz $BUILDS
  rm -rf DDNet-$VERSION
}

build_macos ()
{
  SUFFIX=$1
  FLAGS=$2
  rm -rf macos$SUFFIX
  mkdir macos$SUFFIX
  cd macos$SUFFIX
  PATH=${PATH:+$PATH:}/home/deen/git/osxcross/target/bin
  eval `osxcross-conf`
  export OSXCROSS_OSX_VERSION_MIN=10.9
  cmake -DVERSION=$VERSION -DCMAKE_OSX_ARCHITECTURES="arm64;x86_64" -DCMAKE_BUILD_TYPE=Release -DDISCORD=ON -DWEBSOCKETS=OFF -DIPO=ON -DPREFER_BUNDLED_LIBS=ON -DCMAKE_TOOLCHAIN_FILE=cmake/toolchains/darwin-arm64.toolchain -DCMAKE_OSX_SYSROOT=/home/deen/git/osxcross/target/SDK/MacOSX11.0.sdk/ $(echo $FLAGS) ../ddnet-source
  make -j1 package_default
}

build_macos_website ()
{
  CXXFLAGS="'$CXXFLAGS_WEB'" build_macos "" $UPDATE_FLAGS_MACOS
  mv DDNet-*.dmg $BUILDS/DDNet-$VERSION-macos.dmg
  cd ..
  rm -rf macos
}

build_macos_steam ()
{
  CXXFLAGS="'$CXXFLAGS_STEAM'" build_macos -steam "-DSTEAM=ON"
  mv DDNet-*.dmg ../DDNet-$VERSION-steam-macos.dmg
  cd ..
  rm -rf macos-steam
}

build_remote_macos ()
{
  SUFFIX=$1
  OUR_CXXFLAGS=$2
  FLAGS=$3
  ssh deen@si "export PATH=/opt/homebrew/bin:$PATH && rm -rf macos$SUFFIX && \
  mkdir macos$SUFFIX && \
  cd macos$SUFFIX && \
  export CXXFLAGS=\"'$OUR_CXXFLAGS'\" && \
  cmake -DVERSION=$VERSION -DCMAKE_OSX_ARCHITECTURES=\"arm64;x86_64\" -DCMAKE_BUILD_TYPE=Release -DDISCORD=ON -DWEBSOCKETS=OFF -DIPO=ON -DPREFER_BUNDLED_LIBS=ON $(echo $FLAGS) ../ddnet-source && \
  make -j10 package_default
  "
}

build_remote_macos_website ()
{
  build_remote_macos "" $CXXFLAGS_WEB $UPDATE_FLAGS_MACOS
  scp deen@si:macos/DDNet-\*.dmg $BUILDS/DDNet-$VERSION-macos.dmg
  ssh deen@si "rm -rf macos"
}

build_remote_macos_steam ()
{
  build_remote_macos -steam $CXXFLAGS_STEAM "-DSTEAM=ON"
  rm -rf DDNet-$VERSION-steam-macos
  scp -r deen@si:macos-steam/pack_DDNet-\*_dmg DDNet-$VERSION-steam-macos
  ssh deen@si "rm -rf macos-steam"
}

build_linux ()
{
  PLATFORM=$1
  DIR=$2

  cd $DIR
  mkdir -p proc sys dev
  umount proc sys dev 2> /dev/null || true
  mount -t proc proc proc/
  mount -t sysfs sys sys/
  mount -o bind /dev dev/

  rm -rf ddnet-source ddnet-source-steam ddnet-libs-source $MAIN_REPO_NAME-$MAIN_REPO_BRANCH $LIBS_REPO_NAME-$LIBS_REPO_BRANCH
  unzip -q $BUILDDIR/main.zip
  unzip -q $BUILDDIR/libs.zip
  mv $MAIN_REPO_NAME-$MAIN_REPO_BRANCH ddnet-source
  rm -rf ddnet-source/ddnet-libs
  mv $LIBS_REPO_NAME-$LIBS_REPO_BRANCH ddnet-source/ddnet-libs
  cp -r ddnet-source ddnet-source-steam

  # No Discord lib for Linux available for x86
  if [ "$PLATFORM" = "x86_64" ]; then
    DISCORD=ON
  else
    DISCORD=OFF
  fi

  chroot . sh -c "cd ddnet-source && \
    export CXXFLAGS=\"'$CXXFLAGS_WEB' -no-pie\" && \
    export LDFLAGS=\"-no-pie\" && \
    cmake -DVERSION=$VERSION -DCMAKE_BUILD_TYPE=Release -DDISCORD=$DISCORD -DDISCORD_DYNAMIC=$DISCORD -DWEBSOCKETS=OFF -DIPO=ON $(echo $UPDATE_FLAGS) -DPREFER_BUNDLED_LIBS=ON && \
    make -j1 package_default"
  chroot . sh -c "cd ddnet-source-steam && \
    export CXXFLAGS=\"'$CXXFLAGS_STEAM' -no-pie\" && \
    export LDFLAGS=\"-no-pie\" && \
    cmake -DVERSION=$VERSION -DCMAKE_BUILD_TYPE=Release -DDISCORD=$DISCORD -DDISCORD_DYNAMIC=$DISCORD -DWEBSOCKETS=OFF -DIPO=ON -DSTEAM=ON -DPREFER_BUNDLED_LIBS=ON && \
    make -j1 package_default"
  mv ddnet-source/DDNet-*.tar.xz $BUILDS/DDNet-$VERSION-linux_$PLATFORM.tar.xz
  mv ddnet-source-steam/DDNet-*.tar.xz ../DDNet-$VERSION-steam-linux_$PLATFORM.tar.xz

  rm -rf ddnet-source ddnet-source-steam
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
  cmake -DVERSION=$VERSION -DCMAKE_BUILD_TYPE=RelWithDebInfo -DDISCORD=ON -DWEBSOCKETS=OFF -DPREFER_BUNDLED_LIBS=ON -DCMAKE_TOOLCHAIN_FILE=cmake/toolchains/mingw$PLATFORM.toolchain -DCMAKE_DISABLE_FIND_PACKAGE_GTest=ON -DEXCEPTION_HANDLING=ON $(echo $BUILDOPTS) ../ddnet-source
  make -j1
  XZ_OPT=-9 tar cfJ DDNet-$VERSION-win$PLATFORM$SUFFIX-symbols.tar.xz DDNet.exe DDNet-Server.exe
  make -j1 package_default
  unset PREFIX \
    TARGET_FAMILY TARGET_PLATFORM TARGET_ARCH
}

build_windows_website ()
{
  PLATFORM=$1
  BUILDOPTS=$2
  CXXFLAGS="'$CXXFLAGS_WEB' -pie" build_windows $PLATFORM "$UPDATE_FLAGS $(echo $BUILDOPTS)"
  mv DDNet-*.zip $BUILDS/DDNet-$VERSION-win$PLATFORM.zip
  mv DDNet-*-symbols.tar.xz $BUILDS/
  cd ..
  rm -rf win$PLATFORM
}

build_windows_steam ()
{
  PLATFORM=$1
  BUILDOPTS=$2
  CXXFLAGS="'$CXXFLAGS_STEAM' -pie" build_windows $PLATFORM "-DSTEAM=ON $(echo $BUILDOPTS)" "-steam"
  mv DDNet-*.zip ../DDNet-$VERSION-steam-win$PLATFORM.zip
  mv DDNet-*-symbols.tar.xz $BUILDS/
  cd ..
  rm -rf win$PLATFORM-steam
}

# Get the sources
rm -rf main.zip libs.zip
wget -nv -O main.zip https://github.com/$MAIN_REPO_USER/$MAIN_REPO_NAME/archive/$MAIN_REPO_BRANCH.zip
wget -nv -O libs.zip https://github.com/$LIBS_REPO_USER/$LIBS_REPO_NAME/archive/$LIBS_REPO_BRANCH.zip
rm -rf ddnet-source $MAIN_REPO_NAME-$MAIN_REPO_BRANCH $LIBS_REPO_NAME-$LIBS_REPO_BRANCH
unzip -q main.zip
mv $MAIN_REPO_NAME-$MAIN_REPO_BRANCH ddnet-source
cp -r ddnet-source DDNet-$VERSION

build_source &

unzip -q libs.zip
rm -rf ddnet-source/ddnet-libs
mv $LIBS_REPO_NAME-$LIBS_REPO_BRANCH ddnet-source/ddnet-libs
# Can't cross-compiler currently since macOS with arm is stricter with unsigned
# binaries and signing doesn't work. Temporarily use build from macOS:
MAC_AVAILABLE=true
ssh deen@si "rm -rf ddnet-source" || MAC_AVAILABLE=false
if [ "$MAC_AVAILABLE" = true ]; then
  rsync -avzP ddnet-source deen@si:
  (build_remote_macos_website; build_remote_macos_steam; ssh deen@si "rm -rf ddnet-source") &> builds/mac.log &
fi
#(build_macos_website; build_macos_steam) &> builds/mac.log &

build_linux x86_64 $BUILDDIR/debian10 &> builds/linux_x86_64.log &
CFLAGS=-m32 LDFLAGS=-m32 build_linux x86 $BUILDDIR/debian10_x86 &> builds/linux_x86.log &

# IPO causes issues with DrMinGW stack traces, so disable for now
# https://github.com/ddnet/ddnet/issues/5371
(TARGET_FAMILY=windows TARGET_PLATFORM=win64 TARGET_ARCH=amd64 \
  PREFIX=x86_64-w64-mingw32- PATH=/usr/x86_64-w64-mingw32/bin:$PATH \
  build_windows_website 64 "-DIPO=OFF"

TARGET_FAMILY=windows TARGET_PLATFORM=win64 TARGET_ARCH=amd64 \
  PREFIX=x86_64-w64-mingw32- PATH=/usr/x86_64-w64-mingw32/bin:$PATH \
  build_windows_steam 64 "-DIPO=OFF") &> builds/win64.log &

(TARGET_FAMILY=windows TARGET_PLATFORM=win32 TARGET_ARCH=ia32 \
  PREFIX=i686-w64-mingw32- PATH=/usr/i686-w64-mingw32/bin:$PATH \
  build_windows_website 32 "-DIPO=OFF"

TARGET_FAMILY=windows TARGET_PLATFORM=win32 TARGET_ARCH=ia32 \
  PREFIX=i686-w64-mingw32- PATH=/usr/i686-w64-mingw32/bin:$PATH \
  build_windows_steam 32 "-DIPO=OFF") &> builds/win32.log &

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
cp $BUILDDIR/ddnet-source/ddnet-libs/sdl/linux/lib64/libSDL2-2.0.so.0 $BUILDDIR/ddnet-source/ddnet-libs/discord/linux/lib64/discord_game_sdk.so ddnet
cp $BUILDDIR/steamworks/sdk/redistributable_bin/linux64/libsteam_api.so ddnet
zip -9r DDNet-$VERSION-linux_x86_64.zip ddnet
rm -r ddnet

tar xvf ../DDNet-$VERSION-steam-linux_x86.tar.xz
rm -r DDNet-*-linux_x86/data
mv DDNet-*-linux_x86 ddnet
cp $BUILDDIR/ddnet-source/ddnet-libs/sdl/linux/lib32/libSDL2-2.0.so.0 ddnet
cp $BUILDDIR/steamworks/sdk/redistributable_bin/linux32/libsteam_api.so ddnet
zip -9r DDNet-$VERSION-linux_x86.zip ddnet
rm -r ddnet

#7z x ../DDNet-$VERSION-steam-macos.dmg
if [ "$MAC_AVAILABLE" = true ]; then
  cp -a ../DDNet-$VERSION-steam-macos .
  rm -r DDNet-*-macos/DDNet.app/Contents/Resources/data DDNet-*-macos/DDNet-Server.app/Contents/Resources/data
  mkdir ddnet
  mv DDNet-*-macos/DDNet.app/Contents/MacOS/DDNet DDNet-*-macos/DDNet-Server.app/Contents/MacOS/DDNet-Server* ddnet
  mv DDNet-*-macos/DDNet.app/Contents/Frameworks .
  cp $BUILDDIR/steamworks/sdk/redistributable_bin/osx/libsteam_api.dylib Frameworks
  zip -9r DDNet-$VERSION-macos.zip ddnet Frameworks
  rm -r ddnet Frameworks DDNet-*-macos
fi

NOW=$(date +'%F %R')
echo "Finished build of $VERSION at $NOW"
