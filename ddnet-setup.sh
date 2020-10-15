#!/bin/sh

# From root @ other server:
# cd /
# tar --exclude='teehistorian' --exclude='*.sql' --exclude='*.log*' --exclude='*.fifo' --exclude='nohup.out' -czf ddnet-setup.tar.gz home/teeworlds/servers home/teeworlds/servers home/teeworlds/dnsbl home/teeworlds/run-all.sh home/teeworlds/.config home/teeworlds/.vim* home/teeworlds/.ssh* home/teeworlds/.z* home/teeworlds/.gitconfig etc/zsh etc/vim* etc/mysql etc/ssmtp etc/dnsmasq.d etc/dnsmasq.conf etc/resolv.dnsmasq.conf etc/resolv.conf etc/systemd/system/dnsbl-iphub.service etc/security/limits.conf root/weekly root/.config root/.vim* root/.ssh* root/.z* usr/local/bin/ni usr/local/bin/rni etc/init.d/teeworlds-servers etc/network/if-up.d/iptables etc/apt/apt.conf.d/99defaultrelease etc/apt/sources.list.d etc/timezone etc/apt/apt.conf.d/50unattended-upgrades var/spool/cron/crontabs
# scp ddnet-setup.tar.gz kor.ddnet.tw:/

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 kor \"Korea\""
  exit 1
fi
set -x -e
NAME_LOWER=$1
NAME_UPPER=`echo $1 | tr '[:lower:]' '[:upper:]'`
NAME_INGAME=$2
NAME_SQL=`echo $NAME_UPPER | head -c3`

apt-get -y update
apt-get -y upgrade
apt-get -y install bsdutils tree zsh vim htop git g++ libboost-dev python-msgpack python-requests python-dnspython python-mysqldb sshfs tcpdump gdb pkg-config ntpdate ntp mailutils msmtp msmtp-mta libssl-dev libmariadbclient-dev libmysqlcppconn-dev cmake make unattended-upgrades apt-listchanges iptables-persistent libwebsockets-dev libcurl4-openssl-dev python3 python3-dnslib python3-cachetools dnsmasq strace dnsutils sqlite3 libsqlite3-dev mariadb-client rsync libreadline-dev binutils-dev libpcap-dev libnl-genl-3-dev dh-autoreconf conntrack ncdu iperf3 psmisc ethtool net-tools mtr-tiny adduser cron iptables

hostnamectl set-hostname ddnet$NAME_LOWER
addgroup teeworlds
adduser --gecos "" --home /home/teeworlds --shell /usr/bin/zsh --disabled-password --ingroup users teeworlds
sed -E -i "s/^#?Port .*/Port 6546/" /etc/ssh/sshd_config
sed -E -i "s/^#?PermitRootLogin .*/PermitRootLogin yes/" /etc/ssh/sshd_config
systemctl restart ssh

iptables -t raw -A PREROUTING -p udp -j NOTRACK
iptables -t raw -A OUTPUT -p udp -j NOTRACK
iptables -N serverinfo
iptables -A INPUT -p udp -m u32 --u32 "38=0x67696533" -j serverinfo
iptables -A INPUT -p udp -m u32 --u32 "38=0x66737464" -j serverinfo
iptables -A serverinfo -s 37.187.108.123 -j ACCEPT
iptables -A serverinfo -s 185.107.96.242 -j ACCEPT
iptables -A serverinfo -m hashlimit --hashlimit-above 1000/s --hashlimit-burst 2500 --hashlimit-mode dstport --hashlimit-name si_dstport -j DROP
iptables -A serverinfo -m hashlimit --hashlimit-above 20/s --hashlimit-burst 100 --hashlimit-mode srcip --hashlimit-name si_srcip -j DROP
iptables-save > /etc/iptables.up.rules

tar -C / -xvf ddnet-setup.tar.gz
rm ddnet-setup.tar.gz

systemctl enable dnsbl-iphub
systemctl start dnsbl-iphub
systemctl restart dnsmasq
dpkg-reconfigure -f noninteractive unattended-upgrades
ln -fs /usr/share/zoneinfo/Europe/Berlin /etc/localtime
dpkg-reconfigure -f noninteractive tzdata
apt-get -y update
apt-get -y -t testing install libmysqlcppconn-dev libmysqlcppconn7v5

chsh --shell /usr/bin/zsh
sed -i "s/hostname=.*/hostname=$NAME_LOWER.ddnet.tw/" /etc/ssmtp/ssmtp.conf
update-rc.d teeworlds-servers defaults enable

echo "8298 8300 8303 8304 8305 8306 8308 8309 8311 8312" > /home/teeworlds/servers/all-servers
sed -i "s/^sv_sql_servername .*/sv_sql_servername \"$NAME_SQL\"/" /home/teeworlds/servers/mysql.cfg
sed -i "s/^USER = .*/USER = \"ddnet$NAME_LOWER\"/" /home/teeworlds/servers/serverstatus-client.py
sed -i "s/^sv_name \"DDNet [A-Za-z0-9]* /sv_name \"DDNet $NAME_INGAME /" /home/teeworlds/servers/types/*/flexname.cfg /home/teeworlds/servers/servers/*.cfg

echo "#!/bin/sh

cd /home/teeworlds/servers

for i in `cat all-servers`; do
  nohup ./run64.sh $i > /dev/null &
done

nohup ./serverstatus-client.py &" > /home/teeworlds/servers/run-all.sh
chmod +x /home/teeworlds/servers/run-all.sh
chmod +x /home/teeworlds/run-all.sh

su - teeworlds "./run-all.sh"

# With mysql: mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -p mysql

# Hack for getting approximate time for hosters that totally block NTP:
# date -s "$(wget -qSO- --max-redirect=0 google.com 2>&1 | grep Date: | cut -d' ' -f5-8)Z"
#
# On ddnet.tw:
# vim ServerStatus/server/config.json
# systemctl restart sergate
# cd servers
# vim scripts/status.py
# vim serverlist.json
# vim all-locations
# ./git-update-files-only.sh
#
# On mysql servers:
# iptables -I INPUT -p tcp --dport 3306 -s $IP -j ACCEPT
# iptables-save > /etc/iptables.up.rules
# mysql # grant for teeworlds, blocker, zcatch users
#
# Make sure teehistorian backups work and inform other teehistorian consumers
