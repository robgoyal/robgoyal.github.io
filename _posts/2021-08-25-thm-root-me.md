---
title: RootMe (Try Hack Me)
author: Robin Goyal
date: 2021-08-25 8:30 -0400
categories: [Cybersecurity, Writeups]
tags: [thm, ctf, writeup, web application, reverse shell, privesc, burpsuite, suid, gobuster]
hidden: true
image:
  src: https://tryhackme-images.s3.amazonaws.com/room-icons/11d59cb34397e986062eb515f4d32421.png
---

I am currently in the process of completing these boxes on Try Hack Me again in an effort to document my experience, reinforce my knowledge of the topics, and improve my ability to concisely communicate the pentest lifecycle.

Note: The target IP address may change throughout the writeup as I complete the room over a period of time.

## Scenario

**Title**: RootMe

**Link**: https://tryhackme.com/room/rrootme

**Description**: A ctf for beginners, can you root me?

**Free/Subsciber**: Free

**Difficulty**: Easy


## Enumeration

First things first, let's start off with an nmap scan.

![nmap results](/assets/img/posts/thm-root-me/nmap.jpg)

From the scan results, the target is an Ubuntu OS as noted in the version information for the Apache and SSH services. These services are also the only two open ports:
1. 22 (SSH)
2. 80 (HTTP)


### SSH

No information leaked in the banner so nothing to see here.

### HTTP

The landing page doesn't contain much information other than some self-writing text. No information is leaked in the page source and no robots.txt file. Directory enumeration did return a few results.

![gobuster results](/assets/img/posts/thm-root-me/gobuster.jpg)

Checking out the /panel endpoint, there is a form to upload a file.

![file upload](/assets/img/posts/thm-root-me/file-upload.jpg)

Knowing that the backend langugage is PHP through the PHPSESSID information in the nmap scan results, let's try to upload a PHP reverese shell [^pentest-monkey].

## Initial Foothold

### Reverse Shell

![file upload error](/assets/img/posts/thm-root-me/file-upload-error.jpg)

Looks like PHP files are blocked from being uploaded. There's no indication that this a client-side filter by reviewing the JS source code, so this is probably server-side validation.

Let's intercept the upload request in Burpsuite and utilize an intruder attack.
We will use a list of other PHP extensions in the hope that the server is filtering on the .php extension only [^php-extensions].

#### Extension Filter Bypass

![burp attack](/assets/img/posts/thm-root-me/burp-attack.jpg)

Success! All of the extensions in our payload list except for .php was uploaded. This is clear by the larger response length in the burp intruder attack window.
The gobuster results indicated that there is a /uploads directory so let's verify our files are there.

![uploads](/assets/img/posts/thm-root-me/uploads.jpg)

Great! Now we can use this to trigger our reverse shell connection.

The rev.php3 and rev.php4 did not trigger the reverse shell connection but the rev.php5 file established the connection as seen below.

![initial foothold](/assets/img/posts/thm-root-me/initial-foothold.jpg)

The service running the Apache web server is www-data and if we check /var/www, there is a user.txt flag present.

![user flag](/assets/img/posts/thm-root-me/user-flag.jpg)

User flag: `THM{y0u_g0t_a_sh3ll}`

## Privilege Escalation

One of the privesc vectors to check for are binaries that are misconfigured with the SUID bit set. This allows a lesser privileged user to have the same privileges as the user that owns it.
You can search for these binaries with the command `find / -perm /4000 2>/dev/null`.

It stood out that the /usr/bin/python was in the list of binaries with this bit set. GTFObins also has an entry to escalate your privileges if the SUID bit is set [^gtfobins].

![privilege escalation](/assets/img/posts/thm-root-me/priv-esc.jpg)

Success! We have root privileges and found the root flag as well.

Root Flag: `THM{pr1v1l3g3_3sc4l4t10n}`

## Reflection

The second time around, this box was a great opportunity to learn how to bypass PHP extensions filters as well as learning about the SUID bit privilege escalation vector.

### Killchain Summary

1. Perform directory enumeration to identify the /panel file upload endpoint.
2. Identify a potential PHP extension that the server will accept by brute-forcing a list using Burpsuite.
3. Upload pentestmonkey's PHP reverse shell and catch the reverse shell from Netcat.
4. Escalate privileges by abusing a SUID misconfigured Python binary with a command from GTFObins.

### Misconfigurations

1. The /panel endpoint should be protected by an authentication portal.
2. Robust filter to restricts file uploads which can trigger a reverse shell or restrict outgoing connections on the host-based firewall.
3. Don't configure the Python binary to have SUID privileges.

### Summary of Exploits

#### Privilege Escalation

IF Python has the SUID bit set, obtain a root shell by:

```
/usr/bin/python -c 'import os; os.execl("/bin/bash", "bash", "-p")'
```

This command will execute a series of commands without launching a script or the Python interpreter. The command will import the os module and execute the `execl` function which executes a program but replaces the current process rather than returning.

### Things I Learned

1. Using Burpsuite to bypass file upload restrictions by brute-forcing the list of valid PHP extensions.
2. Escalating privileges using a SUID-bit misconfigured Python binary.

## References

[^pentest-monkey]: <https://github.com/pentestmonkey/php-reverse-shell/blob/master/php-reverse-shell.php>
[^php-extensions]: <https://book.hacktricks.xyz/pentesting-web/file-upload#file-upload-general-methodology>
[^gtfobins]: <https://gtfobins.github.io/gtfobins/python/#suid>
