---
layout: post
title: Introduction to Recursion
decription: Basics of recursion
comments: True
tags: [python, recursion, introduction]
---

While completing the set of videos from the second week of MIT's [Introduction to Computer Science and Programming Using Python](https://www.edx.org/course/introduction-computer-science-mitx-6-00-1x-11) course, I was introduced to recursion. I had heard of recursion before but I wanted to share my understanding of the topic.

<!--more-->


### Introduction

Recursion is a technique used in programming to solve problems which fall under a divide and conquer paradigm. This paradigm revolves around the idea that the solution to a problem will depend on smaller solutions of the same problem. The most common application of recursion in computer science is a recursive function. A recursive function is when a function is called within the function definition. 

Recursion is used to break a problem down to the simplest case which can be solved. As a result recursive functions have two properties associated with them. These properties are: 

- Base case
- Recursive case

The base case will cause the function to exit if it is met. If the base case is not met, the recursive case is executed which should lead us one step closer to the base case.

### Examples

#### Factorial

Calculating the [factorial](https://en.wikipedia.org/wiki/Factorial) of a number can be achieved using recursion. Any value that is passed to the function which is greater than 1 will reach the recursive case, where each function call will eventually reach the base case. 

{% highlight python %}
def factorial(n):

    # Base case
    if n == 1:
        return 1

    # Recursive case
    return n * factorial(n - 1)

factorial(5)
{% endhighlight %}

The expected return value from factorial (5) should be 120 since 5*4*3*2*1 = 120. 
Going through a sample walkthrough of how this works should make it more clear. Using an example input of 5, the factorial of 5 is 5 x 4 x 3 x 2 x 1 = 120. 

- factorial (5) = 5 * factorial (4)
- factorial (5) = 5 * (4 * factorial (3))
- factorial (5) = 5 * (4 * (3 * factorial (2)))
- factorial (5) = 5 * (4 * (3 * (2 * factorial (1))))
- factorial (5) = 5 * (4 * (3 * (2 * (1)))) = 120

In the first call of the function, the base case is not met so we call the factorial function again. The function calls continue until the base case is met. Once the base case is met, the function begins to return the values and break out of each function call. The final call returned a value that is equivalent to the mathematical calculation above. 

### Iteration vs Recursion
Iteration is very similar to recursion but it doesn't require any function calls. The same recursive function for the factorial problem can be written as an iterative solution as well. 

{% highlight python %}
def factorial(n):
    
    # Initialize variable to hold product 
    product = 1

    # Decrementing step size for range
    for i in range(n, 0, -1):
        product *= i

    return product

factorial(5)
{% endhighlight %}

This is an equivalent function in recursion but requires some extra steps such as initializing a variable, defining a range for the iteration, and performing the product calculation. 

### Dangers
Recursive functions are dangerous if the recursive calls do not eventually reach the base case. This can result in infinite recursion since each execution of the function will continue to call the function. Even if infinite recursion does not occur, a large amount of recursive function calls can overload the stack space and cause stack overflow **. 

** In a future post, I will go over stack space and stack overflow.

### Reflection

Recursive functions are elegant solutions and are quite succint in nature. In the factorial example, the recursive implementation required no initialization for variables, no for loops and was easy to understand. This isn't always the case with recursion and can be difficult to read if the problem which is being broken down is more complex. Recursive functions utilize more memory resources whereas iteration can be a more efficient approach with memory restrictions. Ultimately, the approach to take is dependent on the requirements and functionality of the program. 

<aside class="notice">
Hopefully, you enjoyed my first article at discussing and explaining a specific topic. This may have done more harm than good but with practice, I aim to achieve a level of clarity which will allow me to break down even the most complex of topics. I'm very receptive to any comments and discussions regarding this article or anything else you may like. 
</aside>
