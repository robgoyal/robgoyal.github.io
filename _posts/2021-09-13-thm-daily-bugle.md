---
title: Daily Bugle (Try Hack Me)
author: Robin Goyal
date: 2021-09-13 21:30 -0400
categories: [Cybersecurity, Writeups]
tags: [thm, ctf, writeup]
hidden: true
image:
  src: https://tryhackme-images.s3.amazonaws.com/room-icons/5a1494ff275a366be8418a9bf831847c.png
---

I am currently in the process of completing these boxes on Try Hack Me again in an effort to document my experience, reinforce my knowledge of the topics, and improve my ability to concisely communicate the pentest lifecycle.

## Enumeration

![nmap results](/assets/img/posts/thm-daily-bugle/nmap-initial.jpg)

From the initial nmap scan results, there are three open ports:
- 22 (SSH)
- 80 (HTTP)
- 3306 (MySQL)

Some of the information obtained from the nmap scan:
- The web application is an Apache server with PHP as the backend language
- Tons of disallowed entries in the robotx.txt file
- Target is likely a CentOS OS as indicated in the version information for SSH
- The web application is a Joomla CMS (likely an open source product)

There is lots to look into so let's get started!

### SSH

No information leaked in the banner and no potential credentials for an effective brute force so we may have to come back to this.

### MySQL

There is an open MySQL port but connections established from outside of the target environment are usually blocked (only localhost connections). Let's verify this.

![mysql failed login](/assets/img/posts/thm-daily-bugle/mysql-failed-login.jpg)

Nothing much to build off of here either so the web application may be our source of information.

### HTTP

Exploring the web application's landing page.

![landing page](/assets/img/posts/thm-daily-bugle/landing-page.jpg)

We already know that there are many disallowed entries in the robots.txt file. Before we explore the web application further, we should use our google-fu skills to determine if Joomla is a vendor supported CMS product.

#### Joomla

Through a bit of research, Joomla is a CMS with also many exploits and vulnerabilities. We need to determine the version of the CMS to use specific vulnerabilities. Checking for the joomla.xml file in /administrator/manifests/files, the contents contain the exact version for this CMS [^joomla-exploitation].

![joomla version](/assets/img/posts/thm-daily-bugle/joomla-version.jpg)

using searchsploit for that exact version,

![searchsploit](/assets/img/posts/thm-daily-bugle/searchsploit.jpg)

there is an SQLi vulnerability present. Awesome! Let's copy the file and analyze the contents of the second exploit in that list using `searchsploit -m 42033.txt`.

![vulnerability](/assets/img/posts/thm-daily-bugle/vulnerability.jpg)

#### Sqlmap

The exploit provides a bit of information on the vulnerable URL and even provides the exact sqlmap command required against the target.

Running the command but replacing the target URL,

![sqlmap](/assets/img/posts/thm-daily-bugle/sqlmap.jpg)

there are five databases present. We can now use sqlmap to dump the data of `joomla`, and `test` as the other three are default databases in MySQL.

*After fiddling around with sqlmap to dump the database and exploiting the CMS with a Metasploit framework for a while, neither techniques were producing any results. For some reason, despite sqlmap finding an injection point, it was retrieving lots of 500 server errors and unable to get column information. Peeking at the THM hint, it said "Why not use a Python script instead of sqlmap". I should curse myself for peeking at the hint instead of trying other avenues. Oh well.*

A quick google search for "Joomla 3.7 exploit" and the second results points to a Github repository with a Python script [^joomblah].

*Honestly, it was right there.*

#### Joomblah

This was a point-and-click type of exploit requiring no modifications.

![joomblah](/assets/img/posts/thm-daily-bugle/joomblah.jpg)

The script dumped the information of the "Super User" with the username, email, and a hash (Blowfish).

Perhaps John the Ripper with the rockyou wordlist can crack this for us.

![john](/assets/img/posts/thm-daily-bugle/jtr.jpg)

Woot! Now, we have administrative access to the Joomla CMS.

## Initial Foothold

Exploring the panel a bit, there were a LOT of sections and potential pathways to create a reverse shell. However, we can follow [this](https://www.hackingarticles.in/joomla-reverse-shell/) article by hackingarticles.in on uploading a reverse shell within the Joomla CMS.

We'll modify the Beez3 template's index.php file with a reverse shell [^php-rev-shell]. Next, we'll set up a netcat listener on the IP address and Port configured in the payload. Lastly, we need to trigger the reverse shell connection by clicking on Preview Template within the administrative panel.

![reverse shell](/assets/img/posts/thm-daily-bugle/reverse-shell.jpg)

We have obtained a shell as the apache user. Let's try to escalate our privileges to root or a local user.

## Privilege Escalation

### Database Credentials

Searching through the filesystem with the limited access that we had, the web application's root directory had the configuration.php file with the password to the MySQL database.

![config](/assets/img/posts/thm-daily-bugle/config.jpg)

I first tried the password for the root user but that didn't work. Looking at the /home directory, there was one user directory present for jjameson. The database password provided us access to the jjameson user's account.

![user flag](/assets/img/posts/thm-daily-bugle/user-flag.jpg)

### Yum

Now, we need to try to obtain root access! Let's list out jjameson's sudo privileges.

![sudo privs](/assets/img/posts/thm-daily-bugle/sudo-privs.jpg)

jjameson is able to run yum as root with no password. Let's check if gtfobins as an entry on how to abuse this privilege as sudo.

![gtfobins](/assets/img/posts/thm-daily-bugle/gtfobins.jpg)

The first option did not pan out since the target didn't have the fpm command installed. The second option did not require any modification and we obtained a shell as root by following the exact instructions.

![root](/assets/img/posts/thm-daily-bugle/priv-esc.jpg)

Obtaining the flag located at /root/root.txt, we have completed this room!

## Reflection

Without realizing it the first time I completed this room (mostly through the helpful questions/prompts provided by THM), I didn't realize this room was rated as Hard. I think it might be more appropriate as a Medium difficulty room because of identifying where sqlmap is failing and being able to search for an appropriate solution.

Otherwise, a bit of a challenging room that I'm not sure if I could've solved with the one hint that I used today. Lots of opportunity to learn how to use public exploits, thinking outside of the box to obtain user access, and privilege escalation using yum.

## References

[^joomla-exploitation]: <https://hackertarget.com/attacking-enumerating-joomla/>
[^joomblah]: <https://github.com/stefanlucas/Exploit-Joomla>
[^php-rev-shell]: <https://github.com/pentestmonkey/php-reverse-shell/blob/master/php-reverse-shell.php>
