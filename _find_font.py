"""Upgrade all remaining inline chart font sizes to 13/16 for better visibility."""
import re

filepath = 'forestry_dashboard.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all update_layout calls and add/upgrade font settings
# We want to add font=dict(size=13, color='#333') to layouts missing it

lines = content.split('\n')
changed = 0
for i, line in enumerate(lines):
    # Skip already-fixed lines (the chart helpers)
    if i < 1170 or 'font=dict(size=13' in line:
        continue
    # Find update_layout lines in inline charts that are missing font params
    if 'update_layout(' in line and 'font=' not in line:
        # Check next 5 lines to see if font= is already set
        snippet = '\n'.join(lines[i:i+6])
        if 'font=' not in snippet:
            # Find the closing ')' of update_layout and add font before it
            # This is complex, so let's just flag it
            print(f'L{i+1}: {line.rstrip()[:120]}')
            changed += 1

print(f'\nTotal inline charts needing font upgrade: {changed}')
