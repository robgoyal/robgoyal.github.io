---
title: Easy Peasy CTF (Try Hack Me)
author: Robin Goyal
date: 2021-09-09 21:30 -0400
categories: [Cybersecurity, Writeups]
tags: [thm, ctf, writeup]
hidden: true
image:
  src: https://tryhackme-images.s3.amazonaws.com/room-icons/c376e08c928f806745c90c93b051127a.png
---

I am currently in the process of completing these boxes on Try Hack Me again in an effort to document my experience, reinforce my knowledge of the topics, and improve my ability to concisely communicate the pentest lifecycle.

## Enumeration

It's time to perform some enumeration!

![nmap results](/assets/img/posts/thm-ezpz-ctf/nmap.jpg)

The initial nmap scan for the top 1000 ports shows that only port 80 is open. The target is hosting an nginx server (version 1.16.1) but there is not too much information available even about the OS version.

If we can't obtain much information from the web application, we may have to perform a nmap scan of all 65,535 ports. But let's not discredit the web application yet!

### HTTP

Browsing to the IP address of the target, we come across what looks like a default successful installation page of nginx.

![default landing](/assets/img/posts/thm-ezpz-ctf/landing.jpg)

The nmap results did indicate that there was a robots.txt file.

```
User-Agent:*
Disallow:/
Robots Not Allowed
```

Looks like the system administrator was being a little cheeky with the comment at the end.

With no leaked information in the page source either, let's move on to some directory brute forcing using my favorite tool, gobuster!

![gobuster results](/assets/img/posts/thm-ezpz-ctf/gobuster.jpg)

Ouuu, a hidden endpoint!

![hidden page](/assets/img/posts/thm-ezpz-ctf/hidden-page.jpg)

That spooked me a little bit. Seems like some radiation zone but there's no real information present in this image nor in the page source. However, we can continue to dig deeper with gobuster on the /hidden directory.

 ![gobuster hidden results](/assets/img/posts/thm-ezpz-ctf/gobuster-hidden.jpg)

 Another endpoint to visit!

 ![whatever page](/assets/img/posts/thm-ezpz-ctf/whatever-page.jpg)

This is a much friendlier image! Once again, nothing to see here. Even the title says that this is a dead end. The page source does contain a hidden paragraph tag with what looks like base64 encoded data.

![whatever source](/assets/img/posts/thm-ezpz-ctf/whatever-source.jpg)

Decoding the base64 encoded string

```
$ echo ZmxhZ3tmMXJzN19mbDRnfQ== | base64 --decode
flag{f1rs7_fl4g}
```

reveals a flag. This is one of the answers to the questions in the room.

I did some further directory enumeration using a larger wordlist but no results were returned.

### Further Scanning

So that HTTP service looks like its a dead end.

A full nmap scan of all ports revealed two additional ports that we missed in our initial scan.
- 6498 (SSH)
- 65542 (HTTP/Apache)

![nmap round 2](/assets/img/posts/thm-ezpz-ctf/nmap-round-2.jpg)

These two services are not on their standard ports but nevertheless, let's move on to enumeration.

### HTTP (Apache)

The landing page for the web application on port 65542 is the default Apache page. Scanning the page, the third flag is available to us in plainsight.

![flag 3](/assets/img/posts/thm-ezpz-ctf/flag-3.jpg)

I'm not sure if we missed flag 2 but we'll come back to it. Checking out the page source for this Apache page, there is another hidden paragraph tag with more encoded data.

![apache source](/assets/img/posts/thm-ezpz-ctf/apache-source.jpg)

The sentence was about to tell us the encoding style but it cut off. I had only ever known about base64 encoding which didn't return any meaningful data so let's move over to Cyber Chef (great tool for data manipulation and wrangling) to try out other baseXX encoding formats.

![cyberchef](/assets/img/posts/thm-ezpz-ctf/cyberchef.jpg)

It took a few different formats to cycle though but Base62 was the encoding format. This is probably a hidden directory so let's browse to it.

![apache hidden endpoint](/assets/img/posts/thm-ezpz-ctf/apache-hidden-dir.jpg)

Again! Another image that serves no purpose. The page source contains some data that looks like more a hash rather an encoding.

![matrix source](/assets/img/posts/thm-ezpz-ctf/matrix-source.jpg)

Using the hash-identifier tool,

