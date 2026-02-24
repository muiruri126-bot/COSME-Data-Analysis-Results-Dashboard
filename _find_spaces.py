import re
lines = open('forestry_dashboard.py','r',encoding='utf-8').readlines()
for i, line in enumerate(lines):
    # Find quoted strings with leading space followed by uppercase letter
    matches = re.findall(r'["\'](\s[A-Z][^"\']*)["\']', line)
    if matches and not line.strip().startswith('#'):
        for m in matches:
            print(f'L{i+1}: "{m}" -> {line.strip()[:100]}')
