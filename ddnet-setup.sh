#!/bin/sh

# From root @ other server:
# cd /
# tar --exclude='UBSAN*' --exclude='ASAN*' --exclude='ddnet-server*.sqlite*' --exclude='ddnet-block.sqlite' --exclude='teehistorian' --exclude='*.sql' --exclude='*.log*' --exclude='*.fifo' --exclude='nohup.out' --exclude home/teeworlds/servers/test/data/maps -czf ddnet-setup.tar.gz home/teeworlds/servers home/teeworlds/run-all.sh home/teeworlds/.config home/teeworlds/.vim* home/teeworlds/.ssh* home/teeworlds/.z* home/teeworlds/.my.cnf home/teeworlds/dnsbl home/teeworlds/.gitconfig etc/zsh etc/vim* etc/mysql etc/ssmtp etc/dnsmasq.d etc/dnsmasq.conf etc/resolv.dnsmasq.conf etc/resolv.conf etc/resolv.conf.ddnet etc/security/limits.conf root/weekly root/ipset.sh root/.config root/.vim* root/.ssh* root/.z* usr/local/bin/ni usr/local/bin/rni etc/init.d/teeworlds-servers etc/network/if-up.d/iptables etc/apt/sources.list.d etc/timezone etc/apt/apt.conf.d/50unattended-upgrades var/spool/cron/crontabs etc/systemd/system/dnsbl-ipapi.service etc/systemd/journald.conf
# scp ddnet-setup.tar.gz kor.ddnet.org:/

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 kor \"Korea\""
  exit 1
fi
set -x -e
DDNET_IP=$1
NAME_LOWER=$2
NAME_UPPER=`echo $2 | tr '[:lower:]' '[:upper:]'`
NAME_INGAME=$3
NAME_SQL=`echo $NAME_UPPER | head -c3`

apt-get -y update
apt-get -y upgrade
apt-get -y dist-upgrade
apt-get -y install bsdutils tree zsh vim htop git g++ libboost-dev python3-requests sshfs tcpdump gdb pkg-config mailutils msmtp msmtp-mta libssl-dev libmariadb-dev-compat libmariadb-dev libmysqlcppconn-dev cmake make unattended-upgrades apt-listchanges iptables-persistent libwebsockets-dev libcurl4-openssl-dev python3 dnsmasq strace dnsutils sqlite3 libsqlite3-dev mariadb-client rsync libreadline-dev binutils-dev libpcap-dev libnl-genl-3-dev dh-autoreconf conntrack ncdu psmisc ethtool net-tools mtr-tiny adduser cron iptables wget screen libmaxminddb-dev unzip ipset curl zstd python3-pip fd-find fish glances ripgrep python3-cachetools python3-dnslib
rm -rf  /root/.acme.sh
rm -rf ~/.pip # bad tencent server on some CHN locations
if [[ "$NAME_SQL" == "CHN" ]]; then
  pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
fi
apt-get remove python3-dateutil
pip3 install sqlite3-to-mysql --upgrade --break-system-packages || pip3 install sqlite3-to-mysql --upgrade --break-system-packages

hostnamectl set-hostname ddnet$NAME_LOWER
addgroup teeworlds
adduser --comment "" --home /home/teeworlds --shell /usr/bin/zsh --disabled-password --ingroup users teeworlds
sed -E -i "s/^#?Port .*/Port 6546/" /etc/ssh/sshd_config
sed -E -i "s/^#?PermitRootLogin .*/PermitRootLogin yes/" /etc/ssh/sshd_config
systemctl restart ssh

