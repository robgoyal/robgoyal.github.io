---
title: Previse (Hack the Box)
author: Robin Goyal
date: 2021-08-30 17:00 -0400
categories: [Cybersecurity, Writeups]
tags: [htb, ctf, writeup]
hidden: true
image:
  src: https://www.hackthebox.eu/storage/avatars/e3c542ada4b134e29e534e3081ef9650.png
---

Previse is an Active machine on Hack the Box so this writeup will not be posted live to this website until a later date. Some information about the system:
- OS: Linux
- IP: `10.10.11.104`

## Enumeration

First things first, let's start off with an nmap scan.

![nmap results](/assets/img/posts/htb-previse/nmap.jpg)

The target is an Ubuntu OS as indicated in the service version information for SSH and HTTP services. These are also the only two ports that are open on the system.

- 22 (SSH)
- 80 (HTTP)

### HTTP

Initially browsing to the web page, we are redirected to login.php. That saves us the trouble from enumerating the tech stack as the backend language is PHP.

![login](/assets/img/posts/htb-previse/login.jpg)

With no valid credentials leaked anywhere in the page source and no information obtained through robots.txt, let's move on to directory enumeration to map out the application a bit more.

![gobuster](/assets/img/posts/htb-previse/gobuster.jpg)

**Note: Some of the entries are duplicated since the common.txt file contains both /index and /index.php but tagging on the `-x php` extension evalues both as /index.php.**

Okay! So we have a few files to search through. I searched through all of the PHP files that did not redirect to login.php to determine if there was any interesting information. Most of them did not include much information but the nav.php file acted similar to a "sitemap".

![nav](/assets/img/posts/htb-previse/nav.jpg)

I recalled from other THM or HTB experiences, you are able to view the source code of PHP pages. Checking out the source code

![nav source](/assets/img/posts/htb-previse/nav-source.jpg)

Some of the endpoints include:
- Creating an account
- Viewing the status of the website
- Checking out the log data

At this point, I spent a significant amount of time combing through the PHP files but was not able to find anything.

*This is another mistake that I made and one I even mentioned in the writeup for Cap but I did not follow my own advice enough. Similar to Cap, I was collaborating on this box with my friends and one of them provided a minor hint on how they obtained access to the application by creating an account.*

A shot in the dark knowing that this would likely fail but I posted to the `/accounts.php` endpoint with a username and password payload hoping the application would error out with an informative payload.

![account creation attempt](/assets/img/posts/htb-previse/create-account-attempt.jpg)

Looks like I was right and the application is yelling at me to provide the password confirmation. Looking closer at the response, the form is present with the exact fields required for the request. Looks like we got 2 out of 3 fields correct!

![account created](/assets/img/posts/htb-previse/account-creation.jpg)

Success! Looks like our account was added! Now we can authenticate to the application with the credentials `kamikaze:test123`.

*Another piece of helpful information that my friend stumbled upon during his enumeration of the application after I had already created the account was that we are able to view the HTML source prior to its redirection to `/login.php`. You can achieve this by intercepting the request in Burpsuite before it redirects or by using curl which does not redirect by default. I am not sure how I did not know about this earlier but definitely something to note. If I had known about this and viewed the HTML source of the PHP files, I would have been able to create the account with the knowledge that it was possible rather than taking a shot in the dark.*

![accounts](/assets/img/posts/htb-previse/accounts.jpg)

I displayed the last 30 lines to include the form on the account creation page to demonstrate what my friend had learnt.

#### Login

![logged in](/assets/img/posts/htb-previse/logged-in.jpg)

Now that we are logged in, we can browse some of the tabs available in the navigation bar which is probably what the output of the nav.php file was displaying.

The Files section had one uploaded file for the backup of the site as a ZIP file.

![files.zip](/assets/img/posts/htb-previse/files.jpg)

Within this backup, all of the PHP files existed including most of the files that we encountered in gobuster.

## Initial Foothold

Most of the files did not stand out but the logs.php file had an interesting comment along with a piece of Python code that could lead to our initial foothold.

![logs](/assets/img/posts/htb-previse/logs.jpg)

