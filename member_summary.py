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
            elif ropes >= 250:
                category = 'Upper Medium'
            elif ropes >= 150:
                category = 'Lower Medium'
            elif ropes >= 75:
                category = 'Upper Small'
            else:
                category = 'Lower Small'
            
            members_by_category[category].append({
                'name': row.get('Member', ''),
                'group': row.get('Group', ''),
                'ropes': ropes,
                'kg': float(row.get('Total_KG', 0) or 0)
            })
        except:
            pass

# Sort each category by ropes (descending)
for category in members_by_category:
    members_by_category[category].sort(key=lambda x: x['ropes'], reverse=True)

order = ['Large Scale', 'Upper Medium', 'Lower Medium', 'Upper Small', 'Lower Small']

total_all = sum(len(members_by_category[cat]) for cat in members_by_category)
total_ropes_all = sum(sum(m['ropes'] for m in members_by_category[cat]) for cat in members_by_category)
total_kg_all = sum(sum(m['kg'] for m in members_by_category[cat]) for cat in members_by_category)

# Category summary table
print("="*100)
print("CATEGORY SUMMARY - TOTAL MEMBERS PER CATEGORY")
print("="*100)
print(f"{'Category':<20} {'Members':<12} {'Ropes':<15} {'Pct Ropes':<12} {'Kg':<15} {'Pct Kg':<12} {'Avg Ropes':<10}")
print("-"*100)

for category in order:
    if category in members_by_category:
        members = members_by_category[category]
        count = len(members)
        total_ropes = sum(m['ropes'] for m in members)
        total_kg = sum(m['kg'] for m in members)
        avg_ropes = total_ropes / count if count > 0 else 0
        pct_ropes = total_ropes / total_ropes_all * 100 if total_ropes_all > 0 else 0
        pct_kg = total_kg / total_kg_all * 100 if total_kg_all > 0 else 0
        
        print(f"{category:<20} {count:<12} {total_ropes:<15,} {pct_ropes:<11.1f}% {total_kg:<15,.1f} {pct_kg:<11.1f}% {avg_ropes:<10.0f}")

print("-"*100)
print(f"{'TOTAL':<20} {total_all:<12} {total_ropes_all:<15,} {100.0:<11.1f}% {total_kg_all:<15,.1f} {100.0:<11.1f}%")
print("="*100)

# Now show top 20 members ranked by ropes (all categories mixed)
print("\n" + "="*100)
print("TOP 20 MEMBERS RANKED BY OCEAN ROPES (LARGEST TO SMALLEST)")
print("="*100)
print(f"{'Rank':<6} {'Member':<35} {'Category':<20} {'Ropes':<10} {'Kg':<10}")
print("-"*100)

all_members = []
for category in members_by_category:
    all_members.extend([(m, category) for m in members_by_category[category]])

all_members.sort(key=lambda x: x[0]['ropes'], reverse=True)

for i, (member, category) in enumerate(all_members[:20], 1):
    print(f"{i:<6} {member['name']:<35} {category:<20} {member['ropes']:<10} {member['kg']:<10.1f}")

print("="*100)
