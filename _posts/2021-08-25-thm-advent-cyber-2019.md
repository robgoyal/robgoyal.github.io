---
title: Advent of Cyber 2019 (Try Hack Me)
author: Robin Goyal
date: 2021-08-25 18:30 -0400
categories: [Cybersecurity, Writeups]
tags: [thm, ctf, writeup]
published: false
image:
  src: https://tryhackme-images.s3.amazonaws.com/room-icons/9efbcb85d76feac6b711b8ed1b2fd534.png
---

This is the first edition of the Advent of Cyber christmas event that took place in 2019. It contains a series of challenges for each day starting from December 1<sup>st</sup> up until Christmas day. Each challenge introduces a topic, a few readings, and a challenge associated with it.

I will continuously update this post as I approach a challenge or two each day until I have completed all of them!

## [Day 1] Inventory Management

### Scenario

> `Elves needed a way to submit their inventory - have a web page where they submit their requests and the elf mcinventory can look at what others have submitted to approve their requests. It’s a busy time for mcinventory as elves are starting to put in their orders. mcinventory rushes into McElferson’s office. I don’t know what to do. We need to get inventory going. Elves can log on but I can’t actually authorise people’s requests! How will the rest start manufacturing what they want. McElferson calls you to take a look at the website to see if there’s anything you can do to help. `

Target: `http://10.10.173.17:3000`

### Enumeration

Checking out the web application, it is first asking us to login. Since we have no information, let's try to make an account and analyze the network responses upon authentication.

We created an account with the following information.

![account registration](/assets/img/posts/thm-advent-cyber/1/registration.jpg)

Viewing the request and response information upon authentication to the application, there is a cookie set with a value that looks like a Base64 encoding.

![login request](/assets/img/posts/thm-advent-cyber/1/login.jpg)

If we decode the cookie:

```bash
$ echo "dXNlcjEyM3Y0ZXI5bGwxIXNz" | base64 -d
user123v4er9ll1!ss
```

It looks like the cookie has the username with a string appended to it. What if that appended string is the same across cookies? Creating a second account proves this hypothesis!

### Mcinventory

From the scenario, we have to authenticate as the user `mcinventory` to be able to authorise the requests by elves. We need to generate the Base64 encoded cookie with the user `mcinventory` along with the static string.

```bash
$ echo -n 'mcinventoryv4er9ll1!ss' | base64
bWNpbnZlbnRvcnl2NGVyOWxsMSFzcw==
```

Modifying the authid cookie in Firefox's Storage tab, refreshing the page provides us with the admin console where we can approve the requests by elves along with the item that mcinventory requested.

![firewall](/assets/img/posts/thm-advent-cyber/1/firewall.jpg)

### Questions and Answers

1. What is the name of the cookie used for authentication? `authid`
2. If you decode the cookie, what is the value of the fixed part of the cookie? `v4er9ll1!ss`
3. After accessing his account, what did the user mcinventory request? `firewall`

## [Day 2] Arctic Forum

### Scenario

> `A big part of working at the best festival company is the social live! The elves have always loved interacting with everyone. Unfortunately, the christmas monster took down their main form of communication - the arctic forum! Elf McForum has been sobbing away McElferson's office. How could the monster take down the forum! In an attempt to make McElferson happy, she sends you to McForum's office to help. `

Target: `http://10.10.55.249:3000`

Based on the information from the Q&A along with the essential reading, we have to perform directory enumeration.

### Enumeration

Browsing to the web application, we are greeted to a login page at /login but there is no option to register. Let's perform the directory enumeration to see if there is information we can obtain from somewhere else.

Performing a directory enumeration scan, we see the results as below. The interesting part is that most endpoints redirect to /login except for the /sysadmin page.

![gobuster results](/assets/img/posts/thm-advent-cyber/2/gobuster.jpg)

Checking out /sysadmin endpoint displays similar login page to /login but the former contains a comment telling us to check out the github repo for arctic digital design.

![page source comment](/assets/img/posts/thm-advent-cyber/2/comment.jpg)

The ReadMe for the Github repo contains default username and password credentials for the login portal.

![default creds](/assets/img/posts/thm-advent-cyber/2/github.jpg)

### Login

Now that we have a valid set of credentials, we can login with access to the administrative sections.

![admin page](/assets/img/posts/thm-advent-cyber/2/admin.jpg)

### Questions and Answers

1. What is the path of the hidden page? `/sysadmin`
2. What is the password you found? `defaultpass`
3. What do you have to take to the 'partay'? `eggnog`


## [Day 3] Evil Elf

### Scenario

> `An Elf-ministrator, has a network capture file from a computer and needs help to figure out what went on! Are you able to help?`

Target: PCAP file

### PCAP Analysis

There are several thousand packets that are captured but a majority of the packets are TLS packets. There are 3 telnet packets in the Protocol Hierarchy Statistics as noted below!

![protocol hierarchy](/assets/img/posts/thm-advent-cyber/3/protocol-hierarchy.jpg)

The first telnet packet contains a request to echo 'ps4' to a christmas list text file.

![telnet packet 1](/assets/img/posts/thm-advent-cyber/3/telnet-1.jpg)

The second and third telnet packets contain a request-response cycle of the /etc/shadow content! If we follow the TCP stream of one of these telnet packets, the contents of /etc/shadow content is included.

![telnet packets 2 and 3](/assets/img/posts/thm-advent-cyber/3/telnet-2.jpg)

The only password hash saved in /etc/shadow is for the buddy user: `$6$3GvJsNPG$ZrSFprHS13divBhlaKg1rYrYLJ7m1xsYRKxlLh0A1sUc/6SUd7UvekBOtSnSyBwk3vCDqBhrgxQpkdsNN6aYP1`.

### Password Cracking

Saving the password to a text file and using John the Ripper with the rockyou.txt wordlist, the password was cracked within seconds!

![password cracked](/assets/img/posts/thm-advent-cyber/3/password-crack.jpg)

Password: `rainbow`

### Questions and Answers

1. What's the destination IP on packet number 998? `63.32.89.195`
2. What item is on the Christmas list? `ps4`
3. Crack buddy's password! `rainbow`

## Useful Commands

## Reflection

## References