The developer used a Python script to process the logs providing a delimiter as a command line argument to the script. The delimiter argument is provided as a parameter via a POST request (we'll have to search for this) but since the parameter input is not escaped, we can abuse this for command injection leading to a reverse shell. The script is being executed as a system command so we can try to inject Bash commands to obtain a reverse shell.

First, let's search for where this POST request is being submitted in the application so we can abuse this.

![log data](/assets/img/posts/htb-previse/log-data.jpg)

This endpoint was tucked away under the "Management Menu" heading in the navigation bar. Let's capture this request in Burpsuite to see how the front-end submits the request and what the response looks like.

![log burp intercept](/assets/img/posts/htb-previse/burp-log.jpg)

Okay! Now, we have to verify that command injection is possible. One of the ways that I test this courtesy of IppSec on Youtube is to ping my attacker box and capturing the traffic filtering for ICMP packets.

![ping burp intercept](/assets/img/posts/htb-previse/burp-ping.jpg)

Fantastic! Looks like command injection is possible. Now, let's try to use various payloads to generate a reverse shell.

![reverse shell burp intercept](/assets/img/posts/htb-previse/burp-rev.jpg)

After a few attempts with a Bash TCP reverse shell, looks like the target had an OpenBSD version of netcat which allowed us to use the `-e` parameter. Last but not least, let's upgrade this into a fully interactive TTY shell [^shell-upgrade].

One of the first things to check is the services listening as there may be some services listening locally.

![netstat](/assets/img/posts/htb-previse/netstat.jpg)

The netstat output indicates that there is a service listening on port 3306 which is typically the port for MySQL. The contents of config.php contained the credentials for the MySQL database.

```php
<?php

function connectDB(){
    $host = 'localhost';
    $user = 'root';
    $passwd = 'mySQL_p@ssw0rd!:)';
    $db = 'previse';
    $mycon = new mysqli($host, $user, $passwd, $db);
    return $mycon;
}
?>
```

Connecting to the previse database within the MySQL server, there are two tables, accounts and files. Let's dump the accounts database to see if there are other accounts than the kamikaze user we created that may provide us user access to the system.

![mysqldump](/assets/img/posts/htb-previse/mysqldump.jpg)

Looks like the `m4lwhere` user has a hash with a salt that does not appear to be ASCII. This is an md5crypt hash that is frequently used in PHP to hash passwords.

*This took several attempts until I had to ask my friend how they cracked the password. I initially tried to copy the non-ASCII character in the salt from the accounts.php file but this produced no luck as both JTR and Hashcat complained about invalid token length. Next, I modified the encoding displayed in my terminal to ISO-8859-1 and JTR did not complain anymore but it did not crack the password with rockyou.txt.*

After some advice by my friend to approach it the same way but to use md5crypt-long, the password was cracked after several minutes.

![JTR](/assets/img/posts/htb-previse/jtr.jpg)

Success! We finally obtained some credentials `m4lwhere:ilovecody112235!`.

The first thing we should try is to switch into m4lwhere from www-data.

![Switch User](/assets/img/posts/htb-previse/su.jpg)

And we are in! Once we grabbed the user flag, it is time to perform some privilege escalation.

## Privilege Escalation

Let's check out m4lwhere's sudo privileges.

![Sudo Privileges](/assets/img/posts/htb-previse/privileges.jpg)

It appears that m4lwhere is able to execute the script at `/opt/scripts/access_backup.sh` as root if a password is provided. Dumping the contents of the bash script, the script is intended to be run as a cron job to backup the site at a regular interval.

However, the `date` binary used within the two lines is not an absolute path to the date binary which means that we can abuse this using PATH variable manipulation.

 ![privesc](/assets/img/posts/htb-previse/privesc.jpg)

The first thing to do is the prepend the PATH where the manipulated date file will be located. Second, create a binary with the contents of `/bin/bash -p` which will place you in a bash session with the privileges of the user that executed it. Next, run the access_backup.sh script to trigger the manipulated file to escalate your privileges and ta-da!

We have obtained root privileges and can move onto grabbing the root flag completing this box.

## Useful Commands

### Viewing PHP Source Code

Use curl to view the source code of a PHP file even if the page redirects to login.php. IF gobuster indicates there is a response size despite redirection, you will be able to view the source code.

### Steps to Path Variable Manipulation PrivEsc

1. Prepend the PATH with the location of the manipulated binary.
2. Generate the binary with a reverse shell payload or bash shell escalation.
3. Call the script allowing this privesc technique.

## Reflection

I generally find Hack The Box boxes that are rated easy more difficult than the Try Hack Me boxes. This was no exception. There were a few circumstances where I turned to the help of my friends for some advice and I even learned a few things along the way.

There's no harm in asking for advice but looking back, I did not put enough effort in enumerating the application as I should have. I tend to try to move quickly through my enumeration and analysis techniques and I miss critical information. An example of this is noting that the nav.php file contained a "Create Account" comment but I didn't explore this further. Another example is when JTR suggested using md5crypt-long and I didn't want long enough for the program to finish trying to crack the password.

Once again, this box was designed well and used a lot of techniques that I have learned about through THM and other sources. Although I required a bit of help, I can very well see the results of my efforts from learning about cybersecurity and ethical hacking.

## References

[^shell-upgrade]: <https://blog.ropnop.com/upgrading-simple-shells-to-fully-interactive-ttys/>
