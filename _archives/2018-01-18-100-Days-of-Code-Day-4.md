---
layout: post
title: 100 Days of Code&#58; Day 4
comments: true
tags: [100 Days of Code, FreeCodeCamp, Web Development]
---

Day 4 has probably been the most challenging day so far. Along with struggling to send API requests, it's just been a mentally taxing day in my pursuit of learning software development.

<!--more-->

## Projects

#### Wikipedia Viewer

I was able to successfully send an API request with a single string to Wikipedia which returned the top 10 matching Wikipedia pages with little titles, snippets, and other meta information. The next step would be to read through the API to determine how to gather the corresponding pages links.

[Link](https://github.com/robgoyal/FreeCodeCamp/tree/master/FrontEndDevCert/IntermediateProjects/WikipediaViewer) to the project source code.

## Challenges Faced

This day was particularly challenging because I was constantly running into problems regarding Access-Control-Allow-Origin header not present in the request resource. I spent 40 - 45 min trying to solve this and trying to understand CORS requests. Nothing was working and I think it was disappointing to realize that three quarters of the hour was spent trying to solve something which still wasn't making complete sense to me.

## Lessons Learned

I was a bit stubborn and I thought that since I had little experience with sending web requests to API's before, I didn't need to read the official documentation for the Wikipedia API on how to send a request through javascript. I need to take the advice of the official documentation when working with external API's.
