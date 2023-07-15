---
title: Mr. Robot (Try Hack Me)
author: Robin Goyal
date: 2021-09-20 21:30 -0400
categories: [Cybersecurity, Writeups]
tags: [thm, ctf, writeup]
hidden: true
image:
  src: https://tryhackme-images.s3.amazonaws.com/room-icons/7a8797ae59733f2a72f0e8a8748be128.jpeg
---

I am currently in the process of completing these boxes on Try Hack Me again in an effort to document my experience, reinforce my knowledge of the topics, and improve my ability to concisely communicate the pentest lifecycle.

## Scenario

**Title**: Mr. Robot

**Description**: Based on the Mr. Robot show, can you root this box?

**Free/Subscriber**: Free

**Difficulty**: Medium

## Enumeration

![nmap initial](/assets/img/posts/thm-mrrobot/nmap-initial.jpg)

From the information in the nmap scan results, it is not clear on this target's OS.

There are 2 open ports and 1 closed port:
- 80 (HTTP)
- 443 (HTTPS)

Briefly checking the web applications served on port 80 and 443, they seem to be the same web application which makes our life easier.

### HTTP

Let's first browse to the web application before performing any automated scanning.

![landing](/assets/img/posts/thm-mrrobot/landing.jpg)

The web application is interactive and displays a scrolling page of text imitating the bootup a Linux device.

Interacting with some of the options and investigating the Javascript source code which enables the interactivity, there was nothing we could utilize here.

There is a robots.txt file.

```
User-agent: *
fsocity.dic
key-1-of-3.txt
```

Let's download both files.

`$ wget http://10.10.255.152/key-1-of-3.txt`

`$ wget http://10.10.255.152/fsocity.dic`

The key-1-of-3.txt file is the first key we need to submit to the THM room. The second file contains a large list of words that may be useful as potential passwords but are also repeated quite a bit. Let's filter out any words that are repeated.

`$ cat fsocity.dic | sort -u > fsocity-filtered.dic`

The file originally contained over 800,000 words but after filtering out the repeated words, there are just slightly over 11,000 words.

Now, let's kick off some directory enumeration scans using the common.txt SecLists file.

![gobuster first half](/assets/img/posts/thm-mrrobot/gobuster-first-half.jpg)

![gobuster second half](/assets/img/posts/thm-mrrobot/gobuster-second-half.jpg)

This took awfully long despite using 25 threads (typically 10) and approximately 4000 entries in the common.txt file but we got more than enough results which required two separate images.

The results confirm that the web application is serving a Wordpress CMS. This is indicative by the endpoints that are prefixed with the "wp-". With such a large number of entries, it was overwhelming to know where to begin. Most did not lead to web pages that were accessible but checking the "/0" endpoint did lead to a page that looked similar to a typical Wordpress site.

![0 page](/assets/img/posts/thm-mrrobot/0.jpg)

There is also a login page at /wp-login but we don't have a potential username to brute force.

![wp login page](/assets/img/posts/thm-mrrobot/wp-login.jpg)

#### WordPress Enumeration

There are several techniques to enumerate various aspects of WordPress such as the version information, plugins, users, and more [^wp-user-enum]. There is also the wpscan tool that can perform this enumeration for us but I didn't find it as effective.

Sometimes the WordPress version can be leaked in the HTML source as a meta tag. I didn't find it in the index page or on the login page but was able to find it on the /0 endpoint.

![wp version](/assets/img/posts/thm-mrrobot/wp-version.jpg)

There weren't any relevant public exploits that we could use for this specific version of WordPress.

Next, let's enumerate the WordPress users. This can be done by appending a `?author=1` to the end of the URL which should display the posts by that user if the user exists. If the user does exist, the title of the page should change to that specific user.

**Note**: This also did not work on the index page but it did work on the /0 wordpress page.

Cycling through ID's 0 to 10, we discovered two potential users.

![krista](/assets/img/posts/thm-mrrobot/krista.jpg)

![elliot](/assets/img/posts/thm-mrrobot/elliot.jpg)

The remaining ID's displayed "user's Blog" similar to the earlier image displaying the /0 endpoint.

Wordpress also verifies the existence of the user through the login page.

![invalid username](/assets/img/posts/thm-mrrobot/invalid-username.jpg)

