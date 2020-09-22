#!/usr/bin/zsh
# Run with: MAIN_REPO_USER=def- MAIN_REPO_BRANCH=pr-15.0.5 ./build-rc.sh 15.0.5-rc2
autoload zmv
set -e
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin::/opt/android-sdk/tools:/opt/android-sdk/tools/bin:/usr/lib/jvm/default/bin:/usr/bin/site_perl:/usr/bin/vendor_perl:/usr/bin/core_perl
cd /home/deen/isos/ddnet
./build.sh $1 &> builds/DDNet-$1.log
scp -q builds/DDNet-$1* ddnet:/var/www/downloads/tmp
ssh ddnet mv /var/www/downloads/tmp/DDNet-$1\* /var/www/downloads
cd steam
for i in *.zip; do
  mkdir ${i:r}
  cd ${i:r}
  unzip ../$i
  cd ..
done
zmv -W "DDNet-$1-*" '*'
cd /home/deen/isos/ddnet/steamcmd/
sed -e "s/Nightly Build/$1/" app_build_412220.vdf | sed -e "s/\"beta\"/\"releasecandidates\"/" > rc.vdf
steamcmd +login deen_ddnet "$(cat pass)" +run_app_build /home/deen/isos/ddnet/steamcmd/rc.vdf +quit
cd ..
rm -rf builds/DDNet-$1* builds/*.log DDNet-$1* steam/*
