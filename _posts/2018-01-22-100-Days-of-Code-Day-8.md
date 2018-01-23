---
layout: post
title: 100 Days of Code&#58; Day 8
comments: true
tags: [100 Days of Code, Python, Algorithms]
---

Day 8 wasn't the best day for working on my projects. I was supposed to work on the styles for the Wikipedia Viewer but I got lazy and decided to work on some creating some algorithms for my personal data structures and algorithms which was much easier.

<!--more-->

## Projects

#### Searching

As part of designing my own personal algorithms and data structures strictly by definition and not viewing other code, I set a goal to create algorithms for linear and binary search. These algorithms weren't as complex for me to solve since I knew about them before and had written code for them a while ago.

Linear search is a brute force searching algorithm which loops over the entire sequence and looks for the item until it reaches the end at which point it assumes the item isn't in the list.

Binary search takes it one step further in improving the runtime of the search algorithm at the condition that the sequence is sorted. The process at which binary search looks for numbers is that it views the item at the middle of the sequence, and checks if the value that we're looking for is equal to, less than, or greater than that item. If it's equal to, we'll exit the algorithm, otherwise we'll look into the right half or left half the list. We continue this process until we find the item or there's no item to be found.

[Link](https://github.com/robgoyal/PersonalAlgosDS/blob/master/Searching/Python/linearSearch.py) to linear search.

[Link](https://github.com/robgoyal/PersonalAlgosDS/blob/master/Searching/Python/binarySearch.py) to binary search.

## Challenges Faced

At one point, I was stuck writing the solution for the binary search algorithm. I think I was too focused on trying to recreate the algorithm from memory since I had done it before instead of actually understanding what the process of binary search was doing. I was messing up the updating of the two pointer variables which kept track of the subsection of the sequence that I was currently viewing.

## Lessons Learned

Sometimes, I just don't want to write code for websites especially when it comes to styling since I have zero design ability. But as a horrific perfectionist, I can't move on from the Wikipedia Viewer project until I complete the CSS. In the future, it might be more beneficial to work on the style at the same time as when I'm creating the HTML elements instead of at the end.
