#
import datetime
import pytz

title = input("Title: ")
platform = input("Platform (Try Hack Me, Hack the Box, etc): ")
author = "Robin Goyal"
image_src = input("Image Source: ")

# Capture correct time format
eastern_tz = pytz.timezone("US/Eastern")
current_datetime = datetime.datetime.now(eastern_tz)
current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M %z")

# Capture additional categories
categories = ["Cybersecurity", "Writeups"]
additional_categories = input("Categories: ")
for category in additional_categories.split(","):
    if category:
        categories.append(category.strip())

# Capture additional tags
tags = ["thm", "ctf", "writeup"]
additional_tags = input("Tags: ")
for tag in additional_tags.split(","):
    if tag:
        tags.append(tag.strip())

# Capture Scenario Information
scenario_title = title
scenario_description = input("Scenario Description: ")
scenario_difficulty = input("Scenario Difficulty: ")
scenario_link = input("Scenario Link: ")

if platform == "Try Hack Me":
    scenario_state_key = "Free/Subscriber"
    scenario_state_val = input(f"{scenario_state_key}: ")
elif platform == "Hack The Box":
    scenario_state_key = "Active/Retired"
    scenario_state_val = "Retired"

# Create Post Name
today = datetime.date.today()
platform_acronym = "".join([word[0] for word in platform.lower().split()])
title_lowered_dashed = "-".join(title.lower().split())
post_name = f"{today}-{platform_acronym}-{title_lowered_dashed}.md"

# Write Markdown Metadata
header = f"""---
title: {title} ({platform})
author: {author}
date: {current_datetime_str}
categories: [{', '.join(categories)}]
tags: [{', '.join(tags)}]
image:
  src: {image_src}
---
"""

# Write Scenario Information
scenario = f"""
## Scenario

**Title**: {scenario_title}

**Link**: {scenario_link}

**Description**: {scenario_description}

**{scenario_state_key}**: {scenario_state_val}

**Difficulty**: {scenario_difficulty}
"""

## Remaining Writeup Structure
body = f"""

## Enumeration

## Initial Foothold

## Privilege Escalation

## Useful Commands

## Reflection

### Killchain Summary

### Misconfigurations

### Summary of Exploits

### Things I Learned

## References
"""

with open(f"_posts/{post_name}", "w") as f:
    f.write(header)
    f.write(scenario)
    f.write(body)
