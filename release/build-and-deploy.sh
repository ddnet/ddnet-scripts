#!/usr/bin/zsh
renice -n 19 -p $$ > /dev/null
ionice -c 3 -p $$

autoload zmv
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
MAIN_REPO_USER="${MAIN_REPO_USER:-ddnet}"
MAIN_REPO_NAME="${MAIN_REPO_NAME:-ddnet}"
MAIN_REPO_BRANCH="${MAIN_REPO_BRANCH:-master}"

/home/deen/git/codebrowser/generator/codebrowser_generator -h > /dev/null || (cat << EOF
After an LLVM upgrade rebuild codebrowser and osxcross as follows:
$ cd ~/git/codebrowser
$ cmake . -DCMAKE_PREFIX_PATH=/usr/lib/clang/14.0.6 -DCMAKE_BUILD_TYPE=Release
$ make -j4
EOF
exit 1)

cd /home/deen/isos/ddnet
find builds -mindepth 1 -delete

if [ "$1" = "nightly" ]; then
  export UPDATE_FLAGS="-DAUTOUPDATE=OFF -DINFORM_UPDATE=OFF"
  export UPDATE_FLAGS_MACOS="-DINFORM_UPDATE=OFF"
  V="$(curl -s https://raw.githubusercontent.com/$MAIN_REPO_USER/$MAIN_REPO_NAME/$MAIN_REPO_BRANCH/src/game/version.h | grep "^#define GAME_RELEASE_VERSION_INTERNAL" | cut -d' ' -f3)"
  export VERSION="$V-$(date -d '+2 hours' +%Y%m%d)"
  ./build.sh $VERSION &> builds/DDNet-nightly.log

  rm -rf codebrowser
  cd ddnet-source
  rm -rf ddnet-libs
  CC=clang CXX=clang++ cmake . -DCMAKE_BUILD_TYPE=Debug -GNinja -DDEV=ON -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DUPNP=ON -DTEST_MYSQL=ON -DMYSQL=ON -DWEBSOCKETS=ON -DAUTOUPDATE=ON -DVIDEORECORDER=ON -DVULKAN=ON .
  ninja
  /home/deen/git/codebrowser/generator/codebrowser_generator -b . -a -o ../codebrowser -p DDNet:/home/deen/isos/ddnet/ddnet-source/src:$VERSION -d https://ddnet.org/codebrowser-data
  /home/deen/git/codebrowser/indexgenerator/codebrowser_indexgenerator ../codebrowser -d https://ddnet.org/codebrowser-data -p DDNet:/home/deen/isos/ddnet/ddnet-source/src:$VERSION
  cd ..
  rsync -avP --delay-updates --delete-delay codebrowser ddnet:/var/www/
  rm -rf codebrowser
elif [ "$1" = "playground" ]; then
  export UPDATE_FLAGS="-DAUTOUPDATE=OFF -DINFORM_UPDATE=OFF"
  export UPDATE_FLAGS_MACOS="-DINFORM_UPDATE=OFF"
  export MAIN_REPO_USER=Jupeyy
  export MAIN_REPO_BRANCH=playground
  V="$(curl -s https://raw.githubusercontent.com/$MAIN_REPO_USER/$MAIN_REPO_NAME/$MAIN_REPO_BRANCH/src/game/version.h | grep "^#define GAME_RELEASE_VERSION_INTERNAL" | cut -d' ' -f3)"
  export VERSION="$V-$(date -d '+2 hours' +%Y%m%d)"
  ./build.sh $VERSION &> builds/DDNet-playground.log
elif [ "$1" = "rc" ]; then
  export UPDATE_FLAGS="-DAUTOUPDATE=OFF -DINFORM_UPDATE=OFF"
  export UPDATE_FLAGS_MACOS="-DINFORM_UPDATE=OFF"
  export VERSION=$2
  ./build.sh $VERSION &> builds/DDNet-$VERSION.log
elif [ "$1" = "release" ]; then
  VERSION=$2
  ./build.sh $VERSION &> builds/DDNet-$VERSION.log
else
  echo "Unknown parameter: $1"
  echo ""
  echo "Nightly:"
  echo "./build-and-deploy.sh nightly"
  echo ""
  echo "Playground:"
  echo "./build-and-deploy.sh playground"
  echo ""
  echo "Release Candidate:"
  echo "MAIN_REPO_USER=def- MAIN_REPO_BRANCH=pr-15.0.5 ./build-and-deploy.sh rc 15.0.5-rc2"
  echo ""
  echo "Release:"
  echo "./build-and-deploy.sh release 15.0.5"
  echo "and set live for beta, default manually in Steamworks"
  exit 1
fi

if [ "$1" = "nightly" ]; then
  scp -q builds/DDNet-$VERSION*-symbols.tar.xz ddnet:/var/www/downloads/tmp
  rm builds/DDNet-$VERSION*-symbols.tar.xz
  zmv -W "builds/DDNet-$VERSION*" "builds/DDNet-nightly*"
  scp -q builds/DDNet-nightly* ddnet:/var/www/downloads/tmp
  ssh ddnet "mv /var/www/downloads/tmp/DDNet-$VERSION*-symbols.tar.xz /var/www/downloads/symbols; mv /var/www/downloads/tmp/DDNet-nightly* /var/www/downloads"
elif [ "$1" = "playground" ]; then
  scp -q builds/DDNet-$VERSION*-symbols.tar.xz ddnet:/var/www/downloads/tmp
  rm builds/DDNet-$VERSION*-symbols.tar.xz
  zmv -W "builds/DDNet-$VERSION*" "builds/DDNet-playground*"
  scp -q builds/DDNet-playground* ddnet:/var/www/downloads/tmp
  ssh ddnet "mv /var/www/downloads/tmp/DDNet-$VERSION*-symbols.tar.xz /var/www/downloads/symbols; mv /var/www/downloads/tmp/DDNet-playground* /var/www/downloads"
else
  scp -q builds/DDNet-$VERSION* ddnet:/var/www/downloads/tmp
  ssh ddnet "mv /var/www/downloads/tmp/DDNet-$VERSION*-symbols.tar.xz /var/www/downloads/symbols; mv /var/www/downloads/tmp/DDNet-$VERSION* /var/www/downloads"
fi

cd steam
for i in *.zip; do
  mkdir ${i:r}
  cd ${i:r}
  unzip ../$i
  cd ..
done
zmv -W "DDNet-$VERSION-*" '*'

# steamcmd started overwriting/destroying my depot_build_*.vdf files
cd /home/deen/isos/ddnet/
cp steamcmd_orig/* steamcmd
cd /home/deen/isos/ddnet/steamcmd/
sed -e "s/Nightly Build/$1: $VERSION/" app_build_412220.vdf > tmp.vdf
if [ "$1" = "playground" ]; then
  sed -i "s/\"beta\"/\"playground\"/" tmp.vdf
elif [ "$1" != "nightly" ]; then
  sed -i "s/\"beta\"/\"releasecandidates\"/" tmp.vdf
fi
if [ ! -d "/home/deen/isos/ddnet/steam/macos" ]; then
  sed -i "/412224/d" tmp.vdf
fi
# Try a few times, fails sporadically sometimes
repeat 10 {
  steamcmd +login deen_ddnet "$(cat pass)" +run_app_build /home/deen/isos/ddnet/steamcmd/tmp.vdf +quit && break
  sleep 1m
}

cd ..
rm -rf builds/* DDNet-$VERSION* steam/* ddnet-source
