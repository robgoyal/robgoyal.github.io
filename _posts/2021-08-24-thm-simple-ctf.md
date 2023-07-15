---
title: Simple CTF (Try Hack Me)
author: Robin Goyal
date: 2021-08-24 11:30 -0400
categories: [Cybersecurity, Writeups]
tags: [thm, ctf, writeup, ftp, web application, sqli, public exploit, password cracking, cms, reverse shell, vim, privesc]
hidden: true
image:
  src: https://tryhackme-images.s3.amazonaws.com/room-icons/f28ade2b51eb7aeeac91002d41f29c47.png
---

I am currently in the process of completing these boxes on Try Hack Me again along in an effort to document my experience, reinforce my knowledge of the topics, and improve my ability to concisely communicate the pentest lifecycle.

**Note**: The target IP address may change throughout the writeup as I complete the room over a period of time.

## Scenario

**Title**: Simple CTF

**Link**: https://tryhackme.com/room/easyctf

**Description**: Beginner level ctf

**Free/Subsciber**: Free

**Difficulty**: Easy


## Enumeration

First things first, let's start off with an nmap scan of the target.

![nmap scan results](/assets/img/posts/thm-simple-ctf/nmap.jpg)

The target is an Ubuntu OS as noted in the version information for the Apache service.

There are two open ports on the system:
1. 21 (FTP)
2. 80 (HTTP)

### FTP

The nmap scan results indicated that anonymous authentication to the FTP server is allowed. Let's check it out.

![ftp listing](/assets/img/posts/thm-simple-ctf/ftp.jpg)

There's one file present in the pub directory, ForMitch.txt.

```plaintext
Dammit man... you'te the worst dev i've seen. You set the same pass for the system user, and the password is so weak... i cracked it in seconds. Gosh... what a mess!
```

It seems that Mitch set the same weak password for the system user. This might be useful during our enumeration of the HTTP service. There's not much else we can do with the FTP service so let's check out the HTTP service.

### HTTP

The landing page is the default Apache index page but the nmap results indicated there were two entries in the robots.txt file so let's check that out.

![robots.txt](/assets/img/posts/thm-simple-ctf/robots.jpg)

A lot of comments but let's first check out the /openemr-5_0_1_3 before we look into other things.

![404 openemr](/assets/img/posts/thm-simple-ctf/openemr-404.jpg)

Seems like that may have been a misdirection so let's perform some directory enumeration and see if we obtain any results.

![gobuster](/assets/img/posts/thm-simple-ctf/gobuster.jpg)

Browsing to the /simple endpoint, we come across

![CMS page](/assets/img/posts/thm-simple-ctf/cms-landing.jpg)

At the bottom of the page, the CMS displays a version number of 2.2.8.

![CMS version](/assets/img/posts/thm-simple-ctf/cms-version.jpg)

#### SQLi Exploit

We can search for potential exploits for this CMS version.

![searchsploit](/assets/img/posts/thm-simple-ctf/searchsploit.jpg)

That last entry looks promising! We can copy it over to our current directory by `searchsploit -m 46635.py`.

This script exploits a vulnerability in the News module permitting unauthenticated blind time-based SQLi [^cmsms-vuln].

![exploit usage](/assets/img/posts/thm-simple-ctf/exploit-usage.jpg)

`python2 46635.py -u http://10.10.170.54/simple`

Let's run the exploit without using the cracking password functionality.

![SQL injection](/assets/img/posts/thm-simple-ctf/sql-injection.jpg)

Looks like the exploit found some a username, email, salt, and hash! Looking through the exploit script's password cracking functionality, it is brute force cracking the password with a MD5 hash of the salt and password!

#### Password Cracking

Let us try to use hashcat to crack the hash!

![hashcat](/assets/img/posts/thm-simple-ctf/hashcat.jpg)

`mitch:secret`

Looks like Mitch has a password of secret to access the CMS database. The location of the login page is on the home page of the CMS Made Simple page.

![admin location](/assets/img/posts/thm-simple-ctf/admin-location.jpg)

![admin login](/assets/img/posts/thm-simple-ctf/admin-login.jpg)

Browsing to http://10.10.170.54/simple/admin, we have succesfully logged in!

## Initial Foothold

### Reverse Shell

![file manager](/assets/img/posts/thm-simple-ctf/file-manager.jpg)

Looks like the File Manager section maps to the uploads path. Let's try to upload a PHP reverse shell.

![upload error](/assets/img/posts/thm-simple-ctf/upload-error.jpg)

It seems that the upload is not allowed presumably because of the PHP extension but this information isn't displayed on the upload page. The server does return a more informative error.

We are able to upload the file as a txt file and view it at http://10.10.170.54/simple/uploads/shell.txt.

