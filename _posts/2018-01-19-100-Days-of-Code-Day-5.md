---
layout: post
title: 100 Days of Code&#58; Day 5
comments: true
tags: [100 Days of Code, FreeCodeCamp, Web Development]
---

Day 5 consisted of more work on the Wikipedia Viewer project and it was definitely less stressful than Day 4.

<!--more-->

## Projects

#### Wikipedia Viewer

I was able to determine a process for referencing links to the pages returned from the API request. You can type in the URL en.wikipedia.org/curid=pageid into the browser where pageid is an ID to a Wikipedia page and it'll return that page. This is useful since I won't need to make a second API request for URL's for each pageid.

The next step was to determine how to submit the form through keydown event for the enter key as well as clicking submit. Finally, I added the input field value into the request for the API so that upon submitting the form, the results will be displayed in the console (for now).

[Link](https://github.com/robgoyal/FreeCodeCamp/tree/master/FrontEndDevCert/IntermediateProjects/WikipediaViewer) to the project source code.

## Challenges Faced

More challenges arose for this project even after overcoming the cross domain request issue. I wasn't able to fully grasp the semantics of the Wikipedia API for requesting properties of the returned pages. Apparently, I had to make a second request adding on some additional parameters to the original search but I wasn't retrieving the expected results. After some googling, a user posted that adding curid=pageid will return the necessary page.

## Lessons Learned

Today was a lot of trial and error with the Sandbox API and general research by using stackoverflow. My limited experience with Javascript and web development is proving to be a challenge but that's the whole purpose of learning web development through FreeCodeCamp. Since I'm not looking to be a web developer, this is purely a process to learn to problem solve and at least learn Javascript so I could potentially be a backend developer.

Learning to be a software developer is a long process and I'm really excited to become one but I just need to be patient. Solving problems using programming languages is proving to be a lot of fun.
