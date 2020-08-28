#!/usr/bin/zsh
autoload zmv
set -e
cd /home/deen/isos/ddnet
./build.sh nightly &> builds/DDNet-nightly.log
scp -q builds/DDNet-nightly* ddnet:/var/www/downloads/tmp
ssh ddnet mv /var/www/downloads/tmp/DDNet-nightly\* /var/www/downloads
cd steam
for i in *.zip; do
  mkdir ${i:r}
  cd ${i:r}
  unzip ../$i
  cd ..
done
zmv -W 'DDNet-nightly-*' '*'
steamcmd +login deen_ddnet "SECRETPW" +run_app_build /home/deen/isos/ddnet/steamcmd/app_build_412220.vdf +quit
cd ..
rm -rf builds/DDNet-nightly* builds/*.log DDNet-nightly* steam/*
