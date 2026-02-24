"""Utility script: strip all emojis from forestry_dashboard.py."""
import re

with open('forestry_dashboard.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove ALL emoji characters
emoji_pat = re.compile(
    '['
    '\U0001F300-\U0001F9FF'
    '\U00002702-\U000027B0'
    '\U0000FE00-\U0000FE0F'
    '\U0000200D'
    '\U00002600-\U000026FF'
    '\U00002B05-\U00002B55'
    ']+', re.UNICODE)

cleaned = emoji_pat.sub('', content)

# Collapse multiple spaces left behind
cleaned = re.sub(r'  +', ' ', cleaned)

# Fix theme dict keys where emoji was part of the key string
cleaned = cleaned.replace('" Forest Green"', '"Forest Green"')
cleaned = cleaned.replace('" Ocean Blue"', '"Ocean Blue"')
cleaned = cleaned.replace('" Sunset"', '"Sunset"')
cleaned = cleaned.replace('" Earth Tones"', '"Earth Tones"')
cleaned = cleaned.replace('" Professional"', '"Professional"')
# Single-quote variant for default COLORS
cleaned = cleaned.replace("' Forest Green'", "'Forest Green'")

# Fix default COLORS reference
cleaned = cleaned.replace('THEMES[" Forest Green"]', 'THEMES["Forest Green"]')

with open('forestry_dashboard.py', 'w', encoding='utf-8') as f:
    f.write(cleaned)

# Verify
with open('forestry_dashboard.py', 'r', encoding='utf-8') as f:
    verify = f.read()
remaining = emoji_pat.findall(verify)
print(f'Emojis remaining: {len(remaining)}')
if remaining:
    for e in sorted(set(remaining)):
        print(f'  {repr(e)}')
print(f'Lines: {len(verify.splitlines())}')
print('Done - all emojis removed')
