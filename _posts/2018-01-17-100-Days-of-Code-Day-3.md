---
layout: post
title: 100 Days of Code&#58; Day 3
comments: true
tags: [100 Days of Code, Python, Data Structures]
---

I have completed Day 3 of the 100 Days of Code and this is similar to Day 1 where the code written was minimal and the time it took to write the code was less than one hour. It's not difficult to find time but I'm going to try to take on more challenging projects in the next few days.

<!--more-->

## Projects

#### Deque

Today, I implemented a Deque similar to [Day 1](http://robingoyal.tech/blog/100-Days-of-Code-Day-1) where I implemented a Queue using another self-implemented Linked List class. This wasn't challenging either since the Deque operations are pretty basic which is the ability to add or remove nodes from the front or the back. Since the linked list class consists of the same operations just with different names (append, pop), I was just able to create new methods in Deque and call the necessary inherited methods.

[Link](https://github.com/robgoyal/PersonalAlgosDS/blob/master/DataStructures/Python/Deque.py) to the Deque source code.

## Challenges Faced

There weren't any challenges associated with creating a Deque implementation. I had some challenges with researching how to prevent child classes from inheriting unwanted methods. I don't think that it makes sense but I just wanted to see if it was possible to prevent calling certain inherited methods from an instance of a child class.

## Lessons Learned

Even though these classes are easy since I went through the difficult task of creating the Linked List class, it's reinforcing the concept of proper documentation for methods and classes. It's interesting to see your classes have official documentation when calling `help(Deque.Deque)` in the Python interpreter.
