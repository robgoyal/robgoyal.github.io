---
title: Brute It (Try Hack Me)
author: Robin Goyal
date: 2021-09-10 19:30 -0400
categories: [Cybersecurity, Writeups]
tags: [thm, ctf, writeup]
hidden: true
image:
  src: https://tryhackme-images.s3.amazonaws.com/room-icons/e343e8b253b4efc14bf61236d457c923.jpg
---

I am currently in the process of completing these boxes on Try Hack Me again in an effort to document my experience, reinforce my knowledge of the topics, and improve my ability to concisely communicate the pentest lifecycle.

## Enumeration

An initial nmap scan of the top 1000 ports of the target reveals two open ports:
- 22 (SSH)
- 80 (HTTP)

![nmap results](/assets/img/posts/thm-bruteit/nmap-initial.jpg)

The target is an Ubuntu Linux OS as indicated by the version information for the SSH and Apache services.

### HTTP

As indicated by the http-title details in the nmap results, the title for the web application hosted by Apache is the default title.

Browsing to the web application, there is no information visible on the default Apache page, no leaked information in the page source, and no robots.txt file. With no information to progress off of, we shall proceed to directory enumeration.

![gobuster](/assets/img/posts/thm-bruteit/gobuster.jpg)

The /admin endpoint is the only interesting result in the gobuster scan so let's browse to that!

![admin page](/assets/img/posts/thm-bruteit/admin.jpg)

Checking out the page source...

![admin source](/assets/img/posts/thm-bruteit/admin-source.jpg)

The system administrator left a vital piece of information for us to take advantage of (as if anyone would forget the username admin). This may have been the logical approach but since the room is called "bruteit", let's brute force the login as admin.

First, we need to intercept the request to analyze how the payload is structured. This could be in the browser Developer Tools but I like to practice with Burpsuite.

![burp intercept](/assets/img/posts/thm-bruteit/burp-intercept.jpg)

Turning on the intercept and browser proxy, we captured the request. The request contains two fields, user and pass. We could use Burpsuite's Intruder feature to brute force the request but the free version has an obscene throttling rate so let's use Hydra.

If we use Hydra, we need to know what an invalid authentication attempt looks like.

![invalid login](/assets/img/posts/thm-bruteit/invalid-login.jpg)

That string, "Username or password invalid", is important for our success with Hydra. Hydra's http-post-form module expects at least 3 parameters [^hydra]:
- POST endpoint
- POST payload
- Failure string

The last parameter could be other values other than a failure string but failure is the default. Let's construct the hydra command but I will break the command down in the Useful Commands section closer to the bottom of this post.

![hydra](/assets/img/posts/thm-bruteit/hydra.jpg)

Success! Looks like the password for the admin user, `xavier` was present in the rockyou wordlist. Authenticating as admin, we are redirected to /panel.

![panel](/assets/img/posts/thm-bruteit/panel.jpg)

We now have our initial foothold into the target.

## Initial Foothold

Let's download the private key.

```
-----BEGIN RSA PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: AES-128-CBC,E32C44CDC29375458A02E94F94B280EA

JCPsentybdCSx8QMOcWKnIAsnIRETjZjz6ALJkX3nKSI4t40y8WfWfkBiDqvxLIm
UrFu3+/UCmXwceW6uJ7Z5CpqMFpUQN8oGUxcmOdPA88bpEBmUH/vD2K/Z+Kg0vY0
BvbTz3VEcpXJygto9WRg3M9XSVsmsxpaAEl4XBN8EmlKAkR+FLj21qbzPzN8Y7bK
HYQ0L43jIulNKOEq9jbI8O1c5YUwowtVlPBNSlzRMuEhceJ1bYDWyUQk3zpVLaXy
+Z3mZtMq5NkAjidlol1ZtwMxvwDy478DjxNQZ7eR/coQmq2jj3tBeKH9AXOZlDQw
UHfmEmBwXHNK82Tp/2eW/Sk8psLngEsvAVPLexeS5QArs+wGPZp1cpV1iSc3AnVB
VOxaB4uzzTXUjP2H8Z68a34B8tMdej0MLHC1KUcWqgyi/Mdq6l8HeolBMUbcFzqA
vbVm8+6DhZPvc4F00bzlDvW23b2pI4RraI8fnEXHty6rfkJuHNVR+N8ZdaYZBODd
/n0a0fTQ1N361KFGr5EF7LX4qKJz2cP2m7qxSPmtZAgzGavUR1JDvCXzyjbPecWR
y0cuCmp8BC+Pd4s3y3b6tqNuharJfZSZ6B0eN99926J5ne7G1BmyPvPj7wb5KuW1
yKGn32DL/Bn+a4oReWngHMLDo/4xmxeJrpmtovwmJOXo5o+UeEU3ywr+sUBJc3W8
oUOXNfQwjdNXMkgVspf8w7bGecucFdmI0sDiYGNk5uvmwUjukfVLT9JPMN8hOns7
onw+9H+FYFUbEeWOu7QpqGRTZYoKJrXSrzII3YFmxE9u3UHLOqqDUIsHjHccmnqx
zRDSfkBkA6ItIqx55+cE0f0sdofXtvzvCRWBa5GFaBtNJhF940Lx9xfbdwOEZzBD
wYZvFv3c1VePTT0wvWybvo0qJTfauB1yRGM1l7ocB2wiHgZBTxPVDjb4qfVT8FNP
f17Dz/BjRDUIKoMu7gTifpnB+iw449cW2y538U+OmOqJE5myq+U0IkY9yydgDB6u
uGrfkAYp6NDvPF71PgiAhcrzggGuDq2jizoeH1Oq9yvt4pn3Q8d8EvuCs32464l5
O+2w+T2AeiPl74+xzkhGa1EcPJavpjogio0E5VAEavh6Yea/riHOHeMiQdQlM+tN
C6YOrVDEUicDGZGVoRROZ2gDbjh6xEZexqKc9Dmt9JbJfYobBG702VC7EpxiHGeJ
mJZ/cDXFDhJ1lBnkF8qhmTQtziEoEyB3D8yiUvW8xRaZGlOQnZWikyKGtJRIrGZv
OcD6BKQSzYoo36vNPK4U7QAVLRyNDHyeYTo8LzNsx0aDbu1rUC+83DyJwUIxOCmd
6WPCj80p/mnnjcF42wwgOVtXduekQBXZ5KpwvmXjb+yoyPCgJbiVwwUtmgZcUN8B
zQ8oFwPXTszUYgNjg5RFgj/MBYTraL6VYDAepn4YowdaAlv3M8ICRKQ3GbQEV6ZC
miDKAMx3K3VJpsY4aV52au5x43do6e3xyTSR7E2bfsUblzj2b+mZXrmxst+XDU6u
x1a9TrlunTcJJZJWKrMTEL4LRWPwR0tsb25tOuUr6DP/Hr52MLaLg1yIGR81cR+W
-----END RSA PRIVATE KEY-----
```

