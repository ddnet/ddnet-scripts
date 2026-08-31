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
  ./build.sh $VERSION &> builds/DDNet-nightly.log || { echo "build.sh failed, see builds/DDNet-nightly.log"; exit 1 }

  rm -rf codebrowser
  cd ddnet-source
  rm -rf ddnet-libs
  CC=clang CXX=clang++ cmake . -DCMAKE_BUILD_TYPE=Debug -GNinja -DDEV=ON -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DUPNP=ON -DTEST_MYSQL=ON -DMYSQL=ON -DWEBSOCKETS=ON -DAUTOUPDATE=ON -DVIDEORECORDER=ON -DVULKAN=ON .
  ninja
  /home/deen/git/codebrowser/generator/codebrowser_generator -b . -a -o ../codebrowser -p DDNet:/home/deen/isos/ddnet/ddnet-source/src:$VERSION -d https://ddnet.org/codebrowser-data
  /home/deen/git/codebrowser/indexgenerator/codebrowser_indexgenerator ../codebrowser -d https://ddnet.org/codebrowser-data -p DDNet:/home/deen/isos/ddnet/ddnet-source/src:$VERSION
  cd ..
  rsync -avP codebrowser/ ddnet:/var/www/codebrowser.new
  rm -rf codebrowser
  ssh ddnet "cd /var/www && mv codebrowser codebrowser.old && mv codebrowser.new codebrowser && rm -rf codebrowser.old"

  cd ddnet-source
  rm -rf docs/html
  rm -rf docs/warn.log
  doxygen -q
  rsync -avP --delay-updates --delete-delay docs/html/ ddnet:/var/www-codedoc/
  rm -rf docs/html
  rm -rf docs/warn.log
  cd ..

  # TODO: Reenable after https://github.com/ddnet/ddnet/pull/12470
  # rsync -avP --delay-updates --delete-delay ddnet-source/build-emscripten/pack_DDNet-$VERSION-Emscripten_tar_xz/DDNet-$VERSION-Emscripten/ ddnet:/var/www-client/nightly
elif [ "$1" = "playground" ]; then
  export UPDATE_FLAGS="-DAUTOUPDATE=OFF -DINFORM_UPDATE=OFF"
  export UPDATE_FLAGS_MACOS="-DINFORM_UPDATE=OFF"
  export MAIN_REPO_USER=Jupeyy
  export MAIN_REPO_BRANCH=playground
  V="$(curl -s https://raw.githubusercontent.com/$MAIN_REPO_USER/$MAIN_REPO_NAME/$MAIN_REPO_BRANCH/src/game/version.h | grep "^#define GAME_RELEASE_VERSION_INTERNAL" | cut -d' ' -f3)"
  export VERSION="$V-$(date -d '+2 hours' +%Y%m%d)"
  ./build.sh $VERSION &> builds/DDNet-playground.log || { echo "build.sh failed, see builds/DDNet-playground.log"; exit 1 }
elif [ "$1" = "rc" ]; then
  export UPDATE_FLAGS="-DAUTOUPDATE=OFF -DINFORM_UPDATE=OFF"
  export UPDATE_FLAGS_MACOS="-DINFORM_UPDATE=OFF"
  export VERSION=$2
  ./build.sh $VERSION &> builds/DDNet-$VERSION.log || { echo "build.sh failed, see builds/DDNet-$VERSION.log"; exit 1 }

  rsync -avP --delay-updates --delete-delay ddnet-source/build-emscripten/pack_DDNet-$VERSION-Emscripten_tar_xz/DDNet-$VERSION-Emscripten/ ddnet:/var/www-client/$VERSION