![shell.txt](/assets/img/posts/thm-simple-ctf/upload-txt.jpg)

What if we try to rename the file?

![rename](/assets/img/posts/thm-simple-ctf/rename.jpg)

*I tried a few things at this point but nothing was working. I Googled ways on uploading a PHP file to this CMS and came across a post from another CTF which stated that you could copy the file to a .php extension to bypass the upload policy. Eventually, that would have been my next option but I became impatient and looked it up. On top of that, there is a Metasploit module with the exact authenticated RCE Copy functionality[^metasploit].*

![copy](/assets/img/posts/thm-simple-ctf/copy.jpg)

With the file successfully uploaded, we can browse to the shell.php file on the uploads directory and trigger the reverse shell connection!

![reverse shell](/assets/img/posts/thm-simple-ctf/reverse-shell.jpg)

We received a shell as www-data! Let's upgrade this shell into an interactive TTY shell [^shell-upgrade].

Remembering the note from the FTP server, Mitch used the same pass for the system user. Let's switch into mitch's system account with the password `secret`.

![mitch login](/assets/img/posts/thm-simple-ctf/mitch.jpg)

User Flag: `G00d j0b, keep up!`

## Privilege Escalation

Looking into Mitch's sudo privileges, he is able to execute vim as root with no password required.

![sudo privs](/assets/img/posts/thm-simple-ctf/sudo-privs.jpg)

It is quite simple to escalate your privileges if you are able to execute vim as root as detailed in GTFObins [^vim-privesc].

**Gtfobins is a fantastic resource to manipulate binaries that are misconfigured to obtain root access, read files, etc.**

Once I opened up vim as sudo, I ran the following system command to escalate my privileges as root `:!/bin/bash`.

![root flag](/assets/img/posts/thm-simple-ctf/root-flag.jpg)

Root Flag: `W3ll d0n3. You made it!`

## Useful Commands

### Hashcat with Salt

To include a salt along with the hash, separate it by a colon. If you have a MD5 hash and salt, use attack mode 20 with the hash file format as `hash:salt`.

## Reflection

With my second time approaching this challenge, I think I did a significantly better job this time around enumerating the application, finding a vulnerability and a public exploit for that, and the privilege escalation technique.

The one thing I can improve which I noted above was trying all potential methods of exploitation before searching online for a solution. I had already tried the option to move a file myself so I could have just as easily tried to copy the file. I will keep this in mind for future CTF boxes.

This machine is fantastic at targeting an actual CMS application and searching for publicly disclosed vulnerabilities.

### Killchain Summary

1. Authenticate to the FTP server anonymously and grab the ForMitch.txt file
2. Locate the /simple endpoint through directory enumeration
3. Use the public exploit for the version of CMS Made Simple obtain the username and MD5 hash of their password
4. Crack the hash to obtain Mitch's password and gain access to the CMS Made Simple admin console
5. Upload a PHP reverse shell as a TXT file and copy the file renaming it with a PHP extension
6. Escalate privileges through reverse shell by abusing the sudo privileges assigned to the VIM binary

### Misconfigurations

1. The FTP service should not have allowed us to authenticate anonymously.
2. The CMS software had an SQL injection vulnerability and should have patched that by upgrading the CMS. On top of that, the administrators should remove references to the version information for the CMS.
3. Even if the CMS has not been updated, the MD5 hash may not have been cracked if Mitch chose a strong password.
4. The privilege escalation vector was by manipulating the VIM binary which was given full sudo access with no password required which doesn't seem necessary.

### Summary of Exploits

The exploit used to obtain the username, email, and hash through SQL injection is related to CVE-2019-9053. This exploit takes advantage of a vulnerability in the News Module component. An attacker could manipulate the m1_idlist argument as a query parameter which lead to a time-based SQL injection.

A time-based SQL injection relies on the database pausing for a specified amount of time and then returning the results indicating that the query was successful. The attacker can enumerate each letter of the desired piece of data.

#### Privilege Escalation

IF vim has sudo privileges, break out and obtain a root shell by:

```
$ sudo /usr/bin/vim
:!/bin/bash -p
```

This is a feature within VIM to execute commands from the text editor. It is possible to execute a command to launch a Bash interpreter with escalated privileges.

## References

[^cmsms-vuln]: <https://vuldb.com/?id.132463>
[^metasploit]: <https://www.rapid7.com/db/modules/exploit/multi/http/cmsms_upload_rename_rce>
[^shell-upgrade]: <https://blog.ropnop.com/upgrading-simple-shells-to-fully-interactive-ttys>
[^vim-privesc]: <https://gtfobins.github.io/gtfobins/vim/#sudo>