![hash identifier](/assets/img/posts/thm-ezpz-ctf/hashid.jpg)

it recommended two possible hashes which didn't end up being the format of the actual hash.

*The first time I completed this room, I must have spent an hour trying to understand how to crack this hash. My initial instinct when rockyou doesn't match the hash is not to try. It was only because of the unique hash name (GOST R 34.11-94), that I instantly remembered that this is the hash. First time, I tried using hashcat which requires you to specify the hash mode where as JTR can try to autodetect which it did successfully in this case.*

![john](/assets/img/posts/thm-ezpz-ctf/john.jpg)

Letting John the Ripper auto-detect the hash type as the correct hash format, we obtain a password but it's not clear what we're supposed to do with this.

## Initial Foothold

One thing that we haven't looked into is the robots.txt file for this web application.

```
User-Agent:*
Disallow:/
Robots Not Allowed
User-Agent:a18672860d0510e5ab6699730763b250
Allow:/
This Flag Can Enter But Only This Flag No More Exceptions
```

I thought this was a hash but using only hash identifier tools, online rainbow tables, and brute force cracking using a password list did not return any results no matter the hash.

*I tried several things but no vector panned out. After a while, I just looked for a hint on how to proceed from here and it revolved the around matrix style image and steganography.*

Downloading the binarycodepixabay.jpg file from the /n0th1ng3ls3m4tt3rs endpoint and using the steghide tool to determine if there is any embedded data, we obtain some interesting results.

![pixabay steghide](/assets/img/posts/thm-ezpz-ctf/steghide-pixabay.jpg)

When we were prompted with a passphrase, I entered in `mypasswordforthatjob` which was related to the hash that we found on the same page as the binarycoepixabay image.

Outputting the contents of secrettext.txt,

```
username:boring
password:
01101001 01100011 01101111 01101110 01110110 01100101 01110010 01110100 01100101 01100100 01101101 01111001 01110000 01100001 01110011 01110011 01110111 01101111 01110010 01100100 01110100 01101111 01100010 01101001 01101110 01100001 01110010 01111001
```

there is a username and password combination which could potentially provide us our initial foothold into the target system.

The password is saved as binary data so we can use CyberChef to convert this into a string that is actually usable.

![cyberchef binary](/assets/img/posts/thm-ezpz-ctf/cyberchef-binary.jpg)

With the password converted, we now have access to the system.

![boring login](/assets/img/posts/thm-ezpz-ctf/boring-ssh-login.jpg)

We can submit the flag in user.txt and move on to privilege escalation to obtain the root flag.

## Privilege Escalation

Listing out the sudo privileges for the boring user and they are not allowed to run sudo on this target system.

Let's search for any files owned by this user.

![boring files](/assets/img/posts/thm-ezpz-ctf/boring-files.jpg)

I filtered out any files in the /proc, /sys/, /run folders as the find usually returns results for the processes owned by boring. One file stands out quite a bit, /var/www/.mysecretcronjob.sh.

This may indicate the presence of a cron job.

![crontab](/assets/img/posts/thm-ezpz-ctf/crontab.jpg)

The root user is executing the .mysecretcronjob.sh file every minute. Let's check the contents of this file to see if we can use it to our advantage and escalate our privileges!

![secret file](/assets/img/posts/thm-ezpz-ctf/secret-file.jpg)

We can definitely use this to our advantage. The file is owned by boring and is also writable as us. We can add a line to generate a reverse shell back to our attacker system. All we need is a netcat listener to catch the reverse shell. Let's give this a shot.

![root shell](/assets/img/posts/thm-ezpz-ctf/root-shell.jpg)

On the left-hand side, you can see a payload that we used from the [PayloadAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Reverse%20Shell%20Cheatsheet.md#bash-tcp) repository, and on the right, the netcat listener caught the reverse shell as the root user.


We can find the final root flag at /root/.root.txt (hidden -.-), and finally consider this room completed.

## Reflection

This room is probably one of my least favorite rooms that I've completed so far on the THM platform. It's not to say it isn't good and won't teach you a lot. It's very CTF heavy and requires you to be in that mindset in some situations to be able to complete this room.

I required a hint or two which probably wouldn't have been necessary if I had tried all possible vectors. Either way, this room teaches lots about cracking hashes, directory enumeration, steganography, and escalating privileges through a vulnerable cron task.
