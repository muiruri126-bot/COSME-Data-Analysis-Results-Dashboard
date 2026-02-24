"""
Fix all leading-space theme keys, empty icon params, emoji, and leading-space labels
in forestry_dashboard.py
"""
import re

filepath = 'forestry_dashboard.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

original = content

# 1. Fix theme key leading spaces
replacements = [
    ('" Forest Green"', '"Forest Green"'),
    ('" Ocean Blue"', '"Ocean Blue"'),
    ('" Sunset"', '"Sunset"'),
    ('" Earth Tones"', '"Earth Tones"'),
    ('" Professional"', '"Professional"'),
]
for old, new in replacements:
    content = content.replace(old, new)

# 2. Remove the ⏰ emoji
content = content.replace("'⏰'", "''")

# 3. Fix leading-space sidebar labels and radio options
label_replacements = [
    ('" Dataset View"', '"Dataset View"'),
    ('" Combined Overview"', '"Combined Overview"'),
    ('" Forestry Groups"', '"Forestry Groups"'),
    ('" Women Survey"', '"Women Survey"'),
    ('" Show Change (pp) Charts"', '"Show Change (pp) Charts"'),
    ('" Dashboard Theme"', '"Dashboard Theme"'),
]
for old, new in label_replacements:
    content = content.replace(old, new)

# 4. Fix leading-space error messages  
content = content.replace('f" Forestry Excel not found:', 'f"Forestry Excel not found:')
content = content.replace('f" Women Survey Excel not found:', 'f"Women Survey Excel not found:')

# 5. Fix leading-space sidebar markdown headers
content = content.replace('"** Quick Navigate**"', '"**Quick Navigate**"')
content = content.replace('"** Dataset Summary**"', '"**Dataset Summary**"')
content = content.replace('"** Datasets Loaded**"', '"**Datasets Loaded**"')

# 6. Fix leading-space in sidebar nav links and header titles
content = content.replace('> Overview & KPIs<', '>Overview & KPIs<')
content = content.replace('> Group Characteristics<', '>Group Characteristics<')
content = content.replace('> Governance & Gender<', '>Governance & Gender<')
content = content.replace('> Training & Assets<', '>Training & Assets<')
content = content.replace('> Forest Condition<', '>Forest Condition<')
content = content.replace('> Income & Agroforestry<', '>Income & Agroforestry<')
content = content.replace('> Household Profile<', '>Household Profile<')
content = content.replace('> Shocks & Preparedness<', '>Shocks & Preparedness<')
content = content.replace('> Assets & Savings<', '>Assets & Savings<')
content = content.replace('> Roles & Decisions<', '>Roles & Decisions<')
content = content.replace('> Climate & NbS<', '>Climate & NbS<')
content = content.replace('> Life Skills & Norms<', '>Life Skills & Norms<')
content = content.replace('> Forestry Headlines<', '>Forestry Headlines<')
content = content.replace('> Women Survey Headlines<', '>Women Survey Headlines<')
content = content.replace('> Comparative Snapshots<', '>Comparative Snapshots<')
content = content.replace('> Forestry Groups<', '>Forestry Groups<')
content = content.replace('> Women Survey<', '>Women Survey<')

# 7. Fix leading-space in main header h1 titles
content = content.replace('<h1> Community Forest Conservation Dashboard</h1>',
                         '<h1>Community Forest Conservation Dashboard</h1>')
content = content.replace("<h1> Women's Survey Dashboard</h1>",
                         "<h1>Women's Survey Dashboard</h1>")
content = content.replace('<h1> COSME Baseline', '<h1>COSME Baseline')

# 8. Fix breadcrumb leading spaces
content = content.replace('<span> COSME</span>', '<span>COSME</span>')
content = content.replace('<span class="active"> Forestry Groups</span>',
                         '<span class="active">Forestry Groups</span>')
content = content.replace('<span class="active"> Women Survey</span>',
                         '<span class="active">Women Survey</span>')
content = content.replace('<span class="active"> COSME', '<span class="active">COSME')

# 9. Fix tab labels with leading spaces
tab_fixes = [
    ('" Household Profile & Services"', '"Household Profile & Services"'),
    ('" Shocks, Coping & Preparedness"', '"Shocks, Coping & Preparedness"'),
    ('" Assets, Land, Savings & Loans"', '"Assets, Land, Savings & Loans"'),
    ('" Roles, Time Use & Decisions"', '"Roles, Time Use & Decisions"'),
    ('" Climate Change & NbS"', '"Climate Change & NbS"'),
    ('" Life Skills & Social Norms"', '"Life Skills & Social Norms"'),
]
for old, new in tab_fixes:
    content = content.replace(old, new)

# 10. Fix navigate deeper section
content = content.replace('<strong> Navigate deeper:</strong>', '<strong>Navigate deeper:</strong>')

# 11. Fix page_icon empty string
content = content.replace('page_icon=""', 'page_icon="bar_chart"')

# Count changes
changes = 0
for i, (c1, c2) in enumerate(zip(original, content)):
    if c1 != c2:
        changes += 1

print(f"Characters changed: {changes}")
print(f"Original length: {len(original)}")
print(f"New length: {len(content)}")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("File written successfully.")
