---
title: Gaming Server (Try Hack Me)
author: Robin Goyal
date: 2021-09-11 10:45 -0400
categories: [Cybersecurity, Writeups]
tags: [thm, ctf, writeup]
hidden: true
image:
  src: https://tryhackme-images.s3.amazonaws.com/room-icons/80d16a6756c805903806f7ecbdd80f6d.jpeg
---

I am currently in the process of completing these boxes on Try Hack Me again in an effort to document my experience, reinforce my knowledge of the topics, and improve my ability to concisely communicate the pentest lifecycle.

## Enumeration

The initial nmap scan of the top 1000 ports of the target reveals two open ports:
- 22 (SSH)
- 80 (HTTP)

![nmap results](/assets/img/posts/thm-gaming-server/nmap-initial.jpg)

The target is an Ubuntu Linux OS as indicated in the SSH and Apache version information.

Unlike the past few rooms that we have completed, the Apache server does not have the default title upon installation so let's check that out first.

### HTTP

![initial landing page](/assets/img/posts/thm-gaming-server/initial-landing.jpg)

The content of the web application looks something out of Game of Thrones! Before we browse other sections of the application, let's perform some directory enumeration using gobuster!

![gobuster common.txt results](/assets/img/posts/thm-gaming-server/gobuster-common.jpg)

I trimmed the output of the gobuster results as most of the results `.ht*` files that we do not have access to. The command I used to obtain these results is:
`gobuster dir -u 10.10.148.18 -w /usr/share/seclists/Discovery/Web-Content/common.txt -x "php,txt,html,old,bak" -t 25`

A robots.txt file! This wasn't in the nmap results but it may contain more endpoints that we were not exposed to from the gobuster results.

```
user-agent: *
Allow: /
/uploads/
```

Hmm, we have already encountered that in the gobuster results but it must be important. With an uploads directory, there may be a vector to upload a reverse shell payload (possibly /secret?) and trigger the connection from the uploads directory.

Before we switch focus to the /secret and /uploads directories, let's explore the application a bit and check for any information leaked in the content or in the page source.

Only the index.html source leaked some information about a potential name/username.

![index-source](/assets/img/posts/thm-gaming-server/index-source.jpg)

This may be handy afterwards!

## Initial Foothold

We can finally switch focus to the two interesting directories from the gobuster results. Viewing the /secret directory:

![secret index](/assets/img/posts/thm-gaming-server/secret-index.jpg)

This Apache server provides an indexed view for the /secret directory. Viewing the contents of secretKey, it is an SSH private key that is encrypted by a passphrase.

```
-----BEGIN RSA PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: AES-128-CBC,82823EE792E75948EE2DE731AF1A0547

T7+F+3ilm5FcFZx24mnrugMY455vI461ziMb4NYk9YJV5uwcrx4QflP2Q2Vk8phx
H4P+PLb79nCc0SrBOPBlB0V3pjLJbf2hKbZazFLtq4FjZq66aLLIr2dRw74MzHSM
FznFI7jsxYFwPUqZtkz5sTcX1afch+IU5/Id4zTTsCO8qqs6qv5QkMXVGs77F2kS
Lafx0mJdcuu/5aR3NjNVtluKZyiXInskXiC01+Ynhkqjl4Iy7fEzn2qZnKKPVPv8
9zlECjERSysbUKYccnFknB1DwuJExD/erGRiLBYOGuMatc+EoagKkGpSZm4FtcIO
IrwxeyChI32vJs9W93PUqHMgCJGXEpY7/INMUQahDf3wnlVhBC10UWH9piIOupNN
SkjSbrIxOgWJhIcpE9BLVUE4ndAMi3t05MY1U0ko7/vvhzndeZcWhVJ3SdcIAx4g
/5D/YqcLtt/tKbLyuyggk23NzuspnbUwZWoo5fvg+jEgRud90s4dDWMEURGdB2Wt
w7uYJFhjijw8tw8WwaPHHQeYtHgrtwhmC/gLj1gxAq532QAgmXGoazXd3IeFRtGB
6+HLDl8VRDz1/4iZhafDC2gihKeWOjmLh83QqKwa4s1XIB6BKPZS/OgyM4RMnN3u
Zmv1rDPL+0yzt6A5BHENXfkNfFWRWQxvKtiGlSLmywPP5OHnv0mzb16QG0Es1FPl
xhVyHt/WKlaVZfTdrJneTn8Uu3vZ82MFf+evbdMPZMx9Xc3Ix7/hFeIxCdoMN4i6
8BoZFQBcoJaOufnLkTC0hHxN7T/t/QvcaIsWSFWdgwwnYFaJncHeEj7d1hnmsAii
b79Dfy384/lnjZMtX1NXIEghzQj5ga8TFnHe8umDNx5Cq5GpYN1BUtfWFYqtkGcn
vzLSJM07RAgqA+SPAY8lCnXe8gN+Nv/9+/+/uiefeFtOmrpDU2kRfr9JhZYx9TkL
wTqOP0XWjqufWNEIXXIpwXFctpZaEQcC40LpbBGTDiVWTQyx8AuI6YOfIt+k64fG
rtfjWPVv3yGOJmiqQOa8/pDGgtNPgnJmFFrBy2d37KzSoNpTlXmeT/drkeTaP6YW
RTz8Ieg+fmVtsgQelZQ44mhy0vE48o92Kxj3uAB6jZp8jxgACpcNBt3isg7H/dq6
oYiTtCJrL3IctTrEuBW8gE37UbSRqTuj9Foy+ynGmNPx5HQeC5aO/GoeSH0FelTk
cQKiDDxHq7mLMJZJO0oqdJfs6Jt/JO4gzdBh3Jt0gBoKnXMVY7P5u8da/4sV+kJE
99x7Dh8YXnj1As2gY+MMQHVuvCpnwRR7XLmK8Fj3TZU+WHK5P6W5fLK7u3MVt1eq
Ezf26lghbnEUn17KKu+VQ6EdIPL150HSks5V+2fC8JTQ1fl3rI9vowPPuC8aNj+Q
Qu5m65A5Urmr8Y01/Wjqn2wC7upxzt6hNBIMbcNrndZkg80feKZ8RD7wE7Exll2h
v3SBMMCT5ZrBFq54ia0ohThQ8hklPqYhdSebkQtU5HPYh+EL/vU1L9PfGv0zipst
gbLFOSPp+GmklnRpihaXaGYXsoKfXvAxGCVIhbaWLAp5AybIiXHyBWsbhbSRMK+P
-----END RSA PRIVATE KEY-----
```

