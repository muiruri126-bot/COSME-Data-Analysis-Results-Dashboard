import csv
from collections import defaultdict

# Read the CSV
members_by_category = defaultdict(list)

with open('Book1.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            ropes = int(float(row.get('Ropes_Total', 0) or 0))
            
            # Categorize by ropes
            if ropes >= 350:
                category = 'Large Scale'
                icon = '🏆'
            elif ropes >= 250:
                category = 'Upper Medium'
                icon = '⭐'
            elif ropes >= 150:
                category = 'Lower Medium'
                icon = '📊'
            elif ropes >= 75:
                category = 'Upper Small'
                icon = '🌱'
            else:
                category = 'Lower Small'
                icon = '🌿'
            
            members_by_category[category].append({
                'name': row.get('Member', ''),
                'group': row.get('Group', ''),
                'ropes': ropes,
                'kg': float(row.get('Total_KG', 0) or 0),
                'icon': icon
            })
        except:
            pass

# Sort each category by ropes (descending)
for category in members_by_category:
    members_by_category[category].sort(key=lambda x: x['ropes'], reverse=True)

# Print summary
print("=" * 120)
print("MEMBER DISTRIBUTION BY FARMER PROFILE CATEGORY")
print("=" * 120)

order = ['Large Scale', 'Upper Medium', 'Lower Medium', 'Upper Small', 'Lower Small']

for category in order:
    if category in members_by_category:
        members = members_by_category[category]
        count = len(members)
        total_kg = sum(m['kg'] for m in members)
        total_ropes = sum(m['ropes'] for m in members)
        avg_ropes = total_ropes / count if count > 0 else 0
        avg_kg = total_kg / count if count > 0 else 0
        
        icon = members[0]['icon'] if members else ''
        print(f"\n{icon} {category}")
        print(f"   Total: {count} members | {total_ropes:,} ropes ({total_ropes/36596*100:.1f}%) | {total_kg:,.1f} kg ({total_kg/18792*100:.1f}%)")
        print(f"   Average: {avg_ropes:.0f} ropes/member | {avg_kg:.1f} kg/member")
        print(f"   {'─' * 116}")
        
        # Show all members in this category, ranked by ropes
        for i, member in enumerate(members, 1):
            print(f"      {i:3d}. {member['name']:35s} | {member['ropes']:4d} ropes | {member['kg']:8.1f} kg | {member['group']}")

print("\n" + "=" * 120)
total_all = sum(len(members_by_category[cat]) for cat in members_by_category)
total_ropes_all = sum(sum(m['ropes'] for m in members_by_category[cat]) for cat in members_by_category)
total_kg_all = sum(sum(m['kg'] for m in members_by_category[cat]) for cat in members_by_category)
print(f"GRAND TOTAL: {total_all} members | {total_ropes_all:,} ropes | {total_kg_all:,.1f} kg")
print("=" * 120)

# Category summary table
print("\nCATEGORY SUMMARY TABLE:")
print("─" * 120)
print(f"{'Category':<20} {'Members':<12} {'Ropes':<15} {'% of Ropes':<15} {'Kg':<15} {'% of KG':<15} {'Avg Ropes':<15}")
print("─" * 120)

for category in order:
    if category in members_by_category:
        members = members_by_category[category]
        count = len(members)
        total_ropes = sum(m['ropes'] for m in members)
        total_kg = sum(m['kg'] for m in members)
        avg_ropes = total_ropes / count if count > 0 else 0
        pct_ropes = total_ropes / total_ropes_all * 100
        pct_kg = total_kg / total_kg_all * 100
        
        print(f"{category:<20} {count:<12} {total_ropes:<15,} {pct_ropes:<14.1f}% {total_kg:<15,.1f} {pct_kg:<14.1f}% {avg_ropes:<15.0f}")

