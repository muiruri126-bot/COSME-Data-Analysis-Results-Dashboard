import re
with open('forestry_dashboard.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines, 1):
    # Leading-space theme keys
    for key in ['" Forest Green"', '" Ocean Blue"', '" Sunset"', '" Earth Tones"', '" Professional"']:
        if key in line:
            print(f'THEME_KEY L{i}: {line.rstrip()[:120]}')
            break
    # Emoji
    if '\u23f0' in line:
        print(f'EMOJI L{i}: {line.rstrip()[:120]}')
    # Empty _section_header icon
    if "_section_header(''" in line or '_section_header("")' in line:
        print(f'EMPTY_ICON L{i}: {line.rstrip()[:120]}')
    # Leading space in radio/selectbox options
    if re.search(r'"\s+(Combined|Forestry|Women|Show|Dataset|Dashboard)', line):
        print(f'LEADING_SPACE L{i}: {line.rstrip()[:120]}')
print('---DONE---')
