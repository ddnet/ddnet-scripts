#!/usr/bin/zsh
autoload zmv
set -e
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin::/opt/android-sdk/tools:/opt/android-sdk/tools/bin:/usr/lib/jvm/default/bin:/usr/bin/site_perl:/usr/bin/vendor_perl:/usr/bin/core_perl
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
