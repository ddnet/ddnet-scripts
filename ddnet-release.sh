#!/bin/sh

# Build DDNet releases for all platforms

[ $# -ne 1 ] && echo "Usage: ./build.sh VERSION" && exit 1

START_TIME=$(date +%s)
renice -n 19 -p $$ > /dev/null
ionice -n 3 -p $$

PATH=$PATH:/usr/local/bin:/opt/android-sdk/build-tools/23.0.2:/opt/android-sdk/tools:/opt/android-ndk:/opt/android-sdk/platform-tools
BUILDDIR=/media/ddnet
BUILDS=$BUILDDIR/builds
MACLOG=$BUILDS/mac.log
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

# Start the Mac OS X VM
qemu-system-x86_64 -k de -usb -device usb-kbd -device usb-mouse \
  -enable-kvm -vga std -m 2048 -smp 4,cores=4 -cpu core2duo -machine q35 \
  -device isa-applesmc,osk="ourhardworkbythesewordsguardedpleasedontsteal(c)AppleComputerInc" \
  -kernel ./chameleon_svn2360_boot -smbios type=2 \
  -device ide-drive,bus=ide.2,drive=MacHDD \
  -drive id=MacHDD,if=none,file=macosx.img \
  -netdev user,id=hub0port0,hostfwd=tcp::10022-:22 \
  -device e1000-82545em,netdev=hub0port0,id=mac_vnet0 \
  -vnc :4 &>/dev/null &
QEMU_PID=$!
renice -n 17 -p $QEMU_PID
ionice -c 2 -n 7 -p $QEMU_PID

# Get the sources
cd $WEBSITE
rm -f master.zip
wget -nv https://github.com/ddnet/ddnet/archive/master.zip
TIME_PREPARATION=$(($(date +%s) - $START_TIME))

# Mac OS X
build_macosx ()
{
  START_TIME=$(date +%s)
  cd $BUILDDIR

  while ! ssh -p 10022 -o ConnectTimeout=10 localhost exit; do true; done

  ssh -p 10022 localhost "
    source .profile
    rm -rf ddnet-master master.zip &&
    curl -o master.zip http://r0q.no-ip.org/dennis/master.zip &&
    unzip -q master.zip &&
    cd ddnet-master &&
    /usr/local/bin/bam config curl.use_pkgconfig=false opus.use_pkgconfig=false \
      opusfile.use_pkgconfig=false ogg.use_pkgconfig=false compiler=clang &&
    /usr/local/bin/bam release;

    strip DDNet_x86 DDNet_x86_64 DDNet-Server_x86 DDNet-Server_x86_64 dilate_x86 \
      dilate_x86_64 config_store_x86 config_store_x86_64 config_retrieve_x86 \
      config_retrieve_x86_64 &&
    python scripts/make_release.py $VERSION osx &&
    curl -F \"uploadFile=@DDNet-$VERSION-osx.dmg\" r0q.no-ip.org/tw/upload.php &&
    halt" || true

  mv /home/deen/.teeworlds/maps/DDNet-$VERSION-osx.dmg $BUILDS || true
  kill $QEMU_PID
  TIME_MACOSX=$(($(date +%s) - $START_TIME))
}

build_macosx &> $MACLOG &
MACPID=$!

# Linux
build_linux ()
{
  PLATFORM=$1

  rm -rf ddnet-master
  unzip -q $WEBSITE/master.zip
  chroot . sh -c "cd ddnet-master && bam config curl.use_pkgconfig=false \
    opus.use_pkgconfig=false opusfile.use_pkgconfig=false \
    ogg.use_pkgconfig=false && bam release"
  cd ddnet-master
  strip -s DDNet DDNet-Server dilate config_store config_retrieve
  python scripts/make_release.py $VERSION linux_$PLATFORM
  mv DDNet-$VERSION-linux_$PLATFORM.tar.gz $BUILDS
  cd ..
  rm -rf ddnet-master

  unset CFLAGS LDFLAGS PKG_CONFIG_PATH
}

cd $BUILDDIR/debian6
umount proc sys dev 2> /dev/null || true
mount -t proc proc proc/
mount -t sysfs sys sys/
mount -o bind /dev dev/

START_TIME=$(date +%s)
build_linux x86_64
TIME_LINUX_X86_64=$(($(date +%s) - $START_TIME))

START_TIME=$(date +%s)
CFLAGS=-m32 LDFLAGS=-m32 PKG_CONFIG_PATH=/usr/lib32/pkgconfig/ build_linux x86
TIME_LINUX_X86=$(($(date +%s) - $START_TIME))

umount proc sys dev
cd ..

# Windows
build_windows ()
{
  PLATFORM=$1

  rm -rf ddnet-master
  unzip -q $WEBSITE/master.zip
  cd ddnet-master
  bam config curl.use_pkgconfig=false opus.use_pkgconfig=false \
    opusfile.use_pkgconfig=false ogg.use_pkgconfig=false
  CC=${PREFIX}gcc CXX=${PREFIX}g++ WINDRES=${PREFIX}windres bam release
  ${PREFIX}strip -s DDNet.exe DDNet-Server.exe dilate.exe \
    config_store.exe config_retrieve.exe
  python scripts/make_release.py $VERSION win$PLATFORM
  mv DDNet-$VERSION-win$PLATFORM.zip $BUILDS
  cd ..
  rm -rf ddnet-master
  unset PREFIX \
    TARGET_FAMILY TARGET_PLATFORM TARGET_ARCH
}

START_TIME=$(date +%s)
TARGET_FAMILY=windows TARGET_PLATFORM=win64 TARGET_ARCH=amd64 \
  PREFIX=x86_64-w64-mingw32- PATH=/usr/x86_64-w64-mingw32/bin:$PATH \
  build_windows 64
TIME_WINDOWS_X86_64=$(($(date +%s) - $START_TIME))

START_TIME=$(date +%s)
TARGET_FAMILY=windows TARGET_PLATFORM=win32 TARGET_ARCH=ia32 \
  PREFIX=i686-w64-mingw32- PATH=/usr/i686-w64-mingw32/bin:$PATH \
  build_windows 32
TIME_WINDOWS_X86=$(($(date +%s) - $START_TIME))

# Android
START_TIME=$(date +%s)
cd $BUILDDIR/commandergenius/project/jni/application/teeworlds
sed -e "s/YYYY/$VERSION/; s/XXXX/$NUMVERSION/" \
  AndroidAppSettings.tmpl > AndroidAppSettings.cfg
rm -rf src
unzip -q $WEBSITE/master.zip
mv ddnet-master src
cp -r generated src/src/game/
rm -rf AndroidData
./AndroidPreBuild.sh

cd $BUILDDIR/commandergenius
./changeAppSettings.sh -a
android update project -p project
./build.sh
{ jarsigner -verbose -keystore ~/.android/release.keystore -storepass $PASS \
  -sigalg MD5withRSA -digestalg SHA1 \
  project/bin/MainActivity-release-unsigned.apk androidreleasekey; } 2>/dev/null
zipalign 4 project/bin/MainActivity-release-unsigned.apk \
  project/bin/MainActivity-release.apk
mv project/bin/MainActivity-release.apk $BUILDS/DDNet-${VERSION}.apk
TIME_ANDROID=$(($(date +%s) - $START_TIME))

wait $MACPID
cat $MACLOG
rm -f $MACLOG

{ set +x; } 2>/dev/null
echo ""
printf "Preparation:    %4s s\n" "$TIME_PREPARATION"
printf "Linux x86_64:   %4s s\n" "$TIME_LINUX_X86_64"
printf "Linux x86:      %4s s\n" "$TIME_LINUX_X86"
printf "Windows x86_64: %4s s\n" "$TIME_WINDOWS_X86_64"
printf "Windows x86:    %4s s\n" "$TIME_WINDOWS_X86"
printf "Android:        %4s s\n" "$TIME_ANDROID"

NOW=$(date +'%F %R')
echo "Finished build of $VERSION at $NOW"
