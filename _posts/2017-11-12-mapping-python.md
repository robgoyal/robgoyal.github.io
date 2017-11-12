---
layout: post
title: Maps in Python
decription: Using maps in Python
comments: True
tags: [python, functional, introduction, map]
---

Python supports many programming paradigms, one of which is functional programming. Without diving too deep into the intracacies of the functional programming paradigm, we'll discuss a key feature of functional programming which is maps.

<!--more-->

Maps are a higher order function which applies a specific function to a list and returns a new list. This is useful when you want to apply a set of the same operations to all elements of a list.

Let's look at some progressions of using the mapping concept to Python as well as some examples.

## Basic Python Mapping 

```python
def square(x):
    '''
    x: number

    output: number squared
    '''
    return x ** 2

def square_list(L, func):
    '''
    L: list of numbers
    func: function to apply to a number

    output: return a new list
    '''
    
    new_list = []
    for element in L:
        new_list.append(func(element))

    return new_list

print(square_list([1, 2, 3, 4]), square)
>>> [1, 4, 9, 16]
```

The square_list function accepts two arguments, a list of numbers and a function to apply a number. It iterates over the list of numbers L and applies func to each element. The returned value from func is appended to an initialized list and that list is returned after all elements have been squared.

### Map function

Python has a built in function called map which can perform the same functionality that the above example holds.

```python
def square(x):
    '''
    x: number

    output: number squared
    '''
    return x ** 2

result = list(map(square, [1, 2, 3, 4]))
print(result)
>>> [1, 4, 9, 16]
```
The map function creates an iterator with the results of each element of the list squared. The list function creates a list from the iterator.

The above example only applied a single input to the function passed as an argument to map. Let's look at an example with two inputs as an argument to the function. 

```python
def multiply(x, y):
    '''
    x, y: numbers

    output: the multiplication of x and y
    '''

    return x * y

result = list(map(multiply, [1, 4, 7], [2, 5, 8]))
print(result)
>>> [2, 20, 56]
```

`multiply` takes two arguments and returns the multiplied values. This shows that we could pass two lists to `map` so long as the function passed to `map` as an argument takes two arguments. This extends to any number of iterators so long as the number of iterators matches the number of arguments in the function.

### Lambda Functions

Lambda functions are similar to anonymous functions in javascript. There is no name associated with the function. It simply takes some arguments and returns a result. Let's try to convert the above functions into lambda expression. 

```python
result = list(map(lambda x: x ** 2, [1, 2, 3, 4]))
print(result)
>>> [1, 4, 9, 16]
```

Lambda functions must be simple functions. 

Lambda functions can also take multiple variables. 

```python
result = list(map(lambda x, y: x * y, [1, 4, 7], [2, 5, 8]))
print(result)
>>> [2, 20, 56]
```

## Reflection

Hopefully this gentle introduction provides an idea of some of the capabilities of using `map` in Python. Some other functional programming ideas to look into are [filter](https://docs.python.org/3.6/library/functions.html#filter) and [reduce](https://docs.python.org/3/library/functools.html#functools.reduce). These topics may be covered in future blog posts. 