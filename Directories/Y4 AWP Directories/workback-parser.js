// ─── Workback Schedule Parser ────────────────────────────────
const XLSX = require('xlsx');
const path = require('path');

function parseWorkbackSchedule() {
    const filePath = path.join(__dirname, 'COSME Y3 AR and Y4 AWP_Workback Schedule.xlsx');
    const wb = XLSX.readFile(filePath, { cellStyles: true });
    const ws = wb.Sheets['Sheet1'];
    const data = XLSX.utils.sheet_to_json(ws, { header: 1, defval: '' });

    // Row 1 has month start dates (Excel serial numbers) at merged ranges
    // Cols 2-29 = month 1, 30-60 = month 2, etc.
    const months = [];
    const monthBoundaries = [
        { start: 2, end: 29 },
        { start: 30, end: 60 },
        { start: 61, end: 90 },
        { start: 91, end: 121 }
    ];

    monthBoundaries.forEach(b => {
        const serial = data[1] ? data[1][b.start] : '';
        let label = '';
        if (typeof serial === 'number') {
            const d = XLSX.SSF.parse_date_code(serial);
            const monthNames = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
            label = `${monthNames[d.m - 1]} ${d.y}`;
        }
        months.push({ label, startCol: b.start, endCol: b.end });
    });

    // Row 2 has week numbers (1, 2, 3... up to ~28 per month)
    const weekNumbers = data[2] || [];

    // Build total weeks array with month context
    const weeks = [];
    for (let col = 2; col <= 121; col++) {
        const weekNum = weekNumbers[col];
        const month = months.find(m => col >= m.startCol && col <= m.endCol);
        if (weekNum !== '' && weekNum !== undefined) {
            weeks.push({
                col,
                weekNum,
                monthLabel: month ? month.label : ''
            });
        }
    }

    // Parse sections and tasks (rows 3 to ~93)
    const sections = [];
    let currentSection = null;
    const sectionHeaders = [
        'Workplan Narrative', 'Partner Workplans', 'Budget',
        'Y3 AR', 'Narrative Report', 'Partner Narrative Reports',
        'Financial Report'
    ];

    for (let i = 2; i < Math.min(data.length, 95); i++) {
        const row = data[i];
        const taskName = String(row[0] || '').trim();
        if (!taskName) continue;

        // Check if it's a section header
        const isSection = sectionHeaders.some(s => taskName.startsWith(s)) ||
                         (taskName === 'Budget') ||
                         (i === 2 && taskName === 'Workplan Narrative');

        if (isSection) {
            currentSection = { name: taskName, tasks: [] };
            sections.push(currentSection);
            continue;
        }

        // Skip legend/holiday rows
        if (taskName === 'Legend' || taskName === 'Weekend' || taskName === 'Holiday' ||
            taskName.startsWith('Holidays in') || taskName.startsWith('Important') ||
            taskName.match(/^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s/)) continue;

        // It's a task row — find which weeks are marked
        const markedWeeks = [];
        for (let col = 2; col <= 121; col++) {
            const val = row[col];
            if (val !== '' && val !== undefined && val !== null) {
                const week = weeks.find(w => w.col === col);
                if (week) {
                    markedWeeks.push({
                        weekNum: week.weekNum,
                        monthLabel: week.monthLabel,
                        col
                    });
                }
            }
        }

        if (currentSection) {
            currentSection.tasks.push({
                name: taskName,
                markedWeeks,
                rowIndex: i
            });
        }
    }

    return { months, weeks, sections };
}

module.exports = { parseWorkbackSchedule };