update-alternatives --set iptables /usr/sbin/iptables-legacy
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT
iptables -t nat -F
iptables -t mangle -F
iptables -F
iptables -X
iptables -t raw -A PREROUTING -p udp -j NOTRACK
iptables -t raw -A OUTPUT -p udp -j NOTRACK
iptables -N serverinfo
iptables -N newconn
iptables -A INPUT -p udp -m u32 --u32 "38=0x67696533" -j serverinfo
iptables -A INPUT -p udp -m u32 --u32 "38=0x66737464" -j serverinfo
iptables -A INPUT -p udp -m u32 --u32 "32=0x544b454e" -j newconn
iptables -A serverinfo -s 37.187.108.123 -j ACCEPT
iptables -A serverinfo -m hashlimit --hashlimit-above 100/s --hashlimit-burst 250 --hashlimit-mode dstport --hashlimit-name si_dstport -j DROP
iptables -A serverinfo -m hashlimit --hashlimit-above 20/s --hashlimit-burst 100 --hashlimit-mode srcip --hashlimit-name si_srcip -j DROP
iptables -A newconn -m hashlimit --hashlimit-above 100/s --hashlimit-burst 100 --hashlimit-mode dstport --hashlimit-name nc_dstport -j DROP
iptables -I INPUT -s 3.86.106.128 -j DROP
iptables -I INPUT -s 185.82.223.0/24 -j DROP
iptables -I INPUT -s 147.251.0.0/16 -j DROP
iptables -I OUTPUT -d 147.251.0.0/16 -j DROP
iptables -A INPUT -s 127.0.0.1 -j ACCEPT
iptables -I INPUT 1 -p tcp --src $DDNET_IP -j ACCEPT
iptables -I INPUT 2 -p tcp -m tcp --dport 6546 -m state --state NEW -m hashlimit --hashlimit-above 1/minute --hashlimit-mode srcip --hashlimit-name ssh -j DROP
iptables -A INPUT -p tcp -m tcp -m conntrack -m multiport --ctstate NEW ! --dports 27685,6546,22 -j DROP
iptables-save > /etc/iptables.up.rules

tar -C / -xvf ddnet-setup.tar.gz
rm ddnet-setup.tar.gz

ssh-keygen -t rsa -N '' -f /root/.ssh/id_rsa <<< $'\ny'
systemctl disable systemd-resolved
systemctl stop systemd-resolved
systemctl restart dnsmasq
systemctl enable dnsbl-ipapi
systemctl start dnsbl-ipapi
dpkg-reconfigure -f noninteractive unattended-upgrades
ln -fs /usr/share/zoneinfo/Europe/Berlin /etc/localtime
dpkg-reconfigure -f noninteractive tzdata

# Bad ntp servers on China
sed -i "s/ntpupdate.tencentyun.com/de.pool.ntp.org/" /etc/**/*.conf
systemctl enable ntp
systemctl restart ntp

echo "nameserver 127.0.0.1" > /etc/resolv.conf.ddnet
chattr +i /etc/resolv.conf.ddnet
chsh --shell /usr/bin/zsh
sed -i "s/hostname=.*/hostname=$NAME_LOWER.ddnet.org/" /etc/ssmtp/ssmtp.conf
systemctl enable teeworlds-servers

echo "8298 8300 8303 8304 8305 8306 8308 8309" > /home/teeworlds/servers/all-servers
sed -i "s/^sv_sql_servername .*/sv_sql_servername \"$NAME_SQL\"/" /home/teeworlds/servers/mysql.cfg
sed -i "s/^USER = .*/USER = \"ddnet$NAME_LOWER\"/" /home/teeworlds/servers/serverstatus-client.py
sed -i "s/^sv_name \"DDNet [A-Za-z0-9]* /sv_name \"DDNet $NAME_INGAME /" /home/teeworlds/servers/types/*/flexname.cfg /home/teeworlds/servers/servers/*.cfg
su - teeworlds -c "git config --global pull.rebase false"

cat <<EOF > /home/teeworlds/servers/run-all.sh
#!/bin/sh

cd /home/teeworlds/servers

for i in \$(cat all-servers); do
  nohup ./run64.sh \$i > /dev/null &
done

nohup ./serverstatus-client.py &
EOF
cat <<EOF > /home/teeworlds/run-all.sh
#!/usr/bin/env zsh
cd servers
./run-all.sh
EOF

chmod +x /home/teeworlds/servers/run-all.sh
chmod +x /home/teeworlds/run-all.sh

# On CHN servers:
# From another CHN server: cd ~/servers && tar cfz chn.tar.gz types/*/flexvotes.cfg types/*/flexname.cfg announcement.txt ddrace_local_auths.cfg censorlist.txt servers/*.cfg
# cd ~/servers && tar xvf chn.tar.gz
# sed -i "s/CHN4 北京/CHN13 北京/" types/*/flexname.cfg
su - teeworlds "./run-all.sh"
#
# Add the IP on Cloudflare and other firewall we use for db server
# Make sure teehistorian backups work and inform other teehistorian consumers
#
# On ddnet.org:
# vim ServerStatus/server/config.json
# systemctl restart sergate
# cd servers
# vim scripts/status.py
# vim serverlist.json
# vim all-locations
# ./git-update-serverlist-only.sh
#
# Hack for getting approximate time for hosters that totally block NTP:
# date -s "$(wget -qSO- --max-redirect=0 cloudflare.com 2>&1 | grep Date: | cut -d' ' -f5-8)Z"
