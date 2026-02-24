import re
from collections import defaultdict

# Read the HTML file
with open('result_dashboard (19).html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Extract the member rankings section
start_marker = '📋 Member Rankings by Farmer Profile Category'
end_marker = '</div>\n      </div>\n\n      <div style="background: white;'

start_idx = html_content.find(start_marker)
if start_idx == -1:
    print("Could not find the member rankings section")
    exit()

# Find where the section starts with actual data
section_start = html_content.find('<div style="display: grid; gap: 10px;', start_idx)
section_end = html_content.find('      </div>\n      </div>\n\n      <div style="background: white; color: #2c3e50; padding: 25px">', start_idx + 100)

rankings_html = html_content[section_start:section_end]

# Extract member data using regex
# Pattern to match: rank, name with group, category, ocean ropes
pattern = r'#(\d+)\</div>\s*<div[^>]*>([^<]+)<br/><span[^>]*>\(([^)]+)\)</span></div>\s*<div[^>]*background: ([^;]+);[^>]*>([^<]+)</div>\s*<div[^>]*>(\d+)</div>'

members = []
for match in re.finditer(pattern, rankings_html):
    rank = int(match.group(1))
    name = match.group(2).strip()
    group = match.group(3).strip()
    # Extract category from the color-coded div
    category_text = match.group(5).strip()
    
    ocean_ropes = int(match.group(6))
    
    members.append({
        'rank': rank,
        'name': name,
        'group': group,
        'category': category_text,
        'ocean_ropes': ocean_ropes
    })

# Also try a different approach - look for all category positions
categories = defaultdict(list)

# Find all instances of category colors in the rankings section
large_scale_pattern = r'(<div[^>]*background: #1565c0;[^>]*>Large Scale</div>\s*<div[^>]*>(\d+)</div>)'
upper_medium_pattern = r'(<div[^>]*background: #1976d2;[^>]*>Upper Medium</div>\s*<div[^>]*>(\d+)</div>)'
lower_medium_pattern = r'(<div[^>]*background: #0288d1;[^>]*>Lower Medium</div>\s*<div[^>]*>(\d+)</div>)'

large_count = len(re.findall(r'background: #1565c0;[^>]*>Large Scale</div>', rankings_html))
upper_count = len(re.findall(r'background: #1976d2;[^>]*>Upper Medium</div>', rankings_html))
lower_count = len(re.findall(r'background: #0288d1;[^>]*>Lower Medium</div>', rankings_html))

print("=" * 80)
print("MEMBER RANKINGS ANALYSIS")
print("=" * 80)
print(f"\nFound {len(members)} members in rankings table\n")

if members:
    print("DETAILED MEMBER LIST:")
    print("-" * 80)
    for m in sorted(members, key=lambda x: x['rank'])[:30]:  # Show first 30
        print(f"#{m['rank']:2d} | {m['name']:25s} | {m['category']:15s} | {m['ocean_ropes']:4d} ropes | {m['group']}")

# Count by category (from HTML structure)
print("\n" + "=" * 80)
print("SUMMARY BY CATEGORY (from HTML structure)")
print("=" * 80)
print(f"🏆 Large Scale:    {large_count} members")
print(f"⭐ Upper Medium:   {upper_count} members")
print(f"📊 Lower Medium:   {lower_count} members")
print(f"\nTotal visible in top 50+: {large_count + upper_count + lower_count} members")

# Expected total
print("\n" + "=" * 80)
print("NOTES: The table should have 335 total members across all categories")
print("Currently displayed above are representative top rankings")
print("=" * 80)
