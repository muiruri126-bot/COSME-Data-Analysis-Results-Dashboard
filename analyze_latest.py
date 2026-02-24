import csv
from collections import defaultdict

groups = defaultdict(lambda: {'members': 0, 'kg': 0, 'current_ropes': 0, 'target_ropes': 0})

with open('Book1.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        group = row.get('Group', '').strip()
        groups[group]['members'] += 1
        groups[group]['kg'] += float(row.get('Total_KG', 0) or 0)
        groups[group]['current_ropes'] += int(row.get('Ropes_Total', 0) or 0)
        groups[group]['target_ropes'] += int(row.get('Target_Ropes', 0) or 0)

total_members = sum(g['members'] for g in groups.values())
total_kg = sum(g['kg'] for g in groups.values())
total_current = sum(g['current_ropes'] for g in groups.values())
total_target = sum(g['target_ropes'] for g in groups.values())
gap = total_target - total_current

print("GROUP DATA:")
for group in sorted(groups.keys()):
    data = groups[group]
    print(f"{group}: Members={data['members']}, KG={data['kg']:.1f}, CurrentRopes={data['current_ropes']}, TargetRopes={data['target_ropes']}")

print(f"\nTOTALS: Members={total_members}, KG={total_kg:.1f}, CurrentRopes={total_current}, TargetRopes={total_target}, Gap={gap}")
