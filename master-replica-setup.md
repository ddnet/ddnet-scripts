Install `rustc-web` from Debian repositories (more up-to-date than `rustc`
since a more up-to-date version is required for web browsers).

Create user `httpmaster` using `useradd httpmaster`. Generate SSH keys using
`ssh-keygen`.

Download https://github.com/heinrich5991/twmaster-collect, build with `cargo
build --release`, binary ends up in `target/release/collect`, copy binary to
`~/collect`.

Create `~/start_collect_master1` with the following content and `chmod +x` it:
```
#!/bin/sh
RUST_LOG=info exec ~/collect --only-updates -- ssh httpmaster@ddnet.org 'RUST_LOG=info ~/transmit -f /var/www-master1/ddnet/15/servers.json'
```

In `~/.ssh/config`, add config entry for `ddnet.org`.

On `httpmaster@ddnet.org`, in `~/.ssh/authorized_keys`, add
```
command="RUST_LOG=info ~/transmit -f /var/www-master1/ddnet/15/servers.json",no-port-forwarding,no-x11-forwarding,no-agent-forwarding ssh-rsa <key> httpmaster@<server>
```

Run `ssh ddnet.org` and accept the certificate after checking it.

Create systemd service in `/etc/systemd/system/httpmaster-collect.service`:
```
[Unit]
Description=HTTP masterserver fetcher from master1

[Service]
User=httpmaster
Group=httpmaster
WorkingDirectory=/home/httpmaster
ExecStart=/home/httpmaster/start_collect_master1
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

`systemctl enable httpmaster-collect`, `systemctl start httpmaster-collect`.

Make sure port 443 isn't blocked by a firewall. Install `nginx` and `certbot`. `certbot certonly`. `mkdir -p /var/www-master2/ddnet/15/`. `ln -s ~httpmaster/servers.json ~httpmaster/servers.json.gz /var/www-master2/ddnet/15/`. Configure `/etc/nginx/sites-enabled/default`:
```
server {
	listen 80 default_server;
	listen [::]:80 default_server;
	listen 443 ssl default_server;
	listen [::]:443 ssl default_server;
	ssl_certificate /etc/letsencrypt/live/master2.ddnet.org/fullchain.pem;
	ssl_certificate_key /etc/letsencrypt/live/master2.ddnet.org/privkey.pem;
	root /var/www-master2;
	server_name master2.ddnet.org;
	gzip_static on;
	#gzip on;
	#gzip_vary on;
	#gzip_comp_level 9;
	gzip_types text/plain application/javascript application/x-javascript text/javascript text/xml text/css text/html application/json;
}
```

`systemctl restart nginx`

Check that you can access https://master2.ddnet.org/ddnet/15/servers.json.
