---
title: Overpass (Try Hack Me)
author: Robin Goyal
date: 2021-09-19 11:15 -0400
categories: [Cybersecurity, Writeups]
tags: [thm, ctf, writeup]
hidden: true
image:
  src: https://tryhackme-images.s3.amazonaws.com/room-icons/2048656e072dd7caffe455ae2d44b65f.png
---

I am currently in the process of completing these boxes on Try Hack Me again in an effort to document my experience, reinforce my knowledge of the topics, and improve my ability to concisely communicate the pentest lifecycle.

## Scenario

**Title**: Overpass

**Description**: What happens when some broke CompSci students make a password manager?

**Free/Subscriber**: Free

**Difficulty**: Easy

## Enumeration

First things first, we'll enumerate the services accesible on this target.

![nmap initial scan](/assets/img/posts/thm-overpass/nmap-initial.jpg)

There are two open ports on this target:
- 22 (SSH)
- 80 (HTTP)

The service information of SSH reveals that this is an Ubuntu Linux target. Also, something that we have not encountered is that the HTTP application is served by a Golang HTTP server.

### HTTP

![overpass landing](/assets/img/posts/thm-overpass/overpass-landing.jpg)

From the landing page and the About Us section, Overpass is a password manager that allows you to keep your passwords safe using "military grade" encryption.

We're able to download the source code and build script from the Downloads page.

![Downloads Page](/assets/img/posts/thm-overpass/downloads-page.jpg)

Reading through the source code, it's not complicated to understand how the Overpass software works. However, there's not much we can utilize from this to obtain our initial foothold into the system.

Performing a Gobuster scan, we come across a few endpoints that we have already encountered.

![gobuster 2.3 results on /](/assets/img/posts/thm-overpass/gobuster-2.3-root.jpg)

One endpoint that we have not come across however is the /admin page.

Browsing to the page, we're presented with an administrator login prompt.

![admin landing](/assets/img/posts/thm-overpass/admin-landing.jpg)

*I tried a few things such as brute forcing the authentication using Hydra as well as performing more detailed gobuster scans on subsequent endpoints but there was no information revealed.*

I viewed the page source of the Administrator area and started to understand the authentication process.

![admin landing source](/assets/img/posts/thm-overpass/admin-landing-source.jpg)

A file that stands out from within the source code which is linked in the administrator page is login.js.

![login js source](/assets/img/posts/thm-overpass/login-js-source.jpg)

The source code reveals that Javascript was performing an asynchronous request for every authentication attempt through the web browser.

If the credentials were incorrect, the page would be updated with "Incorrect Credentials". However, if the credentials were correct, the application would set a cookie, "SessionToken", and redirect us to /admin.

What if we could just set the cookie ourselves with any value and the backend would accept that providing us access as an administrative user.

Trying out a few different values for the cookie, false worked for us.

![cookie editor](/assets/img/posts/thm-overpass/cookie-editor.jpg)

I'm not sure why false would grant us access when true didn't but that's fine! We now have access!

![admin authenticated](/assets/img/posts/thm-overpass/admin-authenticated.jpg)

We have two pieces of information that we can use to obtain our initial foothold:
- SSH Private Key
- Potential Username: james

## Initial Foothold

Copying the private key to our attacker system, we know it is protected by a passcode so let's use John the Ripper to crack the passcode.

![john the ripper privkey](/assets/img/posts/thm-overpass/john.jpg)

![james initial login](/assets/img/posts/thm-overpass/initial-login.jpg)

Once logged in as James, we find two files in his home directory. The first file is the user.txt flag which we can submit to the THM room.

The second file is a todo.txt file containing remaining tasks for James to complete?

```
To Do:
> Update Overpass' Encryption, Muirland has been complaining that it's not strong enough
> Write down my password somewhere on a sticky note so that I don't forget it.
  Wait, we make a password manager. Why don't I just use that?
> Test Overpass for macOS, it builds fine but I'm not sure it actually works
> Ask Paradox how he got the automated build script working and where the builds go.
  They're not updating on the website
  ```

Points 1 and 3 may not be very helpful to us. However, point 2 implies that James is storing his system password using the Overpass password manager and point 4 may indicate the presence of a cron job.

Let's focus on point 2 and obtain James' password. Searching for the overpass binary on the system using `which overpass`, it is available at /usr/bin/overpass. Running it with option 4,

![overpass james pw](/assets/img/posts/thm-overpass/overpass-james-pw.jpg)

Great! We have James' password. Trying to list out James' sudo privileges and it appears he does not have any. Let's move on to point 4 then and search for any cron jobs.

![crontab](/assets/img/posts/thm-overpass/crontab.jpg)

There is one cron task that is running every minute to download the buildscript from the Overpass web application's download page and executing it. This cron task is running as the root user.

## Privilege Escalation

WHat is interesting is that it is pulling the buildscript.sh file through the overpass.thm address. If we could modify the /etc/hosts file to associate our attacker system's IP address to overpass.thm, we could serve a malicious payload to catch the shell as root.

Listing out the permissions of /etc/hosts file, the file is world readable and writable which is definitely not the typical permission scheme for this file.

![/etc/hosts permissions](/assets/img/posts/thm-overpass/etc-hosts-perms.jpg)

First, we need to set up a netcat listener to catch the reverse shell payload from the cronjob execution. Second, we need to set up a simple Python HTTP server to serve the malicious payload. The malicious payload is located at /downloads/src/buildscript.sh which is what the cron job is requesting.

We'll update the entry in /etc/hosts to overpass.thm to point to 10.6.5.103 instead of 127.0.0.1.

Once our netcat and Python servers are configured, all we can do is wait. This should be a few seconds since the cron job executes every minute.

![root shell](/assets/img/posts/thm-overpass/root-shell.jpg)

Woot woot! We got root!

All we need to do is read the flag at /root/root.txt and submit it to THM to complete this room.

## Reflection

This room focused on very different techniques to abuse our privileges to obtain root. It focused on modifying the /etc/hosts file to hijack a cronjob's regular build script to obtain a root shell.

On top of that, there were opportunities to crack passwords, read Javascript source code, and perform standard enumeration techniques.