elif [ "$1" = "release" ]; then
  VERSION=$2
  ./build.sh $VERSION &> builds/DDNet-$VERSION.log || { echo "build.sh failed, see builds/DDNet-$VERSION.log"; exit 1 }

  rsync -avP --delay-updates --delete-delay ddnet-source/build-emscripten/pack_DDNet-$VERSION-Emscripten_tar_xz/DDNet-$VERSION-Emscripten/ ddnet:/var/www-client/$VERSION
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
  echo "and release the uploaded iOS build in App Store Connect"
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
for vdf in ${(f)"$(sed -n 's/.*"\(depot_build_[0-9]*\.vdf\)".*/\1/p' tmp.vdf)"}; do
  root="$(sed -n 's/.*"ContentRoot"[[:space:]]*"\([^"]*\)".*/\1/p' $vdf)"
  if [ -z "$root" ] || [ -z "$(ls -A $root 2> /dev/null)" ]; then
    echo "Steam depot content root '$root' ($vdf) is missing or empty, aborting upload"
    exit 1
  fi
done

# Try a few times, fails sporadically sometimes
STEAM_OK=0
repeat 10 {
  steamcmd +login deen_ddnet "$(cat pass)" +run_app_build /home/deen/isos/ddnet/steamcmd/tmp.vdf +quit && { STEAM_OK=1; break }
  sleep 1m
}
if [ $STEAM_OK -ne 1 ]; then
  echo "Steam upload failed after 10 attempts"
  exit 1
fi

cd ..

VT_KEY_FILE=/home/deen/isos/ddnet/virustotal_key
if [ -e "$VT_KEY_FILE" ]; then
  VT_KEY="$(cat $VT_KEY_FILE)"
  VT_TMP="$(mktemp -d)"
  typeset -A VT_FILES VT_ANALYSIS VT_SHA

  for zip in builds/DDNet-*-win*.zip(N); do
    dir=$VT_TMP/${${zip:t}:r}
    mkdir $dir
    unzip -q -j $zip "*/DDNet.exe" "*/DDNet-Server.exe" -d $dir
    for exe in $dir/*.exe(N); do
      VT_FILES[${${zip:t}:r}/${exe:t}]=$exe
    done
  done
  for exe in steam/win{64,32}/ddnet/{DDNet,DDNet-Server}.exe(N); do
    VT_FILES[steam-${exe:h:h:t}/${exe:t}]=$exe
  done

  echo "VirusTotal: uploading ${#VT_FILES} Windows executables"
  for label in ${(k)VT_FILES}; do
    exe=$VT_FILES[$label]
    VT_SHA[$label]="$(sha256sum $exe | cut -d' ' -f1)"
    sleep 16 # free API allows 4 requests/minute
    UPLOAD_URL="$(curl -s --max-time 60 -H "x-apikey: $VT_KEY" https://www.virustotal.com/api/v3/files/upload_url | jq -r .data)"
    if [ -z "$UPLOAD_URL" ] || [ "$UPLOAD_URL" = "null" ]; then
      echo "VirusTotal: failed to get upload URL for $label"
      continue
    fi
    sleep 16
    RESP="$(curl -s --max-time 600 -H "x-apikey: $VT_KEY" -F file=@$exe "$UPLOAD_URL")"
    ID="$(echo "$RESP" | jq -r .data.id)"
    if [ -z "$ID" ] || [ "$ID" = "null" ]; then
      echo "VirusTotal: upload failed for $label: $RESP"
    else
      VT_ANALYSIS[$label]=$ID
    fi
  done

  VT_DEADLINE=$(($(date +%s) + 1200))
  while [ ${#VT_ANALYSIS} -gt 0 ] && [ $(date +%s) -lt $VT_DEADLINE ]; do
    for label in ${(k)VT_ANALYSIS}; do
      sleep 16
      RESP="$(curl -s --max-time 60 -H "x-apikey: $VT_KEY" https://www.virustotal.com/api/v3/analyses/$VT_ANALYSIS[$label])"
      [ "$(echo "$RESP" | jq -r .data.attributes.status)" != "completed" ] && continue
      DETECTIONS="$(echo "$RESP" | jq -r '.data.attributes.stats.malicious + .data.attributes.stats.suspicious')"
      if [ "$DETECTIONS" = "0" ]; then
        # echo "VirusTotal: clean: $label"
      else
        echo "VirusTotal: $DETECTIONS detections for $label: https://www.virustotal.com/gui/file/$VT_SHA[$label]"
        echo "$RESP" | jq -r '.data.attributes.results[] | select(.category == "malicious" or .category == "suspicious") | "  \(.engine_name): \(.result // .category)"'
      fi
      unset "VT_ANALYSIS[$label]"
    done
  done
  for label in ${(k)VT_ANALYSIS}; do
    echo "VirusTotal: analysis not finished for $label: https://www.virustotal.com/gui/file/$VT_SHA[$label]"
  done
  rm -rf $VT_TMP
else
  echo "VirusTotal: no $VT_KEY_FILE, skipping scan"
fi

rm -rf builds/* DDNet-$VERSION* steam/* ddnet-source
