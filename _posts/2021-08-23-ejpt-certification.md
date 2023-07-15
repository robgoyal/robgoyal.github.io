---
title: eJPT Certified!
author: Robin Goyal
date: 2021-08-23 8:30 -0400
categories: [Cybersecurity, Certifications]
tags: [eJPT, certification]
pin: true
image:
  src: /assets/img/posts/ejpt-certified/ejpt-certificate.jpg
---

This weekend, I decided to take eLearnSecurity's Junior Penetration Tester exam and I successfully passed it with a score of 19/20. 
Below is a quick post about the exam preparation, my experience, a bit of advice, and some thoughts on the exam.

## Motivation

I was searching for a low-cost introductory certification for penetration testing and several people on a few cybersecurity subreddits recommended it along with John Hammond rating it highly on his Youtube channel [^john-hammond]. 

This certification has been on my radar since early this summer and I am proud to say all the work and training that I have done has led to me passing the exam!

## My Preparation

This certification is accompanied by INE's (previously eLearnSecurity) Penetration Testing Student course which I will link in the Exam Details section below. This course does not expect any prerequisite knowledge and is capable of being the sole resource needed to pass the certification.

I took a slightly different approach in preparation for the exam. For each topic that I did not fully understand, I used TryHackMe to accompany that topic with an informational room or a CTF style room.
An example of this was using the [Overpass 2](https://tryhackme.com/room/overpass2hacked) room in THM to accompany the introduction of Wireshark in the PTS course. 
Overpass 2 is an interesting room where you are tasked with analyzing a packet capture, understanding how a hacker infiltrated the target machine, and using the knowledge gained to infiltrate the target machine yourself. 

**Side note! I think Try Hack Me is another fantastic resource and if you are able to get the paid subscription, it is worth it!**

This is not required but the experience gained through completing rooms to assist in specific topics or just building experience in the pentest lifecycle was valuable during the exam.

Once I felt I had enough experience, I began work on the three black-box pentest labs that are offered in the PTS course. Each of these labs contains a network range and several targets where you have to capture a "flag" on each. 
I approached each lab as if it was an exam scenario and only looked at the official writeup in two situations for minor hints as I had been stuck for 1 to 2 hours. 

The above practice provided me the confidence needed to scan and enumerate targets, perform exploitation techniques, privilege escalation, and comfortability with the various tools.

## Advice

### Preparation
You do not have to follow the same path that I took for the preparation. The PTS covers enough content and provides enough practice opportunities to pass the exam. 

I do recommend putting a heavy emphasis on the labs especially. Obtaining practical hands-on experience is critical to your success in this certification. If you are not able to complete it without going through the writeup, approach it again a few days later trying to complete it with your understanding of the topics.

Completing the black-box pentest labs forcing myself to explore every attack vector and not relying on the writeup is what I attribute a majority of my success to. 

**Note:** Programming knowledge is not required to pass the certification so don't fret if you're not a programming guru.

I found the black-box pentest labs of a higher difficulty than the exam itself so if you're able to complete those, the exam should be a piece of cake.

### Writing the Exam

Without providing too many details, be sure to thoroughly read the letter of engagement that is provided. Read the multiple choice questions a few times over prior to starting as the questions and answers will provide a guide on what information you are looking for.

Most importantly, take lots of breaks. This exam is not like the OCSP. You have three days to complete the exam so if you are feeling like you've hit a roadblock, take a break or maybe a nap and come back to it. 
During the exam, take notes about all of your findings and the commands you have written so you can review the information you have found.

Lastly, don't make the same mistake that I made and overthink every little detail. 

## Exam Details
Details of the exam:

- Cost: $200 USD 
- Duration: 3 Days
- Exam Structure: Multiple Choice
- Passing Grade: 15/20 (75%)
- Certification Link: <https://elearnsecurity.com/product/ejpt-certification/>
- PTS Link: <https://my.ine.com/CyberSecurity/learning-paths/a223968e-3a74-45ed-884d-2d16760b8bbd/penetration-testing-student>

Exam topics to ensure you understand in no particular order:
- Network Scanning
- Target Enumeration
- Information Gathering and Reconnaissance
- Pivoting
- Routing
- Web Application Attacks:
  - XSS
  - SQL Injection
  - Directory Enumeration
- Password Cracking
- Service Authentication Cracking

It's also important to get comfortable with the tools that are covered in the course. 

## Conclusion

I can honestly say I have never enjoyed an exam as much as this one. I cannot overstate the quality of the course materials and certification process than the eLearnSecurity and INE have laid out. I highly recommend it as an introductory certification to anyone interesting in cybersecurity. 

Reach out to me if you have any questions about the certification, course, or anything else!

## References

[^john-hammond]: <https://www.youtube.com/watch?v=CmBeSsCn0zM>
