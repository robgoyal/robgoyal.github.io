---
title: Lian Yu (Try Hack Me)
author: Robin Goyal
date: 2021-09-19 12:00 -0400
categories: [Cybersecurity, Writeups]
tags: [thm, ctf, writeup]
hidden: true
image:
  src: https://tryhackme-images.s3.amazonaws.com/room-icons/c72d580db69a726dfb8da8aa6eaa2f5a.jpeg
---

I am currently in the process of completing these boxes on Try Hack Me again in an effort to document my experience, reinforce my knowledge of the topics, and improve my ability to concisely communicate the pentest lifecycle.

## Scenario

**Title**: Lian Yu

**Description**: Welcome to Lian_YU, this Arrowverse themed beginner CTF box! Capture the flags and have fun.

**Free/Subscriber**: Free

**Difficulty**: Easy

## Enumeration

![nmap initial](/assets/img/posts/thm-lianyu/nmap-initial.jpg)

There are four ports accessible on the target system from the initial nmap scan (top 1000 ports):
- 21 (FTP)
- 22 (SSH)
- 80 (HTTP)
- 111 (RCP)

From the service information for SSH, the target is an Ubuntu Linux target.

*I'm not too familiar with the RPC protocol along with the rpcinfo output but we can add it to our list of things to learn.*

### HTTP

As always, the first thing we should do with a web application is to explore it.

![index page](/assets/img/posts/thm-lianyu/index-page.jpg)

In this case, there doesn't appear to be anything other than an introduction to the room and an explanation of it being a Green Arrow themed room.

With no information in the page source, hyperlinked references, no robots.txt, let's move on to some directory enumeration using gobuster.

![gobuster index](/assets/img/posts/thm-lianyu/gobuster-index.jpg)

The directory enumeration scan returned one result for /island. Browsing to it,

![island index](/assets/img/posts/thm-lianyu/island-index.jpg)

There doesn't appear to be a code word. It may be hidden in the source code!

![island source](/assets/img/posts/thm-lianyu/island-source.jpg)

There we go! The code word is `vigilante`. Trying this out as a URL endpoint did not lead us anywhere. Nor did trying `vigilante:vigilante` for the FTP or SSH services. This may be useful later but let's perform a subsequent gobuster scan on the /island endpoint.

![gobuster island](/assets/img/posts/thm-lianyu/gobuster-island.jpg)

Ouuuu! Another hidden endpoint that probably has more information. However, there was nothing present to us on the actual page. Viewing the page source, there is a hint as a comment.

![2100 source](/assets/img/posts/thm-lianyu/2100-source.jpg)

*The first time I completed this room, I didn't know how to proceed from here so I viewed a hint on a walkthrough to make sense. It is a bit cryptic but thinking about it logically, it makes a bit of sense. On this /island/2100 endpoint, we can find our ticket with a .ticket extension.*

We can add the `-x` extension flag to gobuster to search for files with a .ticket extension.

![gobuster ticket](/assets/img/posts/thm-lianyu/gobuster-ticket.jpg)

We found the ticket! Checking it out, it is just a text file with the following content.

```
This is just a token to get into Queen's Gambit(Ship)


RTy8yhBQdscX
```

The token looks like it has some sort of encoding on it but I first tried using it as the password for the FTP and SSH services with the potential username, `vigilante`.

That didn't work so perhaps it is encoded. I tried the standard base64 encoding but when that failed, I used CyberChef to quickly try out a bunch of encodings.

![cyber chef](/assets/img/posts/thm-lianyu/cyberchef.jpg)

Base58 was the correct encoding scheme! Now, let's try to use the potential credentials `vigilant:!#th3h00d` to access the FTP or SSH services!

![ftp login listing](/assets/img/posts/thm-lianyu/ftp-login-listing.jpg)

The credentials granted us access to the FTP server. Listing the content in the directory, there are three images present. Let's download them onto our local system and begin to analyze them.

![PNG file format](/assets/img/posts/thm-lianyu/leave-me-alone-error.jpg)

For the first image file that we encountered, exiftool reports that the File format error is incorrect. Performing a hexdump of the first few lines which contains the header information, the first six bytes appear to be incorrect as they should be `8950 4e47 0d0a` [^png-header]. Using hexeditor, we can modify these first six bytes to match the correct PNG header format.

If we updated the bytes correctly, we should be able to view the image's metadata using exiftool.

![PNG file exiftool](/assets/img/posts/thm-lianyu/leave-me-alone-exiftool.jpg)

Great! Now, let's view the actual image.

![leave me alone](/assets/img/posts/thm-lianyu/leave-me-alone.jpg)

This may be useful for the other images but let's explore further.

## Initial Foothold

For JPEG images involving steganography, my go-to technique is to extract any hidden data using `steghide`. If it requests a passphrase, I use `stegseek` to crack the passphrase with the rockyou wordlist.

Using steghide on the aa.jpg image requested a passphrase. That is probably what the purpose of the previous image was for which we fixed the PNG header. Using `password` as the passphrase to the steghide prompt, the tool extracted the hidden data to ss.zip.

![steghide extract](/assets/img/posts/thm-lianyu/steghide-extract.jpg)

Unzipping the zip file, there are two files within it. The passwd.txt file does not actually contain any passwords or even a dump of the /etc/passwd file.

```
This is your visa to Land on Lian_Yu # Just for Fun ***


a small Note about it


Having spent years on the island, Oliver learned how to be resourceful and
set booby traps all over the island in the common event he ran into dangerous
people. The island is also home to many animals, including pheasants,
wild pigs and wolves.
```

The shado file's contents may be more helpful with a potential password.

```
M3tahuman
```

We already have the password for the vigilante user. There may be another user on the system that we haven't encountered so far.

Thinking back to the FTP server, the files were served from vigilante's home directory.

![slade ftp user](/assets/img/posts/thm-lianyu/slade-ftp-user.jpg)

We connected to the FTP server dropping into the home directory. Moving up a level and checking the users that have a home directory (alternatively reading the /etc/passwd file), we know that slade is another user.

Let's use the credentials `slade:M3tahuman` to try to authenticate to the target through SSH.

![slade login](/assets/img/posts/thm-lianyu/slade-login.jpg)

Success! We can grab the user.txt flag at /home/slade/user.txt and continue onto privilege escalation.

## Privilege Escalation

Listing out the sudo privileges of slade as we know his password.

![sudo privs](/assets/img/posts/thm-lianyu/sudo-privs.jpg)

With the ability to execute pkexec as sudo, we should be able to just pass /bin/bash as an argument to obtain root access [^gtfobins-pkexec].

![root](/assets/img/posts/thm-lianyu/root.jpg)

We can submit the contents of the root flag to THM and complete this room!

## References

[^png-header]: <https://en.wikipedia.org/wiki/Portable_Network_Graphics#/media/File:PNG-Gradient_hex.png>
[^gtfobins-pkexec]: <https://gtfobins.github.io/gtfobins/pkexec/#sudo>
