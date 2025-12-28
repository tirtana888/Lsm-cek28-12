# Privilege Escalation Enumeration Report

### User Info
```
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

### OS Version
```
PRETTY_NAME="Debian GNU/Linux 13 (trixie)"
NAME="Debian GNU/Linux"
VERSION_ID="13"
VERSION="13 (trixie)"
VERSION_CODENAME=trixie
DEBIAN_VERSION_FULL=13.2
ID=debian
HOME_URL="https://www.debian.org/"
SUPPORT_URL="https://www.debian.org/support"
BUG_REPORT_URL="https://bugs.debian.org/"
```

### Kernel
```
Linux 41218417788b 6.8.0-90-generic #91-Ubuntu SMP PREEMPT_DYNAMIC Tue Nov 18 14:14:30 UTC 2025 x86_64 GNU/Linux
```

### Sudo -l
```
sh: 1: sudo: not found
```

### SUID Binaries
```
/usr/bin/newgrp
/usr/bin/chsh
/usr/bin/gpasswd
/usr/bin/passwd
/usr/bin/su
/usr/bin/umount
/usr/bin/mount
/usr/bin/chfn
```

### Crontabs
```
/etc/cron.daily:
total 20
drwxr-xr-x 2 root root 4096 Dec  8 00:00 .
drwxr-xr-x 1 root root 4096 Dec 28 03:42 ..
-rwxr-xr-x 1 root root 1478 Jun 24  2025 apt-compat
-rwxr-xr-x 1 root root  123 May 27  2025 dpkg
```

### Network
```
Netid State  Recv-Q Send-Q Local Address:Port  Peer Address:PortProcess                      
udp   UNCONN 0      0         127.0.0.11:58635      0.0.0.0:*                                
tcp   LISTEN 0      511          0.0.0.0:80         0.0.0.0:*    users:(("nginx",pid=9,fd=5))
tcp   LISTEN 0      4096      127.0.0.11:34473      0.0.0.0:*
```

### Environment
```
DB_CONNECTION=mysql
USER=www-data
APP_DEBUG=false
MAIL_USERNAME=email_anda@gmail.com
SUPERVISOR_GROUP_NAME=php-fpm
HOSTNAME=41218417788b
DB_PORT=3306
APP_URL=http://ccw84s4g4cgsk440c0ssookc.72.62.122.96.sslip.io/
PHP_INI_DIR=/usr/local/etc/php
SOURCE_COMMIT=3dedc7d16235c2caae5c11a839a05c4c32fbbdde
HOME=/var/www
COOLIFY_FQDN=ccw84s4g4cgsk440c0ssookc.72.62.122.96.sslip.io
DB_DATABASE=default
PHP_LDFLAGS=-Wl,-O1 -pie
LC_CTYPE=C.UTF-8
APP_NAME=RocketLMS
PHP_CFLAGS=-fstack-protector-strong -fpic -fpie -O2 -D_LARGEFILE_SOURCE -D_FILE_OFFSET_BITS=64
PHP_VERSION=8.1.34
DB_USERNAME=mysql
GPG_KEYS=528995BFEDFBA7191D46839EF9BA0ADA31CBD89E 39B641343D8C104B2B146DC3F9C39DC0B9698544 F1F692238FBC1666E5A5CCD4199F9DFEF6FFBAFD
PHP_CPPFLAGS=-fstack-protector-strong -fpic -fpie -O2 -D_LARGEFILE_SOURCE -D_FILE_OFFSET_BITS=64
PHP_ASC_URL=https://www.php.net/distributions/php-8.1.34.tar.xz.asc
PHP_URL=https://www.php.net/distributions/php-8.1.34.tar.xz
MAIL_ENCRYPTION=tls
SERVICE_URL_APP=http://ccw84s4g4cgsk440c0ssookc.72.62.122.96.sslip.io
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
MAIL_PASSWORD=password_aplikasi_anda
COOLIFY_BRANCH="main"
MAIL_HOST=smtp.gmail.com
SUPERVISOR_ENABLED=1
SERVICE_NAME_APP=app
HOST=0.0.0.0
JWT_SECRET=base64:kR3FZvPqN2sX8yW1QhT5jU7mB0dL4aE6cG9fHwJiKoM=
COOLIFY_CONTAINER_NAME=app-rsc0o88oww88wwwgcgs84ocg-033629764263
COOLIFY_RESOURCE_UUID=rsc0o88oww88wwwgcgs84ocg
SUPERVISOR_SERVER_URL=unix:///var/run/supervisor.sock
MAIL_MAILER=smtp
MAIL_PORT=587
COOLIFY_URL=http://ccw84s4g4cgsk440c0ssookc.72.62.122.96.sslip.io
SUPERVISOR_PROCESS_NAME=php-fpm
APP_KEY=base64:BlQYTmcfZGV4XShvK5Z+ffNVWv0qszkUTRuEGmQ76lw=
DB_PASSWORD=0Eb1gsfTMj4MxrLtok6myEkbOq2piZgO7klSdg4cPT3YaIvDiuPi5pYPdpbWQlKm
APP_ENV=production
PHPIZE_DEPS=autoconf 		dpkg-dev 		file 		g++ 		gcc 		libc-dev 		make 		pkg-config 		re2c
PWD=/var/www/public
SERVICE_FQDN_APP=ccw84s4g4cgsk440c0ssookc.72.62.122.96.sslip.io
PHP_SHA256=ffa9e0982e82eeaea848f57687b425ed173aa278fe563001310ae2638db5c251
DB_HOST=m4k0s4wsgwkc4cgwc44oows8
```

### Writable /etc
```
-rw-r--r-- 1 root root   839 Dec  8 00:00 /etc/passwd
-rw-r----- 1 root shadow 474 Dec  8 00:00 /etc/shadow
```

### Mounted Filesystems
```
Filesystem      Size  Used Avail Use% Mounted on
overlay          48G   39G  9.3G  81% /
tmpfs            64M     0   64M   0% /dev
shm              64M     0   64M   0% /dev/shm
/dev/sda1        48G   39G  9.3G  81% /etc/hosts
tmpfs           2.0G     0  2.0G   0% /proc/acpi
tmpfs           2.0G     0  2.0G   0% /proc/scsi
tmpfs           2.0G     0  2.0G   0% /sys/firmware
```

### Process List
```

```
