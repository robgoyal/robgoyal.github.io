---
title: Agent Sudo (Try Hack Me)
author: Robin Goyal
date: 2021-08-26 19:00 -0400
categories: [Cybersecurity, Writeups]
tags: [thm, ctf, writeup, burpsuite, user-agents, web application, ftp, brute force, python, steganography, steghide, base64, 7z2john, jtr, password cracking]
hidden: true
image:
  src: https://tryhackme-images.s3.amazonaws.com/room-icons/aedc6b66c222e15ff740c282a0c3f44e.png
---

I am currently in the process of completing these boxes on Try Hack Me again in an effort to document my experience, reinforce my knowledge of the topics, and improve my ability to concisely communicate the pentest lifecycle.

Note: The target IP address may change throughout the writeup as I complete the room over a period of time.

## Scenario

**Title**: Agent Sudo

**Link**: https://tryhackme.com/room/agentsudoctf

**Description**: You found a secret server located under the deep sea. Your task is to hack inside the server and reveal the truth.

**Free/Subsciber**: Free

**Difficulty**: Easy


## Enumeration

First things first, let's start off with an nmap scan.

![nmap results](/assets/img/posts/thm-agent-sudo/nmap.jpg)

The target is an Ubuntu OS from information gained in the service version information for SSH and the Apache web server.

There are three open ports:
- 21 (FTP)
- 22 (SSH)
- 80 (HTTP)

### FTP

The FTP service does not allow anonymous authentication so we may not be able to do much unless we have potential usernames and passwords.

### SSH

No banner to grab so let's move on to the HTTP service.

### HTTP

![landing page](/assets/img/posts/thm-agent-sudo/landing-page.jpg)

The landing page contains a clue on how we are able to access the site. The user-agent string might be some letter from the alphabet potentially including the word agent.

#### Burpsuite Intruder

Let's generate a list and use Burpsuite's Intruder feature to see if any of the user-agent strings provide access to the website!

```python
import string

with open("useragents.txt", "w") as f:
    for letter in string.ascii_uppercase:
        f.write(letter + "\n")
        f.write("Agent " + letter + "\n")
```

The above code generated a list of the format:

```plaintext
A
Agent A
B
Agent B
...
...
```

With the payload position set for the user-agent in the Intruder attack, we'll load the generated list as potential payloads and launch the attack.

With the attack results, the payload with value "C" has a differing payload length size compared to the rest of the requests.

![burp suite attack](/assets/img/posts/thm-agent-sudo/burp-attack.jpg)

Right click on the request that stands out, scroll down to "Show response in browser", copy the URL, and open it in the browser. Burp will execute the exact request so you don't have to manually modify the request yourself.

![agent chris landing](/assets/img/posts/thm-agent-sudo/agent-chris.jpg)

There's a few pieces of interesting information on the landing page:
- There is a third agent, J
- Agent C's name is chris
- chris has a weak password

### FTP with Credentials

Attempting to brute force both the SSH service and FTP service, Hydra returned a password for Chris on the FTP service with a password of crystal.

![ftp creds](/assets/img/posts/thm-agent-sudo/hydra.jpg)

FTP credentials: `chris:crystal`

![ftp listing](/assets/img/posts/thm-agent-sudo/ftp.jpg)

There are two image files and a text file. The contents of the text file To_agentJ.txt:

```plaintext
Dear agent J,

All these alien like photos are fake! Agent R stored the real picture inside your directory. Your login password is somehow stored in the fake picture. It shouldn't be a problem for you.

From,
Agent C
```

So there is hidden data within the other two images that we might have to extract.

## Initial Foothold

### Steganography

For the first image, cutie.png, let's use the stegextract tool since it's a PNG file. The usual tool that I use, steghide, doesn't support PNG files.

![cutie.png extracted](/assets/img/posts/thm-agent-sudo/extracted.jpg)

So we found a ZIP file that can only be extracted using the 7z command. However, the zip file requires a password. Fortunately, we can brute force this using John the Ripper by converting the zip file into a hash through the zip2john tool.

![cutie.png zip cracked](/assets/img/posts/thm-agent-sudo/extracted-crack.jpg)