![invalid password](/assets/img/posts/thm-mrrobot/invalid-password.jpg)

We can brute force elliot's account using the fsocity-filtered.dic password list and hydra.

![hydra](/assets/img/posts/thm-mrrobot/hydra.jpg)

Success! We have access to the web application as the user elliot.

![login](/assets/img/posts/thm-mrrobot/wp-elliot-login.jpg)

## Initial Foothold

### WordPress Reverse Shell

With the Appearance editor, we are able to edit the 404.php file of the twentyfifteen theme to generate a reverse shell [^panel-rce].

First, let's modify PentestMonkey's PHP reverse shell with our attacker system's IP address and port that netcat will be listening to catch the reverse shell. Copying the source code, we'll update the 404.php code and initialize our netcat listener.

Once we browse to the location of the 404.php file, we should see our Netcat listener catch the reverse shell as the daemon user.

![reverse shell](/assets/img/posts/thm-mrrobot/unprivileged-reverse-shell.jpg)

Let's upgrade our shell and move onto privilege escalation.

## Privilege Escalation

### Horizontal Privilege Escalation

Checking out /home, there is a home directory for the user, robot. Checking the list of files, we see the second key (key-2-of-3.txt) and a password.raw-md5 file.

![robots](/assets/img/posts/thm-mrrobot/robots-password.jpg)

The password file is world readable and contains an MD5 hash. Let's crack the hash using John the Ripper and the RockYou.txt wordlist.

![jtr](/assets/img/posts/thm-mrrobot/jtr.jpg)

Success! Let's switch into the robot user with the given credentials. We can now read the key-2-of-3.txt file and submit it to THM.

### Vertical Privilege Escalation

Robot is not able to run sudo on this target so we'll have to escalate our privileges another way. Let's check for any interesting binaries with the SUID bit enabled.

![suid bins list](/assets/img/posts/thm-mrrobot/suid-bins-list.jpg)

The nmap binary is not a typical SUID enabled binary which stood out. Checking GTFObins, I scrolled down to the bottom to the SUID section and was not able to abuse given the technique they outlined.

![gtfobins nmap suid](/assets/img/posts/thm-mrrobot/gtfobins-wrong-vuln.jpg)

The version of nmap installed on the system did not have the --script option enabled.

*Thinking that the nmap binary was a dead end, I noticed that there is a MySQL database running only accepting localhost connections. After spending lots of time searching through the filesystem for config files and not getting anywhere, I checked the hint for the 3rd and final key but the hint was nmap.*

After spending that time, I searched through GTFObins again to see if there was anything we could take advantage of.

![gtfobins nmap shell](/assets/img/posts/thm-mrrobot/gtfobins-correct-vuln.jpg)

One of the first techniques outlined specified an exploitation technique for versions that the installed nmap version falls within. *If only I had slowed down my pace..*

This is incredibly simple so let's get a root shell and submit the final flag.

![root shell](/assets/img/posts/thm-mrrobot/root-shell.jpg)

## Reflection

This room was significantly more challenging and time consuming than the previous rooms I've completed. Even after completing it once before, it was challenging to complete the second time around.

Realistically, the path to realizing that enumerating the users of the WordPress application is not as straightforward as it seems in the writeup above. It was a massive mish-mash of various techniques, exploit searching, further directory enumeration, and more. It's tough to display all of the things I did to get to the correct killchain.

Lessons Learned:
- Enumerating the WordPress application is key to understanding the available users.
- Nmap should not have been configured with the SUID bit enabled. On top of that, the version of nmap is significantly outdated.
- The robot user's password file which allowed horizontal privilege escalation should not have been world-readable.
- Do not give up on a vector (i.e utilizing nmap to escalate privileges) until you've tried as much as what is possible
- Lastly, the robots.txt should not have leaked the path to the fsocity.dic file which enabled us the initial foothold to the WordPress panel

## References

[^wp-user-enum]: <https://hackertarget.com/wordpress-user-enumeration/>
[^panel-rce]: <https://book.hacktricks.xyz/pentesting/pentesting-web/wordpress#panel-rce>
[^shell-upgrade]: <https://blog.ropnop.com/upgrading-simple-shells-to-fully-interactive-ttys/>
