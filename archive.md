---
layout: page
title: Archive
permalink: /archive/
description: "An archive of posts sorted by year"
---

<section class="archive-post-list">
    {% for post in site.posts %}
        {% assign currentDate = post.date | date: "%Y" %}
        {% if currentDate != myDate %}
            {% unless forloop.first %}</ul>{% endunless %}
            <h3>{{ currentDate }}</h3>
            <ul>
            {% assign myDate = currentDate %}
        {% endif %}
        <li><span class="monospace-date">{{ post.date | date_to_string }}</span> &raquo; <a href="{{ post.url }}">{{ post.title }}</a></li>
        {% if forloop.last %}</ul>{% endif %}
    {% endfor %}
</section>
