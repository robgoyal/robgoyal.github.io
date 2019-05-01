---
layout: post
title: List Comprehensions in Python
description: Using list comprehensions in Python
comments: True
tags: [python, introduction, tricks, comprehension]
---

A few weeks ago, I discussed a functional programming feature, `maps`. Maps are quite useful but sometimes they aren't as readable or as 'Pythonic'. Pythonic usually refers to code that is clear, concise and conforms to the conventions of the Python community. Near the bottom of this post, I'll discuss some differences between comprehensions and Maps. Let us dive into list comprehensions.

<!--more-->

# What are comprehensions?

Comprehensions are a Python construct which can create sequences from other sequences. It's possible to use comprehensions for lists, sets, and dictionaries.

## List Comprehensions

List comprehensions consist of several components:

- Input Sequence
- Iteration over Input Sequence
- Output Expression for new sequence
- Conditional Expression

The above components can be used to create powerful expressions.

List comprehensions create a list from another input sequence. Input sequences can be of type dictionary, list, tuple, set or any iterable. The output expression must be a valid expression which returns a value.

The syntax for list comprehension:

```
new_seq = [output_expression iteration_expression conditional_expression]
```

Let's break down this syntax:

- `[]` represents that we are creating a list
- output_expression is a valid expression which returns a value
- iteration_expression includes two specific elements, an input sequence and a variable to iterate over the input sequence
- conditional_expression is optional but if included, the output_expression value will only be added to the new list sequence if the conditional_expression is met

### Examples

#### Even Digits in a List

The following is an example of retrieving the even digits from an input sequence. Since we are checking to see if the digit is even, we require a conditional expression. We'll look at solutions which use a for loop, map and list comprehensions
##### For Loop

{% highlight python %}
even_values = []
for x in input_sequence:
    if x % 2 == 0:
        even_values.append(x)
{% endhighlight %}

##### Map

```python
even_values = list(map(lambda x: x if x % 2 == 0 else None, input_sequence))
```

The disadvantage of map is that a return value still must be provided for any odd values, which is None. It's possible to use filter to remove None values, something I will discuss in a future post.

##### List Comprehension

```python
even_values = [x for x in input_sequence if x % 2 == 0]
```

#### Length of Words in String

For this example, the input sequence is a string of words. Since we are not checking if the words meet a specific condition, we can opt out of the conditional expression.

##### For Loop

```python
word_lengths = []
for word in input_sequence.split():
    word_lengths.append(len(word))
```

##### Map

```python
word_lengths = list(map(lambda x: len(x), input_sequence.split()))
```

##### List Comprehension

```python
word_lengths = [len(word) for word in input_sequence.split()]
```

### Maps vs Comprehensions

Comprehensions are more readable than maps which is something I mentioned earlier. The main advantage of comprehensions over maps are that they are faster than maps. This is because map calls a function over each element in the input sequence. Function calls are expensive and should be used sparingly. Comprehensions only evaluate an expression and add it to a list structure which isn't as much overhead

## Reflection

It's clear that list comprehensions are the most readable and Pythonic construct for performing these types of procedures (creating a new sequence from original sequence). I think comprehensions are a great way for concise Python expressions with fast performance.

List comprehensions are a prime example of the cliched statement "With great power also comes great responsibility". Even though comprehensions are important constructs with many advantages, it's less concise when there are highly complex output expressions or if there are nested comprehensions. It's better to sacrifice performance for readability and use a for loop approach if possible.

## Extra Resources

For more information regarding comprehensions as well as performance comparison between the three approaches, check out this [blog post](https://www.analyticsvidhya.com/blog/2016/01/python-tutorial-list-comprehension-examples/)!