Before we use John the Ripper and the rockyou wordlist to crack this, we should check if /uploads provides a similar indexed view to /secret.

![uploads index](/assets/img/posts/thm-gaming-server/uploads-index.jpg)

It does! Of the three files, the dict.lst file may contain one of the passphrases for the SSH private key. A quick glance at the other two files did not provide any interesting information. We can ignore those for now and come back to them later if needed.

With the three pieces of information:
- username: john
- private key protected by passphrase: secretKey
- dictionary: dict.lst

This should be enough to obtain our initial foothold into the target.

Let's use ssh2john.py to convert the SSH private key into a crackable file by John the Ripper. Next, we'll use JTR with the dict.lst wordlist and see if it can be cracked.

![john the ripper](/assets/img/posts/thm-gaming-server/john.jpg)

Awesome! I bet letmein was in the rockyou wordlist anyways but a more complicated password in the dict.lst file would've rendered that point moot.

![initial foothold](/assets/img/posts/thm-gaming-server/initial-foothold.jpg)

We have our initial foothold into the system as john and let's grab the user flag.

![user flag](/assets/img/posts/thm-gaming-server/user-flag.jpg)

User Flag: `a5c2ff8b9c2e3d4fe9d4ff2f1a5a6e7e`

## Privilege Escalation

Listing the sudo privileges of john is a dead end as it requests the password which we do not have.

I tried a few other things:
- Searching for files owned by user John or group John
- Searching for any misconfigured SUID binaries
- World readable/writable /etc/shadow and /etc/passwd files

None of these vectors returned anything. As I was about to grab the linpeas enumeration script, I checked the groups for john to see if there was anything out of the ordinary.

![groups](/assets/img/posts/thm-gaming-server/groups.jpg)

The group `lxd` stood out to me. Performing some google-fu for "lxd group privesc" and one of the top hits was an article by hackingarticles on how to abuse this [^lxd-priv-esc].

The abuse of the lxd privileges is WAY beyond my technical knowledge but I will try to summarize the steps very briefly here. The article does a fantastic job of that anyways.

A member of the "lxd" group can escalate their privileges to root even if the user does not have sudo privileges. The user can create a container mounting the root file system (/) into the container and enter the container as the root user.

The steps to configure the abuse as well as exploit are documented in the article. The article mounts the root filesystem to /mnt/root in the container. Once we enter the container, the user will be root and we can find the flag at /mnt/root/root/root.txt.

![root flag](/assets/img/posts/thm-gaming-server/root-flag.jpg)

And there we go! We have completed this room!

Root Flag: `2e337b8c9f3aff0c2b3e8d4e6a7c88fc`

## Reflection

The lxd group being the way to privilge escalation stood out from prior experience of completing this room. I had never encountered this before so the first time I completed this room, I took a quick peek at a walkthrough to know that lxd was the vector for privesc.

This doesn't fall into the standard privilege escalation vectors that a majority of the Easy THM rooms utilize but I love coming across new ones. Recognizing the needle in the haystack comes with experience as you build a mental understanding of what is normal and not normal.

In the end, I enjoyed learning something new and not that it is documented, I hope I won't forget it.

## Useful Commands

### lxd privilege escalation

1. Build the alpine image on attacker system

```
$ git clone  https://github.com/saghul/lxd-alpine-builder.git
$ cd lxd-alpine-builder
$ ./build-alpine
```

2. Transfer the generated tar file to the target

3. Use the following commands to import the image, mount the file system, and enter the container

```
$ lxc image import ./alpine-v3.10-x86_64-20191008_1227.tar.gz --alias myimage
$ lxc init myimage ignite -c security.privileged=true
$ lxc config device add ignite mydevice disk source=/ path=/mnt/root recursive=true
$ lxc start ignite
$ lxc exec ignite /bin/sh
```

## References

[^lxd-priv-esc]: <https://www.hackingarticles.in/lxd-privilege-escalation/>