![privkey passphrase](/assets/img/posts/thm-bruteit/privkey-passphrase.jpg)

Hmm. This probably was not as easy as I thought. The private key is protected by a passphrase.

No matter. There is an incredibly useful series of scripts that convert encrypted files to a hash that John the Ripper can understand and crack. These scripts are of the form `<service>2john`. To crack the private key passphrase, we shall use ssh2john.

The command structure is also incredibly simple, `ssh2john.py id_rsa > filename`.

![jtr](/assets/img/posts/thm-bruteit/john.jpg)

Phew, JTR will crack that SSH encrypted key very quickly.

![ssh](/assets/img/posts/thm-bruteit/ssh.jpg)

Now, we have definitely obtained our initial foothold. Let's grab the user flag and move on to privilege escalation. The user flag is available at /home/john/user.txt.

User Flag: `THM{a_password_is_not_a_barrier}`

## Privilege Escalation

We'll begin by listing out the sudo privileges of the user.

![sudo-privs](/assets/img/posts/thm-bruteit/sudo-privs.jpg)

Okay! Looks like we can use /bin/cat as root with no password which is great since we don't have a password to begin with.

We could read the contents of the root.txt file which is likely located in the root user's directory but we could use this as an opportunity to try to crack the root user's password.

We can save the contents of the /etc/passwd and /etc/shadow file to our attacker machine, use the unshadow command to combine them into a single file and use JTR to crack the hashes.

![JTR shadow crack](/assets/img/posts/thm-bruteit/john-shadow-crack.jpg)

Woot woot! John found the password for the root user in the rockyou.txt file. Let's switch as root and grab the root flag.

![root flag](/assets/img/posts/thm-bruteit/root-flag.jpg)

Root Flag: `THM{pr1v1l3g3_3sc4l4t10n}`

And with that, we have completed the room.

## Useful Commands

### Hydra Post

`hydra -l admin -P /usr/share/wordlists/rockyou.txt 10.10.150.210 http-post-form "/admin/:user=admin&pass=^PASS^:Username or password invalid"`
- `-l admin`: User the username admin
- `-P rockyou.txt`: User the password list provided
- `10.10.150.210`: target to use
- `http-post-form`: Hydra module to use (parameters for the module are separate by colons)
  - `"/admin/"`: POST endpoint
  - `"user=admin&pass=^PASS^"`: The POST payload data. In this case, user and pass are the fields the serve expects. We're hardcoding admin as the username and ^PASS^ is the expected Hydra placeholder for the password from the password list
  - `Username or password invalid`: The failure condition string that Hydra searches for in the resopnse

## Reflection

The first time I completed this room, I think I followed the Try Hack Me questions order which gives a strong pathway to solving this room. At that time, I don't think I would have tried to crack the root user's password and would have just grabbed the file instead.

In this journey to create a writeup and document it on this website, I am not using the questions to guide me to solving this room. With experience, this room is definitely on the easier end but it provides a lot of experience with brute forcing authentication and cracking various sorts of hashes.

## References

[^hydra]: <https://infinitelogins.com/2020/02/22/how-to-brute-force-websites-using-hydra/>
