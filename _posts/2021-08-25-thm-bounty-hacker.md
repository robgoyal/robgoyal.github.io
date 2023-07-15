---
title: Bounty Hacker (Try Hack Me)
author: Robin Goyal
date: 2021-08-25 10:55 -0400
categories: [Cybersecurity, Writeups]
tags: [thm, ctf, writeup, ftp, ssh, privesc, tar, hydra, brute force]
hidden: true
image:
  src: https://tryhackme-images.s3.amazonaws.com/room-icons/11d59cb34397e986062eb515f4d32421.png
---

I am currently in the process of completing these boxes on Try Hack Me again in an effort to document my experience, reinforce my knowledge of the topics, and improve my ability to concisely communicate the pentest lifecycle.

Note: The target IP address may change throughout the writeup as I complete the room over a period of time.

## Scenario

**Title**: Bounty Hacker

**Link**: https://tryhackme.com/room/cowboyhacker

**Description**: You talked a big game about being the most elite hacker in the solar system. Prove it and claim your right to the status of Elite Bounty Hacker!

**Free/Subsciber**: Free

**Difficulty**: Easy


## Enumeration

First things first as always, start off with an nmap scan to enumerate the services on the target.

![nmap results](/assets/img/posts/thm-bounty-hacker/nmap.jpg)

From the version information for the SSH and Apache services in the nmap scan results, the target is an Ubuntu OS. There are a total of three open ports from our scan of the top 1000 ports:

- 21 (FTP)
- 22 (SSH)
- 80 (HTTP)

### FTP

The ftp-anon NSE script indicates that anonymous FTP login is enabled.. Connecting to the server and listing the files shows there's two files present:
- task.txt
- lock.txt

```plaintext
1.) Protect Vicious.
2.) Plan for Red Eye pickup on the moon.

-lin
```

```plaintext
rEddrAGON
ReDdr4g0nSynd!cat3
Dr@gOn$yn9icat3
R3DDr46ONSYndIC@Te
ReddRA60N
R3dDrag0nSynd1c4te
dRa6oN5YNDiCATE
ReDDR4g0n5ynDIc4te
R3Dr4gOn2044
RedDr4gonSynd1cat3
R3dDRaG0Nsynd1c@T3
Synd1c4teDr@g0n
reddRAg0N
REddRaG0N5yNdIc47e
Dra6oN$yndIC@t3
4L1mi6H71StHeB357
rEDdragOn$ynd1c473
DrAgoN5ynD1cATE
ReDdrag0n$ynd1cate
Dr@gOn$yND1C4Te
RedDr@gonSyn9ic47e
REd$yNdIc47e
dr@goN5YNd1c@73
rEDdrAGOnSyNDiCat3
r3ddr@g0N
ReDSynd1ca7e
```

The first file, task.txt, contains two tasks which may be important but doesn't provide much information other than the fact that it was written by **lin** which could be a potential username for further FTP or SSH access.

The second file, lock.txt, may be a password list which could be used in combination with the username, lin, to brute force those services.

### HTTP

Let's first check out the HTTP site. The initial page contains some various quotes from Cowboy Bebop, an anime.

There's no information leaked in the source code, no robots.txt file, and no results in the directory enumeration scan.

Let's approach the SSH service with the data that we found from the FTP server.

## Initial Foothold

### Hydra

As an initial check, no information was leaked in the banner when trying to connect. With the potential username, lin, and the password file, let's use Hydra to brute force the SSH service.

![hydra results](/assets/img/posts/thm-bounty-hacker/hydra.jpg)

Success! We can conncet to the target machine through the SSH service with the credentials `lin:RedDr4gonSynd1cat3`.

In the users home directory, the user.txt flag is available for us!

![user flag](/assets/img/posts/thm-bounty-hacker/user-flag.jpg)

User Flag: `THM{CR1M3_SyNd1C4T3}`

## Privilege Escalation

Checking for the sudo privileges of lin since we have his password, he is able to run the /bin/tar binary as root.

![sudo privileges](/assets/img/posts/thm-bounty-hacker/sudo-privs.jpg)

Fortunately, gtfobins has an incredibly simple example of abusing this to attain a privileged shell [^gtfobins].

![privilege escalation](/assets/img/posts/thm-bounty-hacker/privesc.jpg)

There we go! We have successfully attained a root shell. The above command is attempting to create a tar archive into /dev/null with content from /dev/null and at every checkpoint (1 file), it executes the /bin/bash binary as root which is how we escalated our privileges.

![root flag](/assets/img/posts/thm-bounty-hacker/root-flag.jpg)

Last step is just find the root flag /root.

Root Flag: `THM{80UN7Y_h4cK3r}`

## Reflection

This room was not as difficult as some of the other Easy rated rooms that I have come across on THM but it was a good opportunity to try other vectors instead of getting stuck on one.

The HTTP server had nothing to do with the killchain for this target but it commonly is in these CTF style rooms.

Lastly, the manipulation of the tar command is an interesting method to escalate your privileges.

### Killchain Summary

1. Authenticate anonymously to the FTP server to find a password list and a potential username.
2. Brute-force the SSH server with the username and password list to obtain an initial foothold.
3. Escalate privileges through the tar binary which lin is allowed to execute as root.

### Misconfigurations

1. Anonymous authentication should not have been enabled for the FTP service.
2. Sensitive information was leaked on the FTP server.
3. To prevent brute-force attempts to the SSH service, password authentication should be disabled and private key authentication should have been enabled.
4. The user, lin, should not have had the privileges to run tar as sudo.

### Summary of exploits

#### Privilege Escalation

IF tar has sudo privileges, obtain a root shell by:

```
sudo tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/bash
```

This will attempt to compress the contents of /dev/null into /dev/null but executing an action at each checkpoint. The action will load a Bash interpreter with the privileges of the root user.

### Things I Learned

1. Escalating privileges by abusing the SUDO privileges for the tar binary.

## References

[^gtfobins]: <https://gtfobins.github.io/gtfobins/tar/#sudo>
