---
title: Pickle Rick (Try Hack Me)
author: Robin Goyal
date: 2021-08-28 13:20 -0400
categories: [Cybersecurity, Writeups]
tags: [thm, ctf, writeup, web application, gobuster, python, reverse shell, webshell, privesc]
hidden: true
image:
  src: https://tryhackme-images.s3.amazonaws.com/room-icons/47d2d3ade1795f81a155d0aca6e4da96.jpeg
---

I am currently in the process of completing these boxes on Try Hack Me again in an effort to document my experience, reinforce my knowledge of the topics, and improve my ability to concisely communicate the pentest lifecycle.

Note: The target IP address may change throughout the writeup as I complete the room over a period of time.

## Scenario

**Title**: Pickle Rick

**Link**: https://tryhackme.com/room/picklerick

**Description**: A Rick and Morty CTF. Help turn Rick back into a human!

**Free/Subsciber**: Free

**Difficulty**: Easy

## Enumeration

First things first, let's start off with an nmap scan.

![nmap scan](/assets/img/posts/thm-pickle-rick/nmap.jpg)

The target is an Ubuntu OS identified by the information in the service version for SSH and HTTP. There are two ports open:
- 22 (SSH)
- 80 (HTTP)

### SSH

Nothing much to see here without any potential credentials and no information leaked in the banner.

### HTTP

Browsing to the web server, there is a plead by Rick for Morty to help him out as he forgot the password and he needs to locate the last three ingredients to finish his reversing potion.

![landing page](/assets/img/posts/thm-pickle-rick/landing.jpg)

A username is leaked in the page source! `R1ckRul3s`

![source code](/assets/img/posts/thm-pickle-rick/source.jpg)

The last thing to check before we move onto further enumeration is a presence of the robots.txt file. There is one present but it does not contain any disallow entries except for a string that seems like it could be a password or hint that is used later on.

```plaintext
Wubbalubbadubdub
```

So far, we have a found potential username and password combination:

`R1ckRul3s:Wubbalubbadubdub`

Trying to authenticate ourselves through SSH did not pan out. Let's continue on with some directory enumeration as we cannot progress from what is available to us through the landing page.

![gobuster](/assets/img/posts/thm-pickle-rick/gobuster.jpg)

An interesting result shows up in the Gobuster results, login.php. Maybe our credentials will work there!

![login](/assets/img/posts/thm-pickle-rick/login.jpg)

The creds authenticate us successfully! We're redirected to a portal.php Command Panel page.

![portal](/assets/img/posts/thm-pickle-rick/portal.jpg)

## Initial Foothold

### Reverse Shell

After executing a few commands to identify the type of webshell such as `ls`, `whoami`, it is clear that this is a Bash webshell.

To gain access to the system through the command line, let's try to generate a reverse shell!

![reverse shell](/assets/img/posts/thm-pickle-rick/reverse-shell.jpg)

After creating a netcat listener on port 1234, I tried a few payloads from the PayloadAllTheThings repository for the reverse shell. Ultimately, a python3 reverse shell worked for me in the end [^python-reverse-shell].

We have to stabilise our reverse shell by upgrading it into a fully interactive tty shell [^shell-upgrade]. Once that's done, we can look around the file system as the www-data user.
Checking out the files in the /var/www/html directory where the web server files are served from, we come across the first ingredient.

![first ingredient](/assets/img/posts/thm-pickle-rick/first-ingredient.jpg)

**Sup3rS3cretPickl3Ingred.txt**

```plaintext
mr. meeseek hair
```

Next is to check out the files in the home directory of the rick user and we found the second ingredient!

![second ingredient](/assets/img/posts/thm-pickle-rick/second-ingredient.jpg)

**second ingredients**

```plaintext
1 jerry tear
```

## Privilege Escalation

The third and last file is most likely in the home directory of the root user as I could not find it from the current privileges.

Checking out the privileges of the www-data user, this user is able to execute all commands as root with no password required.

I escalated the privileges of this user through the command `sudo su`.

![privilege escalation](/assets/img/posts/thm-pickle-rick/priv-esc.jpg)

And the third and final ingredient to turn Rick back into a human is found!

![third ingredient](/assets/img/posts/thm-pickle-rick/third-ingredient.jpg)

- 3rd.txt

```plaintext
3rd ingredients: fleeb juice
```

## Reflection

Rick and Morty is one of my favorite animated shows so it was pretty enjoyable to do a CTF kind of focused on that.

This is also my 3<sup>rd</sup> time completing this room so I've pretty confidently figured out the necessary path to find all the ingredients and become root.

The very first time when I was very, very new to all of this, I completed this room through the webshell only. This room is enjoyable and provide many of the standard CTF/THM tactics needed to complete it!

### Killchain Summary

1. View the source code of index.html of the web application to locate the username for Rick.
2. Identify a potential password for Rick in robots.txt.
3. Perform directory enumeration to locate the Command Panel endpoint and authenticate.
4. Initialize netcat to capture a reverse shell connection with a Python payload.
5. Escalate privileges from www-data to root as www-data has full root privileges.l

### Misconfigurations

1. Sensitive information leaks in the source code and robots.txt.
2. www-data should not have full root privileges.
3. The command panel should have improved the command filtering to not allow execution of commands that could provide shell access. Instead of using a blacklist of commands, there may have been better results with a whitelist of commands and filtering further commands.
4. Lock down the host-based firewall to not allow outgoing connections for the reverse shell.

### Things I Learned

- Generating a reverse shell connection with Python.

## References

[^python-reverse-shell]: <https://github.com/swisskyrepo/PayloadsAllTheThings>
[^shell-upgrade]: <https://blog.ropnop.com/upgrading-simple-shells-to-fully-interactive-ttys/>