Success! The password for the zip file is `alien`. Within the zip file, there is a text file, To_agentR.txt, with the content

```plaintext
Agent C,

We need to send the picture to 'QXJlYTUx' as soon as possible!

By,
Agent R
```

That string looks like it is base64 encoded.

```bash
$ echo QXJlYTUx | base64 -d
Area51
```

Great! Let's move onto the second image, cutie-alien.jpg.

Since this is a JPEG image, we can use the steghide series of tools to determine if there is embedded data or not.

![jpeg steghide info](/assets/img/posts/thm-agent-sudo/steghide-info.jpg)

The steghide tool prompted us for a password. Instinctively trying out Area51 as the password, the tool informed us that there is a message.txt file hidden in the image! Let's extract it using

`steghide extract -sf cute-alien.jpg`

The contents of message.txt is

```plaintext
Hi james,

Glad you find this message. Your login password is hackerrules!

Don't ask me why the password look cheesy, ask agent R who set this password for you.

Your buddy,
chris
```

Looks like we are able to log into the server using the credentials `james:hackerrules!`.


Once authenticated to the SSH server, we find the flag in the home directory for james as user_flag.txt

User Flag: `b03d975e8c92a7c04146cfa7a5a313c7`

## Privilege Escalation

Let's check the sudo privileges of james.

![sudo privs](/assets/img/posts/thm-agent-sudo/sudo-privs.jpg)

The version of this sudo program is 1.8.21p2 which is susceptible to a vulnerability. The vulnerability focuses on the configuration of the user's sudo privileges (ALL, !root) where the sudo program doesn't check for the existence of thespecified user id and executes the non-existing id as sudo [^sudo-exploit].

The command `sudo -u#-1 /bin/bash` will escalate you to the root privileges.

![root flag](/assets/img/posts/thm-agent-sudo/root-flag.jpg)

Success! And the root flag was available at /root/root.txt.

Root Flag: `b53a02f55b57d4439e3341834d70c062`

## Reflection

This room was heavily focused on a CTF style which is fine but also took a while to kind of understand how to proceed through the different stages.

However, I learned a lot about extracting data hidden in PNG and JPEG images, brute forcing SSH and FTP services, and a privilege escalation vector that is focused on binaries that are not updated!

### Killchain Summary

1. Retrieve Agent R's note for Chris by brute forcing the user-agents on the web application.
2. Brute force the FTP service for the username chris knowing that he has a weak password.
3. Extract trailing ZIP file hidden in the PNG file.
4. Use zip2john and JTR with rockyou.txt to crack the password for the ZIP file.
5. Base64 decode the codeword in the ZIP file.
6. Use the decoded codeword as the password to the embedded data in the JPG file.
7. Authenticate to the SSH service with the credentials found in the embedded data.
8. Escalate privileges using `sudo -u#-1 /bin/bash`

### Misconfigurations

1. The codenames for the Agents should be more obscure than just the letters of the alphabet.
2. Password policies should not allow weak or common words as passwords.
3. Embedded data within images is not a secure method for transmitting information.
4. System should be updated to remove the sudo privilege escalation vulnerability.

### Summary of Exploits

#### Privilege Escalation

Specifically related to CVE-2019-14287, if the user's privileges are configured with `(ALL, !root) /bin/bash` and the SUDO version is prior to 1.8.28, privileges can be escalated by:

`sudo -u#-1 /bin/bash`

This allows users with sudo privileges to run commands as root even if the specification states that you can run as ALL users except root so long as the ALL keyword is specified [^sudo-exploit].

### Things I Learned

#### Steganography

Extract trailing data from a PNG file.

`stegextract cutie.png`

Bruteforce password cracking for a JPG file.

`stegseek cutie-alien.jpg /usr/share/wordlists/rockyou.txt`

#### Zip Cracking

To use John the Ripper to crack a zip file, we first need to convert it to something that John the Ripper can understand.

`zip2john cutie.zip > cutie.hash`
`john --wordlist=/usr/share/wordlists/rockyou.txt cutie.hash`

## References

[^sudo-exploit]: <https://www.exploit-db.com/exploits/47502>
