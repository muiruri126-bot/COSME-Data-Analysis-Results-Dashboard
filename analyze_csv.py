#!/usr/bin/env python3
import csv
from collections import defaultdict

group_totals = defaultdict(lambda: {'members': 0, 'total_kg': 0, 'current_ropes': 0, 'target_ropes': 0, 'ocean': 0, 'home': 0})

with open('Book1.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        group = row['Group']
        if not group:
            continue
        group_totals[group]['members'] += 1
        group_totals[group]['total_kg'] += float(row['Total_KG'] or 0)
        group_totals[group]['current_ropes'] += float(row['Ropes_Total'] or 0)
        group_totals[group]['target_ropes'] += float(row['Target_Ropes'] or 0)
        group_totals[group]['ocean'] += float(row['Ropes_Ocean'] or 0)
        group_totals[group]['home'] += float(row['Ropes_Home'] or 0)

print('=== ACTUAL CSV TOTALS ===\n')
for group in sorted(group_totals.keys()):
    d = group_totals[group]
    gap = d['target_ropes'] - d['current_ropes']
    print(f'{group}:')
    print(f'  Members: {d["members"]}')
    print(f'  Total KG: {d["total_kg"]:.1f}')
    print(f'  Current Ropes: {d["current_ropes"]:.0f}')
    print(f'  Target Ropes: {d["target_ropes"]:.0f}')
    print(f'  Gap: {gap:.0f}')
    print()

total_members = sum(d['members'] for d in group_totals.values())
total_kg = sum(d['total_kg'] for d in group_totals.values())
total_current = sum(d['current_ropes'] for d in group_totals.values())
total_target = sum(d['target_ropes'] for d in group_totals.values())

print('\n=== GRAND TOTALS ===')
print(f'Total Members: {total_members}')
print(f'Total KG: {total_kg:.1f}')
print(f'Total Current Ropes: {total_current:.0f}')
print(f'Total Target Ropes: {total_target:.0f}')
print(f'Total Rope Gap: {total_target - total_current:.0f}')
