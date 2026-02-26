#!/bin/sh
# Quick backup of Dashboard before making changes
# Usage: ./backup-dashboard.sh [optional-label]
# Creates: backups/Women_Survey_Professional_Dashboard_2026-02-26_label.html

FILE="Women_Survey_Professional_Dashboard.html"
DIR="backups"
LABEL="${1:-manual}"
TIMESTAMP=$(date +%Y-%m-%d_%H%M%S)
BACKUP="${DIR}/${FILE%.html}_${TIMESTAMP}_${LABEL}.html"

mkdir -p "$DIR"
cp "$FILE" "$BACKUP"

LINES=$(wc -l < "$BACKUP" | tr -d ' ')
SIZE=$(stat -c%s "$BACKUP" 2>/dev/null || stat -f%z "$BACKUP")

echo "Backup created: $BACKUP"
echo "  Lines: $LINES | Size: $SIZE bytes"
echo "  Restore with: cp \"$BACKUP\" \"$FILE\""
